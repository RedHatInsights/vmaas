TRUNCATE TABLE oval_file_definition;
TRUNCATE TABLE oval_definition_cpe;
TRUNCATE TABLE oval_definition_errata;
TRUNCATE TABLE oval_definition_cve;
TRUNCATE TABLE oval_definition_test;
TRUNCATE TABLE oval_definition CASCADE;
TRUNCATE TABLE oval_criteria_dependency;
TRUNCATE TABLE oval_criteria CASCADE;
TRUNCATE TABLE oval_file_rpminfo_test;
TRUNCATE TABLE oval_rpminfo_test_state;
TRUNCATE TABLE oval_rpminfo_test CASCADE;
TRUNCATE TABLE oval_file_rpminfo_state;
TRUNCATE TABLE oval_rpminfo_state_arch;
TRUNCATE TABLE oval_rpminfo_state CASCADE;
TRUNCATE TABLE oval_file_rpminfo_object;
TRUNCATE TABLE oval_rpminfo_object CASCADE;
TRUNCATE TABLE oval_file_module_test;
TRUNCATE TABLE oval_module_test CASCADE;
TRUNCATE TABLE oval_file CASCADE;

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
