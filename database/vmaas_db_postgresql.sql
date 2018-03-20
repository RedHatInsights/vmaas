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


create or replace function isdigit(ch CHAR)
    RETURNS BOOLEAN as $$
    BEGIN
        if ascii(ch) between ascii('0') and ascii('9')
        then
            return TRUE;
        end if;
        return FALSE;
    END ;
$$ language 'plpgsql';


    create or replace FUNCTION isalpha(ch CHAR)
    RETURNS BOOLEAN as $$
    BEGIN
        if ascii(ch) between ascii('a') and ascii('z') or
            ascii(ch) between ascii('A') and ascii('Z')
        then
            return TRUE;
        end if;
        return FALSE;
    END;
$$ language 'plpgsql';


create or replace FUNCTION isalphanum(ch CHAR)
RETURNS BOOLEAN as $$
BEGIN
    if ascii(ch) between ascii('a') and ascii('z') or
        ascii(ch) between ascii('A') and ascii('Z') or
        ascii(ch) between ascii('0') and ascii('9')
    then
        return TRUE;
    end if;
    return FALSE;
END;
$$ language 'plpgsql';


create or replace FUNCTION rpmver_array (string1 IN VARCHAR)
RETURNS evr_array_item[] as $$
declare
    str1 VARCHAR := string1;
    digits VARCHAR(10) := '0123456789';
    lc_alpha VARCHAR(27) := 'abcdefghijklmnopqrstuvwxyz';
    uc_alpha VARCHAR(27) := 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
    alpha VARCHAR(54) := lc_alpha || uc_alpha;
    one VARCHAR;
    isnum BOOLEAN;
    ver_array evr_array_item[] := ARRAY[]::evr_array_item[];
BEGIN
    if str1 is NULL
    then
        RAISE EXCEPTION 'VALUE_ERROR.';
    end if;

    one := str1;
    <<segment_loop>>
    while one <> ''
    loop
        declare
            segm1 VARCHAR;
            segm1_n NUMERIC := 0;
        begin
            -- Throw out all non-alphanum characters
            while one <> '' and not isalphanum(one)
            loop
                one := substr(one, 2);
            end loop;
            str1 := one;
            if str1 <> '' and isdigit(str1)
            then
                str1 := ltrim(str1, digits);
                isnum := true;
            else
                str1 := ltrim(str1, alpha);
                isnum := false;
            end if;
            if str1 <> ''
            then segm1 := substr(one, 1, length(one) - length(str1));
            else segm1 := one;
            end if;

            if segm1 = '' then return ver_array; end if; /* arbitrary */
            if isnum
            then
                segm1 := ltrim(segm1, '0');
                if segm1 <> '' then segm1_n := segm1::numeric; end if;
                segm1 := NULL;
            else
            end if;
            ver_array := array_append(ver_array, (segm1_n, segm1)::evr_array_item);
            one := str1;
        end;
    end loop segment_loop;

    return ver_array;
END ;
$$ language 'plpgsql';


-- -----------------------------------------------------
-- Table vmaas.evr
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS evr (
  id SERIAL,
  epoch TEXT NOT NULL,
  version TEXT NOT NULL,
  release TEXT NOT NULL,
  evr evr_t NOT NULL,
  UNIQUE (epoch, version, release),
  PRIMARY KEY (id)
)TABLESPACE pg_default;


-- -----------------------------------------------------
-- Table vmaas.checksum_type
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS checksum_type (
  id SERIAL,
  name TEXT NOT NULL UNIQUE,
  PRIMARY KEY (id)
)TABLESPACE pg_default;


-- -----------------------------------------------------
-- Table vmaas.arch
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS arch (
  id SERIAL,
  name TEXT NOT NULL UNIQUE,
  PRIMARY KEY (id)
)TABLESPACE pg_default;


-- -----------------------------------------------------
-- Table vmaas.package
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS package (
  id SERIAL,
  name TEXT NOT NULL,
  evr_id INT NOT NULL,
  arch_id INT NOT NULL,
  checksum TEXT NOT NULL,
  checksum_type_id INT NOT NULL,
  UNIQUE (checksum_type_id, checksum),
  PRIMARY KEY (id),
  CONSTRAINT evr_id
    FOREIGN KEY (evr_id)
    REFERENCES evr (id),
  CONSTRAINT arch_id
    FOREIGN KEY (arch_id)
    REFERENCES arch (id),
  CONSTRAINT checksum_type_id
    FOREIGN KEY (checksum_type_id)
    REFERENCES checksum_type (id)
)TABLESPACE pg_default;


-- -----------------------------------------------------
-- Table vmaas.product
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS product (
  id SERIAL,
  name TEXT NOT NULL UNIQUE,
  redhat_eng_product_id INT NULL UNIQUE,
  PRIMARY KEY (id)
)TABLESPACE pg_default;


