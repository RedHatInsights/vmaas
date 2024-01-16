-- -----------------------------------------------------
-- Table vmaas.csaf_product_status
-- https://docs.oasis-open.org/csaf/csaf/v2.0/os/csaf-v2.0-os.html#3239-vulnerabilities-property---product-status
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS csaf_product_status (
    id   INT NOT NULL,
    name TEXT UNIQUE NOT NULL, CHECK (NOT empty(name)),
    PRIMARY KEY (id)
)TABLESPACE pg_default;

INSERT INTO csaf_product_status (id, name)
VALUES  (1, 'first_affected'),
        (2, 'first_fixed'),
        (3, 'fixed'),
        (4, 'known_affected'),
        (5, 'known_not_affected'),
        (6, 'last_affected'),
        (7, 'recommended'),
        (8, 'under_investigation')
ON CONFLICT DO NOTHING;


-- -----------------------------------------------------
-- Table vmaas.csaf_products
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS csaf_products (
  id             SERIAL,
  cpe            TEXT NOT NULL, CHECK (NOT empty(cpe)),
  package        TEXT NULL, CHECK (NOT empty(package)),
  module         TEXT NULL, CHECK (NOT empty(module)),
  PRIMARY KEY (id)
)TABLESPACE pg_default;


-- -----------------------------------------------------
-- Table vmaas.csaf_cves
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS csaf_cves (
  id                SERIAL,
  cve               TEXT NOT NULL, CHECK (NOT empty(cve)),
  csaf_product_id   INT NOT NULL,
  product_status_id INT NOT NULL,    
  PRIMARY KEY (id),
  CONSTRAINT csaf_product_id
    FOREIGN KEY (csaf_product_id)
    REFERENCES csaf_products (id),
  CONSTRAINT csaf_product_status_id
    FOREIGN KEY (product_status_id)
    REFERENCES csaf_product_status (id)
)TABLESPACE pg_default;


-- -----------------------------------------------------
-- vmaas users permission setup:
-- vmaas_writer - has rights to INSERT/UPDATE/DELETE; used by reposcan
-- vmaas_reader - has SELECT only; used by webapp
-- -----------------------------------------------------
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO vmaas_writer;
GRANT USAGE, SELECT, UPDATE ON ALL SEQUENCES IN SCHEMA public TO vmaas_writer;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO vmaas_reader;
