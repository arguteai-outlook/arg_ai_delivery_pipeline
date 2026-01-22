"""
arg_ai.db package

Expose stable DB entrypoints at the package level to avoid import churn.
"""

# Prefer the legacy module if present (keeps existing behavior).
try:
    from arg_ai.db_legacy import connect  # type: ignore  # noqa: F401
except Exception:
    # Fallback to a future package-native implementation.
    from arg_ai.db.conn import connect  # type: ignore  # noqa: F401
