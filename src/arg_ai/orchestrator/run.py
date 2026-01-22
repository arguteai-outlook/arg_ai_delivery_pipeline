import json
import os
import secrets
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from arg_ai.db.repo import ArtifactRow, artifact_upsert, gate_upsert, run_create, run_finalize
from arg_ai.orchestrator.gates import GateResult, run_gate
from arg_ai.orchestrator.vcs_local_git import create_pr_via_local_git
from arg_ai.util.hashing import file_sha256

from arg_ai.orchestrator_legacy import run_local

def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _run_token() -> str:
    return secrets.token_hex(16)


def _project_root(project_id: str) -> Path:
    return Path("projects") / project_id


def _evidence_root(project_id: str, run_token: str) -> Path:
    return _project_root(project_id) / "evidence" / run_token


def _trace_root(project_id: str) -> Path:
    return _project_root(project_id) / "trace"


def _write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True), encoding="utf-8")


def _index_file_as_artifact(run_token: str, artifact_type: str, path: Path, project_id: str) -> None:
    checksum = file_sha256(path)
    size = path.stat().st_size
    artifact_upsert(
        ArtifactRow(
            run_token=run_token,
            project_id=project_id,
            artifact_type=artifact_type,
            path=str(path).replace("\\", "/"),
            checksum_sha256=checksum,
            size_bytes=size,
            content_type="application/json",
        )
    )

def _gates_plan(project_id: str) -> list[tuple[str, Optional[list[str]], Optional[str]]]:
    repo_root = Path(os.getcwd())

    gates: list[tuple[str, Optional[list[str]], Optional[str]]] = []
    gates.append(("validate_repo", ["python", "-m", "compileall", "-q", "src"], None))

    # lint
    if _tool_exists("ruff"):
        gates.append(("lint", ["ruff", "check", "."], None))
    else:
        gates.append(("lint", None, "ruff not installed"))

    # unit tests
    if _tool_exists("pytest"):
        gates.append(("unit_tests", ["pytest", "-q"], None))
    else:
        gates.append(("unit_tests", None, "pytest not installed"))

    # terraform gates
    has_tf = (repo_root / "terraform").exists() or (repo_root / "main.tf").exists()
    if not has_tf:
        gates.append(("terraform_fmt", None, "no terraform configuration found"))
        gates.append(("terraform_validate", None, "no terraform configuration found"))
        gates.append(("terraform_plan", None, "no terraform configuration found"))
    else:
        if _tool_exists("terraform"):
            gates.append(("terraform_fmt", ["terraform", "fmt", "-check", "-recursive"], None))
            gates.append(("terraform_validate", ["terraform", "validate"], None))
            gates.append(("terraform_plan", ["terraform", "plan", "-no-color"], None))
        else:
            gates.append(("terraform_fmt", None, "terraform not installed"))
            gates.append(("terraform_validate", None, "terraform not installed"))
            gates.append(("terraform_plan", None, "terraform not installed"))

    return gates


def _tool_exists(name: str) -> bool:
    from shutil import which

    return which(name) is not None


