"""
Module containing classes for fetching/importing repositories from/into database.
"""
from vmaas.common.logging_utils import get_logger
from vmaas.reposcan.database.database_handler import DatabaseHandler
from vmaas.reposcan.database.modules_store import ModulesStore
from vmaas.reposcan.database.package_store import PackageStore
from vmaas.reposcan.database.update_store import UpdateStore


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
        self.organization_to_db_id = {}

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
                              c.name, c.ca_cert, c.cert, c.key, o.name
                       from repo r
                       join organization o on r.org_id = o.id
                       left join arch a on r.basearch_id = a.id
                       left join certificate c on r.certificate_id = c.id
                       left join content_set cs on r.content_set_id = cs.id""")
        repos = {}
        for row in cur.fetchall():
            # (content_set_label, repo_arch, repo_releasever) -> repo_id, repo_url, repo_revision...
            repos[(row[0], row[1], row[2], row[11])] = {"id": row[3], "url": row[4], "revision": row[5],
                                                        "content_set_id": row[6], "cert_name": row[7], "ca_cert": row[8],
                                                        "cert": row[9], "key": row[10]}
        cur.close()
        return repos

    def _import_basearch(self, basearch):
        cur = self.conn.cursor()
        try:
            cur.execute("select id from arch where name = %s", (basearch,))
            arch_id = cur.fetchone()
            if not arch_id:
                cur.execute("insert into arch (name) values(%s) returning id", (basearch,))
                arch_id = cur.fetchone()
            self.conn.commit()
        except Exception:
            self.logger.exception("Failed to import basearch.")
            self.conn.rollback()
            raise
        finally:
            cur.close()
        return arch_id[0]

    def _import_certificate(self, cert_name, ca_cert, cert, key):
        if not key:
            key = None
        cur = self.conn.cursor()
        try:
            cur.execute("select id, ca_cert, cert, key from certificate where name = %s", (cert_name,))
            cert_row = cur.fetchone()
            if not cert_row:
                cur.execute("""insert into certificate (name, ca_cert, cert, key)
                            values (%s, %s, %s, %s) returning id""", (cert_name, ca_cert, cert, key,))
                cert_row = cur.fetchone()
            elif cert_row[1] != ca_cert or cert_row[2] != cert or cert_row[3] != key:
                cur.execute("update certificate set ca_cert = %s, cert = %s, key = %s where name = %s",
                            (ca_cert, cert, key, cert_name,))
            self.conn.commit()
        except Exception:
            self.logger.exception("Failed to import certificate.")
            self.conn.rollback()
            raise
        finally:
            cur.close()
        return cert_row[0]

    def _import_organization(self, organization):
        cur = self.conn.cursor()
        try:
            cur.execute("select id from organization where name = %s", (organization,))
            org_id = cur.fetchone()
            if not org_id:
                cur.execute("""insert into organization (name)
                            values (%s) returning id""", (organization,))
                org_id = cur.fetchone()
            self.conn.commit()
        except Exception:
            self.logger.exception("Failed to import organization.")
            self.conn.rollback()
            raise
        finally:
            cur.close()
        return org_id[0]

    def cleanup_unused_data(self):
        """
        Deletes packages and errata not associated with any repo etc.
        """
        cur = self.conn.cursor()
        try:
            cur.execute("""select p.id from package p where not exists (
                             select 1 from pkg_repo pr where pr.pkg_id = p.id
                           ) and p.source_package_id is not null
                        """)
            packages_to_delete = cur.fetchall()

            cur.execute("""select e.id from errata e where not exists (
                             select 1 from errata_repo er where er.errata_id = e.id
                           )
                        """)
            updates_to_delete = cur.fetchall()

            if packages_to_delete:
                cur.execute("""delete from pkg_errata pe where pe.pkg_id in %s""", (tuple(packages_to_delete),))
                cur.execute("""delete from module_rpm_artifact mra where mra.pkg_id in %s""",
                            (tuple(packages_to_delete),))
                cur.execute("""delete from package p where p.id in %s""", (tuple(packages_to_delete),))

            if updates_to_delete:
                cur.execute("""delete from pkg_errata pe where pe.errata_id in %s""", (tuple(updates_to_delete),))
                cur.execute("""delete from errata_cve ec where ec.errata_id in %s""", (tuple(updates_to_delete),))
                cur.execute("""delete from errata_refs er where er.errata_id in %s""", (tuple(updates_to_delete),))
                cur.execute("""delete from errata e where e.id in %s""", (tuple(updates_to_delete),))
            self.conn.commit()
        except Exception:  # pylint: disable=broad-except
            self.logger.exception("Failed to clean up unused data.")
            self.conn.rollback()
        finally:
            cur.close()

    def delete_content_set(self, content_set_label,  # pylint: disable=too-many-positional-arguments
                           whole_content_set=False, basearch=None, releasever=None, organization=None):
        """
        Deletes repositories and their content from DB.
        """
        content_set_id = self.content_set_to_db_id[content_set_label]
        cur = self.conn.cursor()
        try:
            query = "select id from repo where content_set_id = %s"
            query_args = [content_set_id]
            cur.execute(query, tuple(query_args))
            all_cs_repo_ids = cur.fetchall()

            if basearch:
                query += " and basearch_id = (select id from arch where name = %s)"
                query_args.append(basearch)
            elif not whole_content_set:
                query += " and basearch_id is null"
            if releasever:
                query += " and releasever = %s"
                query_args.append(releasever)
            elif not whole_content_set:
                query += " and releasever is null"
            if organization and not whole_content_set:
                query += " and org_id = (select id from organization where name = %s)"
                query_args.append(organization)
            cur.execute(query, tuple(query_args))
            to_delete_repo_ids = cur.fetchall()

            for repo_id in to_delete_repo_ids:
                cur.execute("select id from module where repo_id = %s", (repo_id,))
                module_ids = cur.fetchall()
                if module_ids:
                    cur.execute("select id from module_stream where module_id in %s", (tuple(module_ids),))
                    module_stream_ids = cur.fetchall()
                    if module_stream_ids:
                        cur.execute("""delete from module_profile_pkg
                                        where profile_id in (select id from module_profile
                                                            where stream_id in %s)""", (tuple(module_stream_ids),))
                        cur.execute("delete from module_rpm_artifact where stream_id in %s",
                                    (tuple(module_stream_ids),))
                        cur.execute("delete from pkg_errata where module_stream_id in %s", (tuple(module_stream_ids),))
                        cur.execute("delete from module_profile where stream_id in %s", (tuple(module_stream_ids),))
                        cur.execute("delete from module_stream_require where module_stream_id in %s",
                                    (tuple(module_stream_ids),))
                    cur.execute("delete from module_stream where module_id in %s", (tuple(module_ids),))
                cur.execute("delete from module where repo_id = %s", (repo_id,))
                cur.execute("delete from pkg_repo where repo_id = %s", (repo_id,))
                cur.execute("delete from errata_repo where repo_id = %s", (repo_id,))
                cur.execute("delete from cpe_repo where repo_id = %s", (repo_id,))
                cur.execute("delete from repo where id = %s", (repo_id,))
            if len(all_cs_repo_ids) == len(to_delete_repo_ids):
                cur.execute("delete from cpe_content_set where content_set_id = %s", (content_set_id,))
                cur.execute("delete from content_set where id = %s", (content_set_id,))
            self.conn.commit()
        except Exception:  # pylint: disable=broad-except
            self.logger.exception("Failed to delete content set.")
            self.conn.rollback()
        finally:
            cur.close()

    def import_repository(self, repo):
        """
        Imports or updates repository record in DB.
        """
        org_id = self.organization_to_db_id.get(repo.organization)
        if not org_id:
            org_id = self._import_organization(repo.organization)
            self.organization_to_db_id[repo.organization] = org_id

        if repo.ca_cert:
            # will raise exception if db error occurs
            cert_id = self._import_certificate(repo.cert_name, repo.ca_cert, repo.cert, repo.key)
        else:
            cert_id = None

        if repo.basearch:
            # will raise exception if db error occurs
            basearch_id = self._import_basearch(repo.basearch)
        else:
            basearch_id = None

        cur = self.conn.cursor()
        try:
            content_set_id = self.content_set_to_db_id[repo.content_set]
            cur.execute("""select id, revision from repo where content_set_id = %s
                           and ((%s is null and basearch_id is null) or basearch_id = %s)
                           and ((%s is null and releasever is null) or releasever = %s)
                           and org_id = %s
                        """,
                        (content_set_id, basearch_id, basearch_id, repo.releasever, repo.releasever, org_id))
            db_repo = cur.fetchone()
            if not db_repo:
                cur.execute("""insert into repo (url, content_set_id, basearch_id, releasever,
                                                 org_id, revision, eol, certificate_id)
                            values (%s, %s, %s, %s, %s, %s, false, %s) returning id, revision""",
                            (repo.repo_url, content_set_id, basearch_id, repo.releasever, org_id,
                             repo.get_revision(), cert_id,))
                db_repo = cur.fetchone()
            else:
                revision = repo.get_revision()
                # if revision in repo object is None, re-use current revision from DB (don't update)
                # this method is called from 2 different places with 2 different states of repo object
                if not revision:
                    revision = db_repo[1]
                cur.execute("""update repo set revision = %s, url = %s, certificate_id = %s where id = %s""",
                            (revision, repo.repo_url, cert_id, db_repo[0],))
            self.conn.commit()
            return db_repo[0]
        except Exception:
            self.logger.exception("Failed to import or update repository.")
            self.conn.rollback()
            raise
        finally:
            cur.close()

    def store(self, repository):
        """
        Store single repository content into DB.
        First, basic repository info is processed, then all packages, then all updates.
        Some steps may be skipped if given data doesn't exist or are already synced.
        """
        try:
            repo_id = self.import_repository(repository)
            self.package_store.store(repo_id, repository.list_packages())
            self.module_store.store(repo_id, repository.list_modules())
            self.update_store.store(repo_id, repository.list_updates())
        except Exception:  # pylint: disable=broad-except
            # exception already logged.
            pass
