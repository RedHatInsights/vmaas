-- -----------------------------------------------------
-- Table vmaas.oval_operation_evr
-- from https://oval-community-guidelines.readthedocs.io/en/latest/oval-schema-documentation/oval-common-schema.html
-- Subset of values used in RH OVALs
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS oval_operation_evr (
  id INT NOT NULL,
  name TEXT UNIQUE NOT NULL, CHECK (NOT empty(name)),
  PRIMARY KEY (id)
)TABLESPACE pg_default;

INSERT INTO oval_operation_evr (id, name) VALUES
  (1, 'equals'), (2, 'less than');


-- -----------------------------------------------------
-- Table vmaas.oval_check_rpminfo
-- from https://oval-community-guidelines.readthedocs.io/en/latest/oval-schema-documentation/oval-common-schema.html
-- Subset of values used in RH OVALs
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS oval_check_rpminfo (
  id INT NOT NULL,
  name TEXT UNIQUE NOT NULL, CHECK (NOT empty(name)),
  PRIMARY KEY (id)
)TABLESPACE pg_default;

INSERT INTO oval_check_rpminfo (id, name) VALUES
  (1, 'at least one');


-- -----------------------------------------------------
-- Table vmaas.oval_check_existence_rpminfo
-- from https://oval-community-guidelines.readthedocs.io/en/latest/oval-schema-documentation/oval-common-schema.html
-- Subset of values used in RH OVALs
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS oval_check_existence_rpminfo (
  id INT NOT NULL,
  name TEXT UNIQUE NOT NULL, CHECK (NOT empty(name)),
  PRIMARY KEY (id)
)TABLESPACE pg_default;

INSERT INTO oval_check_existence_rpminfo (id, name) VALUES
  (1, 'at_least_one_exists'), (2, 'none_exist');


-- -----------------------------------------------------
-- Table vmaas.oval_definition_type
-- from https://oval-community-guidelines.readthedocs.io/en/latest/oval-schema-documentation/oval-common-schema.html
-- Subset of values used in RH OVALs
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS oval_definition_type (
  id INT NOT NULL,
  name TEXT UNIQUE NOT NULL, CHECK (NOT empty(name)),
  PRIMARY KEY (id)
)TABLESPACE pg_default;

INSERT INTO oval_definition_type (id, name) VALUES
  (1, 'patch'), (2, 'vulnerability');


-- -----------------------------------------------------
-- Table vmaas.oval_criteria_operator
-- from https://oval-community-guidelines.readthedocs.io/en/latest/oval-schema-documentation/oval-common-schema.html
-- Subset of values used in RH OVALs
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS oval_criteria_operator (
  id INT NOT NULL,
  name TEXT UNIQUE NOT NULL, CHECK (NOT empty(name)),
  PRIMARY KEY (id)
)TABLESPACE pg_default;

INSERT INTO oval_criteria_operator (id, name) VALUES
  (1, 'AND'), (2, 'OR');


-- -----------------------------------------------------
-- Table vmaas.oval_file
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS oval_file (
  id SERIAL,
  oval_id TEXT UNIQUE NOT NULL, CHECK (NOT empty(oval_id)),
  updated TIMESTAMP WITH TIME ZONE NOT NULL,
  PRIMARY KEY (id)
)TABLESPACE pg_default;


-- -----------------------------------------------------
-- Table vmaas.oval_rpminfo_object
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS oval_rpminfo_object (
  id SERIAL,
  oval_id TEXT UNIQUE NOT NULL, CHECK (NOT empty(oval_id)),
  package_name_id INT NOT NULL,
  version INT NOT NULL,
  PRIMARY KEY (id),
  CONSTRAINT package_name_id
    FOREIGN KEY (package_name_id)
    REFERENCES package_name (id)
)TABLESPACE pg_default;


-- -----------------------------------------------------
-- Table vmaas.oval_file_rpminfo_object
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS oval_file_rpminfo_object (
  file_id INT NOT NULL,
  rpminfo_object_id INT NOT NULL,
  UNIQUE (file_id, rpminfo_object_id),
  CONSTRAINT file_id
    FOREIGN KEY (file_id)
    REFERENCES oval_file (id),
  CONSTRAINT rpminfo_object_id
    FOREIGN KEY (rpminfo_object_id)
    REFERENCES oval_rpminfo_object (id)
)TABLESPACE pg_default;

CREATE INDEX ON oval_file_rpminfo_object (rpminfo_object_id);


