from __future__ import annotations

import glob
import os

from arg_ai.db import connect


MIGRATIONS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "..", "..", "migrations")


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
    migrations = sorted(glob.glob(os.path.join(MIGRATIONS_DIR, "*.sql")))
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
