import argparse

from arg_ai.migrate import migrate
from arg_ai.orchestrator import run_local


def main() -> int:
    parser = argparse.ArgumentParser(prog="arg_ai")
    sub = parser.add_subparsers(dest="command", required=True)

    p_db = sub.add_parser("db", help="database utilities")
    db_sub = p_db.add_subparsers(dest="db_command", required=True)
    db_sub.add_parser("migrate", help="apply migrations").set_defaults(_fn=lambda _a: migrate())

    p_run = sub.add_parser("run", help="run orchestrator (local hello-run for milestone 1)")
    p_run.add_argument("--project", required=True, help="project_id (e.g. ses_email_pilot)")
    p_run.set_defaults(_fn=lambda a: run_local(project_id=a.project))

    args = parser.parse_args()
    return int(args._fn(args) or 0)