-- -----------------------------------------------------
-- Table vmaas.oval_rpminfo_state
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS oval_rpminfo_state (
  id SERIAL,
  oval_id TEXT UNIQUE NOT NULL, CHECK (NOT empty(oval_id)),
  evr_id INT,
  evr_operation_id INT,
  version INT NOT NULL,
  PRIMARY KEY (id),
  CONSTRAINT evr_id
    FOREIGN KEY (evr_id)
    REFERENCES evr (id),
  CONSTRAINT evr_operation_id
    FOREIGN KEY (evr_operation_id)
    REFERENCES oval_operation_evr (id)
)TABLESPACE pg_default;


-- -----------------------------------------------------
-- Table vmaas.oval_rpminfo_state_arch
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS oval_rpminfo_state_arch (
  rpminfo_state_id INT NOT NULL,
  arch_id INT NOT NULL,
  UNIQUE (rpminfo_state_id, arch_id),
  CONSTRAINT rpminfo_state_id
    FOREIGN KEY (rpminfo_state_id)
    REFERENCES oval_rpminfo_state (id),
  CONSTRAINT arch_id
    FOREIGN KEY (arch_id)
    REFERENCES arch (id)
)TABLESPACE pg_default;


-- -----------------------------------------------------
-- Table vmaas.oval_file_rpminfo_state
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS oval_file_rpminfo_state (
  file_id INT NOT NULL,
  rpminfo_state_id INT NOT NULL,
  UNIQUE (file_id, rpminfo_state_id),
  CONSTRAINT file_id
    FOREIGN KEY (file_id)
    REFERENCES oval_file (id),
  CONSTRAINT rpminfo_state_id
    FOREIGN KEY (rpminfo_state_id)
    REFERENCES oval_rpminfo_state (id)
)TABLESPACE pg_default;

CREATE INDEX ON oval_file_rpminfo_state (rpminfo_state_id);


-- -----------------------------------------------------
-- Table vmaas.oval_rpminfo_test
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS oval_rpminfo_test (
  id SERIAL,
  oval_id TEXT UNIQUE NOT NULL, CHECK (NOT empty(oval_id)),
  rpminfo_object_id INT NOT NULL,
  check_id INT NOT NULL,
  check_existence_id INT NOT NULL,
  version INT NOT NULL,
  PRIMARY KEY (id),
  CONSTRAINT rpminfo_object_id
    FOREIGN KEY (rpminfo_object_id)
    REFERENCES oval_rpminfo_object (id),
  CONSTRAINT check_id
    FOREIGN KEY (check_id)
    REFERENCES oval_check_rpminfo (id),
  CONSTRAINT check_existence_id
    FOREIGN KEY (check_existence_id)
    REFERENCES oval_check_existence_rpminfo (id)
)TABLESPACE pg_default;


-- -----------------------------------------------------
-- Table vmaas.oval_rpminfo_test_state
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS oval_rpminfo_test_state (
  rpminfo_test_id INT NOT NULL,
  rpminfo_state_id INT NOT NULL,
  UNIQUE (rpminfo_test_id, rpminfo_state_id),
  CONSTRAINT rpminfo_test_id
    FOREIGN KEY (rpminfo_test_id)
    REFERENCES oval_rpminfo_test (id),
  CONSTRAINT rpminfo_state_id
    FOREIGN KEY (rpminfo_state_id)
    REFERENCES oval_rpminfo_state (id)
)TABLESPACE pg_default;


-- -----------------------------------------------------
-- Table vmaas.oval_file_rpminfo_test
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS oval_file_rpminfo_test (
  file_id INT NOT NULL,
  rpminfo_test_id INT NOT NULL,
  UNIQUE (file_id, rpminfo_test_id),
  CONSTRAINT file_id
    FOREIGN KEY (file_id)
    REFERENCES oval_file (id),
  CONSTRAINT rpminfo_test_id
    FOREIGN KEY (rpminfo_test_id)
    REFERENCES oval_rpminfo_test (id)
)TABLESPACE pg_default;

CREATE INDEX ON oval_file_rpminfo_test (rpminfo_test_id);


-- -----------------------------------------------------
-- Table vmaas.oval_criteria
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS oval_criteria (
  id SERIAL,
  operator_id INT NOT NULL,
  CONSTRAINT operator_id
    FOREIGN KEY (operator_id)
    REFERENCES oval_criteria_operator (id),
  PRIMARY KEY (id)
)TABLESPACE pg_default;


