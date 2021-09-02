-- -----------------------------------------------------
-- Table vmaas.module_stream_dep
-- -----------------------------------------------------

CREATE TABLE IF NOT EXISTS module_stream_require (
  module_stream_id INT NOT NULL,
  require_id INT NOT NULL,
  CONSTRAINT module_stream_id
    FOREIGN KEY (module_stream_id)
    REFERENCES module_stream (id),
  CONSTRAINT require_id
    FOREIGN KEY (require_id)
    REFERENCES module_stream (id),
  CONSTRAINT module_stream_dep_uq
    UNIQUE (module_stream_id, require_id)
) TABLESPACE pg_default;

GRANT SELECT ON TABLE module_stream_require TO vmaas_reader;
GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE module_stream_require TO vmaas_writer;
