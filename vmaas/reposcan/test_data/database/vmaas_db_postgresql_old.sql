-- -----------------------------------------------------
-- Vulnerability Metadata as a Service database
--
-- When making changes into this file, you need to increment
-- the version number in db_version table and create update 
-- script in the upgrade folder.
-- ----------------------------------------------------- 

-- -----------------------------------------------------
-- Table db_version
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS db_version (
  name TEXT NOT NULL,
  version INT NOT NULL,
  PRIMARY KEY (name)
)TABLESPACE pg_default;

-- Increment this when editing this file
INSERT INTO db_version (name, version) VALUES ('schema_version', 0);

-- -----------------------------------------------------
-- evr type
-- represents version and release as arrays of parsed components
-- of proper type (numeric or varchar)
-- this allow us to use standard array operation for = > <
-- and most importantly sorting
-- -----------------------------------------------------
create type evr_array_item as (
        n       NUMERIC,
        s       TEXT
);

create type evr_t as (
        epoch INT,
        version evr_array_item[],
        release evr_array_item[]
);

create or replace FUNCTION empty(t TEXT)
RETURNS BOOLEAN as $$
BEGIN
    return t ~ '^[[:space:]]*$';
END;
$$ language 'plpgsql';

create or replace FUNCTION errata_changed()
RETURNS TRIGGER as $$
BEGIN
    update dbchange set errata_changes = CURRENT_TIMESTAMP;
    return NULL;
END;
$$ language 'plpgsql';

create or replace FUNCTION repos_changed()
RETURNS TRIGGER as $$
BEGIN
    update dbchange set repository_changes = CURRENT_TIMESTAMP;
    return NULL;
END;
$$ language 'plpgsql';

create or replace FUNCTION cves_changed()
RETURNS TRIGGER as $$
BEGIN
    update dbchange set cve_changes = CURRENT_TIMESTAMP;
    return NULL;
END;
$$ language 'plpgsql';

create or replace FUNCTION last_change()
RETURNS TRIGGER as $$
BEGIN
    update dbchange set last_change = CURRENT_TIMESTAMP;
    return NULL;
END;
$$ language 'plpgsql';

create or replace FUNCTION set_last_updated()
  RETURNS TRIGGER AS
$set_last_updated$
  BEGIN
    IF (TG_OP = 'UPDATE') OR
       NEW.last_updated IS NULL THEN
      NEW.last_updated := CURRENT_TIMESTAMP;
    END IF;
    RETURN NEW;
  END;
$set_last_updated$
  LANGUAGE 'plpgsql';


-- -----------------------------------------------------
-- Table vmaas.evr
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS evr (
  id SERIAL,
  epoch TEXT NOT NULL, CHECK (NOT empty(epoch)),
  version TEXT NOT NULL, CHECK (NOT empty(version)),
  release TEXT NOT NULL, CHECK (NOT empty(release)),
  evr evr_t NOT NULL,
  UNIQUE (epoch, version, release),
  PRIMARY KEY (id)
)TABLESPACE pg_default;


-- -----------------------------------------------------
-- Table vmaas.arch
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS arch (
  id SERIAL,
  name TEXT NOT NULL UNIQUE, CHECK (NOT empty(name)),
  PRIMARY KEY (id)
)TABLESPACE pg_default;

INSERT INTO arch (name) VALUES
  ('noarch'), ('i386'), ('i486'), ('i586'), ('i686'), ('alpha'), ('alphaev6'), ('ia64'), ('sparc'),
  ('sparcv9'), ('sparc64'), ('s390'), ('athlon'), ('s390x'), ('ppc'), ('ppc64'), ('ppc64le'),
  ('pSeries'), ('iSeries'), ('x86_64'), ('ppc64iseries'), ('ppc64pseries'), ('ia32e'), ('amd64'), ('aarch64'),
  ('armv7hnl'), ('armv7hl'), ('armv7l'), ('armv6hl'), ('armv6l'), ('armv5tel'), ('src');


-- -----------------------------------------------------
-- Table vmaas.arch_compatibility
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS arch_compatibility (
  from_arch_id INT NOT NULL,
  to_arch_id INT NOT NULL,

  CONSTRAINT from_arch_id
    FOREIGN KEY (from_arch_id)
    REFERENCES arch (id),
  CONSTRAINT to_arch_id
    FOREIGN KEY (to_arch_id)
    REFERENCES arch (id)
)TABLESPACE pg_default;

