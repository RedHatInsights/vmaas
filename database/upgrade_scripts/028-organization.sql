-- -----------------------------------------------------
-- Table vmaas.organization
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS organization (
  id SERIAL,
  name TEXT NOT NULL UNIQUE, CHECK (NOT empty(name)),
  PRIMARY KEY (id)
)TABLESPACE pg_default;

INSERT INTO organization (id, name) VALUES
  (1, 'DEFAULT');

-- -----------------------------------------------------
-- vmaas users permission setup:
-- vmaas_writer - has rights to INSERT/UPDATE/DELETE; used by reposcan
-- vmaas_reader - has SELECT only; used by webapp
-- -----------------------------------------------------
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE public.organization TO vmaas_writer;
GRANT USAGE, SELECT, UPDATE ON SEQUENCE public.organization_id_seq TO vmaas_writer;
GRANT SELECT ON TABLE public.organization TO vmaas_reader;

ALTER TABLE repo
  ADD COLUMN org_id INT NULL,
  ADD CONSTRAINT org_id FOREIGN KEY (org_id) REFERENCES organization (id);

UPDATE repo SET org_id = 1;

ALTER TABLE repo ALTER COLUMN org_id SET NOT NULL;

DROP INDEX repo_content_set_id_key;
DROP INDEX repo_content_set_id_basearch_id_key;
DROP INDEX repo_content_set_id_releasever_key;
DROP INDEX repo_content_set_id_basearch_id_releasever_key;

CREATE UNIQUE INDEX repo_content_set_id_key ON repo (content_set_id, org_id) WHERE basearch_id IS NULL AND releasever IS NULL;
CREATE UNIQUE INDEX repo_content_set_id_basearch_id_key ON repo (content_set_id, org_id, basearch_id) WHERE basearch_id IS NOT NULL AND releasever IS NULL;
CREATE UNIQUE INDEX repo_content_set_id_releasever_key ON repo (content_set_id, org_id, releasever) WHERE basearch_id IS NULL AND releasever IS NOT NULL;
CREATE UNIQUE INDEX repo_content_set_id_basearch_id_releasever_key ON repo (content_set_id, org_id, basearch_id, releasever) WHERE basearch_id IS NOT NULL AND releasever IS NOT NULL;
