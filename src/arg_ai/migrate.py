from __future__ import annotations

import glob
import os

from arg_ai.db import connect


def _ensure_migrations_table(conn) -> None:
    with conn.cursor() as cur:
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS schema_migrations (
                version TEXT PRIMARY KEY,
                applied_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            );
            """
        )
    conn.commit()


def migrate() -> None:
    # Milestone 1: migrations are repo-local and Git-canonical.
    # Assumption: commands are run from repo root.
    migrations_dir = os.path.join(os.getcwd(), "migrations")
    migrations = sorted(glob.glob(os.path.join(migrations_dir, "*.sql")))

    if not migrations:
        raise RuntimeError(f"no migrations found in: {migrations_dir}")

    with connect() as conn:
        _ensure_migrations_table(conn)

        with conn.cursor() as cur:
            cur.execute("SELECT version FROM schema_migrations;")
            applied = {row[0] for row in cur.fetchall()}

        for path in migrations:
            version = os.path.basename(path)
            if version in applied:
                continue

            with open(path, "r", encoding="utf-8") as f:
                sql = f.read()

            with conn.cursor() as cur:
                cur.execute(sql)
                cur.execute("INSERT INTO schema_migrations (version) VALUES (%s);", (version,))
            conn.commit()