INSERT INTO arch_compatibility (from_arch_id, to_arch_id)
  SELECT f.id, t.id FROM arch AS f, arch AS t WHERE f.name = 'noarch' AND t.name = 'noarch'
  UNION ALL
  SELECT f.id, t.id FROM arch AS f, arch AS t WHERE f.name = 'i386' AND t.name = 'noarch'
  UNION ALL
  SELECT f.id, t.id FROM arch AS f, arch AS t WHERE f.name = 'i386' AND t.name = 'i386'
  UNION ALL
  SELECT f.id, t.id FROM arch AS f, arch AS t WHERE f.name = 'noarch' AND t.name = 'i386'
  UNION ALL
  SELECT f.id, t.id FROM arch AS f, arch AS t WHERE f.name = 'i486' AND t.name = 'noarch'
  UNION ALL
  SELECT f.id, t.id FROM arch AS f, arch AS t WHERE f.name = 'i486' AND t.name = 'i486'
  UNION ALL
  SELECT f.id, t.id FROM arch AS f, arch AS t WHERE f.name = 'noarch' AND t.name = 'i486'
  UNION ALL
  SELECT f.id, t.id FROM arch AS f, arch AS t WHERE f.name = 'i586' AND t.name = 'noarch'
  UNION ALL
  SELECT f.id, t.id FROM arch AS f, arch AS t WHERE f.name = 'i586' AND t.name = 'i586'
  UNION ALL
  SELECT f.id, t.id FROM arch AS f, arch AS t WHERE f.name = 'noarch' AND t.name = 'i586'
  UNION ALL
  SELECT f.id, t.id FROM arch AS f, arch AS t WHERE f.name = 'i686' AND t.name = 'noarch'
  UNION ALL
  SELECT f.id, t.id FROM arch AS f, arch AS t WHERE f.name = 'i686' AND t.name = 'i686'
  UNION ALL
  SELECT f.id, t.id FROM arch AS f, arch AS t WHERE f.name = 'noarch' AND t.name = 'i686'
  UNION ALL
  SELECT f.id, t.id FROM arch AS f, arch AS t WHERE f.name = 'alpha' AND t.name = 'noarch'
  UNION ALL
  SELECT f.id, t.id FROM arch AS f, arch AS t WHERE f.name = 'alpha' AND t.name = 'alpha'
  UNION ALL
  SELECT f.id, t.id FROM arch AS f, arch AS t WHERE f.name = 'noarch' AND t.name = 'alpha'
  UNION ALL
  SELECT f.id, t.id FROM arch AS f, arch AS t WHERE f.name = 'alphaev6' AND t.name = 'noarch'
  UNION ALL
  SELECT f.id, t.id FROM arch AS f, arch AS t WHERE f.name = 'alphaev6' AND t.name = 'alphaev6'
  UNION ALL
  SELECT f.id, t.id FROM arch AS f, arch AS t WHERE f.name = 'noarch' AND t.name = 'alphaev6'
  UNION ALL
  SELECT f.id, t.id FROM arch AS f, arch AS t WHERE f.name = 'ia64' AND t.name = 'noarch'
  UNION ALL
  SELECT f.id, t.id FROM arch AS f, arch AS t WHERE f.name = 'ia64' AND t.name = 'ia64'
  UNION ALL
  SELECT f.id, t.id FROM arch AS f, arch AS t WHERE f.name = 'noarch' AND t.name = 'ia64'
  UNION ALL
  SELECT f.id, t.id FROM arch AS f, arch AS t WHERE f.name = 'sparc' AND t.name = 'noarch'
  UNION ALL
  SELECT f.id, t.id FROM arch AS f, arch AS t WHERE f.name = 'sparc' AND t.name = 'sparc'
  UNION ALL
  SELECT f.id, t.id FROM arch AS f, arch AS t WHERE f.name = 'noarch' AND t.name = 'sparc'
  UNION ALL
  SELECT f.id, t.id FROM arch AS f, arch AS t WHERE f.name = 'sparcv9' AND t.name = 'noarch'
  UNION ALL
  SELECT f.id, t.id FROM arch AS f, arch AS t WHERE f.name = 'sparcv9' AND t.name = 'sparcv9'
  UNION ALL
  SELECT f.id, t.id FROM arch AS f, arch AS t WHERE f.name = 'noarch' AND t.name = 'sparcv9'
  UNION ALL
  SELECT f.id, t.id FROM arch AS f, arch AS t WHERE f.name = 'sparc64' AND t.name = 'noarch'
  UNION ALL
  SELECT f.id, t.id FROM arch AS f, arch AS t WHERE f.name = 'sparc64' AND t.name = 'sparc64'
  UNION ALL
  SELECT f.id, t.id FROM arch AS f, arch AS t WHERE f.name = 'noarch' AND t.name = 'sparc64'
  UNION ALL
  SELECT f.id, t.id FROM arch AS f, arch AS t WHERE f.name = 's390' AND t.name = 'noarch'
  UNION ALL
  SELECT f.id, t.id FROM arch AS f, arch AS t WHERE f.name = 's390' AND t.name = 's390'
  UNION ALL
  SELECT f.id, t.id FROM arch AS f, arch AS t WHERE f.name = 'noarch' AND t.name = 's390'
  UNION ALL
  SELECT f.id, t.id FROM arch AS f, arch AS t WHERE f.name = 'athlon' AND t.name = 'noarch'
  UNION ALL
  SELECT f.id, t.id FROM arch AS f, arch AS t WHERE f.name = 'athlon' AND t.name = 'athlon'
  UNION ALL
  SELECT f.id, t.id FROM arch AS f, arch AS t WHERE f.name = 'noarch' AND t.name = 'athlon'
  UNION ALL
  SELECT f.id, t.id FROM arch AS f, arch AS t WHERE f.name = 's390x' AND t.name = 'noarch'
  UNION ALL
  SELECT f.id, t.id FROM arch AS f, arch AS t WHERE f.name = 's390x' AND t.name = 's390x'
  UNION ALL
  SELECT f.id, t.id FROM arch AS f, arch AS t WHERE f.name = 'noarch' AND t.name = 's390x'
  UNION ALL
  SELECT f.id, t.id FROM arch AS f, arch AS t WHERE f.name = 'ppc' AND t.name = 'noarch'
  UNION ALL
  SELECT f.id, t.id FROM arch AS f, arch AS t WHERE f.name = 'ppc' AND t.name = 'ppc'
  UNION ALL
  SELECT f.id, t.id FROM arch AS f, arch AS t WHERE f.name = 'noarch' AND t.name = 'ppc'
  UNION ALL
  SELECT f.id, t.id FROM arch AS f, arch AS t WHERE f.name = 'ppc64' AND t.name = 'noarch'
  UNION ALL
  SELECT f.id, t.id FROM arch AS f, arch AS t WHERE f.name = 'ppc64' AND t.name = 'ppc64'
  UNION ALL
  SELECT f.id, t.id FROM arch AS f, arch AS t WHERE f.name = 'noarch' AND t.name = 'ppc64le'
  UNION ALL
  SELECT f.id, t.id FROM arch AS f, arch AS t WHERE f.name = 'ppc64le' AND t.name = 'ppc64le'
  UNION ALL
  SELECT f.id, t.id FROM arch AS f, arch AS t WHERE f.name = 'ppc64le' AND t.name = 'noarch'
  UNION ALL
  SELECT f.id, t.id FROM arch AS f, arch AS t WHERE f.name = 'noarch' AND t.name = 'ppc64'
  UNION ALL
  SELECT f.id, t.id FROM arch AS f, arch AS t WHERE f.name = 'pseries' AND t.name = 'noarch'
  UNION ALL
  SELECT f.id, t.id FROM arch AS f, arch AS t WHERE f.name = 'pseries' AND t.name = 'pseries'
  UNION ALL
  SELECT f.id, t.id FROM arch AS f, arch AS t WHERE f.name = 'noarch' AND t.name = 'pseries'
  UNION ALL
  SELECT f.id, t.id FROM arch AS f, arch AS t WHERE f.name = 'iseries' AND t.name = 'noarch'
  UNION ALL
  SELECT f.id, t.id FROM arch AS f, arch AS t WHERE f.name = 'iseries' AND t.name = 'iseries'
  UNION ALL
  SELECT f.id, t.id FROM arch AS f, arch AS t WHERE f.name = 'noarch' AND t.name = 'iseries'
  UNION ALL
  SELECT f.id, t.id FROM arch AS f, arch AS t WHERE f.name = 'x86_64' AND t.name = 'noarch'
  UNION ALL
  SELECT f.id, t.id FROM arch AS f, arch AS t WHERE f.name = 'x86_64' AND t.name = 'x86_64'
  UNION ALL
  SELECT f.id, t.id FROM arch AS f, arch AS t WHERE f.name = 'noarch' AND t.name = 'x86_64'
  UNION ALL
  SELECT f.id, t.id FROM arch AS f, arch AS t WHERE f.name = 'ppc64iseries' AND t.name = 'noarch'
  UNION ALL
  SELECT f.id, t.id FROM arch AS f, arch AS t WHERE f.name = 'ppc64iseries' AND t.name = 'ppc64iseries'
  UNION ALL
  SELECT f.id, t.id FROM arch AS f, arch AS t WHERE f.name = 'noarch' AND t.name = 'ppc64iseries'
  UNION ALL
  SELECT f.id, t.id FROM arch AS f, arch AS t WHERE f.name = 'ppc64pseries' AND t.name = 'noarch'
  UNION ALL
  SELECT f.id, t.id FROM arch AS f, arch AS t WHERE f.name = 'ppc64pseries' AND t.name = 'ppc64pseries'
  UNION ALL
  SELECT f.id, t.id FROM arch AS f, arch AS t WHERE f.name = 'noarch' AND t.name = 'ppc64pseries'
  UNION ALL
  SELECT f.id, t.id FROM arch AS f, arch AS t WHERE f.name = 'noarch' AND t.name = 'armv7l'
  UNION ALL
  SELECT f.id, t.id FROM arch AS f, arch AS t WHERE f.name = 'armv7l' AND t.name = 'armv7l'
  UNION ALL
  SELECT f.id, t.id FROM arch AS f, arch AS t WHERE f.name = 'armv7l' AND t.name = 'noarch'
  UNION ALL
  SELECT f.id, t.id FROM arch AS f, arch AS t WHERE f.name = 'noarch' AND t.name = 'armv6hl'
  UNION ALL
  SELECT f.id, t.id FROM arch AS f, arch AS t WHERE f.name = 'armv6hl' AND t.name = 'armv6hl'
  UNION ALL
  SELECT f.id, t.id FROM arch AS f, arch AS t WHERE f.name = 'armv6hl' AND t.name = 'noarch'
  UNION ALL
  SELECT f.id, t.id FROM arch AS f, arch AS t WHERE f.name = 'noarch' AND t.name = 'armv6l'
  UNION ALL
  SELECT f.id, t.id FROM arch AS f, arch AS t WHERE f.name = 'armv6l' AND t.name = 'armv6l'
  UNION ALL
  SELECT f.id, t.id FROM arch AS f, arch AS t WHERE f.name = 'armv6l' AND t.name = 'noarch'
  UNION ALL
  SELECT f.id, t.id FROM arch AS f, arch AS t WHERE f.name = 'noarch' AND t.name = 'armv5tel'
  UNION ALL
  SELECT f.id, t.id FROM arch AS f, arch AS t WHERE f.name = 'armv5tel' AND t.name = 'armv5tel'
  UNION ALL
  SELECT f.id, t.id FROM arch AS f, arch AS t WHERE f.name = 'armv5tel' AND t.name = 'noarch'
  UNION ALL
  SELECT f.id, t.id FROM arch AS f, arch AS t WHERE f.name = 'noarch' AND t.name = 'armv7hl'
  UNION ALL
  SELECT f.id, t.id FROM arch AS f, arch AS t WHERE f.name = 'armv7hl' AND t.name = 'armv7hl'
  UNION ALL
  SELECT f.id, t.id FROM arch AS f, arch AS t WHERE f.name = 'armv7hl' AND t.name = 'noarch'
  UNION ALL
  SELECT f.id, t.id FROM arch AS f, arch AS t WHERE f.name = 'noarch' AND t.name = 'armv7hnl'
  UNION ALL
  SELECT f.id, t.id FROM arch AS f, arch AS t WHERE f.name = 'armv7hnl' AND t.name = 'armv7hnl'
  UNION ALL
  SELECT f.id, t.id FROM arch AS f, arch AS t WHERE f.name = 'armv7hnl' AND t.name = 'noarch'
  UNION ALL
  SELECT f.id, t.id FROM arch AS f, arch AS t WHERE f.name = 'noarch' AND t.name = 'aarch64'
  UNION ALL
  SELECT f.id, t.id FROM arch AS f, arch AS t WHERE f.name = 'aarch64' AND t.name = 'aarch64'
  UNION ALL
  SELECT f.id, t.id FROM arch AS f, arch AS t WHERE f.name = 'aarch64' AND t.name = 'noarch'
  UNION ALL
  SELECT f.id, t.id FROM arch AS f, arch AS t WHERE f.name = 'amd64' AND t.name = 'noarch'
  UNION ALL
  SELECT f.id, t.id FROM arch AS f, arch AS t WHERE f.name = 'amd64' AND t.name = 'amd64'
  UNION ALL
  SELECT f.id, t.id FROM arch AS f, arch AS t WHERE f.name = 'noarch' AND t.name = 'amd64';


