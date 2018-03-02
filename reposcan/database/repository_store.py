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
        self.conn = DatabaseHandler.get_connection()
        self.package_store = PackageStore()
        self.update_store = UpdateStore()

    def list_repositories(self):
        """List repositories stored in DB. Dictionary with repository name as key is returned."""
        cur = self.conn.cursor()
        cur.execute("""select r.id, r.name, r.url, r.revision, c.name, c.ca_cert, c.cert, c.key from repo r
                    left join certificate c on r.certificate_id = c.id""")
        repos = {}
        for row in cur.fetchall():
            # repo_name -> repo_id, repo_url, repo_revision
            repos[row[1]] = {"id": row[0], "url": row[2], "revision": row[3],
                             "cert_name": row[4], "ca_cert": row[5], "cert": row[6], "key": row[7]}
        cur.close()
        return repos

    def _import_certificate(self, cert_name, ca_cert, cert, key):
        cur = self.conn.cursor()
        cur.execute("select id from certificate where name = %s", (cert_name,))
        cert_id = cur.fetchone()
        if not cert_id:
            cur.execute("""insert into certificate (name, ca_cert, cert, key)
                        values (%s, %s, %s, %s) returning id""", (cert_name, ca_cert, cert, key,))
            cert_id = cur.fetchone()
        else:
            cur.execute("update certificate set ca_cert = %s, cert = %s, key = %s where name = %s",
                        (ca_cert, cert, key, cert_name,))
        cur.close()
        self.conn.commit()
        return cert_id[0]

    def _import_repository(self, repo):
        if repo.ca_cert:
            cert_id = self._import_certificate(repo.cert_name, repo.ca_cert, repo.cert, repo.key)
        else:
            cert_id = None
        cur = self.conn.cursor()
        cur.execute("select id from repo where name = %s", (repo.repo_name,))
        repo_id = cur.fetchone()
        if not repo_id:
            # FIXME: add product logic
            cur.execute("""insert into repo (name, url, revision, eol, certificate_id)
                        values (%s, %s, to_timestamp(%s), false, %s) returning id""",
                        (repo.repo_name, repo.repo_url, repo.repomd.get_revision(), cert_id,))
            repo_id = cur.fetchone()
        else:
            # Update repository timestamp
            cur.execute("update repo set revision = to_timestamp(%s), certificate_id = %s where id = %s",
                        (repo.repomd.get_revision(), cert_id, repo_id[0],))
        cur.close()
        self.conn.commit()
        return repo_id[0]

    def store(self, repository):
        """
        Store single repository into DB.
        First, basic repository info is processed, then all packages, then all updates.
        Some steps may be skipped if given data doesn't exist or are already synced.
        """
        self.logger.log("Syncing repository: %s" % repository.repo_name)
        repo_id = self._import_repository(repository)
        self.package_store.store(repo_id, repository.list_packages())
        self.update_store.store(repo_id, repository.list_updates())
