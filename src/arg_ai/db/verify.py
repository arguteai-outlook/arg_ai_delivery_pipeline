from __future__ import annotations

from dataclasses import dataclass

from arg_ai.db.conn import get_conn


@dataclass(frozen=True)
class VerifyIssue:
    table_name: str
    issue: str


EXPECTED_COLUMNS: dict[str, set[str]] = {
    "schema_migrations": {"version", "applied_at"},
    "runs": {
        "run_token",
        "project_id",
        "status",
        "mode",
        "pr_url",
        "branch_name",
        "commit_sha",
        "created_at",
        "updated_at",
        "finished_at",
    },
    "artifacts": {
        "run_token",
        "artifact_type",
        "path",
        "sha256",
        "size_bytes",
        "metadata_json",
        "created_at",
        "updated_at",
    },
    "gates": {
        "gate_id",
        "run_token",
        "gate_name",
        "status",
        "exit_code",
        "started_at",
        "finished_at",
        "duration_ms",
        "evidence_paths",
        "notes",
        "created_at",
        "updated_at",
    },
}


def verify_db_schema() -> int:
    issues: list[VerifyIssue] = []

    with get_conn() as (_conn, cur):
        for table_name, expected_cols in EXPECTED_COLUMNS.items():
            cur.execute(
                """
                SELECT column_name
                FROM information_schema.columns
                WHERE table_schema = 'public'
                  AND table_name = %s
                ORDER BY column_name;
                """,
                (table_name,),
            )
            rows = cur.fetchall()
            if not rows:
                issues.append(VerifyIssue(table_name, "missing_table"))
                continue

            actual = {r[0] for r in rows}
            missing = sorted(expected_cols - actual)
            extra = sorted(actual - expected_cols)

            if missing:
                issues.append(VerifyIssue(table_name, f"missing_columns: {', '.join(missing)}"))
            if extra:
                issues.append(VerifyIssue(table_name, f"extra_columns: {', '.join(extra)}"))

    if issues:
        for i in issues:
            print(f"{i.table_name}: {i.issue}")
        return 2

    print("db schema verify: ok")
    return 0
