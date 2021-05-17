-- -----------------------------------------------------
-- Table vmaas.oval_module_test
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS oval_module_test (
  id SERIAL,
  oval_id TEXT UNIQUE NOT NULL, CHECK (NOT empty(oval_id)),
  module_stream TEXT NOT NULL, CHECK (NOT empty(module_stream)),
  version INT NOT NULL,
  PRIMARY KEY (id)
)TABLESPACE pg_default;


-- -----------------------------------------------------
-- Table vmaas.oval_file_module_test
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS oval_file_module_test (
  file_id INT NOT NULL,
  module_test_id INT NOT NULL,
  UNIQUE (file_id, module_test_id),
  CONSTRAINT file_id
    FOREIGN KEY (file_id)
    REFERENCES oval_file (id),
  CONSTRAINT module_test_id
    FOREIGN KEY (module_test_id)
    REFERENCES oval_module_test (id)
)TABLESPACE pg_default;

-- -----------------------------------------------------
-- Table vmaas.oval_criteria_dependency
-- -----------------------------------------------------
ALTER TABLE oval_criteria_dependency DROP COLUMN id; -- no use for it

ALTER TABLE oval_criteria_dependency DROP CONSTRAINT dep_criteria_id_dep_test_id;
DROP INDEX ocd_dep_criteria_id_dep_test_id_1;
DROP INDEX ocd_dep_criteria_id_dep_test_id_2;

ALTER TABLE oval_criteria_dependency ADD COLUMN dep_module_test_id INT;
ALTER TABLE oval_criteria_dependency ADD CONSTRAINT dep_criteria_id_dep_test_id
    CHECK((dep_criteria_id IS NOT NULL AND dep_test_id IS NULL AND dep_module_test_id IS NULL) OR
          (dep_criteria_id IS NULL AND dep_test_id IS NOT NULL AND dep_module_test_id IS NULL) OR
          (dep_criteria_id IS NULL AND dep_test_id IS NULL AND dep_module_test_id IS NOT NULL));
ALTER TABLE oval_criteria_dependency ADD CONSTRAINT dep_module_test_id FOREIGN KEY (dep_module_test_id) REFERENCES oval_module_test (id);
CREATE UNIQUE INDEX ocd_dep_criteria_id_dep_test_id_1 ON oval_criteria_dependency (parent_criteria_id, dep_criteria_id)
    WHERE dep_criteria_id IS NOT NULL AND dep_test_id IS NULL AND dep_module_test_id IS NULL;
CREATE UNIQUE INDEX ocd_dep_criteria_id_dep_test_id_2 ON oval_criteria_dependency (parent_criteria_id, dep_test_id)
    WHERE dep_criteria_id IS NULL AND dep_test_id IS NOT NULL AND dep_module_test_id IS NULL;
CREATE UNIQUE INDEX ocd_dep_criteria_id_dep_test_id_3 ON oval_criteria_dependency (parent_criteria_id, dep_module_test_id)
    WHERE dep_criteria_id IS NULL AND dep_test_id IS NULL AND dep_module_test_id IS NOT NULL;


-- -----------------------------------------------------
-- vmaas users permission setup:
-- vmaas_writer - has rights to INSERT/UPDATE/DELETE; used by reposcan
-- vmaas_reader - has SELECT only; used by webapp
-- -----------------------------------------------------
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO vmaas_writer;
GRANT USAGE, SELECT, UPDATE ON ALL SEQUENCES IN SCHEMA public TO vmaas_writer;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO vmaas_reader;

UPDATE oval_file SET updated = '1970-01-01'; -- re-sync all
update oval_definition set version = 0;