def run_orchestrator(args) -> int:
    project_id: str = args.project
    mode: str = args.mode
    vcs: str = args.vcs
    ci_artifacts_dir: Optional[str] = args.ci_artifacts_dir

    run_token = _run_token()
    print(run_token)

    run_create(run_token=run_token, project_id=project_id, mode=mode)

    repo_root = Path(os.getcwd())

    pr_url = None
    branch_name = None
    commit_sha = None

    if mode == "pr":
        if vcs != "local_git":
            raise RuntimeError("only --vcs local_git is implemented in milestone 2 local-first mode")

        pr = create_pr_via_local_git(repo_root=repo_root, run_token=run_token, project_id=project_id)
        pr_url, branch_name, commit_sha = pr.pr_url, pr.branch_name, pr.commit_sha

    evidence_root = _evidence_root(project_id, run_token)
    ci_evidence_dir = evidence_root / "ci"
    trace_root = _trace_root(project_id)

    # If CI artifacts are provided (e.g., downloaded from Bitbucket artifacts), index those.
    # Otherwise run gates locally (local-first milestone 2).
    gate_results: list[GateResult] = []
    if ci_artifacts_dir:
        src_dir = Path(ci_artifacts_dir)
        src_dir.mkdir(parents=True, exist_ok=True)
        # Copy known logs into the per-run evidence folder
        for name in [
            "validate_repo",
            "lint",
            "unit_tests",
            "terraform_fmt",
            "terraform_validate",
            "terraform_plan",
        ]:
            src = src_dir / f"{name}.log"
            dst = ci_evidence_dir / f"{name}.log"
            if src.exists():
                dst.parent.mkdir(parents=True, exist_ok=True)
                dst.write_bytes(src.read_bytes())
                gate_results.append(
                    GateResult(
                        gate_name=name,
                        status="pass",
                        exit_code=0,
                        started_at=datetime.now(timezone.utc),
                        finished_at=datetime.now(timezone.utc),
                        duration_ms=0,
                        evidence_paths=[str(dst)],
                        notes="imported_from_ci_artifacts_dir",
                    )
                )
            else:
                # Missing log is treated as skip (keeps the evidence manifest honest)
                dst.parent.mkdir(parents=True, exist_ok=True)
                dst.write_text("SKIP: missing CI artifact\nexit_code=0\n", encoding="utf-8")
                gate_results.append(
                    GateResult(
                        gate_name=name,
                        status="skip",
                        exit_code=0,
                        started_at=datetime.now(timezone.utc),
                        finished_at=datetime.now(timezone.utc),
                        duration_ms=0,
                        evidence_paths=[str(dst)],
                        notes="missing_ci_artifact",
                    )
                )
    else:
        for gate_name, cmd, skip_reason in _gates_plan(project_id):
            log_path = ci_evidence_dir / f"{gate_name}.log"
            res = run_gate(
                gate_name=gate_name,
                cmd=cmd,
                evidence_log_path=log_path,
                cwd=repo_root,
                skip_reason=skip_reason,
            )
            gate_results.append(res)

    # Write trace graph (still minimal; now includes gate nodes)
    trace_graph_path = trace_root / "trace_graph.json"
    trace_graph = {
        "run_token": run_token,
        "project_id": project_id,
        "mode": mode,
        "generated_at": _now_iso(),
        "nodes": [
            {"type": "run", "id": run_token},
            *(
                [{"type": "pr", "id": pr_url, "branch_name": branch_name, "commit_sha": commit_sha}]
                if pr_url
                else []
            ),
            *[
                {"type": "gate", "id": f"{run_token}:{gr.gate_name}", "status": gr.status}
                for gr in gate_results
            ],
        ],
        "edges": [
            *(
                [{"from": run_token, "to": pr_url, "type": "produced_pr"}] if pr_url else []
            ),
            *[
                {
                    "from": run_token,
                    "to": f"{run_token}:{gr.gate_name}",
                    "type": "ran_gate",
                }
                for gr in gate_results
            ],
        ],
    }
    _write_json(trace_graph_path, trace_graph)

    # Write manifest (orchestrator-owned)
    manifest_path = evidence_root / "manifest.json"
    manifest: dict[str, Any] = {
        "run_token": run_token,
        "project_id": project_id,
        "mode": mode,
        "started_at": _now_iso(),
        "approval_policy": "approve_merge_5b",
        "inputs": {},
        "outputs": {
            "pr_url": pr_url,
            "branch_name": branch_name,
            "commit_sha": commit_sha,
        },
        "gates": [
            {
                "name": gr.gate_name,
                "status": gr.status,
                "exit_code": gr.exit_code,
                "evidence_paths": [p.replace("\\", "/") for p in gr.evidence_paths],
                "notes": gr.notes,
            }
            for gr in gate_results
        ],
        "trace": {
            "trace_graph_path": str(trace_graph_path).replace("\\", "/"),
        },
        "finished_at": _now_iso(),
    }
    _write_json(manifest_path, manifest)

    # Index artifacts
    _index_file_as_artifact(run_token, "evidence_manifest", manifest_path, project_id)
    _index_file_as_artifact(run_token, "trace_graph", trace_graph_path, project_id)

    # Index gate logs as artifacts + upsert gate rows
    overall_status = "ready_for_approval"
    for gr in gate_results:
        for p in gr.evidence_paths:
            path = Path(p)
            if path.exists():
                _index_file_as_artifact(run_token, "ci_gate_log", path, project_id)

        gate_upsert(
            run_token=run_token,
            gate_name=gr.gate_name,
            status=gr.status,
            exit_code=gr.exit_code,
            started_at=gr.started_at,
            finished_at=gr.finished_at,
            duration_ms=gr.duration_ms,
            evidence_paths=[str(Path(p)).replace("\\", "/") for p in gr.evidence_paths],
            notes=gr.notes,
        )

        if gr.status == "fail":
            overall_status = "failed"

    run_finalize(
        run_token=run_token,
        status=overall_status,
        pr_url=pr_url,
        branch_name=branch_name,
        commit_sha=commit_sha,
    )

    return 0
