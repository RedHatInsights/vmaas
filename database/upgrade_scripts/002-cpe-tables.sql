-- -----------------------------------------------------
-- Table vmaas.cpe
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS cpe (
  id SERIAL,
  label TEXT NOT NULL UNIQUE, CHECK (NOT empty(label)),
  name TEXT NULL, CHECK (NOT empty(name)),
  PRIMARY KEY (id)
)TABLESPACE pg_default;

-- -----------------------------------------------------
-- Table vmaas.cpe_content_set
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS cpe_content_set (
  cpe_id INT NOT NULL,
  content_set_id INT NOT NULL,
  UNIQUE (cpe_id, content_set_id),
  CONSTRAINT cpe_id
    FOREIGN KEY (cpe_id)
    REFERENCES cpe (id),
  CONSTRAINT content_set_id
    FOREIGN KEY (content_set_id)
    REFERENCES content_set (id)
)TABLESPACE pg_default;

CREATE INDEX ON cpe_content_set(content_set_id);

GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO vmaas_writer;
GRANT USAGE, SELECT, UPDATE ON ALL SEQUENCES IN SCHEMA public TO vmaas_writer;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO vmaas_reader;


-- dbchange triggers
ALTER TABLE dbchange ADD COLUMN cpe_changes TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP;

DROP TRIGGER last_change ON dbchange;
CREATE TRIGGER last_change AFTER UPDATE OF errata_changes, cpe_changes, cve_changes, repository_changes, pkgtree_change ON dbchange
  FOR EACH STATEMENT EXECUTE PROCEDURE last_change();

create or replace FUNCTION cpes_changed()
RETURNS TRIGGER as $$
BEGIN
    update dbchange set cpe_changes = CURRENT_TIMESTAMP;
    return NULL;
END;
$$ language 'plpgsql';

CREATE TRIGGER cpe_changed AFTER INSERT OR UPDATE OR DELETE ON cpe
  FOR EACH STATEMENT
  EXECUTE PROCEDURE cpes_changed();

CREATE TRIGGER cpe_changed AFTER INSERT OR UPDATE OR DELETE ON cpe_content_set
  FOR EACH STATEMENT
  EXECUTE PROCEDURE cpes_changed();
