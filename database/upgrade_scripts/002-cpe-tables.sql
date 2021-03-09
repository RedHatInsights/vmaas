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
