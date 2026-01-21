import argparse

from arg_ai.db.migrate import migrate_db
from arg_ai.db.verify import verify_db_schema
from arg_ai.orchestrator.run import run_orchestrator

def main() -> int:
    parser = argparse.ArgumentParser(prog="arg_ai")
    sub = parser.add_subparsers(dest="command", required=True)

    db = sub.add_parser("db")
    db_sub = db.add_subparsers(dest="db_command", required=True)

    db_migrate = db_sub.add_parser("migrate")
    db_migrate.set_defaults(fn=lambda _args: migrate_db())

    db_verify = db_sub.add_parser("verify")
    db_verify.set_defaults(fn=lambda _args: verify_db_schema())
    
    run = sub.add_parser("run")
    run.add_argument("--project", required=True)
    run.add_argument("--mode", choices=["local", "pr"], default="local")
    run.add_argument("--vcs", choices=["local_git"], default="local_git")
    run.add_argument("--ci_artifacts_dir", default=None)
    run.set_defaults(fn=lambda args: run_orchestrator(args))

    args = parser.parse_args()
    return int(args.fn(args))
