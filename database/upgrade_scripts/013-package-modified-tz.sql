ALTER TABLE package DROP COLUMN modified;
ALTER TABLE package ADD COLUMN IF NOT EXISTS modified TIMESTAMP NOT NULL DEFAULT (now() at time zone 'utc');
