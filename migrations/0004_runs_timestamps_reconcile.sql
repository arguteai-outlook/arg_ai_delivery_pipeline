BEGIN;

-- Ensure both operational and domain timestamps exist
ALTER TABLE runs
ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ;

ALTER TABLE runs
ADD COLUMN IF NOT EXISTS finished_at TIMESTAMPTZ;

-- updated_at should always exist and reflect row mutation time
ALTER TABLE runs
ALTER COLUMN updated_at SET DEFAULT NOW();

UPDATE runs
SET updated_at = COALESCE(updated_at, created_at, NOW())
WHERE updated_at IS NULL;

ALTER TABLE runs
ALTER COLUMN updated_at SET NOT NULL;

-- finished_at should be NULL until the run is finalized.
-- If an earlier schema mistakenly set DEFAULT NOW(), remove it.
ALTER TABLE runs
ALTER COLUMN finished_at DROP DEFAULT;

-- Clean up rows that were created with finished_at defaulting to NOW()
-- Keep finished_at only for terminal statuses.
UPDATE runs
SET finished_at = NULL
WHERE status IN ('running')
  AND finished_at IS NOT NULL;

COMMIT;