-- -----------------------------------------------------
-- Table vmaas.content_set
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS content_set (
  id SERIAL,
  label TEXT NOT NULL UNIQUE,
  name TEXT NULL,
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
  name TEXT NOT NULL UNIQUE,
  ca_cert TEXT NOT NULL,
  cert TEXT NULL,
  key TEXT NULL,
  CONSTRAINT cert_key CHECK(key IS NULL OR cert IS NOT NULL),
  PRIMARY KEY (id)
)TABLESPACE pg_default;


-- -----------------------------------------------------
-- Table vmaas.repo
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS repo (
  id SERIAL,
  label TEXT NOT NULL UNIQUE,
  name TEXT NULL,
  url TEXT NOT NULL,
  content_set_id INT NULL,
  arch_id INT NULL,
  releasever TEXT NULL,
  eol BOOLEAN NOT NULL,
  revision TIMESTAMP WITH TIME ZONE NOT NULL,
  certificate_id INT NULL,
  PRIMARY KEY (id),
  CONSTRAINT content_set_id
    FOREIGN KEY (content_set_id)
    REFERENCES content_set (id),
  CONSTRAINT arch_id
    FOREIGN KEY (arch_id)
    REFERENCES arch (id),
  CONSTRAINT certificate_id
    FOREIGN KEY (certificate_id)
    REFERENCES certificate (id)
)TABLESPACE pg_default;


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


-- -----------------------------------------------------
-- Table vmaas.severity
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS severity (
  id SERIAL,
  name TEXT NOT NULL UNIQUE,
  PRIMARY KEY (id)
)TABLESPACE pg_default;


-- -----------------------------------------------------
-- Table vmaas.errata_type
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS errata_type (
  id SERIAL,
  name TEXT NOT NULL UNIQUE,
  PRIMARY KEY (id)
)TABLESPACE pg_default;


-- -----------------------------------------------------
-- Table vmaas.errata
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS errata (
  id SERIAL,
  name TEXT NOT NULL UNIQUE,
  synopsis TEXT NOT NULL,
  severity_id INT NOT NULL,
  errata_type_id INT NOT NULL,
  summary TEXT NOT NULL,
  description TEXT NOT NULL,
  solution TEXT,
  issued TIMESTAMP NOT NULL,
  updated TIMESTAMP NOT NULL,
  PRIMARY KEY (id),
  CONSTRAINT severity_id
    FOREIGN KEY (severity_id)
    REFERENCES severity (id),
  CONSTRAINT errata_type_id
    FOREIGN KEY (errata_type_id)
    REFERENCES errata_type (id)
)TABLESPACE pg_default;


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


-- -----------------------------------------------------
-- Table vmaas.pkg_errata
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS pkg_errata (
  pkg_id INT NOT NULL,
  errata_id INT NOT NULL,
  UNIQUE (pkg_id, errata_id),
  CONSTRAINT pkg_id
    FOREIGN KEY (pkg_id)
    REFERENCES package (id),
  CONSTRAINT errata_id
    FOREIGN KEY (errata_id)
    REFERENCES errata (id)
)TABLESPACE pg_default;


-- -----------------------------------------------------
-- Table vmaas.cve
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS cve (
  id SERIAL,
  name TEXT NOT NULL UNIQUE,
  description TEXT NULL,
  severity_id INT,
  published_date TIMESTAMP,
  modified_date TIMESTAMP,
  cvss3_score NUMERIC(5,3),
  iava TEXT,
  redhat_url TEXT,
  secondary_url TEXT,
  PRIMARY KEY (id),
  CONSTRAINT severity_id
    FOREIGN KEY (severity_id)
    REFERENCES severity (id)
)TABLESPACE pg_default;

-- -----------------------------------------------------
-- Table vmaas.cwe
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS cwe (
  id SERIAL,
  name TEXT NOT NULL UNIQUE,
  link TEXT NOT NULL,
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

-- -----------------------------------------------------
-- Table vmaas.errata_refs
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS errata_refs (
  errata_id INT NOT NULL,
  type TEXT NOT NULL,
  name TEXT NOT NULL,
  UNIQUE (errata_id, type, name),
  CONSTRAINT errata_id
    FOREIGN KEY (errata_id)
    REFERENCES errata (id)
)TABLESPACE pg_default;

-- -----------------------------------------------------
-- Table vmaas.metadata
-- -----------------------------------------------------
-- This table holds different timestamps, checksums and
-- other persistent data for vmaas processes.
-- E.g. source timestamps for cve importer

CREATE TABLE IF NOT EXISTS metadata (
  id SERIAL,
  key TEXT NOT NULL UNIQUE,
  value TEXT NOT NULL,
  PRIMARY KEY (id)
)TABLESPACE pg_default;

