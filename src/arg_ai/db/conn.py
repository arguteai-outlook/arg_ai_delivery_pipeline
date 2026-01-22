"""
Connection helper.

This file exists so arg_ai.db.conn can become the long-term home of DB connectivity.
In the short term, arg_ai.db.__init__ will prefer db_legacy.connect if it exists.
"""

from __future__ import annotations

import os
from contextlib import contextmanager
from typing import Iterator, Tuple

import psycopg


def connect() -> psycopg.Connection:
    host = os.environ.get("ARG_AI_DB_HOST", "localhost")
    port = int(os.environ.get("ARG_AI_DB_PORT", "5432"))
    dbname = os.environ.get("ARG_AI_DB_NAME", "arg_ai")
    user = os.environ.get("ARG_AI_DB_USER", "arg_ai")
    password = os.environ.get("ARG_AI_DB_PASSWORD", "arg_ai")
    return psycopg.connect(host=host, port=port, dbname=dbname, user=user, password=password)


@contextmanager
def get_conn() -> Iterator[Tuple[psycopg.Connection, psycopg.Cursor]]:
    conn = connect()
    try:
        with conn.cursor() as cur:
            yield conn, cur
    finally:
        conn.close()
