DELETE FROM oval_file_definition;
DELETE FROM oval_definition_cpe;
DELETE FROM oval_definition_errata;
DELETE FROM oval_definition_cve;
DELETE FROM oval_definition_test;
DELETE FROM oval_definition;
DELETE FROM oval_criteria_dependency;
DELETE FROM oval_criteria;
DELETE FROM oval_file_rpminfo_test;
DELETE FROM oval_rpminfo_test_state;
DELETE FROM oval_rpminfo_test;
DELETE FROM oval_file_rpminfo_state;
DELETE FROM oval_rpminfo_state_arch;
DELETE FROM oval_rpminfo_state;
DELETE FROM oval_file_rpminfo_object;
DELETE FROM oval_rpminfo_object;
DELETE FROM oval_file_module_test;
DELETE FROM oval_module_test;
DELETE FROM oval_file;

ALTER TABLE oval_rpminfo_object ADD COLUMN file_id INT NOT NULL;
ALTER TABLE oval_rpminfo_state ADD COLUMN file_id INT NOT NULL;
ALTER TABLE oval_rpminfo_test ADD COLUMN file_id INT NOT NULL;
ALTER TABLE oval_module_test ADD COLUMN file_id INT NOT NULL;
ALTER TABLE oval_definition ADD COLUMN file_id INT NOT NULL;

ALTER TABLE oval_rpminfo_object DROP CONSTRAINT oval_rpminfo_object_oval_id_key;
ALTER TABLE oval_rpminfo_state DROP CONSTRAINT oval_rpminfo_state_oval_id_key;
ALTER TABLE oval_rpminfo_test DROP CONSTRAINT oval_rpminfo_test_oval_id_key;
ALTER TABLE oval_module_test DROP CONSTRAINT oval_module_test_oval_id_key;
ALTER TABLE oval_definition DROP CONSTRAINT oval_definition_oval_id_key;

ALTER TABLE oval_rpminfo_object ADD UNIQUE (file_id, oval_id);
ALTER TABLE oval_rpminfo_state ADD UNIQUE (file_id, oval_id);
ALTER TABLE oval_rpminfo_test ADD UNIQUE (file_id, oval_id);
ALTER TABLE oval_module_test ADD UNIQUE (file_id, oval_id);
ALTER TABLE oval_definition ADD UNIQUE (file_id, oval_id);

DROP TABLE oval_file_rpminfo_object;
DROP TABLE oval_file_rpminfo_state;
DROP TABLE oval_file_rpminfo_test;
DROP TABLE oval_file_module_test;
DROP TABLE oval_file_definition;
