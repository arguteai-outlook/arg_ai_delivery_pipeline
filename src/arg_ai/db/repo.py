import json
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Optional

from arg_ai.db.conn import get_conn


@dataclass(frozen=True)
class ArtifactRow:
    run_token: str
    artifact_type: str
    path: str
    sha256: str
    size_bytes: int
    metadata: dict[str, Any]


def run_create(run_token: str, project_id: str, mode: str) -> None:
    with get_conn() as (conn, cur):
        cur.execute(
            """
            INSERT INTO runs (
              run_token, project_id, status, mode, created_at, updated_at, finished_at
            )
            VALUES (%s, %s, %s, %s, NOW(), NOW(), NULL)
            ON CONFLICT (run_token) DO UPDATE
            SET status = EXCLUDED.status,
                mode = EXCLUDED.mode,
                updated_at = NOW();
            """,
            (run_token, project_id, "running", mode),
        )
        conn.commit()


def run_finalize(
    run_token: str,
    status: str,
    pr_url: Optional[str] = None,
    branch_name: Optional[str] = None,
    commit_sha: Optional[str] = None,
) -> None:
    with get_conn() as (conn, cur):
        cur.execute(
            """
            UPDATE runs
            SET status = %s,
                pr_url = COALESCE(%s, pr_url),
                branch_name = COALESCE(%s, branch_name),
                commit_sha = COALESCE(%s, commit_sha),
                updated_at = NOW(),
                finished_at = NOW()
            WHERE run_token = %s;
            """,
            (status, pr_url, branch_name, commit_sha, run_token),
        )
        conn.commit()


def artifact_upsert(row: ArtifactRow) -> None:
    with get_conn() as (conn, cur):
        cur.execute(
            """
            INSERT INTO artifacts (run_token, artifact_type, path, sha256, size_bytes, metadata_json, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s::JSONB, NOW(), NOW())
            ON CONFLICT (run_token, path) DO UPDATE
            SET artifact_type = EXCLUDED.artifact_type,
                sha256 = EXCLUDED.sha256,
                size_bytes = EXCLUDED.size_bytes,
                metadata_json = EXCLUDED.metadata_json,
                updated_at = NOW();
            """,
            (
                row.run_token,
                row.artifact_type,
                row.path,
                row.sha256,
                row.size_bytes,
                json.dumps(row.metadata),
            ),
        )
        conn.commit()


def gate_upsert(
    run_token: str,
    gate_name: str,
    status: str,
    exit_code: Optional[int],
    started_at: Optional[datetime],
    finished_at: Optional[datetime],
    duration_ms: Optional[int],
    evidence_paths: list[str],
    notes: Optional[str],
) -> None:
    started_at = started_at or datetime.now(timezone.utc)
    finished_at = finished_at or datetime.now(timezone.utc)
    with get_conn() as (conn, cur):
        cur.execute(
            """
            INSERT INTO gates (
              run_token, gate_name, status, exit_code, started_at, finished_at, duration_ms, evidence_paths, notes, created_at, updated_at
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s::JSONB, %s, NOW(), NOW())
            ON CONFLICT (run_token, gate_name) DO UPDATE
            SET status = EXCLUDED.status,
                exit_code = EXCLUDED.exit_code,
                started_at = EXCLUDED.started_at,
                finished_at = EXCLUDED.finished_at,
                duration_ms = EXCLUDED.duration_ms,
                evidence_paths = EXCLUDED.evidence_paths,
                notes = EXCLUDED.notes,
                updated_at = NOW();
            """,
            (
                run_token,
                gate_name,
                status,
                exit_code,
                started_at,
                finished_at,
                duration_ms,
                json.dumps(evidence_paths),
                notes,
            ),
        )
        conn.commit()
