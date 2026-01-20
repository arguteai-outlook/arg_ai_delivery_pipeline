from __future__ import annotations

import os
from datetime import datetime, timezone

from arg_ai.db import connect
from arg_ai.migrate import migrate
from arg_ai.util import file_size, make_run_token, sha256_file, write_json


def run_local(project_id: str) -> None:
    # Ensure DB is ready and schema is present (keeps demo single-command friendly).
    migrate()

    run_token = make_run_token()
    now = datetime.now(timezone.utc).isoformat()

    manifest_path = os.path.join("projects", project_id, "evidence", run_token, "manifest.json")
    trace_graph_path = os.path.join("projects", project_id, "trace", "trace_graph.json")

    manifest = {
        "run_token": run_token,
        "project_id": project_id,
        "created_at": now,
        "approval_policy": {"exists": True, "executed": False},
        "inputs": [],
        "outputs": [
            {"type": "evidence_manifest", "path": manifest_path},
            {"type": "trace_graph", "path": trace_graph_path},
        ],
        "gates": [],
        "notes": "milestone_1_stub",
    }

    trace_graph = {
        "project_id": project_id,
        "updated_at": now,
        "last_run_token": run_token,
        "nodes": [],
        "edges": [],
        "notes": "milestone_1_stub",
    }

    write_json(manifest_path, manifest)
    write_json(trace_graph_path, trace_graph)

    manifest_checksum = sha256_file(manifest_path)
    trace_checksum = sha256_file(trace_graph_path)

    manifest_size = file_size(manifest_path)
    trace_size = file_size(trace_graph_path)

    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO runs (run_token, project_id, status, created_at)
                VALUES (%s, %s, %s, NOW())
                """,
                (run_token, project_id, "created"),
            )

            # upsert artifacts for this run
            cur.execute(
                """
                INSERT INTO artifacts (
                    run_token, project_id, artifact_type, path,
                    checksum_sha256, size_bytes, content_type,
                    created_at, updated_at
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
                ON CONFLICT (run_token, path) DO UPDATE SET
                    artifact_type = EXCLUDED.artifact_type,
                    checksum_sha256 = EXCLUDED.checksum_sha256,
                    size_bytes = EXCLUDED.size_bytes,
                    content_type = EXCLUDED.content_type,
                    updated_at = NOW()
                """,
                (
                    run_token,
                    project_id,
                    "evidence_manifest",
                    manifest_path,
                    manifest_checksum,
                    manifest_size,
                    "application/json",
                ),
            )

            cur.execute(
                """
                INSERT INTO artifacts (
                    run_token, project_id, artifact_type, path,
                    checksum_sha256, size_bytes, content_type,
                    created_at, updated_at
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
                ON CONFLICT (run_token, path) DO UPDATE SET
                    artifact_type = EXCLUDED.artifact_type,
                    checksum_sha256 = EXCLUDED.checksum_sha256,
                    size_bytes = EXCLUDED.size_bytes,
                    content_type = EXCLUDED.content_type,
                    updated_at = NOW()
                """,
                (
                    run_token,
                    project_id,
                    "trace_graph",
                    trace_graph_path,
                    trace_checksum,
                    trace_size,
                    "application/json",
                ),
            )

        conn.commit()

    # Minimal, deterministic console output (useful for scripting later).
    print(run_token)
