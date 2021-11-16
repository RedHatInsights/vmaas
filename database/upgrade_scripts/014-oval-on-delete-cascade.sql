ALTER TABLE oval_rpminfo_state_arch
  DROP CONSTRAINT rpminfo_state_id,
  ADD CONSTRAINT rpminfo_state_id FOREIGN KEY (rpminfo_state_id) REFERENCES oval_rpminfo_state (id) ON DELETE CASCADE;

ALTER TABLE oval_rpminfo_test
  DROP CONSTRAINT rpminfo_object_id,
  ADD CONSTRAINT rpminfo_object_id FOREIGN KEY (rpminfo_object_id) REFERENCES oval_rpminfo_object (id) ON DELETE CASCADE;

ALTER TABLE oval_rpminfo_test_state
  DROP CONSTRAINT rpminfo_test_id,
  DROP CONSTRAINT rpminfo_state_id,
  ADD CONSTRAINT rpminfo_test_id FOREIGN KEY (rpminfo_test_id) REFERENCES oval_rpminfo_test (id) ON DELETE CASCADE,
  ADD CONSTRAINT rpminfo_state_id FOREIGN KEY (rpminfo_state_id) REFERENCES oval_rpminfo_state (id) ON DELETE CASCADE;

ALTER TABLE oval_definition_test
  DROP CONSTRAINT definition_id,
  DROP CONSTRAINT rpminfo_test_id,
  ADD CONSTRAINT definition_id FOREIGN KEY (definition_id) REFERENCES oval_definition (id) ON DELETE CASCADE,
  ADD CONSTRAINT rpminfo_test_id FOREIGN KEY (rpminfo_test_id) REFERENCES oval_rpminfo_test (id) ON DELETE CASCADE;

ALTER TABLE oval_definition_cve
  DROP CONSTRAINT definition_id,
  ADD CONSTRAINT definition_id FOREIGN KEY (definition_id) REFERENCES oval_definition (id) ON DELETE CASCADE;

ALTER TABLE oval_definition_errata
  DROP CONSTRAINT definition_id,
  ADD CONSTRAINT definition_id FOREIGN KEY (definition_id) REFERENCES oval_definition (id) ON DELETE CASCADE;

ALTER TABLE oval_definition_cpe
  DROP CONSTRAINT definition_id,
  ADD CONSTRAINT definition_id FOREIGN KEY (definition_id) REFERENCES oval_definition (id) ON DELETE CASCADE;

ALTER TABLE oval_criteria_dependency
  DROP CONSTRAINT dep_test_id,
  DROP CONSTRAINT dep_module_test_id,
  ADD CONSTRAINT dep_test_id FOREIGN KEY (dep_test_id) REFERENCES oval_rpminfo_test (id) ON DELETE CASCADE,
  ADD CONSTRAINT dep_module_test_id FOREIGN KEY (dep_module_test_id) REFERENCES oval_module_test (id) ON DELETE CASCADE;
