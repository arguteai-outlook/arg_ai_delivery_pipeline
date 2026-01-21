import os
from contextlib import contextmanager

import psycopg


def _dsn() -> str:
    return os.getenv("ARG_AI_DB_DSN", "postgresql://arg_ai:arg_ai@localhost:5432/arg_ai")


@contextmanager
def get_conn():
    with psycopg.connect(_dsn()) as conn:
        with conn.cursor() as cur:
            yield conn, cur
