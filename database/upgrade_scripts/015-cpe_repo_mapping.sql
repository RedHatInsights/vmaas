-- -----------------------------------------------------
-- Table vmaas.cpe_repo
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS cpe_repo (
  cpe_id INT NOT NULL,
  repo_id INT NOT NULL,
  UNIQUE (cpe_id, repo_id),
  CONSTRAINT cpe_id
    FOREIGN KEY (cpe_id)
    REFERENCES cpe (id),
  CONSTRAINT repo_id
    FOREIGN KEY (repo_id)
    REFERENCES repo (id)
)TABLESPACE pg_default;
CREATE TRIGGER cpe_changed AFTER INSERT OR UPDATE OR DELETE ON cpe_repo
  FOR EACH STATEMENT
  EXECUTE PROCEDURE cpes_changed();

CREATE INDEX ON cpe_repo(repo_id);

GRANT SELECT ON TABLE cpe_repo TO vmaas_reader;
GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE cpe_repo TO vmaas_writer;