-- -----------------------------------------------------
-- Table vmaas.package_name
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS package_name (
  id SERIAL,
  name TEXT NOT NULL UNIQUE, CHECK (NOT empty(name)),
  PRIMARY KEY (id)
)TABLESPACE pg_default;


-- -----------------------------------------------------
-- Table vmaas.package
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS package (
  id SERIAL,
  name_id INT NOT NULL,
  evr_id INT NOT NULL,
  arch_id INT NOT NULL,
  summary TEXT NULL, CHECK (NOT empty(summary)),
  description TEXT NULL, CHECK (NOT empty(description)),
  source_package_id INT NULL,
  UNIQUE (name_id, evr_id, arch_id),
  PRIMARY KEY (id),
  CONSTRAINT name_id
    FOREIGN KEY (name_id)
    REFERENCES package_name (id),
  CONSTRAINT evr_id
    FOREIGN KEY (evr_id)
    REFERENCES evr (id),
  CONSTRAINT arch_id
    FOREIGN KEY (arch_id)
    REFERENCES arch (id),
  CONSTRAINT source_package_id
    FOREIGN KEY (source_package_id)
    REFERENCES package (id)
)TABLESPACE pg_default;

CREATE INDEX ON package(name_id);
CREATE INDEX ON package(evr_id);


