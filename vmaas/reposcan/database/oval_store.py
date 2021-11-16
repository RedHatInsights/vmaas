"""
Module containing classes for fetching/importing OVAL data from/into database.
"""
from psycopg2.extras import execute_values

from vmaas.common.date_utils import format_datetime
from vmaas.common.rpm_utils import parse_rpm_name
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
        self.oval_file_map = self._prepare_table_map(cols=["oval_id"], to_cols=["id", "updated"], table="oval_file")
        self.oval_check_map = self._prepare_table_map(cols=["name"], table="oval_check_rpminfo")
        self.oval_check_existence_map = self._prepare_table_map(cols=["name"], table="oval_check_existence_rpminfo")
        self.oval_object_map = self._prepare_table_map(cols=["file_id", "oval_id"],
                                                       to_cols=["id", "package_name_id", "version"],
                                                       table="oval_rpminfo_object")
        self.oval_state_map = self._prepare_table_map(cols=["file_id", "oval_id"],
                                                      to_cols=["id", "evr_id", "evr_operation_id", "version"],
                                                      table="oval_rpminfo_state")
        self.oval_test_map = self._prepare_table_map(cols=["file_id", "oval_id"],
                                                     to_cols=["id", "rpminfo_object_id", "check_id",
                                                              "check_existence_id", "version"],
                                                     table="oval_rpminfo_test")
        self.oval_module_test_map = self._prepare_table_map(cols=["file_id", "oval_id"],
                                                            to_cols=["id", "module_stream", "version"],
                                                            table="oval_module_test")
        self.oval_definition_map = self._prepare_table_map(cols=["file_id", "oval_id"],
                                                           to_cols=["id", "definition_type_id",
                                                                    "criteria_id", "version"],
                                                           table="oval_definition")
        self.oval_definition_type_map = self._prepare_table_map(cols=["name"], table="oval_definition_type")
        self.oval_criteria_operator_map = self._prepare_table_map(cols=["name"], table="oval_criteria_operator")

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

    def delete_oval_file(self, oval_id):
        """
        Deletes oval file from DB.
        """
        db_id = self.oval_file_map[oval_id][0]
        cur = self.conn.cursor()
        try:
            cur.execute("""delete from oval_criteria_dependency
                           where dep_test_id in (select id from oval_rpminfo_test where file_id = %s)""",
                        (db_id,))
            cur.execute("""delete from oval_criteria_dependency
                           where dep_module_test_id in (select id from oval_module_test where file_id = %s)""",
                        (db_id,))
            cur.execute("""delete from oval_rpminfo_test_state
                           where rpminfo_test_id in (select id from oval_rpminfo_test where file_id = %s)""",
                        (db_id,))
            cur.execute("""delete from oval_definition_test
                           where rpminfo_test_id in (select id from oval_rpminfo_test where file_id = %s)""",
                        (db_id,))
            cur.execute("""delete from oval_definition_cve
                           where definition_id in (select id from oval_definition where file_id = %s)""",
                        (db_id,))
            cur.execute("""delete from oval_definition_errata
                           where definition_id in (select id from oval_definition where file_id = %s)""",
                        (db_id,))
            cur.execute("""delete from oval_definition_cpe
                           where definition_id in (select id from oval_definition where file_id = %s)""",
                        (db_id,))
            cur.execute("""delete from oval_rpminfo_state_arch
                           where rpminfo_state_id in (select id from oval_rpminfo_state where file_id = %s)""",
                        (db_id,))
            cur.execute("delete from oval_definition where file_id = %s", (db_id,))
            cur.execute("delete from oval_rpminfo_test where file_id = %s", (db_id,))
            cur.execute("delete from oval_module_test where file_id = %s", (db_id,))
            cur.execute("delete from oval_rpminfo_state where file_id = %s", (db_id,))
            cur.execute("delete from oval_rpminfo_object where file_id = %s", (db_id,))
            cur.execute("delete from oval_file where id = %s", (db_id,))
            self.conn.commit()
        except Exception:  # pylint: disable=broad-except
            self.logger.exception("Failed to delete oval file.")
            self.conn.rollback()
        finally:
            cur.close()

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

    def _populate_data(self, entity, file_id, data, item_check_func, table_name, cols, refresh_maps_func,
                       items_to_delete_func):
        """Generic method to populate table with OVAL entity (objects, states, tests, etc.)."""
        to_insert = []
        to_update = []
        for item in data:
            to_insert_row, to_update_row = item_check_func(file_id, item)
            if to_insert_row:
                to_insert.append(to_insert_row)
            if to_update_row:
                to_update.append(to_update_row)
        to_delete = items_to_delete_func(file_id, {item["id"] for item in data})
        self.logger.debug("OVAL %s to insert: %d", entity, len(to_insert))
        self.logger.debug("OVAL %s to update: %d", entity, len(to_update))
        self.logger.debug("OVAL %s to delete: %d", entity, len(to_delete))
        try:
            cur = self.conn.cursor()
            if to_insert:
                execute_values(cur, f"""insert into {table_name} ({', '.join(cols)}) values %s
                                        returning id, {', '.join(cols)}""",
                               to_insert, page_size=len(to_insert))
                refresh_maps_func(cur)
            if to_update:
                execute_values(cur,
                               f"""update {table_name} set {', '.join([f'{col} = v.{col}' for col in cols])}
                                   from (values %s) as v(id, {', '.join(cols)})
                                   where {table_name}.id = v.id
                                   returning {table_name}.id, {', '.join([f'{table_name}.{col}' for col in cols])}
                                """,
                               to_update, page_size=len(to_update))
                refresh_maps_func(cur)
            if to_delete:
                cur.execute(f"""delete from {table_name} where file_id = %s and oval_id in %s
                                returning file_id, oval_id""",
                            (file_id, tuple(to_delete)))
                refresh_maps_func(cur, delete=True)
            self.conn.commit()
        except Exception: # pylint: disable=broad-except
            self.logger.exception("Failure while inserting, updating or deleting %s data: ", entity)
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
                if isinstance(item_id, tuple):
                    item_id = item_id[0]
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
        """Check if object is in DB to insert/update."""
        name_id = self.package_store.package_name_map.get(item["name"])
        if not name_id:
            self.logger.warning("Package name not found: %s", item["name"])
            return None, None
        to_insert_row = to_update_row = None
        current_version = self.oval_object_map.get((file_id, item["id"]))
        if current_version:
            # Data in DB are different
            if current_version[1:] != (name_id, item["version"]):
                to_update_row = (current_version[0], file_id, item["id"], name_id, item["version"])
        else:
            to_insert_row = (file_id, item["id"], name_id, item["version"])
        return to_insert_row, to_update_row

    def _object_refresh_maps(self, cur, delete=False):
        """Add imported data to caches."""
        if not delete:
            for obj_id, file_id, oval_id, name_id, version in cur.fetchall():
                self.oval_object_map[(file_id, oval_id)] = (obj_id, name_id, version)
        else:
            for file_id, oval_id in cur.fetchall():
                del self.oval_object_map[(file_id, oval_id)]

    def _objects_to_delete(self, file_id, latest_data):
        """Get list of oval_ids which are in DB but not in latest file."""
        return [oval_id for (f_id, oval_id) in self.oval_object_map
                if f_id == file_id and oval_id not in latest_data]

    def _populate_objects(self, oval_file_id, objects):
        # Populate missing package names
        self.package_store.populate_dep_table("package_name", {obj["name"] for obj in objects},
                                              self.package_store.package_name_map)
        # Insert/update data
        self._populate_data("objects", oval_file_id, objects, self._object_import_check, "oval_rpminfo_object",
                            ["file_id", "oval_id", "package_name_id", "version"], self._object_refresh_maps,
                            self._objects_to_delete)

    def _state_import_check(self, file_id, item):
        """Check if state is in DB to insert/update."""
        evr_id = evr_operation_id = None
        if item['evr'] is not None:
            epoch, version, release = item['evr']
            evr_id = self.package_store.evr_map.get((epoch, version, release))
            if not evr_id:
                self.logger.warning("EVR not found: %s, %s, %s", epoch, version, release)
                return None, None
        if item["evr_operation"] is not None:
            evr_operation_id = self.evr_operation_map.get(item["evr_operation"])
            if not evr_operation_id:
                self.logger.warning("Unsupported EVR operation: %s", item["evr_operation"])
                return None, None
        to_insert_row = to_update_row = None
        current_version = self.oval_state_map.get((file_id, item["id"]))
        if current_version:
            # Data in DB are different
            if current_version[1:] != (evr_id, evr_operation_id, item["version"]):
                to_update_row = (current_version[0], file_id, item["id"], evr_id, evr_operation_id, item["version"])
        else:
            to_insert_row = (file_id, item["id"], evr_id, evr_operation_id, item["version"])
        return to_insert_row, to_update_row

    def _state_refresh_maps(self, cur, delete=False):
        """Add imported data to caches."""
        if not delete:
            for state_id, file_id, oval_id, evr_id, evr_operation_id, version in cur.fetchall():
                self.oval_state_map[(file_id, oval_id)] = (state_id, evr_id, evr_operation_id, version)
        else:
            for file_id, oval_id in cur.fetchall():
                del self.oval_state_map[(file_id, oval_id)]

    def _states_to_delete(self, file_id, latest_data):
        """Get list of oval_ids which are in DB but not in latest file."""
        return [oval_id for (f_id, oval_id) in self.oval_state_map
                if f_id == file_id and oval_id not in latest_data]

    def _populate_states(self, oval_file_id, states):
        # Parse EVR first
        for state in states:
            if state['evr'] is not None:
                # FIXME: as an input to common.rpm.parse_rpm_name, we don't have function to parse evr only
                fake_nevra = f"pn-{state['evr']}.noarch"
                _, epoch, version, release, _ = parse_rpm_name(fake_nevra)
                state['evr'] = (epoch, version, release)
        # Populate missing EVRs
        self.package_store.populate_evrs({state['evr'] for state in states if state['evr'] is not None})
        # Insert/update data
        self._populate_data("states", oval_file_id, states, self._state_import_check, "oval_rpminfo_state",
                            ["file_id", "oval_id", "evr_id", "evr_operation_id", "version"], self._state_refresh_maps,
                            self._states_to_delete)
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
                                            self.oval_state_map[(oval_file_id, state["id"])][0],
                                            archs, self.package_store.arch_map)

    def _test_import_check(self, file_id, item):
        """Check if test is in DB to insert/update."""
        rpminfo_object_id = self.oval_object_map.get((file_id, item["object"]))
        if not rpminfo_object_id:
            self.logger.warning("OVAL object not found: %s", item["object"])
            return None, None
        rpminfo_object_id = rpminfo_object_id[0]
        check_id = self.oval_check_map.get(item["check"])
        if not check_id:
            self.logger.warning("OVAL check not found: %s", item["check"])
            return None, None
        check_existence_id = self.oval_check_existence_map.get(item["check_existence"])
        if not check_existence_id:
            self.logger.warning("OVAL check_existence not found: %s", item["check_existence"])
            return None, None
        to_insert_row = to_update_row = None
        current_version = self.oval_test_map.get((file_id, item["id"]))
        if current_version:
            # Data in DB are different
            if current_version[1:] != (rpminfo_object_id, check_id, check_existence_id, item["version"]):
                to_update_row = (current_version[0], file_id, item["id"], rpminfo_object_id, check_id,
                                 check_existence_id, item["version"])
        else:
            to_insert_row = (file_id, item["id"], rpminfo_object_id, check_id, check_existence_id, item["version"])
        return to_insert_row, to_update_row

    def _test_refresh_maps(self, cur, delete=False):
        """Add imported data to caches."""
        if not delete:
            for test_id, file_id, oval_id, rpminfo_object_id, check_id, check_existence_id, version in cur.fetchall():
                self.oval_test_map[(file_id, oval_id)] = (test_id, rpminfo_object_id, check_id,
                                                          check_existence_id, version)
        else:
            for file_id, oval_id in cur.fetchall():
                del self.oval_test_map[(file_id, oval_id)]

    def _tests_to_delete(self, file_id, latest_data):
        """Get list of oval_ids which are in DB but not in latest file."""
        return [oval_id for (f_id, oval_id) in self.oval_test_map
                if f_id == file_id and oval_id not in latest_data]

    def _populate_tests(self, oval_file_id, tests):
        # Insert/update data
        self._populate_data("tests", oval_file_id, tests, self._test_import_check, "oval_rpminfo_test",
                            ["file_id", "oval_id", "rpminfo_object_id", "check_id", "check_existence_id", "version"],
                            self._test_refresh_maps, self._tests_to_delete)
        for test in tests:
            if (oval_file_id, test["id"]) in self.oval_test_map:  # Make sure test is imported
                states = [{"id": state} for state in test["states"]]
                self._populate_associations("test", "states", "rpminfo_test_id", "rpminfo_state_id",
                                            "oval_rpminfo_test_state",
                                            self.oval_test_map[(oval_file_id, test["id"])][0],
                                            states, self.oval_state_map, file_id=oval_file_id)

    def _module_test_import_check(self, file_id, item):
        """Check if module test is in DB to insert/update."""
        to_insert_row = to_update_row = None
        current_version = self.oval_module_test_map.get((file_id, item["id"]))
        if current_version:
            # Data in DB are different
            if current_version[1:] != (item["module_stream"], item["version"]):
                to_update_row = (current_version[0], file_id, item["id"], item["module_stream"], item["version"])
        else:
            to_insert_row = (file_id, item["id"], item["module_stream"], item["version"])
        return to_insert_row, to_update_row

    def _module_test_refresh_maps(self, cur, delete=False):
        """Add imported data to caches."""
        if not delete:
            for test_id, file_id, oval_id, module_stream, version in cur.fetchall():
                self.oval_module_test_map[(file_id, oval_id)] = (test_id, module_stream, version)
        else:
            for file_id, oval_id in cur.fetchall():
                del self.oval_module_test_map[(file_id, oval_id)]

    def _module_tests_to_delete(self, file_id, latest_data):
        """Get list of oval_ids which are in DB but not in latest file."""
        return [oval_id for (f_id, oval_id) in self.oval_module_test_map
                if f_id == file_id and oval_id not in latest_data]

    def _populate_module_tests(self, oval_file_id, module_tests):
        # Insert/update data
        self._populate_data("module-tests", oval_file_id, module_tests, self._module_test_import_check,
                            "oval_module_test", ["file_id", "oval_id", "module_stream", "version"],
                            self._module_test_refresh_maps, self._module_tests_to_delete)

    def _populate_definition_criteria(self, cur, file_id, criteria, current_criteria_id):
        # pylint: disable=too-many-branches, too-many-statements
        operator_id = self.oval_criteria_operator_map.get(criteria["operator"])
        if not operator_id:
            self.logger.warning("OVAL criteria operator not found: %s", criteria["operator"])
            return None
        current_dep_criteria = []
        current_dep_tests = set()
        current_dep_module_tests = set()

        # Update type in current criteria row and fetch current dependencies
        # If current_criteria_id is None in args, just insert it
        if current_criteria_id:
            cur.execute("update oval_criteria set operator_id = %s where id = %s", (operator_id, current_criteria_id))
            cur.execute("""select dep_criteria_id, dep_test_id, dep_module_test_id
                           from oval_criteria_dependency
                           where parent_criteria_id = %s""", (current_criteria_id,))
            for dep_criteria_id, dep_test_id, dep_module_test_id in cur.fetchall():
                if dep_criteria_id:
                    current_dep_criteria.append(dep_criteria_id)
                if dep_test_id:
                    current_dep_tests.add(dep_test_id)
                if dep_module_test_id:
                    current_dep_module_tests.add(dep_module_test_id)
            criteria_id = current_criteria_id
        else:
            cur.execute("insert into oval_criteria (operator_id) values (%s) returning id", (operator_id,))
            criteria_id = cur.fetchone()[0]

        # Find out which test dependencies to insert and which to remove
        dependencies_to_import = []
        for test in criteria["criterions"]:
            test_id = self.oval_test_map.get((file_id, test))
            module_test_id = self.oval_module_test_map.get((file_id, test))
            if test_id:  # Unsuported test type may not be imported (rpmverifyfile etc.)
                test_id = test_id[0]
                if test_id not in current_dep_tests:
                    dependencies_to_import.append((criteria_id, None, test_id, None))
                else:
                    current_dep_tests.remove(test_id)
            if module_test_id:
                module_test_id = module_test_id[0]
                if module_test_id not in current_dep_module_tests:
                    dependencies_to_import.append((criteria_id, None, None, module_test_id))
                else:
                    current_dep_module_tests.remove(module_test_id)

        # Re-use dependent criteria ids when inserting/updating dependant criteria recursively
        current_dep_criteria = sorted(current_dep_criteria)
        for child_criteria in criteria["criteria"]:
            if current_dep_criteria:
                child_criteria_id = current_dep_criteria.pop(0)
                child_criteria_id = self._populate_definition_criteria(cur, file_id, child_criteria,
                                                                       child_criteria_id)  # Recursion
            else:
                child_criteria_id = None
                child_criteria_id = self._populate_definition_criteria(cur, file_id, child_criteria,
                                                                       child_criteria_id)  # Recursion
                dependencies_to_import.append((criteria_id, child_criteria_id, None, None))

        # Import dependencies
        if dependencies_to_import:
            execute_values(cur, """insert into oval_criteria_dependency
                                   (parent_criteria_id, dep_criteria_id, dep_test_id, dep_module_test_id)
                                   values %s""", dependencies_to_import, page_size=len(dependencies_to_import))

        # Remove no longer needed dependencies
        if current_dep_tests:
            cur.execute("""delete from oval_criteria_dependency
                           where parent_criteria_id = %s and dep_test_id in %s""",
                        (criteria_id, tuple(current_dep_tests)))
        if current_dep_module_tests:
            cur.execute("""delete from oval_criteria_dependency
                           where parent_criteria_id = %s and dep_module_test_id in %s""",
                        (criteria_id, tuple(current_dep_module_tests)))
        if current_dep_criteria:
            cur.execute("""delete from oval_criteria_dependency
                           where parent_criteria_id = %s and dep_criteria_id in %s""",
                        (criteria_id, tuple(current_dep_criteria)))

        return criteria_id

    def _definition_import_check(self, file_id, item):
        """Check if definition is in DB to insert/update."""
        definition_type = self.oval_definition_type_map.get(item["type"])
        if not definition_type:
            self.logger.warning("OVAL definition type not found: %s", item["type"])
            return None, None
        to_insert_row = to_update_row = None
        current_version = self.oval_definition_map.get((file_id, item["id"]))
        if current_version:
            criteria_id = current_version[2]
        else:
            criteria_id = None
        try:
            cur = self.conn.cursor()
            criteria_id = self._populate_definition_criteria(cur, file_id, item["criteria"], criteria_id)
            self.conn.commit()
        except Exception: # pylint: disable=broad-except
            self.logger.exception("Failure while inserting criteria: ")
            self.conn.rollback()
        if current_version:
            # Data in DB are different
            if current_version[1:] != (definition_type, criteria_id, item["version"]):
                to_update_row = (current_version[0], file_id, item["id"], definition_type,
                                 criteria_id, item["version"])
        else:
            to_insert_row = (file_id, item["id"], definition_type, criteria_id, item["version"])
        return to_insert_row, to_update_row

    def _definition_refresh_maps(self, cur, delete=False):
        """Add imported data to caches."""
        if not delete:
            for definition_id, file_id, oval_id, definition_type_id, criteria_id, version in cur.fetchall():
                self.oval_definition_map[(file_id, oval_id)] = (definition_id, definition_type_id,
                                                                criteria_id, version)
        else:
            for file_id, oval_id in cur.fetchall():
                del self.oval_definition_map[(file_id, oval_id)]

    def _definitions_to_delete(self, file_id, latest_data):
        """Get list of oval_ids which are in DB but not in latest file."""
        return [oval_id for (f_id, oval_id) in self.oval_definition_map
                if f_id == file_id and oval_id not in latest_data]

    def _populate_definitions(self, oval_file_id, definitions):
        # Insert/update data
        self._populate_data("definitions", oval_file_id, definitions, self._definition_import_check,
                            "oval_definition", ["file_id", "oval_id", "definition_type_id", "criteria_id", "version"],
                            self._definition_refresh_maps, self._definitions_to_delete)
        for definition in definitions:
            if (oval_file_id, definition["id"]) in self.oval_definition_map:  # Make sure definition is imported
                cves = [{"id": cve} for cve in definition["cves"]]
                advisories = [{"id": advisory} for advisory in definition["advisories"]]
                cpes = [{"id": cpe} for cpe in definition["cpes"]]
                tests = [{"id": test} for test in list(set(definition["tests"]))]  # Make unique
                # Store missing CPEs (they are often substrings of CPEs already in DB)
                self.cpe_store.populate_cpes({cpe: None for cpe in definition["cpes"]
                                              if cpe not in self.cpe_store.cpe_label_to_id})
                if not cves:
                    self.logger.warning("OVAL definition has empty CVE list: %s", definition["id"])
                if not advisories and definition["type"] != "vulnerability":
                    self.logger.warning("OVAL definition has empty errata list: %s", definition["id"])
                if not tests:
                    self.logger.warning("OVAL definition has empty test list: %s", definition["id"])

                definition_id = self.oval_definition_map[(oval_file_id, definition["id"])][0]
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
