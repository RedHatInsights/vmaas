""""
Module containing classes for importing CPE metadata from/into database.
"""
from datetime import datetime, timezone
from psycopg2.extras import execute_values

from vmaas.reposcan.database.object_store import ObjectStore
from vmaas.reposcan.mnm import FAILED_IMPORT_CPE, FAILED_UPDATE_CPE
from vmaas.common.date_utils import format_datetime


class CpeStore(ObjectStore):
    """
    Interface to store CPE metadata.
    """

    CPE_DICT_UPDATED_KEY = 'redhatcpedict:updated'
    CPE_REPO_MAP_UPDATED_KEY = 'redhatcperepomap:updated'

    def __init__(self):
        super().__init__()
        self.arch_map = self._prepare_table_map(cols=["name"], table="arch")
        self.cpe_label_to_id = {}
        self.cpe_label_to_name = {}

        cur = self.conn.cursor()
        cur.execute("select id, label, name from cpe")
        for cpe_id, label, name in cur.fetchall():
            self.cpe_label_to_id[label] = cpe_id
            self.cpe_label_to_name[label] = name
        cur.close()

    def _save_lastmodified(self, lastmodified, key):
        lastmodified = format_datetime(lastmodified)
        cur = self.conn.cursor()
        # Update timestamp
        cur.execute("update metadata set value = %s where key = %s",
                    (lastmodified, key,))
        if cur.rowcount < 1:
            cur.execute("insert into metadata (key, value) values (%s, %s)",
                        (key, lastmodified))
        cur.close()
        self.conn.commit()

    def populate_cpes(self, cpes):  # pylint: disable=too-many-branches
        """
        Insert or update CPE items.
        """
        to_import = []
        to_update = []

        for label, name in cpes.items():
            if label not in self.cpe_label_to_name:
                to_import.append((label, name))
            elif self.cpe_label_to_name[label] != name and name is not None:
                to_update.append((label, name))

        self.logger.debug("CPEs in DB: %s", len(self.cpe_label_to_id))
        self.logger.debug("CPEs to import: %s", len(to_import))
        self.logger.debug("CPEs to update: %s", len(to_update))

        if to_import:
            cur = self.conn.cursor()
            try:
                execute_values(cur, """insert into cpe
                                    (label, name)
                                    values %s
                                    returning id, label, name""",
                               to_import, page_size=len(to_import))
                for cpe_id, label, name in cur.fetchall():
                    self.cpe_label_to_id[label] = cpe_id
                    self.cpe_label_to_name[label] = name
                self.conn.commit()
            except Exception:  # pylint: disable=broad-except
                self.logger.exception("Failure while inserting into cpe table: ")
                FAILED_IMPORT_CPE.inc()
                self.conn.rollback()
            finally:
                cur.close()

        if to_update:
            cur = self.conn.cursor()
            try:
                execute_values(cur, """update cpe set name = v.name
                                    from (values %s) as v(label, name)
                                    where cpe.label = v.label
                                    returning cpe.id, cpe.label, cpe.name""",
                               to_update, page_size=len(to_update))
                for cpe_id, label, name in cur.fetchall():
                    self.cpe_label_to_id[label] = cpe_id
                    self.cpe_label_to_name[label] = name
                self.conn.commit()
            except Exception:  # pylint: disable=broad-except
                self.logger.exception("Failure while updating cpe table: ")
                FAILED_UPDATE_CPE.inc()
                self.conn.rollback()
            finally:
                cur.close()

    def _populate_missing_mapping_cpes(self, repo_mapping):
        # Make sure all CPEs are in DB, even if they are not in CPE dict
        unknown_cpes = {}
        for content_set_label in repo_mapping["data"]:
            for cpe_label in repo_mapping["data"][content_set_label]["cpes"]:
                if cpe_label not in self.cpe_label_to_id:
                    unknown_cpes[cpe_label] = None
        self.populate_cpes(unknown_cpes)

    def _parse_mapping_file(self, repo_mapping):
        to_return = []
        for repo_label in repo_mapping["data"]:
            repo_label_parts = repo_label.split("__")
            content_set_label = repo_label_parts[0]
            basearch = None
            releasever = None
            if len(repo_label_parts) > 1:
                for part in repo_label_parts[1:]:
                    part = part.replace("_DOT_", ".")
                    if part in self.arch_map:
                        basearch = part
                    else:
                        releasever = part
            cpes = repo_mapping["data"][repo_label]["cpes"]
            to_return.append((content_set_label, basearch, releasever, cpes))
        return to_return

    def _populate_content_set_mapping(self, repo_list):  # pylint: disable=too-many-branches,too-many-statements
        cur = self.conn.cursor()
        cur.execute("select label, id from content_set")
        content_set_label_to_id = dict(cur.fetchall())

        current_associations = {}
        cur.execute("select cpe_id, content_set_id from cpe_content_set")
        for cpe_id, content_set_id in cur.fetchall():
            current_associations.setdefault(content_set_id, set()).add(cpe_id)
        cur.close()

        to_import = []
        to_delete = []
        unknown_cs_cnt = 0
        for content_set_label, basearch, releasever, cpes in repo_list:
            if basearch or releasever:  # Associate with repo and not content set
                continue

            cs_id = content_set_label_to_id.get(content_set_label)
            if cs_id is None:
                self.logger.debug("Unknown content set: %s", content_set_label)
                unknown_cs_cnt += 1
                continue

            # Find missing pairs to import and eliminate already existing
            for cpe_id in {self.cpe_label_to_id[cpe_label] for cpe_label in cpes}:
                if cpe_id in current_associations.get(cs_id, set()):
                    current_associations[cs_id].remove(cpe_id)
                else:
                    to_import.append((cpe_id, cs_id))

        # Delete all remaining pairs
        to_delete = [(cpe_id, cs_id) for cs_id, cpes in current_associations.items() for cpe_id in cpes]

        self.logger.debug("CPE-CS pairs to import: %s", len(to_import))
        self.logger.debug("CPE-CS pairs to delete: %s", len(to_delete))

        if unknown_cs_cnt:
            self.logger.warning("Unknown content sets in mapping file: %s", unknown_cs_cnt)

        if to_import:
            cur = self.conn.cursor()
            try:
                execute_values(cur, """insert into cpe_content_set
                                    (cpe_id, content_set_id)
                                    values %s""",
                               to_import, page_size=len(to_import))
                self.conn.commit()
            except Exception:  # pylint: disable=broad-except
                self.logger.exception("Failure while inserting into cpe_content_set table: ")
                FAILED_IMPORT_CPE.inc()
                self.conn.rollback()
            finally:
                cur.close()

        if to_delete:
            cur = self.conn.cursor()
            try:
                for cpe_id, content_set_id in to_delete:
                    # Slow but deleting should not happen often
                    cur.execute("delete from cpe_content_set where cpe_id = %s and content_set_id = %s",
                                (cpe_id, content_set_id,))
                self.conn.commit()
            except Exception:  # pylint: disable=broad-except
                self.logger.exception("Failure while deleting from cpe_content_set table: ")
                FAILED_UPDATE_CPE.inc()
                self.conn.rollback()
            finally:
                cur.close()

    def _populate_repo_mapping(self, repo_list):  # pylint: disable=too-many-branches,too-many-statements
        cur = self.conn.cursor()
        cur.execute("""select cs.label, a.name, r.releasever, r.id
                       from content_set cs join
                            repo r on r.content_set_id = cs.id join
                            arch a on r.basearch_id = a.id
                       order by cs.label, a.name, r.releasever, r.id
                    """)
        content_set_to_repos = {}
        for content_set_label, basearch, releasever, repo_id in cur.fetchall():
            content_set_to_repos.setdefault(content_set_label, []).append((basearch, releasever, repo_id))

        current_associations = {}
        cur.execute("select cpe_id, repo_id from cpe_repo")
        for cpe_id, repo_id in cur.fetchall():
            current_associations.setdefault(repo_id, set()).add(cpe_id)
        cur.close()

        to_import = []
        to_delete = []
        unknown_cs_cnt = 0
        for content_set_label, required_basearch, required_releasever, cpes in repo_list:
            if not required_basearch and not required_releasever:  # Associate with content_set and not repo
                continue

            repos = content_set_to_repos.get(content_set_label)
            if repos is None:
                self.logger.debug("Unknown content set: %s", content_set_label)
                unknown_cs_cnt += 1
                continue

            for basearch, releasever, repo_id in repos:
                if required_basearch and required_basearch != basearch:
                    continue
                if required_releasever and required_releasever != releasever:
                    continue

                # Find missing pairs to import and eliminate already existing
                for cpe_id in {self.cpe_label_to_id[cpe_label] for cpe_label in cpes}:
                    if cpe_id in current_associations.get(repo_id, set()):
                        current_associations[repo_id].remove(cpe_id)
                    else:
                        to_import.append((cpe_id, repo_id))

        # Delete all remaining pairs
        to_delete = [(cpe_id, repo_id) for repo_id, cpes in current_associations.items() for cpe_id in cpes]

        self.logger.debug("CPE-Repo pairs to import: %s", len(to_import))
        self.logger.debug("CPE-Repo pairs to delete: %s", len(to_delete))

        if unknown_cs_cnt:
            self.logger.warning("Unknown content sets in mapping file: %s", unknown_cs_cnt)

        if to_import:
            cur = self.conn.cursor()
            try:
                execute_values(cur, """insert into cpe_repo
                                    (cpe_id, repo_id)
                                    values %s""",
                               to_import, page_size=len(to_import))
                self.conn.commit()
            except Exception:  # pylint: disable=broad-except
                self.logger.exception("Failure while inserting into cpe_repo table: ")
                FAILED_IMPORT_CPE.inc()
                self.conn.rollback()
            finally:
                cur.close()

        if to_delete:
            cur = self.conn.cursor()
            try:
                for cpe_id, repo_id in to_delete:
                    # Slow but deleting should not happen often
                    cur.execute("delete from cpe_repo where cpe_id = %s and repo_id = %s",
                                (cpe_id, repo_id,))
                self.conn.commit()
            except Exception:  # pylint: disable=broad-except
                self.logger.exception("Failure while deleting from cpe_repo table: ")
                FAILED_UPDATE_CPE.inc()
                self.conn.rollback()
            finally:
                cur.close()

    def _populate_mappings(self, repo_mapping):
        self._populate_missing_mapping_cpes(repo_mapping)
        repo_list = self._parse_mapping_file(repo_mapping)
        self._populate_content_set_mapping(repo_list)
        self._populate_repo_mapping(repo_list)

    def store(self, cpe_dict, repo_mapping):
        """
        Store CPE metadata in the database.
        """
        self._save_lastmodified(cpe_dict.lastmodified, CpeStore.CPE_DICT_UPDATED_KEY)
        self._save_lastmodified(datetime.now(timezone.utc), CpeStore.CPE_REPO_MAP_UPDATED_KEY)
        self.logger.info("Syncing CPE dictionary.")
        self.populate_cpes(cpe_dict.cpes)  # Import missing CPEs and lookup all IDs
        self.logger.info("Syncing CPE repository mapping.")
        self._populate_mappings(repo_mapping)
        self.logger.debug("Syncing CPE metadata finished.")
