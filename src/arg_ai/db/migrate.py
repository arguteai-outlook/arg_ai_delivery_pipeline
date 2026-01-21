import os
from pathlib import Path

from arg_ai.db.conn import get_conn


def migrate_db() -> int:
    root = Path(os.getcwd())
    mig_dir = root / "migrations"
    if not mig_dir.exists():
        raise RuntimeError(f"migrations directory not found at {mig_dir}")

    sql_files = sorted(mig_dir.glob("*.sql"))
    if not sql_files:
        raise RuntimeError(f"no migrations found in {mig_dir}")

    with get_conn() as (conn, cur):
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS schema_migrations (
              version TEXT PRIMARY KEY,
              applied_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            );
            """
        )

        cur.execute("SELECT version FROM schema_migrations;")
        applied = {row[0] for row in cur.fetchall()}

        for f in sql_files:
            version = f.name
            if version in applied:
                continue
            sql = f.read_text(encoding="utf-8")
            cur.execute(sql)
            cur.execute(
                "INSERT INTO schema_migrations (version) VALUES (%s);",
                (version,),
            )

        conn.commit()

    return 0
