"""
Compatibility shim.

Some legacy modules import `arg_ai.migrate`. The canonical migration entrypoint
is now `arg_ai.db.migrate.migrate_db`.

Keep this shim until all legacy imports are removed.
"""

from __future__ import annotations

from arg_ai.db.migrate import migrate_db


def migrate(*_args, **_kwargs) -> int:
    # Keep signature permissive for legacy callers.
    return migrate_db()
