"""
Module containing shared code between various *Store classes
"""
import typing as t
from vmaas.common.logging_utils import get_logger
from vmaas.reposcan.database.database_handler import DatabaseHandler

PrepareTableMapType = dict[str, int] | dict[str, tuple[t.Any, ...]] | dict[tuple[str, ...], int] | dict[tuple[str, ...], tuple[t.Any, ...]]


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

    def _prepare_table_map(self, cols: t.Iterable[str], table: str, to_cols: t.Iterable[str] | None = None,
                           where: str | None = None) -> PrepareTableMapType:
        """Create map from table map[columns] -> or(column, tuple(columns))."""
        if not to_cols:
            to_cols = ["id"]
        cols_len = len(cols)
        to_cols_len = len(to_cols)
        table_map = {}
        cur = self.conn.cursor()
        sql = "select %s, %s from %s" % (", ".join(cols), ", ".join(to_cols), table)
        if where:
            sql = f"{sql} where {where}"
        cur.execute(sql)
        for row in cur.fetchall():
            if cols_len == 1:
                key = row[0]
            else:
                key = tuple(row[:cols_len])
            if to_cols_len == 1:
                value = row[-1]
            else:
                value = tuple(row[cols_len:])
            table_map[key] = value
        self.conn.commit()
        return table_map
