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
        self.content_set_to_db_id = {}
        self.logger = SimpleLogger()
        self.conn = DatabaseHandler.get_connection()
        self.package_store = PackageStore()
        self.update_store = UpdateStore()

    def set_content_set_db_mapping(self, content_set_to_db_id):
        """Set content set to DB is mapping from product_store"""
        self.content_set_to_db_id = content_set_to_db_id

    def _get_content_set_id(self, repo):
        if repo.content_set in self.content_set_to_db_id:
            return self.content_set_to_db_id[repo.content_set]
        return None

    def list_repositories(self):
        """List repositories stored in DB. Dictionary with repository name as key is returned."""
        cur = self.conn.cursor()
        cur.execute("""select r.id, r.name, r.url, r.revision, cs.id, cs.label, c.name, c.ca_cert, c.cert, c.key
                       from repo r
                       left join certificate c on r.certificate_id = c.id
                       left join content_set cs on r.content_set_id = cs.id""")
        repos = {}
        for row in cur.fetchall():
            # repo_name -> repo_id, repo_url, repo_revision
            repos[row[1]] = {"id": row[0], "url": row[2], "revision": row[3], "content_set_id": row[4],
                             "content_set": row[5], "cert_name": row[6], "ca_cert": row[7], "cert": row[8],
                             "key": row[9]}
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
        content_set_id = self._get_content_set_id(repo)
        if not repo_id:
            cur.execute("""insert into repo (name, url, revision, eol, certificate_id, content_set_id)
                        values (%s, %s, to_timestamp(%s), false, %s, %s) returning id""",
                        (repo.repo_name, repo.repo_url, repo.repomd.get_revision(), cert_id, content_set_id,))
            repo_id = cur.fetchone()
        else:
            # Update repository timestamp
            cur.execute("""update repo set revision = to_timestamp(%s), certificate_id = %s, content_set_id = %s
                        where id = %s""", (repo.repomd.get_revision(), cert_id, content_set_id, repo_id[0],))
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
