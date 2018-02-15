"""
Module containing classes for fetching/importing repositories from/into database.
"""
from cli.logger import SimpleLogger
from database.database_handler import DatabaseHandler
from database.package_store import PackageStore
from database.update_store import UpdateStore


class RepositoryStore:
    """
    Class providing interface for listing repositories stored in DB and storing repositories one by one.
    """
    def __init__(self):
        self.logger = SimpleLogger()
        self.repositories = []
        self.conn = DatabaseHandler.get_connection()
        self.package_store = PackageStore()
        self.update_store = UpdateStore()

    def list_repositories(self):
        """List repositories stored in DB. Dictionary with repository name as key is returned."""
        cur = self.conn.cursor()
        cur.execute("select id, name, url, revision from repo")
        repos = {}
        for row in cur.fetchall():
            # repo_name -> repo_id, repo_url, repo_revision
            repos[row[1]] = {"id": row[0], "url": row[2], "revision": row[3]}
        cur.close()
        return repos

    def _import_repository(self, repo_url, revision):
        cur = self.conn.cursor()
        cur.execute("select id from repo where name = %s", (repo_url,))
        repo_id = cur.fetchone()
        if not repo_id:
            # FIXME: add product logic
            cur.execute("""insert into repo (name, url, revision, eol)
                        values (%s, %s, to_timestamp(%s), false) returning id""",
                        (repo_url, repo_url, revision,))
            repo_id = cur.fetchone()
        else:
            # Update repository timestamp
            cur.execute("update repo set revision = to_timestamp(%s) where id = %s", (revision, repo_id[0],))
        cur.close()
        self.conn.commit()
        return repo_id[0]

    def store(self, repository):
        """
        Store single repository into DB.
        First, basic repository info is processed, then all packages, then all updates.
        Some steps may be skipped if given data doesn't exist or are already synced.
        """
        self.logger.log("Syncing repository: %s" % repository.repo_url)
        repo_id = self._import_repository(repository.repo_url, repository.repomd.get_revision())
        self.package_store.store(repo_id, repository.list_packages())
        self.update_store.store(repo_id, repository.list_updates())
