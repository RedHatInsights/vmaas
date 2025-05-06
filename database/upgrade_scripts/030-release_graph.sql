-- -----------------------------------------------------
-- Table vmaas.release_graph
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS release_graph (
  id    SERIAL,
  name  TEXT NOT NULL, CHECK (NOT empty(name)),
  graph JSONB NOT NULL,
  checksum TEXT NOT NULL,
  PRIMARY KEY (id)
)TABLESPACE pg_default;

-- -----------------------------------------------------
-- vmaas users permission setup:
-- vmaas_writer - has rights to INSERT/UPDATE/DELETE; used by reposcan
-- vmaas_reader - has SELECT only; used by webapp
-- -----------------------------------------------------
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE public.operating_system TO vmaas_writer;
GRANT USAGE, SELECT, UPDATE ON SEQUENCE public.operating_system_id_seq TO vmaas_writer;
GRANT SELECT ON TABLE public.operating_system TO vmaas_reader;