-- -----------------------------------------------------
-- Table vmaas.product
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS product (
  id SERIAL,
  name TEXT NOT NULL UNIQUE, CHECK (NOT empty(name)),
  redhat_eng_product_id INT NULL UNIQUE,
  PRIMARY KEY (id)
)TABLESPACE pg_default;


-- -----------------------------------------------------
-- Table vmaas.content_set
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS content_set (
  id SERIAL,
  label TEXT NOT NULL UNIQUE, CHECK (NOT empty(label)),
  name TEXT NULL, CHECK (NOT empty(name)),
  product_id INT NOT NULL,
  PRIMARY KEY (id),
  CONSTRAINT product_id
    FOREIGN KEY (product_id)
    REFERENCES product (id)
)TABLESPACE pg_default;


-- -----------------------------------------------------
-- Table vmaas.certificate
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS certificate (
  id SERIAL,
  name TEXT NOT NULL UNIQUE, CHECK (NOT empty(name)),
  ca_cert TEXT NOT NULL, CHECK (NOT empty(ca_cert)),
  cert TEXT NULL, CHECK (NOT empty(cert)),
  key TEXT NULL, CHECK (NOT empty(key)),
  CONSTRAINT cert_key CHECK(key IS NULL OR cert IS NOT NULL),
  PRIMARY KEY (id)
)TABLESPACE pg_default;


