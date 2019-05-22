"""
Module containing classes for fetching/importing packages from/into database.
"""
from psycopg2.extras import execute_values

from database.object_store import ObjectStore


class PackageStore(ObjectStore):
    """
    Class providing interface for storing packages and related info.
    All packages from repository are imported to the DB at once.
    """
    def __init__(self):
        super().__init__()
        self.arch_map = self._prepare_table_map(cols=["name"], table="arch")
        self.evr_map = self._prepare_table_map(cols=["epoch", "version", "release"], table="evr")
        self.package_name_map = self._prepare_table_map(cols=["name"], table="package_name")
        self.package_map = self._prepare_table_map(cols=["name_id", "evr_id", "arch_id"], table="package")

    def _populate_dep_table(self, table, unique_items, table_map):
        """Populate dependency table with column 'name'."""
        cur = self.conn.cursor()
        self.logger.debug("Unique %s's in repository: %d", table, len(unique_items))
        to_import = []
        for row in unique_items:
            if row not in table_map:
                to_import.append((row, ))

        self.logger.debug("%s's to import: %d", table, len(to_import))
        if to_import:
            sql = "insert into %s (name) values %%s returning id, name" % table
            execute_values(cur, sql, to_import, page_size=len(to_import))
            for row in cur.fetchall():
                table_map[row[1]] = row[0]

        cur.close()
        self.conn.commit()

    def _populate_evrs(self, unique_evrs):
        cur = self.conn.cursor()
        self.logger.debug("Unique EVRs in repository: %d", len(unique_evrs))
        to_import = []
        for epoch, version, release in unique_evrs:
            if (epoch, version, release) not in self.evr_map:
                to_import.append((epoch, version, release, epoch, version, release))

        self.logger.debug("EVRs to import: %d", len(to_import))
        if to_import:
            execute_values(cur,
                           """insert into evr (epoch, version, release, evr) values %s
                           returning id, epoch, version, release""",
                           to_import, template=b"(%s, %s, %s, (%s, rpmver_array(%s), rpmver_array(%s)))",
                           page_size=len(to_import))
            for evr_id, evr_epoch, evr_ver, evr_rel in cur.fetchall():
                self.evr_map[(evr_epoch, evr_ver, evr_rel)] = evr_id
        cur.close()
        self.conn.commit()

    def _populate_dependent_tables(self, packages):
        unique_archs = set()
        unique_evrs = set()
        unique_names = set()
        for pkg in packages:
            unique_archs.add(pkg["arch"])
            unique_evrs.add((pkg["epoch"], pkg["ver"], pkg["rel"]))
            unique_names.add(pkg["name"])

        self._populate_dep_table("arch", unique_archs, self.arch_map)
        self._populate_dep_table("package_name", unique_names, self.package_name_map)
        self._populate_evrs(unique_evrs)

    def _populate_packages(self, packages):
        self._populate_dependent_tables(packages)
        cur = self.conn.cursor()
        unique_packages = {}
        for pkg in packages:
            name_id = self.package_name_map[pkg["name"]]
            evr_id = self.evr_map[(pkg["epoch"], pkg["ver"], pkg["rel"])]
            arch_id = self.arch_map[pkg["arch"]]
            unique_packages[(name_id, evr_id, arch_id)] = \
                (name_id, evr_id, arch_id, pkg["summary"], pkg["description"])
        package_ids = []
        to_import = []
        for name_id, evr_id, arch_id in unique_packages:
            if (name_id, evr_id, arch_id) not in self.package_map:
                to_import.append(unique_packages[(name_id, evr_id, arch_id)])
            else:
                package_ids.append(self.package_map[(name_id, evr_id, arch_id)])

        self.logger.debug("Packages to import: %d", len(to_import))
        if to_import:
            execute_values(cur,
                           """insert into package
                              (name_id, evr_id, arch_id, summary, description)
                              values %s
                              returning id, name_id, evr_id, arch_id""",
                           to_import, page_size=len(to_import))
            for pkg_id, name_id, evr_id, arch_id in cur.fetchall():
                self.package_map[(name_id, evr_id, arch_id)] = pkg_id
                package_ids.append(pkg_id)
        cur.close()
        self.conn.commit()
        return package_ids

    def _associate_packages(self, package_ids, repo_id):
        cur = self.conn.cursor()
        associated_with_repo = set()
        cur.execute("select pkg_id from pkg_repo where repo_id = %s", (repo_id,))
        for row in cur.fetchall():
            associated_with_repo.add(row[0])
        self.logger.debug("Packages associated with repository: %d", len(associated_with_repo))
        to_associate = []
        for pkg_id in package_ids:
            if pkg_id in associated_with_repo:
                associated_with_repo.remove(pkg_id)
            else:
                to_associate.append(pkg_id)
        self.logger.debug("New packages to associate with repository: %d", len(to_associate))
        self.logger.debug("Packages to disassociate with repository: %d", len(associated_with_repo))
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
        """
        Import all packages from repository into all related DB tables.
        """
        self.logger.info("Syncing %d packages.", len(packages))
        package_ids = self._populate_packages(packages)
        self._associate_packages(package_ids, repo_id)
        self.logger.info("Syncing packages finished.")
