CREATE INDEX IF NOT EXISTS idx_runs_project_created_at ON runs (project_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_artifacts_run_token ON artifacts (run_token);
CREATE INDEX IF NOT EXISTS idx_artifacts_project_path ON artifacts (project_id, path);
