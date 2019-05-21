"""
Module containing classes for fetching/importing packages from/into database.
"""
from psycopg2.extras import execute_values

from database.object_store import ObjectStore

CHECKSUM_TYPE_ALIASES = {"sha": "sha1"}


class PackageStore(ObjectStore):
    """
    Class providing interface for storing packages and related info.
    All packages from repository are imported to the DB at once.
    """
    def __init__(self):
        super().__init__()
        self.arch_map = self._prepare_table_map(cols=["name"], table="arch")
        self.checksum_type_map = self._prepare_table_map(cols=["name"], table="checksum_type")
        self.evr_map = self._prepare_table_map(cols=["epoch", "version", "release"], table="evr")
        self.package_name_map = self._prepare_table_map(cols=["name"], table="package_name")
        self.package_map = self._prepare_table_map(cols=["checksum_type_id", "checksum"], table="package")

    def _populate_archs(self, unique_archs):
        cur = self.conn.cursor()
        self.logger.debug("Unique architectures in repository: %d", len(unique_archs))
        to_import = []
        for name in unique_archs:
            if name not in self.arch_map:
                to_import.append((name,))

        self.logger.debug("Architectures to import: %d", len(to_import))
        if to_import:
            execute_values(cur, "insert into arch (name) values %s returning id, name",
                           to_import, page_size=len(to_import))
            for arch_id, name in cur.fetchall():
                self.arch_map[name] = arch_id
        cur.close()
        self.conn.commit()

    def _populate_checksum_types(self, unique_checksum_types):
        cur = self.conn.cursor()
        self.logger.debug("Unique checksum types in repository: %d", len(unique_checksum_types))
        to_import = []
        for name in unique_checksum_types:
            if name not in self.checksum_type_map:
                to_import.append((name,))

        self.logger.debug("Checksum types to import: %d", len(to_import))
        if to_import:
            execute_values(cur, "insert into checksum_type (name) values %s returning id, name",
                           to_import, page_size=len(to_import))
            for ct_id, name in cur.fetchall():
                self.checksum_type_map[name] = ct_id
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

    def _populate_package_names(self, unique_names):
        cur = self.conn.cursor()
        self.logger.debug("Unique package names in repository: %d", len(unique_names))
        to_import = []
        self.package_name_map = self._prepare_table_map(["name"], "package_name")
        for name in unique_names:
            if name not in self.package_name_map:
                to_import.append((name,))

        self.logger.debug("Package names to import: %d", len(to_import))
        if to_import:
            execute_values(cur,
                           """insert into package_name (name) values %s returning id, name""",
                           to_import, page_size=len(to_import))
            for name_id, name in cur.fetchall():
                self.package_name_map[name] = name_id
        cur.close()
        self.conn.commit()

    def _populate_dependent_tables(self, packages):
        unique_archs = set()
        unique_checksum_types = set()
        unique_evrs = set()
        unique_names = set()
        for pkg in packages:
            unique_archs.add(pkg["arch"])
            if pkg["checksum_type"] in CHECKSUM_TYPE_ALIASES:
                pkg["checksum_type"] = CHECKSUM_TYPE_ALIASES[pkg["checksum_type"]]
            unique_checksum_types.add(pkg["checksum_type"])
            unique_evrs.add((pkg["epoch"], pkg["ver"], pkg["rel"]))
            unique_names.add(pkg["name"])
        self._populate_archs(unique_archs)
        self._populate_checksum_types(unique_checksum_types)
        self._populate_evrs(unique_evrs)
        self._populate_package_names(unique_names)

    def _populate_packages(self, packages):
        self._populate_dependent_tables(packages)
        cur = self.conn.cursor()
        unique_packages = {}
        for pkg in packages:
            unique_packages[(self.checksum_type_map[pkg["checksum_type"]], pkg["checksum"])] = \
                (self.package_name_map[pkg["name"]], self.evr_map[(pkg["epoch"], pkg["ver"], pkg["rel"])],
                 self.arch_map[pkg["arch"]], self.checksum_type_map[pkg["checksum_type"]],
                 pkg["checksum"], pkg["summary"], pkg["description"])
        package_ids = []
        to_import = []
        for checksum_type_id, checksum in unique_packages:
            if (checksum_type_id, checksum) not in self.package_map:
                to_import.append(unique_packages[(checksum_type_id, checksum)])
            else:
                package_ids.append(self.package_map[(checksum_type_id, checksum)])

        self.logger.debug("Packages to import: %d", len(to_import))
        if to_import:
            execute_values(cur,
                           """insert into package
                              (name_id, evr_id, arch_id, checksum_type_id, checksum, summary, description)
                              values %s
                              returning id, checksum_type_id, checksum""",
                           to_import, page_size=len(to_import))
            for pkg_id, checksum_type_id, checksum in cur.fetchall():
                self.package_map[(checksum_type_id, checksum)] = pkg_id
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
