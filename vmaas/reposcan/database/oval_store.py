"""
Module containing classes for fetching/importing OVAL data from/into database.
"""
from psycopg2.extras import execute_values

from vmaas.common.dateutil import format_datetime
from vmaas.common.rpm import parse_rpm_name
from vmaas.reposcan.database.object_store import ObjectStore
from vmaas.reposcan.database.cpe_store import CpeStore
from vmaas.reposcan.database.package_store import PackageStore


class OvalStore(ObjectStore):  # pylint: disable=too-many-instance-attributes
    """
    Class providing interface for fetching/importing OVAL data from/into the DB.
    """
    OVAL_FEED_UPDATED_KEY = 'redhatovalfeed:updated'
    # Not in DB table like other operations because we don't need this information further
    SUPPORTED_ARCH_OPERATIONS = ["equals", "pattern match"]

    def __init__(self):
        super().__init__()
        self.cpe_store = CpeStore()
        self.package_store = PackageStore()
        self.evr_operation_map = self._prepare_table_map(cols=["name"], table="oval_operation_evr")
        self.cve_map = self._prepare_table_map(cols=["name"], table="cve")
        self.errata_map = self._prepare_table_map(cols=["name"], table="errata")
        self.oval_check_map = self._prepare_table_map(cols=["name"], table="oval_check_rpminfo")
        self.oval_check_existence_map = self._prepare_table_map(cols=["name"], table="oval_check_existence_rpminfo")
        self.oval_object_map = self._prepare_table_map(cols=["file_id", "oval_id"], table="oval_rpminfo_object")
        self.oval_object_version_map = self._prepare_table_map(cols=["file_id", "oval_id"], table="oval_rpminfo_object",
                                                               to_col="version")
        self.oval_state_map = self._prepare_table_map(cols=["file_id", "oval_id"], table="oval_rpminfo_state")
        self.oval_state_version_map = self._prepare_table_map(cols=["file_id", "oval_id"], table="oval_rpminfo_state",
                                                              to_col="version")
        self.oval_test_map = self._prepare_table_map(cols=["file_id", "oval_id"], table="oval_rpminfo_test")
        self.oval_test_version_map = self._prepare_table_map(cols=["file_id", "oval_id"], table="oval_rpminfo_test",
                                                             to_col="version")
        self.oval_module_test_map = self._prepare_table_map(cols=["file_id", "oval_id"], table="oval_module_test")
        self.oval_module_test_version_map = self._prepare_table_map(cols=["file_id", "oval_id"],
                                                                    table="oval_module_test", to_col="version")
        self.oval_definition_map = self._prepare_table_map(cols=["file_id", "oval_id"], table="oval_definition")
        self.oval_definition_version_map = self._prepare_table_map(cols=["file_id", "oval_id"], table="oval_definition",
                                                                   to_col="version")
        self.oval_definition_type_map = self._prepare_table_map(cols=["name"], table="oval_definition_type")
        self.oval_criteria_operator_map = self._prepare_table_map(cols=["name"], table="oval_criteria_operator")

    def list_oval_definitions(self):
        """List oval definitions and their timestamps stored in DB. Dictionary with oval id as key is returned."""
        cur = self.conn.cursor()
        cur.execute("""select oval_id, updated from oval_file""")
        return dict(cur.fetchall())

    def save_lastmodified(self, lastmodified):
        """Store OVAL file timestamp."""
        lastmodified = format_datetime(lastmodified)
        cur = self.conn.cursor()
        # Update timestamp
        cur.execute("update metadata set value = %s where key = %s",
                    (lastmodified, self.OVAL_FEED_UPDATED_KEY,))
        if cur.rowcount < 1:
            cur.execute("insert into metadata (key, value) values (%s, %s)",
                        (self.OVAL_FEED_UPDATED_KEY, lastmodified))
        cur.close()
        self.conn.commit()

    def _save_oval_file_updated(self, oval_id, updated):
        cur = self.conn.cursor()
        # Update timestamp
        cur.execute("update oval_file set updated = %s where oval_id = %s returning id",
                    (updated, oval_id,))
        if cur.rowcount < 1:
            cur.execute("insert into oval_file (oval_id, updated) values (%s, %s) returning id",
                        (oval_id, updated,))
        db_id_row = cur.fetchone()
        cur.close()
        self.conn.commit()
        return db_id_row[0]

    def _populate_data(self, entity, file_id, data, import_check_func, query, refresh_maps_func):
        """Generic method to populate table with OVAL entity (objects, states, tests, etc.)."""
        to_import = []
        # Append only here, not delete rows, same item may be referenced from multiple files
        for item in data:
            row = import_check_func(file_id, item)
            if row:
                to_import.append(row)
        self.logger.debug("OVAL %s to import: %d", entity, len(to_import))
        if to_import:
            try:
                cur = self.conn.cursor()
                execute_values(cur, query, to_import, page_size=len(to_import))
                refresh_maps_func(cur)
                self.conn.commit()
            except Exception: # pylint: disable=broad-except
                self.logger.exception("Failure while inserting %s data: ", entity)
                self.conn.rollback()
            finally:
                cur.close()

    def _populate_associations(self, entity_one, entity_many, ent_one_id_col, ent_many_id_col,
                               table_name, ent_one_id, ent_many_data, import_check_map, file_id=None,
                               missing_ok=False):
        """Associate/disassociate many_entities (objects, states, archs) with entity_one (state, test)."""
        try:
            cur = self.conn.cursor()
            associated_with_entity_one = set()
            cur.execute(f"select {ent_many_id_col} from {table_name} where {ent_one_id_col} = %s", (ent_one_id,))
            for row in cur.fetchall():
                associated_with_entity_one.add(row[0])
            self.logger.debug("OVAL %s associated with %s %s: %d", entity_many, entity_one, ent_one_id,
                             len(associated_with_entity_one))
            to_associate = []
            for item in ent_many_data:
                checked_key = (file_id, item["id"]) if file_id else item["id"]
                item_id = import_check_map.get(checked_key)
                if not item_id:
                    if not missing_ok:
                        self.logger.warning("Item (%s) not found: %s", entity_many, checked_key)
                    continue
                if item_id in associated_with_entity_one:
                    associated_with_entity_one.remove(item_id)
                else:
                    to_associate.append(item_id)
            self.logger.debug("New OVAL %s to associate with %s %s: %d", entity_many, entity_one, ent_one_id,
                             len(to_associate))
            self.logger.debug("OVAL %s to disassociate with %s %s: %d",
                             entity_many, entity_one, ent_one_id, len(associated_with_entity_one))
            if to_associate:
                execute_values(cur, f"insert into {table_name} ({ent_one_id_col}, {ent_many_id_col}) values %s",
                               [(ent_one_id, item_id) for item_id in to_associate], page_size=len(to_associate))
            if associated_with_entity_one:
                cur.execute(f"delete from {table_name} where {ent_one_id_col} = %s and {ent_many_id_col} in %s",
                            (ent_one_id, tuple(associated_with_entity_one),))
            self.conn.commit()
        except Exception: # pylint: disable=broad-except
            self.logger.exception("Failure while (dis)associating OVAL %s with %s %s: ",
                                  entity_many, entity_one, ent_one_id)
            self.conn.rollback()
        finally:
            cur.close()

    def _object_import_check(self, file_id, item):
        """Check if object is in DB, return None if it's up to date and row to import otherwise."""
        if item["version"] <= self.oval_object_version_map.get((file_id, item["id"]), -1):
            return None
        name_id = self.package_store.package_name_map.get(item["name"])
        if not name_id:
            self.logger.warning("Package name not found: %s", item["name"])
            return None
        return file_id, item["id"], name_id, item["version"]

    def _object_refresh_maps(self, cur):
        """Add imported data to caches."""
        for obj_id, file_id, oval_id, version in cur.fetchall():
            self.oval_object_map[(file_id, oval_id)] = obj_id
            self.oval_object_version_map[(file_id, oval_id)] = version

    def _populate_objects(self, oval_file_id, objects):
        query = """insert into oval_rpminfo_object (file_id, oval_id, package_name_id, version) values %s
                   on conflict (file_id, oval_id) do update set
                   package_name_id = EXCLUDED.package_name_id, version = EXCLUDED.version
                   returning id, file_id, oval_id, version"""
        # Populate missing package names
        self.package_store.populate_dep_table("package_name", {obj["name"] for obj in objects},
                                              self.package_store.package_name_map)
        self._populate_data("objects", oval_file_id, objects, self._object_import_check, query,
                            self._object_refresh_maps)

    def _state_import_check(self, file_id, item):
        """Check if state is in DB, return None if it's up to date and row to import otherwise."""
        if item["version"] <= self.oval_state_version_map.get((file_id, item["id"]), -1):
            return None
        evr_id = evr_operation_id = None
        if item['evr'] is not None:
            epoch, version, release = item['evr']
            evr_id = self.package_store.evr_map.get((epoch, version, release))
            if not evr_id:
                self.logger.warning("EVR not found: %s, %s, %s", epoch, version, release)
                return None
        if item["evr_operation"] is not None:
            evr_operation_id = self.evr_operation_map.get(item["evr_operation"])
            if not evr_operation_id:
                self.logger.warning("Unsupported EVR operation: %s", item["evr_operation"])
                return None
        return file_id, item["id"], evr_id, evr_operation_id, item["version"]

    def _state_refresh_maps(self, cur):
        """Add imported data to caches."""
        for state_id, file_id, oval_id, version in cur.fetchall():
            self.oval_state_map[(file_id, oval_id)] = state_id
            self.oval_state_version_map[(file_id, oval_id)] = version

    def _populate_states(self, oval_file_id, states):
        query = """insert into oval_rpminfo_state (file_id, oval_id, evr_id, evr_operation_id, version) values %s
                   on conflict (file_id, oval_id) do update set
                   evr_id = EXCLUDED.evr_id, evr_operation_id = EXCLUDED.evr_operation_id,
                   version = EXCLUDED.version
                   returning id, file_id, oval_id, version"""
        # Parse EVR first
        for state in states:
            if state['evr'] is not None:
                # FIXME: as an input to common.rpm.parse_rpm_name, we don't have function to parse evr only
                fake_nevra = f"pn-{state['evr']}.noarch"
                _, epoch, version, release, _ = parse_rpm_name(fake_nevra)
                state['evr'] = (epoch, version, release)
        # Populate missing EVRs
        self.package_store.populate_evrs({state['evr'] for state in states if state['evr'] is not None})
        self._populate_data("states", oval_file_id, states, self._state_import_check, query, self._state_refresh_maps)
        for state in states:
            if state["arch_operation"] is not None and state["arch_operation"] not in self.SUPPORTED_ARCH_OPERATIONS:
                self.logger.warning("Unsupported arch operation: %s", state["arch_operation"])
                continue
            if (oval_file_id, state["id"]) in self.oval_state_map:  # Make sure state is imported
                # Simplified logic, can contain any regex but RH oval files contains only logical OR
                archs = []
                if state["arch"] is not None:
                    archs.extend([{"id": arch} for arch in state["arch"].split("|")])
                self._populate_associations("state", "archs", "rpminfo_state_id", "arch_id",
                                            "oval_rpminfo_state_arch",
                                            self.oval_state_map[(oval_file_id, state["id"])],
                                            archs, self.package_store.arch_map)

    def _test_import_check(self, file_id, item):
        """Check if test is in DB, return None if it's up to date and row to import otherwise."""
        if item["version"] <= self.oval_test_version_map.get((file_id, item["id"]), -1):
            return None
        rpminfo_object_id = self.oval_object_map.get((file_id, item["object"]))
        if not rpminfo_object_id:
            self.logger.warning("OVAL object not found: %s", item["object"])
            return None
        check_id = self.oval_check_map.get(item["check"])
        if not check_id:
            self.logger.warning("OVAL check not found: %s", item["check"])
            return None
        check_existence_id = self.oval_check_existence_map.get(item["check_existence"])
        if not check_existence_id:
            self.logger.warning("OVAL check_existence not found: %s", item["check_existence"])
            return None
        return file_id, item["id"], rpminfo_object_id, check_id, check_existence_id, item["version"]

    def _test_refresh_maps(self, cur):
        """Add imported data to caches."""
        for test_id, file_id, oval_id, version in cur.fetchall():
            self.oval_test_map[(file_id, oval_id)] = test_id
            self.oval_test_version_map[(file_id, oval_id)] = version

    def _populate_tests(self, oval_file_id, tests):
        query = """insert into oval_rpminfo_test
                   (file_id, oval_id, rpminfo_object_id, check_id, check_existence_id, version) values %s
                   on conflict (file_id, oval_id) do update set
                   rpminfo_object_id = EXCLUDED.rpminfo_object_id, check_id = EXCLUDED.check_id,
                   check_existence_id = EXCLUDED.check_existence_id, version = EXCLUDED.version
                   returning id, file_id, oval_id, version"""
        self._populate_data("tests", oval_file_id, tests, self._test_import_check, query, self._test_refresh_maps)
        for test in tests:
            if (oval_file_id, test["id"]) in self.oval_test_map:  # Make sure test is imported
                states = [{"id": state} for state in test["states"]]
                self._populate_associations("test", "states", "rpminfo_test_id", "rpminfo_state_id",
                                            "oval_rpminfo_test_state",
                                            self.oval_test_map[(oval_file_id, test["id"])],
                                            states, self.oval_state_map, file_id=oval_file_id)

    def _module_test_import_check(self, file_id, item):
        """Check if module test is in DB, return None if it's up to date and row to import otherwise."""
        if item["version"] <= self.oval_module_test_version_map.get((file_id, item["id"]), -1):
            return None
        return file_id, item["id"], item["module_stream"], item["version"]

    def _module_test_refresh_maps(self, cur):
        """Add imported data to caches."""
        for test_id, file_id, oval_id, version in cur.fetchall():
            self.oval_module_test_map[(file_id, oval_id)] = test_id
            self.oval_module_test_version_map[(file_id, oval_id)] = version

    def _populate_module_tests(self, oval_file_id, module_tests):
        query = """insert into oval_module_test
                   (file_id, oval_id, module_stream, version) values %s
                   on conflict (file_id, oval_id) do update set
                   module_stream = EXCLUDED.module_stream, version = EXCLUDED.version
                   returning id, file_id, oval_id, version"""
        self._populate_data("module-tests", oval_file_id, module_tests, self._module_test_import_check, query,
                            self._module_test_refresh_maps)

    def _populate_definition_criteria(self, cur, file_id, criteria):
        operator_id = self.oval_criteria_operator_map.get(criteria["operator"])
        if not operator_id:
            self.logger.warning("OVAL criteria operator not found: %s", criteria["operator"])
            return None
        cur.execute("insert into oval_criteria (operator_id) values (%s) returning id", (operator_id,))
        criteria_id = cur.fetchone()[0]
        dependencies_to_import = []
        for test in criteria["criterions"]:
            test_id = self.oval_test_map.get((file_id, test))
            module_test_id = self.oval_module_test_map.get((file_id, test))
            if test_id:  # Unsuported test type may not be imported (rpmverifyfile etc.)
                dependencies_to_import.append((criteria_id, None, test_id, None))
            if module_test_id:
                dependencies_to_import.append((criteria_id, None, None, module_test_id))

        for child_criteria in criteria["criteria"]:
            child_criteria_id = self._populate_definition_criteria(cur, file_id, child_criteria)  # Recursion
            dependencies_to_import.append((criteria_id, child_criteria_id, None, None))
        # Import dependencies
        if dependencies_to_import:
            execute_values(cur, """insert into oval_criteria_dependency
                                   (parent_criteria_id, dep_criteria_id, dep_test_id, dep_module_test_id)
                                   values %s""", dependencies_to_import, page_size=len(dependencies_to_import))
        return criteria_id

    def _definition_import_check(self, file_id, item):
        """Check if definition is in DB, return None if it's up to date and row to import otherwise."""
        if item["version"] <= self.oval_definition_version_map.get((file_id, item["id"]), -1):
            return None
        definition_type = self.oval_definition_type_map.get(item["type"])
        if not definition_type:
            self.logger.warning("OVAL definition type not found: %s", item["type"])
            return None
        criteria_id = None
        if item["criteria"]:
            try:
                cur = self.conn.cursor()
                criteria_id = self._populate_definition_criteria(cur, file_id, item["criteria"])
                self.conn.commit()
            except Exception: # pylint: disable=broad-except
                self.logger.exception("Failure while inserting criteria: ")
                self.conn.rollback()
        return file_id, item["id"], definition_type, criteria_id, item["version"]

    def _definition_refresh_maps(self, cur):
        """Add imported data to caches."""
        for definition_id, file_id, oval_id, version in cur.fetchall():
            self.oval_definition_map[(file_id, oval_id)] = definition_id
            self.oval_definition_version_map[(file_id, oval_id)] = version

    def _populate_definitions(self, oval_file_id, definitions):
        query = """insert into oval_definition
                   (file_id, oval_id, definition_type_id, criteria_id, version) values %s
                   on conflict (file_id, oval_id) do update set
                   definition_type_id = EXCLUDED.definition_type_id, criteria_id = EXCLUDED.criteria_id,
                   version = EXCLUDED.version
                   returning id, file_id, oval_id, version"""
        self._populate_data("definitions", oval_file_id, definitions, self._definition_import_check, query,
                            self._definition_refresh_maps)
        for definition in definitions:
            if (oval_file_id, definition["id"]) in self.oval_definition_map:  # Make sure definition is imported
                cves = [{"id": cve} for cve in definition["cves"]]
                advisories = [{"id": advisory} for advisory in definition["advisories"]]
                cpes = [{"id": cpe} for cpe in definition["cpes"]]
                # Store missing CPEs (they are often substrings of CPEs already in DB)
                self.cpe_store.populate_cpes({cpe: None for cpe in definition["cpes"]
                                              if cpe not in self.cpe_store.cpe_label_to_id})
                tests = []
                criteria = definition["criteria"]
                criteria_stack = []
                while criteria is not None:
                    tests.extend(criteria["criterions"])
                    criteria_stack.extend(criteria["criteria"])
                    if criteria_stack:
                        criteria = criteria_stack.pop()
                    else:
                        criteria = None
                if not cves:
                    self.logger.warning("OVAL definition has empty CVE list: %s", definition["id"])
                if not advisories and definition["type"] != "vulnerability":
                    self.logger.warning("OVAL definition has empty errata list: %s", definition["id"])
                if not tests:
                    self.logger.warning("OVAL definition has empty test list: %s", definition["id"])
                tests = [{"id": test} for test in list(set(tests))]  # Make unique
                definition_id = self.oval_definition_map[(oval_file_id, definition["id"])]
                self._populate_associations("definition", "cves", "definition_id", "cve_id",
                                            "oval_definition_cve", definition_id, cves, self.cve_map)
                self._populate_associations("definition", "advisories", "definition_id", "errata_id",
                                            "oval_definition_errata", definition_id, advisories, self.errata_map)
                self._populate_associations("definition", "cpes", "definition_id", "cpe_id",
                                            "oval_definition_cpe", definition_id, cpes, self.cpe_store.cpe_label_to_id)
                self._populate_associations("definition", "tests", "definition_id", "rpminfo_test_id",
                                            "oval_definition_test", definition_id, tests, self.oval_test_map,
                                            file_id=oval_file_id,
                                            missing_ok=True)  # Don't log unsupported test types (rpmverifyfile etc.)

    def store(self, oval_file):
        """Store single OVAL definitions file into DB."""
        oval_file_id = self._save_oval_file_updated(oval_file.oval_id, oval_file.updated)
        self._populate_objects(oval_file_id, oval_file.objects)
        self._populate_states(oval_file_id, oval_file.states)
        self._populate_tests(oval_file_id, oval_file.tests)
        self._populate_module_tests(oval_file_id, oval_file.module_tests)
        self._populate_definitions(oval_file_id, oval_file.definitions)
