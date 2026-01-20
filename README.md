# arg_ai_delivery_pipeline (Milestone 1)

Milestone 1 goal: local "Hello Run" demo.

## Prereqs
- Docker Desktop (docker compose available)
- Python 3.10+ (Windows)
- Git Bash recommended on Windows

## Quick start (Git Bash)

```bash

# 1) Start Postgres
docker compose up -d

# 2) Create venv + install (editable)
python -m venv .venv
source .venv/Scripts/activate
python -m pip install --upgrade pip
pip install -e .

# 3) Apply migrations
python -m arg_ai db migrate

# 4) Run "Hello Run" (prints run_token)
python -m arg_ai run --project ses_email_pilot

# 5) Verify outputs (replace <run_token>)
ls -la projects/ses_email_pilot/evidence/<run_token>/manifest.json
ls -la projects/ses_email_pilot/trace/trace_graph.json

cat projects/ses_email_pilot/evidence/<run_token>/manifest.json
cat projects/ses_email_pilot/trace/trace_graph.json

# 6) Verify Postgres rows
docker exec -it arg_ai_postgres psql -U arg_ai -d arg_ai -c "\dt"
docker exec -it arg_ai_postgres psql -U arg_ai -d arg_ai -c "SELECT run_token, project_id, status, created_at FROM runs ORDER BY created_at DESC LIMIT 5;"
docker exec -it arg_ai_postgres psql -U arg_ai -d arg_ai -c "SELECT run_token, artifact_type, path, checksum_sha256, size_bytes FROM artifacts ORDER BY artifact_id DESC LIMIT 10;"
