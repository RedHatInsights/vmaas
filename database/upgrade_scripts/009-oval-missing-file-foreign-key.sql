ALTER TABLE oval_rpminfo_object ADD CONSTRAINT file_id FOREIGN KEY (file_id) REFERENCES oval_file (id);
ALTER TABLE oval_rpminfo_state ADD CONSTRAINT file_id FOREIGN KEY (file_id) REFERENCES oval_file (id);
ALTER TABLE oval_rpminfo_test ADD CONSTRAINT file_id FOREIGN KEY (file_id) REFERENCES oval_file (id);
ALTER TABLE oval_module_test ADD CONSTRAINT file_id FOREIGN KEY (file_id) REFERENCES oval_file (id);
ALTER TABLE oval_definition ADD CONSTRAINT file_id FOREIGN KEY (file_id) REFERENCES oval_file (id);
