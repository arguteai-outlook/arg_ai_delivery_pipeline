#!/usr/bin/env bash
set -euo pipefail

# Milestone 1: deterministic local demo runner (Git Bash friendly)

docker compose up -d

if [ ! -d ".venv" ]; then
  python -m venv .venv
fi

# shellcheck disable=SC1091
source .venv/Scripts/activate

python -m pip install --upgrade pip
pip install -e .

python -m arg_ai db migrate

echo "Running hello-run..."
run_token="$(python -m arg_ai run --project ses_email_pilot)"
echo "run_token=${run_token}"

echo "Verifying files..."
test -f "projects/ses_email_pilot/evidence/${run_token}/manifest.json"
test -f "projects/ses_email_pilot/trace/trace_graph.json"

echo "Verifying database..."
docker exec -it arg_ai_postgres psql -U arg_ai -d arg_ai -c "SELECT run_token, project_id, status, created_at FROM runs WHERE run_token='${run_token}';"
docker exec -it arg_ai_postgres psql -U arg_ai -d arg_ai -c "SELECT artifact_type, path, checksum_sha256, size_bytes FROM artifacts WHERE run_token='${run_token}' ORDER BY artifact_id;"

echo "OK"