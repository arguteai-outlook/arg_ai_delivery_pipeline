from contextlib import contextmanager
from typing import Iterator

import psycopg

from arg_ai.config import get_db_config


@contextmanager
def connect() -> Iterator["psycopg.Connection"]:
    cfg = get_db_config()
    conn = psycopg.connect(cfg.dsn)
    try:
        yield conn
    finally:
        conn.close()
