""""
Module containing classes for fetching/importing cve list metadata from/into database.
"""

from cli.logger import SimpleLogger
from database.database_handler import DatabaseHandler
from database.cve_store import CveStore


class CveRepoStore:
    """
    Interface to store cve list metadata (e.g lastmodified).
    """
    def __init__(self):
        self.logger = SimpleLogger()
        self.repo = []
        self.conn = DatabaseHandler.get_connection()
        self.cve_store = CveStore()

    def list_lastmodified(self):
        """
        Fetch map of lastmodified dates for cve lists we've downloaded in the past.
        """
        lastmodified = {}
        cur = self.conn.cursor()
        cur.execute("select key, value from metadata where key like 'nistcve:%'")
        for row in cur.fetchall():
            label = row[0][8:]        # strip nistcve: prefix
            lastmodified[label] = row[1]
        cur.close()
        return lastmodified

    def _import_repo(self, label, lastmodified):
        key = 'nistcve:' + label
        cur = self.conn.cursor()
        cur.execute("select id from metadata where key = %s", (key,))
        repo_id = cur.fetchone()
        if not repo_id:
            cur.execute("insert into metadata (key, value) values (%s, %s) returning id",
                        (key, lastmodified))
            repo_id = cur.fetchone()
        else:
            # Update repository timestamp
            cur.execute("update metadata set value = %s where id = %s", (lastmodified, repo_id[0],))
        cur.close()
        self.conn.commit()
        return repo_id[0]

    def store(self, repo):
        """
        Store list of CVEs in the database.
        """
        self.logger.log("Syncing CVE list: %s" % repo.label)
        self._import_repo(repo.label, repo.meta.get_lastmodified())
        self.logger.log("Syncing CVEs : %s" % repo.get_count())
        self.cve_store.store(repo)