-- -----------------------------------------------------
-- Table vmaas.repo
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS repo (
  id SERIAL,
  url TEXT NOT NULL, CHECK (NOT empty(url)),
  content_set_id INT NOT NULL,
  basearch_id INT NULL,
  releasever TEXT NULL, CHECK (NOT empty(releasever)),
  eol BOOLEAN NOT NULL,
  revision TIMESTAMP WITH TIME ZONE NULL,
  certificate_id INT NULL,
  PRIMARY KEY (id),
  CONSTRAINT content_set_id
    FOREIGN KEY (content_set_id)
    REFERENCES content_set (id),
  CONSTRAINT basearch_id
    FOREIGN KEY (basearch_id)
    REFERENCES arch (id),
  CONSTRAINT certificate_id
    FOREIGN KEY (certificate_id)
    REFERENCES certificate (id)
)TABLESPACE pg_default;
CREATE UNIQUE INDEX repo_content_set_id_key ON repo (content_set_id) WHERE basearch_id IS NULL AND releasever IS NULL;
CREATE UNIQUE INDEX repo_content_set_id_basearch_id_key ON repo (content_set_id, basearch_id) WHERE basearch_id IS NOT NULL AND releasever IS NULL;
CREATE UNIQUE INDEX repo_content_set_id_releasever_key ON repo (content_set_id, releasever) WHERE basearch_id IS NULL AND releasever IS NOT NULL;
CREATE UNIQUE INDEX repo_content_set_id_basearch_id_releasever_key ON repo (content_set_id, basearch_id, releasever) WHERE basearch_id IS NOT NULL AND releasever IS NOT NULL;
CREATE TRIGGER repo_changed AFTER INSERT OR UPDATE OR DELETE ON repo
  FOR EACH STATEMENT
  EXECUTE PROCEDURE repos_changed();


-- -----------------------------------------------------
-- Table vmaas.pkg_repo
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS pkg_repo (
  pkg_id INT NOT NULL,
  repo_id INT NOT NULL,
  UNIQUE (pkg_id, repo_id),
  CONSTRAINT pkg_id
    FOREIGN KEY (pkg_id)
    REFERENCES package (id),
  CONSTRAINT repo_id
    FOREIGN KEY (repo_id)
    REFERENCES repo (id)
)TABLESPACE pg_default;
CREATE TRIGGER pkg_repo_changed AFTER INSERT OR UPDATE OR DELETE ON pkg_repo
  FOR EACH STATEMENT
  EXECUTE PROCEDURE repos_changed();

CREATE INDEX ON pkg_repo(repo_id);


-- -----------------------------------------------------
-- Table vmaas.errata_severity
-- from https://access.redhat.com/security/updates/classification
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS errata_severity (
  id INT NOT NULL,
  name TEXT NOT NULL UNIQUE, CHECK (NOT empty(name)),
  PRIMARY KEY (id)
)TABLESPACE pg_default;

