-- -----------------------------------------------------
-- Table vmaas.vexfeed_file
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS vexfeed_file (
  id        SERIAL,
  name      TEXT UNIQUE NOT NULL, CHECK (NOT empty(name)),
  updated   TIMESTAMP WITH TIME ZONE,
  PRIMARY KEY (id)
)TABLESPACE pg_default;

-- -----------------------------------------------------
-- Table vmaas.vexfeed_product
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS vexfeed_product (
  id                SERIAL,
  cpe_id            INT NOT NULL,
  package_name_id   INT NOT NULL,
  package_id        INT NULL,
  module_stream     TEXT NULL CHECK (NOT empty(module_stream)),
  variant_suffix    TEXT NOT NULL CHECK (NOT empty(variant_suffix)) DEFAULT 'N/A',
  PRIMARY KEY (id),
  CONSTRAINT vexfeed_product_cpe_id
    FOREIGN KEY (cpe_id)
    REFERENCES cpe (id),
  CONSTRAINT vexfeed_product_package_name_id
    FOREIGN KEY (package_name_id)
    REFERENCES package_name (id),
  CONSTRAINT vexfeed_product_package_id
    FOREIGN KEY (package_id)
    REFERENCES package (id)
)TABLESPACE pg_default;

CREATE UNIQUE INDEX ON vexfeed_product(cpe_id, variant_suffix, package_name_id) WHERE package_name_id IS NOT NULL AND package_id IS NULL AND module_stream IS NULL;
CREATE UNIQUE INDEX ON vexfeed_product(cpe_id, variant_suffix, package_name_id, module_stream) WHERE package_name_id IS NOT NULL AND package_id IS NULL AND module_stream IS NOT NULL;
CREATE UNIQUE INDEX ON vexfeed_product(cpe_id, variant_suffix, package_name_id, package_id) WHERE package_name_id IS NOT NULL and package_id IS NOT NULL AND module_stream IS NULL;
CREATE UNIQUE INDEX ON vexfeed_product(cpe_id, variant_suffix, package_name_id, package_id, module_stream) WHERE package_name_id IS NOT NULL and package_id IS NOT NULL AND module_stream IS NOT NULL;

-- -----------------------------------------------------
-- Table vmaas.vexfeed_cve_product
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS vexfeed_cve_product (
  id                     SERIAL,
  cve_id                 INT NOT NULL,
  vexfeed_product_id     INT NOT NULL,
  csaf_product_status_id INT NOT NULL,
  vexfeed_file_id        INT NOT NULL,
  erratum                TEXT,
  PRIMARY KEY (id),
  CONSTRAINT vexfeed_cve_product_cve_id
    FOREIGN KEY (cve_id)
    REFERENCES cve (id),
  CONSTRAINT vexfeed_cve_product_product_id
    FOREIGN KEY (vexfeed_product_id)
    REFERENCES vexfeed_product (id),
  CONSTRAINT vexfeed_cve_product_status_id
    FOREIGN KEY (csaf_product_status_id)
    REFERENCES csaf_product_status (id),
  CONSTRAINT vexfeed_cve_product_file_id
    FOREIGN KEY (vexfeed_file_id)
    REFERENCES vexfeed_file (id),
  CONSTRAINT vexfeed_cve_product_ids_uq
    UNIQUE (cve_id, vexfeed_product_id)
)TABLESPACE pg_default;

CREATE INDEX ON vexfeed_cve_product(vexfeed_product_id);
CREATE INDEX ON vexfeed_cve_product(vexfeed_file_id);
