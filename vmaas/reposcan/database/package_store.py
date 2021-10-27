"""
Module containing classes for fetching/importing packages from/into database.
"""
from psycopg2.extras import execute_values

from vmaas.reposcan.database.object_store import ObjectStore
from vmaas.common import rpm_utils


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

    def populate_dep_table(self, table, unique_items, table_map):
        """Populate dependency table with column 'name'."""
        self.logger.debug("Unique %s's in repository: %d", table, len(unique_items))
        to_import = []
        for row in unique_items:
            if row not in table_map:
                to_import.append((row, ))

        self.logger.debug("%s's to import: %d", table, len(to_import))
        if to_import:
            cur = self.conn.cursor()
            try:
                sql = "insert into %s (name) values %%s returning id, name" % table
                execute_values(cur, sql, to_import, page_size=len(to_import))
                for row in cur.fetchall():
                    table_map[row[1]] = row[0]
                self.conn.commit()
            except Exception: # pylint: disable=broad-except
                self.logger.exception("Failure while inserting into %s", table)
                self.conn.rollback()
            finally:
                cur.close()

    def populate_evrs(self, unique_evrs):
        """Populate evr table."""
        self.logger.debug("Unique EVRs in repository: %d", len(unique_evrs))
        to_import = []
        for epoch, version, release in unique_evrs:
            if (epoch, version, release) not in self.evr_map:
                to_import.append((epoch, version, release, epoch,
                                  rpm_utils.rpmver2sqlarray(version), rpm_utils.rpmver2sqlarray(release)))

        self.logger.debug("EVRs to import: %d", len(to_import))
        if to_import:
            cur = self.conn.cursor()
            try:
                execute_values(cur,
                               """insert into evr (epoch, version, release, evr) values %s
                               returning id, epoch, version, release""",
                               to_import, template=b"(%s, %s, %s, (%s, %s, %s))",
                               page_size=len(to_import))
                for evr_id, evr_epoch, evr_ver, evr_rel in cur.fetchall():
                    self.evr_map[(evr_epoch, evr_ver, evr_rel)] = evr_id
                self.conn.commit()
            except Exception: # pylint: disable=broad-except
                self.logger.exception("Failure while inserting into evr table")
                self.conn.rollback()
            finally:
                cur.close()

    def _populate_dependent_tables(self, packages):
        unique_archs = set()
        unique_evrs = set()
        unique_names = set()
        for pkg in packages:
            unique_archs.add(pkg["arch"])
            unique_evrs.add((pkg["epoch"], pkg["ver"], pkg["rel"]))
            unique_names.add(pkg["name"])

        self.populate_dep_table("arch", unique_archs, self.arch_map)
        self.populate_dep_table("package_name", unique_names, self.package_name_map)
        self.populate_evrs(unique_evrs)

    def _get_source_package_id(self, pkg):
        source_package_id = None
        if pkg["srpm"]:
            name, epoch, ver, rel, arch = rpm_utils.parse_rpm_name(pkg["srpm"], default_epoch=pkg["epoch"],
                                                             raise_exception=True)
            name_id = self.package_name_map[name]
            evr_id = self.evr_map[(epoch, ver, rel)]
            arch_id = self.arch_map[arch]
            source_package_id = self.package_map[(name_id, evr_id, arch_id)]
        return source_package_id

    def _populate_packages(self, packages):
        unique_packages = {}
        for pkg in packages:
            name_id = self.package_name_map[pkg["name"]]
            evr_id = self.evr_map[(pkg["epoch"], pkg["ver"], pkg["rel"])]
            arch_id = self.arch_map[pkg["arch"]]
            source_package_id = self._get_source_package_id(pkg)
            unique_packages[(name_id, evr_id, arch_id)] = \
                (name_id, evr_id, arch_id, pkg["summary"], pkg["description"], source_package_id)
        package_ids = []
        to_import = []
        for name_id, evr_id, arch_id in unique_packages:
            if (name_id, evr_id, arch_id) not in self.package_map:
                to_import.append(unique_packages[(name_id, evr_id, arch_id)])
            else:
                package_ids.append(self.package_map[(name_id, evr_id, arch_id)])

        self.logger.debug("Packages to import: %d", len(to_import))
        if to_import:
            cur = self.conn.cursor()
            try:
                execute_values(cur,
                               """insert into package
                                  (name_id, evr_id, arch_id, summary, description, source_package_id)
                                  values %s
                                  returning id, name_id, evr_id, arch_id""",
                               to_import, page_size=len(to_import))
                for pkg_id, name_id, evr_id, arch_id in cur.fetchall():
                    self.package_map[(name_id, evr_id, arch_id)] = pkg_id
                    package_ids.append(pkg_id)
                self.conn.commit()
            except Exception: # pylint: disable=broad-except
                self.logger.exception("Failure while inserting into package table")
                self.conn.rollback()
            finally:
                cur.close()
        return package_ids

    def _associate_packages(self, package_ids, repo_id):
        cur = self.conn.cursor()
        try:
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
            self.conn.commit()
        except Exception: # pylint: disable=broad-except
            self.logger.exception("Failure while associating packages with repo_id %s", repo_id)
            self.conn.rollback()
        finally:
            cur.close()

    @staticmethod
    def _get_source_packages(packages):
        unique_source_packages = set()
        for pkg in packages:
            if pkg["srpm"]:
                unique_source_packages.add(rpm_utils.parse_rpm_name(pkg["srpm"], default_epoch=pkg["epoch"],
                                                              raise_exception=True))
        source_packages = []
        for name, epoch, ver, rel, arch in unique_source_packages:
            source_packages.append(dict(name=name, epoch=epoch, ver=ver, rel=rel, arch=arch,
                                        srpm=None, summary=None, description=None))
        return source_packages

    def store(self, repo_id, packages):
        """
        Import all packages from repository into all related DB tables.
        """
        source_packages = self._get_source_packages(packages)
        self.logger.debug("Syncing %d packages.", len(packages))
        if packages:
            self._populate_dependent_tables(source_packages + packages)
            self._populate_packages(source_packages)
            package_ids = self._populate_packages(packages)
            self._associate_packages(package_ids, repo_id)
        self.logger.debug("Syncing packages finished.")