-- -----------------------------------------------------
-- Table vmaas.oval_criteria_dependency
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS oval_criteria_dependency (
  id SERIAL,
  parent_criteria_id INT NOT NULL,
  dep_criteria_id INT,
  dep_test_id INT,
  CONSTRAINT dep_criteria_id_dep_test_id CHECK((dep_criteria_id IS NOT NULL AND dep_test_id IS NULL) OR (dep_criteria_id IS NULL AND dep_test_id IS NOT NULL)),
  CONSTRAINT parent_criteria_id
    FOREIGN KEY (parent_criteria_id)
    REFERENCES oval_criteria (id),
  CONSTRAINT dep_criteria_id
    FOREIGN KEY (dep_criteria_id)
    REFERENCES oval_criteria (id),
  CONSTRAINT dep_test_id
    FOREIGN KEY (dep_test_id)
    REFERENCES oval_rpminfo_test (id),
  PRIMARY KEY (id)
)TABLESPACE pg_default;

CREATE UNIQUE INDEX ocd_dep_criteria_id_dep_test_id_1 ON oval_criteria_dependency (parent_criteria_id, dep_criteria_id) WHERE dep_criteria_id IS NOT NULL AND dep_test_id IS NULL;
CREATE UNIQUE INDEX ocd_dep_criteria_id_dep_test_id_2 ON oval_criteria_dependency (parent_criteria_id, dep_test_id) WHERE dep_criteria_id IS NULL AND dep_test_id IS NOT NULL;


-- -----------------------------------------------------
-- Table vmaas.oval_definition
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS oval_definition (
  id SERIAL,
  oval_id TEXT UNIQUE NOT NULL, CHECK (NOT empty(oval_id)),
  definition_type_id INT NOT NULL,
  criteria_id INT,
  version INT NOT NULL,
  PRIMARY KEY (id),
  CONSTRAINT definition_type_id
    FOREIGN KEY (definition_type_id)
    REFERENCES oval_definition_type (id),
  CONSTRAINT criteria_id
    FOREIGN KEY (criteria_id)
    REFERENCES oval_criteria (id)
)TABLESPACE pg_default;


-- -----------------------------------------------------
-- Table vmaas.oval_definition_test
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS oval_definition_test (
  definition_id INT NOT NULL,
  rpminfo_test_id INT NOT NULL,
  UNIQUE (definition_id, rpminfo_test_id),
  CONSTRAINT definition_id
    FOREIGN KEY (definition_id)
    REFERENCES oval_definition (id),
  CONSTRAINT rpminfo_test_id
    FOREIGN KEY (rpminfo_test_id)
    REFERENCES oval_rpminfo_test (id)
)TABLESPACE pg_default;


-- -----------------------------------------------------
-- Table vmaas.oval_definition_cve
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS oval_definition_cve (
  definition_id INT NOT NULL,
  cve_id INT NOT NULL,
  UNIQUE (definition_id, cve_id),
  CONSTRAINT definition_id
    FOREIGN KEY (definition_id)
    REFERENCES oval_definition (id),
  CONSTRAINT cve_id
    FOREIGN KEY (cve_id)
    REFERENCES cve (id)
)TABLESPACE pg_default;


-- -----------------------------------------------------
-- Table vmaas.oval_definition_errata
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS oval_definition_errata (
  definition_id INT NOT NULL,
  errata_id INT NOT NULL,
  UNIQUE (definition_id, errata_id),
  CONSTRAINT definition_id
    FOREIGN KEY (definition_id)
    REFERENCES oval_definition (id),
  CONSTRAINT errata_id
    FOREIGN KEY (errata_id)
    REFERENCES errata (id)
)TABLESPACE pg_default;


-- -----------------------------------------------------
-- Table vmaas.oval_definition_cpe
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS oval_definition_cpe (
  definition_id INT NOT NULL,
  cpe_id INT NOT NULL,
  UNIQUE (definition_id, cpe_id),
  CONSTRAINT definition_id
    FOREIGN KEY (definition_id)
    REFERENCES oval_definition (id),
  CONSTRAINT cpe_id
    FOREIGN KEY (cpe_id)
    REFERENCES cpe (id)
)TABLESPACE pg_default;


-- -----------------------------------------------------
-- Table vmaas.oval_file_definition
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS oval_file_definition (
  file_id INT NOT NULL,
  definition_id INT NOT NULL,
  UNIQUE (file_id, definition_id),
  CONSTRAINT file_id
    FOREIGN KEY (file_id)
    REFERENCES oval_file (id),
  CONSTRAINT definition_id
    FOREIGN KEY (definition_id)
    REFERENCES oval_definition (id)
)TABLESPACE pg_default;

CREATE INDEX ON oval_file_definition (definition_id);


-- -----------------------------------------------------
-- vmaas users permission setup:
-- vmaas_writer - has rights to INSERT/UPDATE/DELETE; used by reposcan
-- vmaas_reader - has SELECT only; used by webapp
-- -----------------------------------------------------
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO vmaas_writer;
GRANT USAGE, SELECT, UPDATE ON ALL SEQUENCES IN SCHEMA public TO vmaas_writer;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO vmaas_reader;
