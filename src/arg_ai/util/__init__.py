"""
arg_ai.util package

Stable utility namespace. Keep public helpers importable from arg_ai.util.
"""
try:
    from arg_ai.util_legacy import *  # noqa: F403,F401
except Exception:
    pass