INSERT INTO errata_severity (id, name) VALUES
  (1, 'None'), (2, 'Low'), (3, 'Moderate'), (4, 'Important'), (5, 'Critical');


-- -----------------------------------------------------
-- Table vmaas.errata_type
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS errata_type (
  id SERIAL,
  name TEXT NOT NULL UNIQUE, CHECK (NOT empty(name)),
  PRIMARY KEY (id)
)TABLESPACE pg_default;


-- -----------------------------------------------------
-- Table vmaas.errata
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS errata (
  id SERIAL,
  name TEXT NOT NULL UNIQUE, CHECK (NOT empty(name)),
  synopsis TEXT, CHECK (NOT empty(synopsis)),
  severity_id INT,
  errata_type_id INT NOT NULL,
  summary TEXT, CHECK (NOT empty(summary)),
  description TEXT, CHECK (NOT empty(description)),
  solution TEXT, CHECK (NOT empty(solution)),
  issued TIMESTAMP WITH TIME ZONE NOT NULL,
  updated TIMESTAMP WITH TIME ZONE NOT NULL,
  PRIMARY KEY (id),
  CONSTRAINT severity_id
    FOREIGN KEY (severity_id)
    REFERENCES errata_severity (id),
  CONSTRAINT errata_type_id
    FOREIGN KEY (errata_type_id)
    REFERENCES errata_type (id)
)TABLESPACE pg_default;
CREATE TRIGGER errata_changed AFTER INSERT OR UPDATE OR DELETE ON errata
  FOR EACH STATEMENT
  EXECUTE PROCEDURE errata_changed();


-- -----------------------------------------------------
-- Table vmaas.errata_repo
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS errata_repo (
  errata_id INT NOT NULL,
  repo_id INT NOT NULL,
  UNIQUE (errata_id, repo_id),
  CONSTRAINT errata_id
    FOREIGN KEY (errata_id)
    REFERENCES errata (id),
  CONSTRAINT repo_id
    FOREIGN KEY (repo_id)
    REFERENCES repo (id)
)TABLESPACE pg_default;
CREATE TRIGGER errata_repo AFTER INSERT OR UPDATE OR DELETE ON errata_repo
  FOR EACH STATEMENT
  EXECUTE PROCEDURE errata_changed();

CREATE INDEX ON errata_repo(repo_id);


-- -----------------------------------------------------
-- Table vmaas.cve_impact
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS cve_impact (
  id INT NOT NULL,
  name TEXT NOT NULL UNIQUE, CHECK (NOT empty(name)),
  PRIMARY KEY (id)
)TABLESPACE pg_default;

INSERT INTO cve_impact (id, name) VALUES
  (0, 'NotSet'), (1, 'None'), (2, 'Low'), (3, 'Medium'), (4, 'Moderate'),
  (5, 'Important'), (6, 'High'), (7, 'Critical');

-- -----------------------------------------------------
-- Table vmaas.cve_source
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS cve_source (
  id INT NOT NULL,
  name TEXT NOT NULL UNIQUE, CHECK (NOT empty(name)),
  PRIMARY KEY (id)
)TABLESPACE pg_default;

INSERT INTO cve_source (id, name) VALUES
  (1, 'Red Hat');

-- -----------------------------------------------------
-- Table vmaas.cve
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS cve (
  id SERIAL,
  name TEXT NOT NULL UNIQUE, CHECK (NOT empty(name)),
  description TEXT NULL, CHECK (NOT empty(description)),
  impact_id INT NOT NULL DEFAULT 0,
  published_date TIMESTAMP WITH TIME ZONE NULL,
  modified_date TIMESTAMP WITH TIME ZONE NULL,
  cvss3_score NUMERIC(5,3),
  cvss3_metrics TEXT, CHECK (NOT empty(cvss3_metrics)),
  iava TEXT, CHECK (NOT empty(iava)),
  redhat_url TEXT, CHECK (NOT empty(redhat_url)),
  secondary_url TEXT, CHECK (NOT empty(secondary_url)),
  source_id INT,
  cvss2_score NUMERIC(5,3),
  cvss2_metrics TEXT, CHECK (NOT empty(cvss2_metrics)),
  PRIMARY KEY (id),
  CONSTRAINT impact_id
    FOREIGN KEY (impact_id)
    REFERENCES cve_impact (id),
  CONSTRAINT cve_source_id
    FOREIGN KEY (source_id)
    REFERENCES cve_source (id)
)TABLESPACE pg_default;
CREATE TRIGGER cve_changed AFTER INSERT OR UPDATE OR DELETE ON cve
  FOR EACH STATEMENT
  EXECUTE PROCEDURE cves_changed();

