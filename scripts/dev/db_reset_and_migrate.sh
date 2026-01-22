#!/usr/bin/env bash
set -euo pipefail

docker compose down -v
docker compose up -d

# Wait for Postgres to accept connections (no guessing / no sleep-only)
echo "Waiting for Postgres to be ready..."
for i in {1..60}; do
  if docker exec arg_ai_postgres pg_isready -U arg_ai -d arg_ai >/dev/null 2>&1; then
    echo "Postgres is ready."
    break
  fi
  if [ "$i" -eq 60 ]; then
    echo "ERROR: Postgres did not become ready in time."
    docker logs arg_ai_postgres --tail 200 || true
    exit 1
  fi
  sleep 1
done

python -m arg_ai db migrate

# If verify is wired:
python -m arg_ai db verify
