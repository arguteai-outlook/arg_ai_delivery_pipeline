import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class PrInfo:
    pr_url: str
    branch_name: str
    commit_sha: str


def _git(args: list[str], repo_root: Path) -> str:
    proc = subprocess.run(
        ["git", *args],
        cwd=str(repo_root),
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed: {proc.stderr.strip()}")
    return (proc.stdout or "").strip()


def create_pr_via_local_git(repo_root: Path, run_token: str, project_id: str) -> PrInfo:
    _ = _git(["rev-parse", "--is-inside-work-tree"], repo_root)

    branch = f"arg_ai/run_{run_token}"
    _git(["checkout", "-b", branch], repo_root)

    # Commit a tiny canonical doc note (tracked) so the PR has a diff.
    note_path = repo_root / "projects" / project_id / "docs" / "run_notes" / f"{run_token}.md"
    note_path.parent.mkdir(parents=True, exist_ok=True)
    note_path.write_text(
        f"# Run Note\n\nrun_token: {run_token}\nproject_id: {project_id}\n\n",
        encoding="utf-8",
    )

    _git(["add", str(note_path)], repo_root)
    _git(["commit", "-m", f"arg_ai: run note {run_token}"], repo_root)

    commit_sha = _git(["rev-parse", "HEAD"], repo_root)
    pr_url = f"local://{branch}"

    return PrInfo(pr_url=pr_url, branch_name=branch, commit_sha=commit_sha)
