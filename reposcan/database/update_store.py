"""
Module containing classes for fetching/importing updates from/into database.
"""
from psycopg2.extras import execute_values

from cli.logger import SimpleLogger
from database.database_handler import DatabaseHandler


class UpdateStore: # pylint: disable=too-few-public-methods
    """
    Class providing interface for storing updates and related info.
    All updates from repository are imported to the DB at once.
    """
    def __init__(self):
        self.logger = SimpleLogger()
        self.conn = DatabaseHandler.get_connection()

    def _get_nevras_in_repo(self, repo_id):
        cur = self.conn.cursor()
        # Select all packages synced from current repository and save them to dict accessible by NEVRA
        nevras_in_repo = {}
        cur.execute("""select p.id, p.name, evr.epoch, evr.version, evr.release, a.name
                               from package p inner join
                                    evr on p.evr_id = evr.id inner join
                                    arch a on p.arch_id = a.id inner join
                                    pkg_repo pr on p.id = pr.pkg_id and pr.repo_id = %s""", (repo_id,))
        for row in cur.fetchall():
            nevras_in_repo[(row[1], row[2], row[3], row[4], row[5])] = row[0]
        cur.close()
        return nevras_in_repo

    def _get_associations_todo(self, repo_id, updates, update_map, update_to_packages):
        nevras_in_repo = self._get_nevras_in_repo(repo_id)
        to_associate = []
        for update in updates:
            update_id = update_map[update["id"]]
            for pkg in update["pkglist"]:
                nevra = (pkg["name"], pkg["epoch"], pkg["ver"], pkg["rel"], pkg["arch"])
                if nevra not in nevras_in_repo:
                    self.logger.log("NEVRA associated with %s not found in repository: (%s)" %
                                    (update["id"], ",".join(nevra)))
                    continue
                package_id = nevras_in_repo[nevra]
                if update_id in update_to_packages and package_id in update_to_packages[update_id]:
                    # Already associated, remove from set
                    update_to_packages[update_id].remove(package_id)
                else:
                    # Not associated -> associate
                    to_associate.append((package_id, update_id))

        # Disassociate rest of package IDs
        to_disassociate = []
        for update_id in update_to_packages:
            for package_id in update_to_packages[update_id]:
                to_disassociate.append((package_id, update_id))

        return to_associate, to_disassociate

    def _populate_severities(self, updates):
        severities = {}
        cur = self.conn.cursor()
        cur.execute("select id, name from severity")
        for row in cur.fetchall():
            severities[row[1]] = row[0]
        missing_severities = set()
        for update in updates:
            if str(update["severity"]) not in severities:
                missing_severities.add((str(update["severity"]),))
        self.logger.log("Severities missing in DB: %d" % len(missing_severities))
        if missing_severities:
            execute_values(cur, "insert into severity (name) values %s returning id, name",
                           missing_severities, page_size=len(missing_severities))
            for row in cur.fetchall():
                severities[row[1]] = row[0]
        cur.close()
        self.conn.commit()
        return severities

    def _populate_updates(self, updates):
        severity_map = self._populate_severities(updates)
        cur = self.conn.cursor()
        update_map = {}
        names = set()
        for update in updates:
            names.add((update["id"],))
        if names:
            execute_values(cur,
                           """select id, name from errata
                              inner join (values %s) t(name)
                              using (name)
                           """, list(names), page_size=len(names))
            for row in cur.fetchall():
                update_map[row[1]] = row[0]
                # Remove to not insert this update
                names.remove((row[1],))
        self.logger.log("Updates already in DB: %d" % len(update_map))
        self.logger.log("Updates to import: %d" % len(names))
        if names:
            import_data = []
            for update in updates:
                if (update["id"],) in names:
                    import_data.append((update["id"], update["title"], severity_map[str(update["severity"])], update["description"],update["issued"], update["updated"], update["solution"]))
            execute_values(cur,
                           """insert into errata (name, synopsis, severity_id, description, issued, updated, solution) values %s
                              returning id, name""",
                           import_data, page_size=len(import_data))
            for row in cur.fetchall():
                update_map[row[1]] = row[0]
        cur.close()
        self.conn.commit()
        return update_map

    def _associate_packages(self, updates, update_map, repo_id):
        cur = self.conn.cursor()
        # Select packages already associated with updates, from current repository only
        # Save them to dict: errata_id -> set(package_id)
        update_to_packages = {}
        if update_map:
            cur.execute("""select e.id, pe.pkg_id
                           from errata e inner join
                                pkg_errata pe on e.id = pe.errata_id inner join
                                pkg_repo pr on pe.pkg_id = pr.pkg_id and pr.repo_id = %s
                           where e.id in %s""", (repo_id, tuple(update_map.values()),))
            for row in cur.fetchall():
                if row[0] not in update_to_packages:
                    update_to_packages[row[0]] = set()
                update_to_packages[row[0]].add(row[1])

        to_associate, to_disassociate = self._get_associations_todo(repo_id, updates, update_map, update_to_packages)

        self.logger.log("New update-package associations: %d" % len(to_associate))
        self.logger.log("Update-package disassociations: %d" % len(to_disassociate))

        if to_associate:
            execute_values(cur, "insert into pkg_errata (pkg_id, errata_id) values %s",
                           list(to_associate), page_size=len(to_associate))

        if to_disassociate:
            cur.execute("delete from pkg_errata where (pkg_id, errata_id) in %s", (tuple(to_disassociate),))

        cur.close()
        self.conn.commit()

    def _associate_updates(self, update_map, repo_id):
        cur = self.conn.cursor()
        associated_with_repo = set()
        cur.execute("select errata_id from errata_repo where repo_id = %s", (repo_id,))
        for row in cur.fetchall():
            associated_with_repo.add(row[0])
        self.logger.log("Updates associated with repository: %d" % len(associated_with_repo))
        to_associate = []
        for update_id in update_map.values():
            if update_id in associated_with_repo:
                associated_with_repo.remove(update_id)
            else:
                to_associate.append(update_id)
        self.logger.log("New updates to associate with repository: %d" % len(to_associate))
        self.logger.log("Updates to disassociate with repository: %d" % len(associated_with_repo))
        if to_associate:
            execute_values(cur, "insert into errata_repo (repo_id, errata_id) values %s",
                           [(repo_id, update_id) for update_id in to_associate], page_size=len(to_associate))
        # Are there updates to disassociate?
        if associated_with_repo:
            cur.execute("delete from errata_repo where repo_id = %s and errata_id in %s",
                        (repo_id, tuple(associated_with_repo),))
        cur.close()
        self.conn.commit()

    def _populate_cves(self, updates):
        cur = self.conn.cursor()
        cve_map = {}
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
        self.logger.log("CVEs already in DB: %d" % len(cve_map))
        self.logger.log("CVEs to import: %d" % len(names))
        if names:
            execute_values(cur,
                           """insert into cve (name) values %s
                              returning id, name""",
                           list(names), page_size=len(names))
            for row in cur.fetchall():
                cve_map[row[1]] = row[0]
        cur.close()
        self.conn.commit()
        return cve_map

    def _associate_cves(self, updates, update_map, cve_map):
        cur = self.conn.cursor()
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
            for cve in set([cve["id"] for cve in update["references"] if cve["type"] == "cve"]):
                cve_id = cve_map[cve]
                if update_id in update_to_cves and cve_id in update_to_cves[update_id]:
                    # Already associated, remove from set
                    update_to_cves[update_id].remove(cve_id)
                else:
                    # Not associated -> associate
                    to_associate.append((update_id, cve_id))

        # Disassociate rest of update IDs
        to_disassociate = []
        for update_id in update_to_cves:
            for cve_id in update_to_cves[update_id]:
                to_disassociate.append((update_id, cve_id))

        self.logger.log("New update-CVE associations: %d" % len(to_associate))
        self.logger.log("Update-CVE disassociations: %d" % len(to_disassociate))

        if to_associate:
            execute_values(cur, "insert into errata_cve (errata_id, cve_id) values %s",
                           to_associate, page_size=len(to_associate))

        if to_disassociate:
            cur.execute("delete from errata_cve where (errata_id, cve_id) in %s", (tuple(to_disassociate),))

        cur.close()
        self.conn.commit()

    def store(self, repo_id, updates):
        """
        Import all updates from repository into all related DB tables.
        """
        self.logger.log("Syncing %d updates." % len(updates))
        update_map = self._populate_updates(updates)
        self._associate_packages(updates, update_map, repo_id)
        self._associate_updates(update_map, repo_id)
        cve_map = self._populate_cves(updates)
        self._associate_cves(updates, update_map, cve_map)
        self.logger.log("Syncing updates finished.")
