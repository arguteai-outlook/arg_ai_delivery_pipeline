#!/usr/bin/env bash
set -euo pipefail

docker compose up -d

python -m venv .venv
# Git Bash on Windows:
# shellcheck disable=SC1091
source .venv/Scripts/activate

pip install -U pip
pip install -e ".[dev]"

python -m arg_ai db migrate

python -m arg_ai run --project ses_email_pilot --mode pr --vcs local_git

echo ""
echo "Inspect DB (requires psql installed locally):"
echo "  psql \"postgresql://arg_ai:arg_ai@localhost:5432/arg_ai\" -c \"SELECT run_token, mode, pr_url, commit_sha FROM runs ORDER BY created_at DESC LIMIT 3;\""
echo "  psql \"postgresql://arg_ai:arg_ai@localhost:5432/arg_ai\" -c \"SELECT gate_name, status, exit_code FROM gates WHERE run_token = (SELECT run_token FROM runs ORDER BY created_at DESC LIMIT 1) ORDER BY gate_name;\""
