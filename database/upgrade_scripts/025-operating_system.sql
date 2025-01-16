-- -----------------------------------------------------
-- Table vmaas.operating_system
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS operating_system (
  id SERIAL,
  name TEXT NOT NULL, CHECK (NOT empty(name)),
  major INT NOT NULL,
  minor INT NOT NULL,
  ga DATE NOT NULL,
  system_profile JSONB,
  PRIMARY KEY (id),
  CONSTRAINT operating_system_name_major_minor_uq
    UNIQUE (name, major, minor)
)TABLESPACE pg_default;

-- -----------------------------------------------------
-- vmaas users permission setup:
-- vmaas_writer - has rights to INSERT/UPDATE/DELETE; used by reposcan
-- vmaas_reader - has SELECT only; used by webapp
-- -----------------------------------------------------
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE public.operating_system TO vmaas_writer;
GRANT USAGE, SELECT, UPDATE ON SEQUENCE public.operating_system_id_seq TO vmaas_writer;
GRANT SELECT ON TABLE public.operating_system TO vmaas_reader;
