from psycopg2.extras import execute_values

from cli.logger import SimpleLogger
from database.database_handler import DatabaseHandler


class PackageStore:
    def __init__(self):
        self.logger = SimpleLogger()
        self.conn = DatabaseHandler.get_connection()

    def _populate_archs(self, packages):
        archs = {}
        cur = self.conn.cursor()
        cur.execute("select id, name from arch")
        for row in cur.fetchall():
            archs[row[1]] = row[0]
        missing_archs = set()
        for pkg in packages:
            if pkg["arch"] not in archs:
                missing_archs.add((pkg["arch"],))
        self.logger.log("Architectures missing in DB: %d" % len(missing_archs))
        if missing_archs:
            execute_values(cur, "insert into arch (name) values %s returning id, name",
                           missing_archs, page_size=len(missing_archs))
            for row in cur.fetchall():
                archs[row[1]] = row[0]
        cur.close()
        self.conn.commit()
        return archs

    def _populate_checksum_types(self, packages):
        checksums = {}
        cur = self.conn.cursor()
        cur.execute("select id, name from checksum_type")
        for row in cur.fetchall():
            checksums[row[1]] = row[0]
        missing_checksum_types = set()
        for pkg in packages:
            if pkg["checksum_type"] not in checksums:
                missing_checksum_types.add((pkg["checksum_type"],))
        self.logger.log("Checksum types missing in DB: %d" % len(missing_checksum_types))
        if missing_checksum_types:
            execute_values(cur, "insert into checksum_type (name) values %s returning id, name",
                           missing_checksum_types, page_size=len(missing_checksum_types))
            for row in cur.fetchall():
                checksums[row[1]] = row[0]
        cur.close()
        self.conn.commit()
        return checksums

    def _populate_evrs(self, packages):
        cur = self.conn.cursor()
        evr_map = {}
        unique_evrs = set()
        for pkg in packages:
            unique_evrs.add((pkg["epoch"], pkg["ver"], pkg["rel"]))
        self.logger.log("Unique EVRs in repository: %d" % len(unique_evrs))
        execute_values(cur,
                       """select id, epoch, version, release from evr
                       inner join (values %s) t(epoch, version, release)
                       using (epoch, version, release)""",
                       list(unique_evrs), page_size=len(unique_evrs))
        for row in cur.fetchall():
            evr_map[(row[1], row[2], row[3])] = row[0]
            # Remove to not insert this evr
            unique_evrs.remove((row[1], row[2], row[3]))
        self.logger.log("EVRs already in DB: %d" % len(evr_map))

        to_import = []
        for (epoch, version, release) in unique_evrs:
            to_import.append((epoch, version, release, epoch, version, release))
        self.logger.log("EVRs to import: %d" % len(to_import))
        if to_import:
            execute_values(cur,
                           """insert into evr (epoch, version, release, evr) values %s
                           returning id, epoch, version, release""",
                           to_import, template=b"(%s, %s, %s, (%s, rpmver_array(%s), rpmver_array(%s)))",
                           page_size=len(to_import))
            for row in cur.fetchall():
                evr_map[(row[1], row[2], row[3])] = row[0]
        cur.close()
        self.conn.commit()
        return evr_map

    def _populate_packages(self, packages):
        archs = self._populate_archs(packages)
        checksum_types = self._populate_checksum_types(packages)
        evr_map = self._populate_evrs(packages)
        cur = self.conn.cursor()
        pkg_map = {}
        checksums = set()
        for pkg in packages:
            checksums.add((checksum_types[pkg["checksum_type"]], pkg["checksum"]))
        execute_values(cur,
                       """select id, checksum_type_id, checksum from package
                          inner join (values %s) t(checksum_type_id, checksum)
                          using (checksum_type_id, checksum)
                       """, list(checksums), page_size=len(checksums))
        for row in cur.fetchall():
            pkg_map[(row[1], row[2])] = row[0]
            # Remove to not insert this package
            checksums.remove((row[1], row[2]))
        self.logger.log("Packages already in DB: %d" % len(pkg_map))
        self.logger.log("Packages to import: %d" % len(checksums))
        if checksums:
            import_data = []
            for pkg in packages:
                if (checksum_types[pkg["checksum_type"]], pkg["checksum"]) in checksums:
                    import_data.append((pkg["name"], evr_map[(pkg["epoch"], pkg["ver"], pkg["rel"])],
                                        archs[pkg["arch"]], checksum_types[pkg["checksum_type"]], pkg["checksum"]))
            execute_values(cur,
                           """insert into package (name, evr_id, arch_id, checksum_type_id, checksum) values %s
                              returning id, checksum_type_id, checksum""",
                           import_data, page_size=len(import_data))
            for row in cur.fetchall():
                pkg_map[(row[1], row[2])] = row[0]
        cur.close()
        self.conn.commit()
        return pkg_map

    def _associate_packages(self, pkg_map, repo_id):
        cur = self.conn.cursor()
        associated_with_repo = set()
        cur.execute("select pkg_id from pkg_repo where repo_id = %s", (repo_id,))
        for row in cur.fetchall():
            associated_with_repo.add(row[0])
        self.logger.log("Packages associated with repository: %d" % len(associated_with_repo))
        to_associate = []
        for pkg_id in pkg_map.values():
            if pkg_id in associated_with_repo:
                associated_with_repo.remove(pkg_id)
            else:
                to_associate.append(pkg_id)
        self.logger.log("New packages to associate with repository: %d" % len(to_associate))
        self.logger.log("Packages to disassociate with repository: %d" % len(associated_with_repo))
        if to_associate:
            execute_values(cur, "insert into pkg_repo (repo_id, pkg_id) values %s",
                           [(repo_id, pkg_id) for pkg_id in to_associate], page_size=len(to_associate))
        # Are there packages to disassociate?
        if associated_with_repo:
            cur.execute("delete from pkg_repo where repo_id = %s and pkg_id in %s",
                        (repo_id, tuple(associated_with_repo),))
        cur.close()
        self.conn.commit()

    def store(self, repo_id, packages):
        self.logger.log("Syncing %d packages." % len(packages))
        package_map = self._populate_packages(packages)
        self._associate_packages(package_map, repo_id)
        self.logger.log("Syncing packages finished.")
