"""
Module containing classes for fetching/importing updates from/into database.
"""
from psycopg2.extras import execute_values

from vmaas.reposcan.database.object_store import ObjectStore
from vmaas.reposcan.database.modules_store import ModulesStore


class UpdateStore(ObjectStore):
    """
    Class providing interface for storing updates and related info.
    All updates from repository are imported to the DB at once.
    """

    def _get_associations_todo(self, repo_id, updates, update_map, update_to_packages):
        nevras_in_repo = self._get_nevras_in_repo(repo_id)
        modules_in_repo = self._get_modules_in_repo(repo_id)
        module_ids_in_repo = set(modules_in_repo.values())
        to_associate = []
        for update in updates:
            update_id = update_map[update["id"]]
            for pkg in update["pkglist"]:
                nevra = (pkg["name"], pkg["epoch"], pkg["ver"], pkg["rel"], pkg["arch"])
                module = (pkg["module_name"], pkg["module_stream"], pkg["module_version"], pkg["module_context"],
                          pkg["module_arch"]) if "module_name" in pkg else None
                if nevra not in nevras_in_repo:
                    self.logger.debug("NEVRA associated with %s not found in repository: (%s)",
                                      update["id"], ",".join(nevra))
                    continue
                if module and module not in modules_in_repo:
                    # this errata introduced new module N:S:V:C, create a record for it in DB
                    module_dict = {'name': module[0], 'stream': module[1], 'version': module[2],
                                   'context': module[3], 'arch': module[4]}
                    new_module = ModulesStore().create_module(repo_id, module_dict)
                    if new_module and 'stream_id' in new_module:
                        modules_in_repo[module] = new_module['stream_id']
                package_id = nevras_in_repo[nevra]
                module_id = modules_in_repo[module] if module else None
                if update_id in update_to_packages and (package_id, module_id) in update_to_packages[update_id]:
                    # Already associated, remove from set
                    update_to_packages[update_id].remove((package_id, module_id))
                else:
                    # Not associated -> associate
                    to_associate.append((package_id, update_id, module_id))

        # Disassociate rest of package IDs
        to_disassociate = []
        for update_id in update_to_packages:
            for package_id, module_id in update_to_packages[update_id]:
                # Can safely remove only tuples with module IDs in current repo
                # otherwise we delete reference with other repo modules.
                # Unfortunately module table has repo_id column so we hit this problem
                if not module_id or module_id in module_ids_in_repo:
                    to_disassociate.append((package_id, update_id, module_id))

        return to_associate, to_disassociate

    def _populate_errata_severities(self):
        severities = {}
        cur = self.conn.cursor()
        cur.execute("select id, name from errata_severity")
        for row in cur.fetchall():
            severities[row[1]] = row[0]
        cur.close()
        self.conn.commit()
        return severities

    def _populate_errata_types(self, updates):
        errata_types = {}
        cur = self.conn.cursor()
        try:
            cur.execute("select id, name from errata_type")
            for row in cur.fetchall():
                errata_types[row[1]] = row[0]
            missing_errata_types = set()
            for update in updates:
                if str(update["type"]) not in errata_types:
                    missing_errata_types.add((str(update["type"]),))
            self.logger.debug("Errata_types missing in DB: %d", len(missing_errata_types))
            if missing_errata_types:
                execute_values(cur, "insert into errata_type (name) values %s returning id, name",
                               missing_errata_types, page_size=len(missing_errata_types))
                for row in cur.fetchall():
                    errata_types[row[1]] = row[0]
            self.conn.commit()
        except Exception:  # pylint: disable=broad-except
            self.logger.exception("Failure inserting into errata_type.")
            self.conn.rollback()
        finally:
            cur.close()
        return errata_types

    def _populate_updates(self, updates):
        errata_severity_map = self._populate_errata_severities()
        errata_type_map = self._populate_errata_types(updates)
        cur = self.conn.cursor()
        update_map = {}
        try:
            errata = []
            for update in updates:
                erratum = (
                    update["id"], update["title"],
                    errata_severity_map[update["severity"]] if update["severity"] in errata_severity_map else None,
                    errata_type_map[str(update["type"])],
                    update["summary"], update["description"],
                    update["issued"], update["updated"],
                    update["solution"], update["reboot"]
                )
                errata.append(erratum)
            execute_values(cur, """
                insert into errata (name, synopsis, severity_id,
                               errata_type_id, summary, description, issued, updated,
                               solution, requires_reboot) values %s
                               on conflict (name) do update set requires_reboot = excluded.requires_reboot
            """, errata)

            names = set()
            for update in updates:
                names.add(update["id"])

            cur.execute("""select id, name from errata where name in %s""", (tuple(names),))
            for row in cur.fetchall():
                if row[1] in names:
                    update_map[row[1]] = row[0]
            self.logger.debug("Updates loaded from DB: %d", len(update_map))
            self.conn.commit()
        except Exception:  # pylint: disable=broad-except
            self.logger.exception("Failure inserting into errata.")
            self.conn.rollback()
        finally:
            cur.close()
        return update_map

    def _associate_source_packages(self, update_map):
        """
        Process all missing source packages associations with errata.
        """
        cur = self.conn.cursor()
        try:
            to_associate = []
            to_disassociate = []
            if update_map:
                # Select src packages already associated with updates
                cur.execute("""select pkg_id, errata_id, module_stream_id
                               from pkg_errata pe inner join
                                    package p on p.id = pe.pkg_id
                               where p.source_package_id is null
                                 and pe.errata_id in %s""",
                            (tuple(update_map.values()),))
                already_associated = set(cur.fetchall())

                # Select srpm packages that should be associated
                cur.execute("""select distinct source_package_id, errata_id, pe.module_stream_id
                               from pkg_errata pe inner join
                                    package p on p.id = pe.pkg_id
                               where source_package_id is not null
                                 and pe.errata_id in %s""",
                            (tuple(update_map.values()),))
                for row in cur.fetchall():
                    if row not in already_associated:
                        to_associate.append(row)
                    else:
                        already_associated.remove(row)
                to_disassociate = list(already_associated)

            self.logger.debug("New update-src-package associations: %d", len(to_associate))
            self.logger.debug("Update-src-package disassociations: %d", len(to_disassociate))

            if to_associate:
                execute_values(cur, "insert into pkg_errata (pkg_id, errata_id, module_stream_id) values %s",
                               to_associate, page_size=len(to_associate))
            if to_disassociate:
                cur.execute("delete from pkg_errata where (pkg_id, errata_id, module_stream_id) in %s",
                            (tuple(to_disassociate),))
            self.conn.commit()
        except Exception:  # pylint: disable=broad-except
            self.logger.exception("Failure changing src package associations.")
            self.conn.rollback()
        finally:
            cur.close()

    def _associate_packages(self, updates, update_map, repo_id):
        cur = self.conn.cursor()
        try:
            # Select packages already associated with updates, from current repository only
            # Save them to dict: errata_id -> set(package_id)
            update_to_packages = {}
            if update_map:
                cur.execute("""select e.id, pe.pkg_id, pe.module_stream_id
                               from errata e inner join
                                    pkg_errata pe on e.id = pe.errata_id inner join
                                    pkg_repo pr on pe.pkg_id = pr.pkg_id and pr.repo_id = %s
                               where e.id in %s""", (repo_id, tuple(update_map.values()),))
                for row in cur.fetchall():
                    if row[0] not in update_to_packages:
                        update_to_packages[row[0]] = set()
                    update_to_packages[row[0]].add((row[1], row[2]))

            to_associate, to_disassociate = self._get_associations_todo(repo_id, updates, update_map,
                                                                        update_to_packages)

            self.logger.debug("New update-package associations: %d", len(to_associate))
            self.logger.debug("Update-package disassociations: %d", len(to_disassociate))

            if to_associate:
                execute_values(cur, "insert into pkg_errata (pkg_id, errata_id, module_stream_id) values %s",
                               list(to_associate), page_size=len(to_associate))
            if to_disassociate:
                cur.execute("delete from pkg_errata where (pkg_id, errata_id, module_stream_id) in %s",
                            (tuple(to_disassociate),))
            self.conn.commit()
        except Exception:  # pylint: disable=broad-except
            self.logger.exception("Failure changing package associations.")
            self.conn.rollback()
        finally:
            cur.close()

    def _associate_updates(self, update_map, repo_id):
        cur = self.conn.cursor()
        try:
            associated_with_repo = set()
            cur.execute("select errata_id from errata_repo where repo_id = %s", (repo_id,))
            for row in cur.fetchall():
                associated_with_repo.add(row[0])
            self.logger.debug("Updates associated with repository: %d", len(associated_with_repo))
            to_associate = []
            for update_id in update_map.values():
                if update_id in associated_with_repo:
                    associated_with_repo.remove(update_id)
                else:
                    to_associate.append(update_id)
            self.logger.debug("New updates to associate with repository: %d", len(to_associate))
            self.logger.debug("Updates to disassociate with repository: %d", len(associated_with_repo))
            if to_associate:
                execute_values(cur, "insert into errata_repo (repo_id, errata_id) values %s",
                               [(repo_id, update_id) for update_id in to_associate], page_size=len(to_associate))
            # Are there updates to disassociate?
            if associated_with_repo:
                cur.execute("delete from errata_repo where repo_id = %s and errata_id in %s",
                            (repo_id, tuple(associated_with_repo),))
            self.conn.commit()
        except Exception:  # pylint: disable=broad-except
            self.logger.exception("Failure updating errata_repo data.")
            self.conn.rollback()
        finally:
            cur.close()

    def _populate_cves(self, updates):
        cur = self.conn.cursor()
        cve_map = {}
        try:
            names = set()
            for update in updates:
                for reference in update["references"]:
                    if reference["type"] == "cve":
                        names.add((reference["id"],))
            if names:
                execute_values(cur,
                               """select id, name from cve
                                  inner join (values %s) t(name)
                                  using (name)
                               """, list(names), page_size=len(names))
                for row in cur.fetchall():
                    cve_map[row[1]] = row[0]
                    # Remove to not insert this CVE
                    names.remove((row[1],))
            self.logger.debug("CVEs already in DB: %d", len(cve_map))
            self.logger.debug("CVEs to import: %d", len(names))
            if names:
                execute_values(cur,
                               """insert into cve (name) values %s
                                  returning id, name""",
                               list(names), page_size=len(names))
                for row in cur.fetchall():
                    cve_map[row[1]] = row[0]
            self.conn.commit()
        except Exception:  # pylint: disable=broad-except
            self.logger.exception("Failure inserting into cve.")
            self.conn.rollback()
        finally:
            cur.close()
        return cve_map

    def _associate_cves(self, updates, update_map, cve_map):  # pylint: disable=too-many-branches
        cur = self.conn.cursor()
        try:
            update_to_cves = {}
            if update_map:
                cur.execute("select errata_id, cve_id from errata_cve where errata_id in %s",
                            (tuple(update_map.values()),))
                for row in cur.fetchall():
                    if row[0] not in update_to_cves:
                        update_to_cves[row[0]] = set()
                    update_to_cves[row[0]].add(row[1])

            to_associate = []
            for update in updates:
                update_id = update_map[update["id"]]
                for cve in {cve["id"] for cve in update["references"] if cve["type"] == "cve"}:
                    cve_id = cve_map[cve]
                    if update_id in update_to_cves and cve_id in update_to_cves[update_id]:
                        # Already associated, remove from set
                        update_to_cves[update_id].remove(cve_id)
                    else:
                        # Not associated -> associate
                        to_associate.append((update_id, cve_id))

            # Disassociate rest of update IDs
            to_disassociate = []
            for update_id, update_dict in update_to_cves.items():
                for cve_id in update_dict:
                    to_disassociate.append((update_id, cve_id))

            self.logger.debug("New update-CVE associations: %d", len(to_associate))
            self.logger.debug("Update-CVE disassociations: %d", len(to_disassociate))

            if to_associate:
                execute_values(cur, "insert into errata_cve (errata_id, cve_id) values %s",
                               to_associate, page_size=len(to_associate))

            if to_disassociate:
                cur.execute("delete from errata_cve where (errata_id, cve_id) in %s", (tuple(to_disassociate),))
            self.conn.commit()
        except Exception:  # pylint: disable=broad-except
            self.logger.exception("Failure updating errata_cve data.")
            self.conn.rollback()
        finally:
            cur.close()

    def _associate_refs(self, updates, update_map):  # pylint: disable=too-many-branches
        cur = self.conn.cursor()
        try:  # pylint: disable=too-many-nested-blocks
            refs_to_add = set()
            refs_to_remove = []
            existing_refs_count = 0
            for update in updates:
                for reference in update["references"]:
                    if reference["type"] == "bugzilla" or reference["type"] == "other":
                        if reference["id"]:  # many 'other' refs have no id
                            ref_name = reference["id"]
                            if reference["type"] == "other":
                                ref_name += "-%s" % update["id"]
                            refs_to_add.add((update_map[update["id"]], reference["type"], ref_name))
            if refs_to_add:
                cur.execute("select errata_id, type, name from errata_refs where errata_id in %s",
                            (tuple(update_map.values()),))
                for row in cur.fetchall():
                    if (row[0], row[1], row[2]) in refs_to_add:
                        refs_to_add.remove((row[0], row[1], row[2]))
                        existing_refs_count += 1
                    else:
                        refs_to_remove.append((row[0], row[1], row[2]))
            self.logger.debug("Refs already in DB: %d", existing_refs_count)
            self.logger.debug("Refs to import: %d", len(refs_to_add))
            self.logger.debug("Refs to disassociate: %d", len(refs_to_remove))
            if refs_to_add:
                execute_values(cur,
                               "insert into errata_refs (errata_id, type, name) values %s",
                               list(refs_to_add), page_size=len(refs_to_add))
            if refs_to_remove:
                cur.execute("delete from errata_refs where (errata_id, type, name) in %s",
                            (tuple(refs_to_remove),))
            self.conn.commit()
        except Exception:  # pylint: disable=broad-except
            self.logger.exception("Failure updating errata_refs data.")
            self.conn.rollback()
        finally:
            cur.close()

    def store(self, repo_id, updates):
        """
        Import all updates from repository into all related DB tables.
        """
        self.logger.debug("Syncing %d updates.", len(updates))
        if updates:
            update_map = self._populate_updates(updates)
            self._associate_packages(updates, update_map, repo_id)
            self._associate_source_packages(update_map)
            self._associate_updates(update_map, repo_id)
            cve_map = self._populate_cves(updates)
            self._associate_cves(updates, update_map, cve_map)
            self._associate_refs(updates, update_map)
        self.logger.debug("Syncing updates finished.")