-- -----------------------------------------------------
-- Table vmaas.cwe
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS cwe (
  id SERIAL,
  name TEXT NOT NULL UNIQUE, CHECK (NOT empty(name)),
  link TEXT NOT NULL, CHECK (NOT empty(link)),
  PRIMARY KEY (id)
)TABLESPACE pg_default;
-- -----------------------------------------------------
-- Table vmaas.cve_cwe
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS cve_cwe (
  cve_id INT NOT NULL,
  cwe_id INT NOT NULL,
  UNIQUE (cve_id, cwe_id),
  CONSTRAINT cve_id
    FOREIGN KEY (cve_id)
    REFERENCES cve (id),
  CONSTRAINT cwe_id
    FOREIGN KEY (cwe_id)
    REFERENCES cwe (id)
)TABLESPACE pg_default;
CREATE TRIGGER cve_cwe_changed AFTER INSERT OR UPDATE OR DELETE ON cve_cwe
  FOR EACH STATEMENT
  EXECUTE PROCEDURE cves_changed();

CREATE INDEX ON cve_cwe(cwe_id);


-- -----------------------------------------------------
-- Table vmaas.errata_cve
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS errata_cve (
  errata_id INT NOT NULL,
  cve_id INT NOT NULL,
  UNIQUE (errata_id, cve_id),
  CONSTRAINT errata_id
    FOREIGN KEY (errata_id)
    REFERENCES errata (id),
  CONSTRAINT cve_id
    FOREIGN KEY (cve_id)
    REFERENCES cve (id)
)TABLESPACE pg_default;
CREATE TRIGGER errata_cve_changed AFTER INSERT OR UPDATE OR DELETE ON errata_cve
  FOR EACH STATEMENT
  EXECUTE PROCEDURE errata_changed();

CREATE INDEX ON errata_cve(cve_id);


-- -----------------------------------------------------
-- Table vmaas.errata_refs
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS errata_refs (
  errata_id INT NOT NULL,
  type TEXT NOT NULL, CHECK (NOT empty(type)),
  name TEXT NOT NULL, CHECK (NOT empty(name)),
  UNIQUE (errata_id, type, name),
  CONSTRAINT errata_id
    FOREIGN KEY (errata_id)
    REFERENCES errata (id)
)TABLESPACE pg_default;
CREATE TRIGGER errata_refs_changed AFTER INSERT OR UPDATE OR DELETE ON errata_refs
  FOR EACH STATEMENT
  EXECUTE PROCEDURE errata_changed();

-- -----------------------------------------------------
-- Table vmaas.metadata
-- -----------------------------------------------------
-- This table holds different timestamps, checksums and
-- other persistent data for vmaas processes.
-- E.g. source timestamps for cve importer

CREATE TABLE IF NOT EXISTS metadata (
  id SERIAL,
  key TEXT NOT NULL UNIQUE, CHECK (NOT empty(key)),
  value TEXT NOT NULL, CHECK (NOT empty(value)),
  PRIMARY KEY (id)
)TABLESPACE pg_default;

-- Table vmaas.dbchange
-- This table is updated by database triggers on changes to errata, cve, or repo entities
-- It provides a shortcut for external users to be able to tell if there is any 'new' data
-- since they last talked to the db
CREATE TABLE IF NOT EXISTS  dbchange (
  errata_changes TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
  cve_changes TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
  repository_changes TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
  last_change TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
  pkgtree_change TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
)TABLESPACE pg_default;
CREATE TRIGGER last_change AFTER UPDATE OF errata_changes, cve_changes, repository_changes, pkgtree_change ON dbchange
  FOR EACH STATEMENT EXECUTE PROCEDURE last_change();
INSERT INTO dbchange (errata_changes, cve_changes, repository_changes, pkgtree_change)
  VALUES (CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);

-- -----------------------------------------------------
-- Table vmaas.module
-- -----------------------------------------------------

CREATE TABLE IF NOT EXISTS module (
  id SERIAL,
  name VARCHAR(32) NOT NULL,
  repo_id INT NOT NULL,
  arch_id INT NOT NULL,
  PRIMARY KEY (id),
  CONSTRAINT repo_id
    FOREIGN KEY (repo_id)
    REFERENCES repo (id),
  CONSTRAINT arch_id
    FOREIGN KEY (arch_id)
    REFERENCES arch (id),
  CONSTRAINT module_name_repo_arch_id_uq
    UNIQUE (name, repo_id, arch_id)
) TABLESPACE pg_default;

-- -----------------------------------------------------
-- Table vmaas.module_stream
-- -----------------------------------------------------

