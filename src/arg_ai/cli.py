import argparse


def _db_migrate_cmd() -> int:
    from arg_ai.db.migrate import migrate_db

    return int(migrate_db())


def _db_verify_cmd() -> int:
    from arg_ai.db.verify import verify_db_schema

    return int(verify_db_schema())


def _run_cmd(args) -> int:
    from arg_ai.orchestrator.run import run_orchestrator

    return int(run_orchestrator(args))


def main() -> int:
    parser = argparse.ArgumentParser(prog="arg_ai")
    sub = parser.add_subparsers(dest="command", required=True)

    db = sub.add_parser("db")
    db_sub = db.add_subparsers(dest="db_command", required=True)

    db_migrate = db_sub.add_parser("migrate")
    db_migrate.set_defaults(fn=lambda _args: _db_migrate_cmd())

    db_verify = db_sub.add_parser("verify")
    db_verify.set_defaults(fn=lambda _args: _db_verify_cmd())

    run = sub.add_parser("run")
    run.add_argument("--project", required=True)
    run.add_argument("--mode", choices=["local", "pr"], default="local")
    run.add_argument("--vcs", choices=["local_git"], default="local_git")
    run.add_argument("--ci_artifacts_dir", default=None)
    run.set_defaults(fn=_run_cmd)

    args = parser.parse_args()
    return int(args.fn(args))
