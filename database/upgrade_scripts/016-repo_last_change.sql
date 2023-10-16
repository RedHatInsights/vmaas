create or replace FUNCTION repo_last_change()
  RETURNS TRIGGER AS
$repo_last_change$
  BEGIN
    IF TG_OP = 'UPDATE' THEN
      IF NEW.revision IS DISTINCT FROM OLD.revision THEN
        NEW.last_change = CURRENT_TIMESTAMP;
      END IF;
    ELSIF TG_OP = 'INSERT' THEN
      NEW.last_change = CURRENT_TIMESTAMP;
    END IF;
    RETURN NEW;
  END;
$repo_last_change$
  LANGUAGE 'plpgsql';

ALTER TABLE repo ADD COLUMN last_change TIMESTAMP WITH TIME ZONE;
UPDATE repo SET last_change = CURRENT_TIMESTAMP;
ALTER TABLE repo ALTER COLUMN last_change SET NOT NULL;

CREATE TRIGGER repo_last_change BEFORE INSERT OR UPDATE ON repo
  FOR EACH ROW
  EXECUTE PROCEDURE repo_last_change();
