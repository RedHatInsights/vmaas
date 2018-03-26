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
        """List repositories stored in DB. Dictionary with repository label as key is returned."""
        cur = self.conn.cursor()
        cur.execute("""select cs.label, a.name, r.releasever, r.id, r.url, r.revision, cs.id,
                              c.name, c.ca_cert, c.cert, c.key
                       from repo r
                       left join arch a on r.basearch_id = a.id
                       left join certificate c on r.certificate_id = c.id
                       left join content_set cs on r.content_set_id = cs.id""")
        repos = {}
        for row in cur.fetchall():
            # (content_set_label, repo_arch, repo_releasever) -> repo_id, repo_url, repo_revision...
            repos[(row[0], row[1], row[2])] = {"id": row[3], "url": row[4], "revision": row[5],
                                               "content_set_id": row[6], "cert_name": row[7], "ca_cert": row[8],
                                               "cert": row[9], "key": row[10]}
        cur.close()
        return repos

    def _import_basearch(self, basearch):
        cur = self.conn.cursor()
        cur.execute("select id from arch where name = %s", (basearch,))
        arch_id = cur.fetchone()
        if not arch_id:
            cur.execute("insert into arch (name) values(%s) returning id", (basearch,))
            arch_id = cur.fetchone()
        cur.close()
        self.conn.commit()
        return arch_id[0]

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
        basearch_id = self._import_basearch(repo.basearch)
        content_set_id = self._get_content_set_id(repo)
        cur = self.conn.cursor()
        cur.execute("select id from repo where content_set_id = %s and basearch_id = %s and releasever = %s",
                    (content_set_id, basearch_id, repo.releasever))
        repo_id = cur.fetchone()
        if not repo_id:
            cur.execute("""insert into repo (url, content_set_id, basearch_id, releasever,
                                             revision, eol, certificate_id)
                        values (%s, %s, %s, %s, %s, false, %s) returning id""",
                        (repo.repo_url, content_set_id, basearch_id, repo.releasever,
                         repo.repomd.get_revision(), cert_id,))
            repo_id = cur.fetchone()
        else:
            # Update repository timestamp
            cur.execute("""update repo set revision = %s, certificate_id = %s, content_set_id = %s,
                                           basearch_id = %s, releasever = %s
                        where id = %s""", (repo.repomd.get_revision(), cert_id, content_set_id, basearch_id,
                                           repo.releasever, repo_id[0],))
        cur.close()
        self.conn.commit()
        return repo_id[0]

    def store(self, repository):
        """
        Store single repository into DB.
        First, basic repository info is processed, then all packages, then all updates.
        Some steps may be skipped if given data doesn't exist or are already synced.
        """
        self.logger.log("Syncing repository: %s" % ", ".join((repository.content_set, repository.basearch,
                                                              repository.releasever)))
        repo_id = self._import_repository(repository)
        self.package_store.store(repo_id, repository.list_packages())
        self.update_store.store(repo_id, repository.list_updates())
