"""
Module containing shared code between various *Store classes
"""

from common.logging_utils import get_logger
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

    def _get_modules_in_repo(self, repo_id):
        cur = self.conn.cursor()
        modules_in_repo = {}
        cur.execute(""" select ms.id, m.name, ms.stream_name, ms.version, ms.context, a.name
                          from module m
                          join module_stream ms on m.id = ms.module_id
                          join arch a on m.arch_id = a.id
                         where m.repo_id = %s
                    """, (repo_id,))
        for row in cur.fetchall():
            modules_in_repo[(row[1], row[2], row[3], row[4], row[5])] = row[0]
        cur.close()
        return modules_in_repo

    def _prepare_table_map(self, cols, table):
        """Create map from table map[columns] -> id."""
        table_map = {}
        cur = self.conn.cursor()
        if len(cols) == 1:
            sql = "select id, %s from %s" % (cols[0], table)
            cur.execute(sql)
            for row in cur.fetchall():
                table_map[row[1]] = row[0]  # column value is a key
        else:
            sql = "select id, %s from %s" % (",".join(cols), table)
            cur.execute(sql)
            for row in cur.fetchall():
                table_map[tuple(row[1:])] = row[0]  # tuple of columns values is a key
        self.conn.commit()
        return table_map
