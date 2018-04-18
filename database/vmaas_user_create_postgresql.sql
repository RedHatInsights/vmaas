-- -----------------------------------------------------
-- vmaas users:
-- vmaas_writer - will have rights to INSERT/UPDATE/DELETE; used by reposcan
-- vmaas_reader - will have SELECT only; used by webapp
-- -----------------------------------------------------
CREATE USER vmaas_writer;
CREATE USER vmaas_reader;
