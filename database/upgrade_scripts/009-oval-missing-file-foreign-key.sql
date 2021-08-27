ALTER TABLE oval_rpminfo_object ADD CONSTRAINT file_id FOREIGN KEY (file_id) REFERENCES oval_file (id);
ALTER TABLE oval_rpminfo_state ADD CONSTRAINT file_id FOREIGN KEY (file_id) REFERENCES oval_file (id);
ALTER TABLE oval_rpminfo_test ADD CONSTRAINT file_id FOREIGN KEY (file_id) REFERENCES oval_file (id);
ALTER TABLE oval_module_test ADD CONSTRAINT file_id FOREIGN KEY (file_id) REFERENCES oval_file (id);
ALTER TABLE oval_definition ADD CONSTRAINT file_id FOREIGN KEY (file_id) REFERENCES oval_file (id);

CREATE INDEX ON oval_rpminfo_test(rpminfo_object_id); -- deletion performance
CREATE INDEX ON oval_rpminfo_test_state(rpminfo_state_id); -- deletion performance
CREATE INDEX ON oval_criteria_dependency(dep_test_id); -- deletion performance
CREATE INDEX ON oval_criteria_dependency(dep_module_test_id); -- deletion performance
CREATE INDEX ON oval_definition_test(rpminfo_test_id); -- deletion performance
