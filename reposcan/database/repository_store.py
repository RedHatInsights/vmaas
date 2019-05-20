"""
Module containing classes for fetching/importing repositories from/into database.
"""
from common.logging import get_logger
from database.database_handler import DatabaseHandler
from database.modules_store import ModulesStore
from database.package_store import PackageStore
from database.update_store import UpdateStore


class RepositoryStore:
    """
    Class providing interface for listing repositories stored in DB and storing repositories one by one.
    """
    def __init__(self):
        self.logger = get_logger(__name__)
        self.conn = DatabaseHandler.get_connection()
        self.module_store = ModulesStore()
        self.package_store = PackageStore()
        self.update_store = UpdateStore()
        self.content_set_to_db_id = self._prepare_content_set_map()

    def _prepare_content_set_map(self):
        cur = self.conn.cursor()
        cur.execute("""select id, label from content_set""")
        content_sets = {}
        for cs_id, cs_label in cur.fetchall():
            content_sets[cs_label] = cs_id
        cur.close()
        return content_sets

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
        if not key:
            key = None
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

    def cleanup_unused_data(self):
        """
        Deletes packages and errata not associated with any repo etc.
        """
        cur = self.conn.cursor()
        cur.execute("""select p.id from package p where not exists (
                         select 1 from pkg_repo pr where pr.pkg_id = p.id
                       )
                    """)
        packages_to_delete = [pkg_id for pkg_id in cur.fetchall()]

        cur.execute("""select e.id from errata e where not exists (
                         select 1 from errata_repo er where er.errata_id = e.id
                       )
                    """)
        updates_to_delete = [update_id for update_id in cur.fetchall()]

        if packages_to_delete:
            cur.execute("""delete from pkg_errata pe where pe.pkg_id in %s""", (tuple(packages_to_delete),))
            cur.execute("""delete from package p where p.id in %s""", (tuple(packages_to_delete),))

        if updates_to_delete:
            cur.execute("""delete from pkg_errata pe where pe.errata_id in %s""", (tuple(updates_to_delete),))
            cur.execute("""delete from errata_cve ec where ec.errata_id in %s""", (tuple(updates_to_delete),))
            cur.execute("""delete from errata_refs er where er.errata_id in %s""", (tuple(updates_to_delete),))
            cur.execute("""delete from errata e where e.id in %s""", (tuple(updates_to_delete),))

        cur.close()
        self.conn.commit()

    def delete_content_set(self, content_set_label):
        """
        Deletes repositories and their content from DB.
        """
        content_set_id = self.content_set_to_db_id[content_set_label]
        cur = self.conn.cursor()
        cur.execute("""select id from repo where content_set_id = %s""", (content_set_id,))
        repo_ids = [repo_id for repo_id in cur.fetchall()]
        for repo_id in repo_ids:
            cur.execute("delete from pkg_repo where repo_id = %s", (repo_id,))
            cur.execute("delete from errata_repo where repo_id = %s", (repo_id,))
            cur.execute("delete from repo where id = %s", (repo_id,))
        cur.execute("delete from content_set where id = %s", (content_set_id,))
        cur.close()
        self.conn.commit()

    def import_repository(self, repo):
        """
        Imports or updates repository record in DB.
        """
        if repo.ca_cert:
            cert_id = self._import_certificate(repo.cert_name, repo.ca_cert, repo.cert, repo.key)
        else:
            cert_id = None

        if repo.basearch:
            basearch_id = self._import_basearch(repo.basearch)
        else:
            basearch_id = None
        content_set_id = self.content_set_to_db_id[repo.content_set]
        cur = self.conn.cursor()
        cur.execute("""select id from repo where content_set_id = %s
                       and ((%s is null and basearch_id is null) or basearch_id = %s)
                       and ((%s is null and releasever is null) or releasever = %s)
                    """,
                    (content_set_id, basearch_id, basearch_id, repo.releasever, repo.releasever))
        repo_id = cur.fetchone()
        if not repo_id:
            cur.execute("""insert into repo (url, content_set_id, basearch_id, releasever,
                                             revision, eol, certificate_id)
                        values (%s, %s, %s, %s, %s, false, %s) returning id""",
                        (repo.repo_url, content_set_id, basearch_id, repo.releasever,
                         repo.get_revision(), cert_id,))
            repo_id = cur.fetchone()
        else:
            # Update repository timestamp
            cur.execute("""update repo set revision = %s, certificate_id = %s, content_set_id = %s,
                                           basearch_id = %s, releasever = %s
                        where id = %s""", (repo.get_revision(), cert_id, content_set_id, basearch_id,
                                           repo.releasever, repo_id[0],))
        cur.close()
        self.conn.commit()
        return repo_id[0]

    def store(self, repository):
        """
        Store single repository content into DB.
        First, basic repository info is processed, then all packages, then all updates.
        Some steps may be skipped if given data doesn't exist or are already synced.
        """
        self.logger.info("Syncing repository: %s", ", ".join(filter(None, (repository.content_set, repository.basearch,
                                                                           repository.releasever))))
        repo_id = self.import_repository(repository)
        self.package_store.store(repo_id, repository.list_packages())
        #  self.module_store.store(repo_id, repository.list_modules())
        self.update_store.store(repo_id, repository.list_updates())
