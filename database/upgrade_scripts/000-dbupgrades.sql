CREATE TABLE IF NOT EXISTS db_version (
  name TEXT NOT NULL,
  version INT NOT NULL,
  PRIMARY KEY (name)
)TABLESPACE pg_default;

-- Increment this when editing this file
INSERT INTO db_version (name, version) VALUES ('schema_version', 0);

CREATE TABLE db_upgrade_log IF NOT EXISTS (
  id SERIAL,
  version INT NOT NULL,
  status TEXT NOT NULL,
  script TEXT,
  returncode INT,
  stdout TEXT,
  stderr TEXT,
  last_updated TIMESTAMP WITH TIME ZONE NOT NULL
) TABLESPACE pg_default;

CREATE TRIGGER db_upgrade_log_set_last_updated
  BEFORE INSERT OR UPDATE ON db_upgrade_log
  FOR EACH ROW EXECUTE PROCEDURE set_last_updated();

CREATE OR REPLACE FUNCTION set_last_updated()
  RETURNS TRIGGER AS
$set_last_updated$
  BEGIN
    IF (TG_OP = 'UPDATE') OR
       NEW.last_updated IS NULL THEN
      NEW.last_updated := CURRENT_TIMESTAMP;
    END IF;
    RETURN NEW;
  END;
$set_last_updated$
  LANGUAGE 'plpgsql';

