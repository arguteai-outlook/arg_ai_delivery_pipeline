CREATE TABLE IF NOT EXISTS gates (
  gate_id BIGSERIAL PRIMARY KEY,
  run_token TEXT NOT NULL REFERENCES runs(run_token) ON DELETE CASCADE,
  gate_name TEXT NOT NULL,
  status TEXT NOT NULL,
  exit_code INTEGER,
  started_at TIMESTAMPTZ,
  finished_at TIMESTAMPTZ,
  duration_ms INTEGER,
  evidence_paths JSONB NOT NULL DEFAULT '[]'::JSONB,
  notes TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE UNIQUE INDEX IF NOT EXISTS gates_run_token_gate_name_ux
ON gates (run_token, gate_name);

CREATE INDEX IF NOT EXISTS gates_run_token_ix
ON gates (run_token);

CREATE INDEX IF NOT EXISTS gates_status_ix
ON gates (status);
