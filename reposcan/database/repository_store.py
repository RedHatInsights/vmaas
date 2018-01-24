from cli.logger import SimpleLogger
from database.database_handler import DatabaseHandler
from database.package_store import PackageStore
from database.update_store import UpdateStore


class RepositoryStore:
    def __init__(self):
        self.logger = SimpleLogger()
        self.repositories = []
        self.conn = DatabaseHandler.get_connection()
        self.package_store = PackageStore()
        self.update_store = UpdateStore()

    def _import_repository(self, repo_url):
        cur = self.conn.cursor()
        cur.execute("select id from repo where name = %s", (repo_url,))
        repo_id = cur.fetchone()
        if not repo_id:
            # FIXME: add product logic
            cur.execute("insert into repo (name, eol) values (%s, false) returning id", (repo_url,))
            repo_id = cur.fetchone()
        cur.close()
        self.conn.commit()
        return repo_id[0]

    def store(self, repository):
        self.logger.log("Syncing repository: %s" % repository.repo_url)
        repo_id = self._import_repository(repository.repo_url)
        self.package_store.store(repo_id, repository.list_packages())
        self.update_store.store(repo_id, repository.list_updates())
