-- -----------------------------------------------------
-- Table vmaas.csaf_file
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS csaf_file (
  id        SERIAL,
  name      TEXT UNIQUE NOT NULL, CHECK (NOT empty(name)),
  updated   TIMESTAMP WITH TIME ZONE,
  PRIMARY KEY (id)
)TABLESPACE pg_default;

-- -----------------------------------------------------
-- vmaas users permission setup:
-- vmaas_writer - has rights to INSERT/UPDATE/DELETE; used by reposcan
-- vmaas_reader - has SELECT only; used by webapp
-- -----------------------------------------------------
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE public.csaf_file TO vmaas_writer;
GRANT USAGE, SELECT, UPDATE ON SEQUENCE public.csaf_file_id_seq TO vmaas_writer;
GRANT SELECT ON TABLE public.csaf_file TO vmaas_reader;
