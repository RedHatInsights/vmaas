"""
Module containing shared code between various *Store classes
"""

from common.logging import get_logger
from database.database_handler import DatabaseHandler

class ObjectStore:
    """Shared code between various *Store classes"""

    def __init__(self):
        self.logger = get_logger(__name__)
        self.conn = DatabaseHandler.get_connection()

    def _get_nevras_in_repo(self, repo_id):
        cur = self.conn.cursor()
        # Select all packages synced from current repository and save them to dict accessible by NEVRA
        nevras_in_repo = {}
        cur.execute("""select p.id, pn.name, evr.epoch, evr.version, evr.release, a.name
                               from package p inner join
                                    package_name pn on p.name_id = pn.id inner join
                                    evr on p.evr_id = evr.id inner join
                                    arch a on p.arch_id = a.id inner join
                                    pkg_repo pr on p.id = pr.pkg_id and pr.repo_id = %s""", (repo_id,))
        for row in cur.fetchall():
            nevras_in_repo[(row[1], row[2], row[3], row[4], row[5])] = row[0]
        cur.close()
        return nevras_in_repo

    def _prepare_arch_map(self):
        arch_map = {}
        cur = self.conn.cursor()
        cur.execute("select id, name from arch")
        for arch_id, name in cur.fetchall():
            arch_map[name] = arch_id
        self.conn.commit()
        return arch_map

    def _prepare_package_name_map(self):
        package_name_map = {}
        cur = self.conn.cursor()
        cur.execute("SELECT id, name from package_name")
        for name_id, name in cur.fetchall():
            package_name_map[name] = name_id
        self.conn.commit()
        return package_name_map