CREATE TABLE IF NOT EXISTS module_stream (
  id SERIAL,
  module_id INT NOT NULL,
  stream_name VARCHAR(8) NOT NULL,
  version BIGINT NOT NULL,
  context VARCHAR(8) NOT NULL,
  is_default BOOLEAN NOT NULL,
  PRIMARY KEY (id),
  CONSTRAINT module_id
    FOREIGN KEY (module_id)
    REFERENCES module (id),
  CONSTRAINT module_stream_ids_uq
    UNIQUE (module_id, stream_name, version, context)
) TABLESPACE pg_default;

-- -----------------------------------------------------
-- Table vmaas.module_profile
-- -----------------------------------------------------

CREATE TABLE IF NOT EXISTS module_profile (
  id SERIAL,
  stream_id INT NOT NULL,
  profile_name VARCHAR(16) NOT NULL,
  is_default BOOLEAN NOT NULL,
  PRIMARY KEY (id),
  CONSTRAINT stream_id
    FOREIGN KEY (stream_id)
    REFERENCES module_stream (id),
  CONSTRAINT module_profile_stream_uq
    UNIQUE (stream_id, profile_name)
) TABLESPACE pg_default;

-- -----------------------------------------------------
-- Table vmaas.module_rpm_artifact
-- -----------------------------------------------------

CREATE TABLE IF NOT EXISTS module_rpm_artifact (
  pkg_id INT NOT NULL,
  stream_id INT NOT NULL,
  CONSTRAINT pkg_id
    FOREIGN KEY (pkg_id)
    REFERENCES package (id),
  CONSTRAINT stream_id
    FOREIGN KEY (stream_id)
    REFERENCES module_stream (id),
  CONSTRAINT module_rpm_artifact_ids_uq
    UNIQUE (pkg_id, stream_id)
) TABLESPACE pg_default;

-- -----------------------------------------------------
-- Table vmaas.module_profile_pkg
-- -----------------------------------------------------

CREATE TABLE IF NOT EXISTS module_profile_pkg (
  package_name_id INT NOT NULL,
  profile_id INT NOT NULL,
  CONSTRAINT package_name_id
    FOREIGN KEY (package_name_id)
    REFERENCES package_name (id),
  CONSTRAINT profile_id
    FOREIGN KEY (profile_id)
    REFERENCES module_profile (id),
  CONSTRAINT module_profile_pkg_ids_uq
    UNIQUE (package_name_id, profile_id)
) TABLESPACE pg_default;


-- -----------------------------------------------------
-- Table vmaas.pkg_errata
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS pkg_errata (
  pkg_id INT NOT NULL,
  errata_id INT NOT NULL,
  module_stream_id INT,
  CONSTRAINT pkg_id
    FOREIGN KEY (pkg_id)
    REFERENCES package (id),
  CONSTRAINT errata_id
    FOREIGN KEY (errata_id)
    REFERENCES errata (id),
  CONSTRAINT module_stream_id
    FOREIGN KEY (module_stream_id)
    REFERENCES module_stream (id)
)TABLESPACE pg_default;
CREATE TRIGGER pkg_errata_changed AFTER INSERT OR UPDATE OR DELETE ON pkg_errata
  FOR EACH STATEMENT
  EXECUTE PROCEDURE errata_changed();

CREATE UNIQUE INDEX pkg_errata_pkgid_errataid ON pkg_errata (pkg_id, errata_id)
WHERE module_stream_id IS NULL;
CREATE UNIQUE INDEX pkg_errata_pkgid_streamid_errataid ON pkg_errata (pkg_id, module_stream_id, errata_id)
WHERE module_stream_id IS NOT NULL;

CREATE INDEX ON pkg_errata(errata_id);
CREATE INDEX ON pkg_errata(module_stream_id);

CREATE TABLE IF NOT EXISTS db_upgrade_log (
  id SERIAL,
  version INT NOT NULL,
  status TEXT NOT NULL,
  script TEXT,
  returncode INT,
  stdout TEXT,
  stderr TEXT,
  last_updated TIMESTAMP WITH TIME ZONE NOT NULL
) TABLESPACE pg_default;

CREATE TRIGGER db_upgrade_log_set_last_updated
  BEFORE INSERT OR UPDATE ON db_upgrade_log
  FOR EACH ROW EXECUTE PROCEDURE set_last_updated();


-- -----------------------------------------------------
-- vmaas users permission setup:
-- vmaas_writer - has rights to INSERT/UPDATE/DELETE; used by reposcan
-- vmaas_reader - has SELECT only; used by webapp
-- -----------------------------------------------------
CREATE USER vmaas_writer;
CREATE USER vmaas_reader;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO vmaas_writer;
GRANT USAGE, SELECT, UPDATE ON ALL SEQUENCES IN SCHEMA public TO vmaas_writer;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO vmaas_reader;
