DROP TABLE csaf_cves;
DROP TABLE csaf_products;
UPDATE csaf_file SET updated = NULL;

-- -----------------------------------------------------
-- Table vmaas.csaf_product
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS csaf_product (
  id                SERIAL,
  cpe_id            INT NOT NULL,
  package_name_id   INT NULL,
  package_id        INT NULL,
  module_stream     TEXT NULL CHECK (NOT empty(module_stream)),
  PRIMARY KEY (id),
  CONSTRAINT cpe_id
    FOREIGN KEY (cpe_id)
    REFERENCES cpe (id),
  CONSTRAINT package_name_id
    FOREIGN KEY (package_name_id)
    REFERENCES package_name (id),
  CONSTRAINT package_id
    FOREIGN KEY (package_id)
    REFERENCES package (id),
  CONSTRAINT pkg_id CHECK(
    (package_name_id IS NOT NULL AND package_id IS NULL) OR
    (package_name_id IS NULL AND package_id IS NOT NULL))
)TABLESPACE pg_default;

CREATE UNIQUE INDEX ON csaf_product(cpe_id, package_name_id) WHERE package_name_id IS NOT NULL AND package_id IS NULL AND module_stream IS NULL;
CREATE UNIQUE INDEX ON csaf_product(cpe_id, package_id) WHERE package_id IS NOT NULL AND package_name_id IS NULL AND module_stream IS NULL;
CREATE UNIQUE INDEX ON csaf_product(cpe_id, package_name_id, module_stream) WHERE package_name_id IS NOT NULL AND package_id IS NULL AND module_stream IS NOT NULL;
CREATE UNIQUE INDEX ON csaf_product(cpe_id, package_id, module_stream) WHERE package_id IS NOT NULL AND package_name_id IS NULL AND module_stream IS NOT NULL;

-- -----------------------------------------------------
-- Table vmaas.csaf_cve_product
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS csaf_cve_product (
  id                     SERIAL,
  cve_id                 INT NOT NULL,
  csaf_product_id        INT NOT NULL,
  csaf_product_status_id INT NOT NULL,
  csaf_file_id           INT NOT NULL,
  PRIMARY KEY (id),
  CONSTRAINT cve_id
    FOREIGN KEY (cve_id)
    REFERENCES cve (id),
  CONSTRAINT csaf_product_id
    FOREIGN KEY (csaf_product_id)
    REFERENCES csaf_product (id),
  CONSTRAINT csaf_product_status_id
    FOREIGN KEY (csaf_product_status_id)
    REFERENCES csaf_product_status (id),
  CONSTRAINT csaf_file_id
    FOREIGN KEY (csaf_file_id)
    REFERENCES csaf_file (id),
  CONSTRAINT csaf_cve_product_ids_uq
    UNIQUE (cve_id, csaf_product_id)
)TABLESPACE pg_default;


-- -----------------------------------------------------
-- vmaas users permission setup:
-- vmaas_writer - has rights to INSERT/UPDATE/DELETE; used by reposcan
-- vmaas_reader - has SELECT only; used by webapp
-- -----------------------------------------------------
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO vmaas_writer;
GRANT USAGE, SELECT, UPDATE ON ALL SEQUENCES IN SCHEMA public TO vmaas_writer;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO vmaas_reader;
