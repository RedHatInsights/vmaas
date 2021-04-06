""""
Module containing classes for importing CPE metadata from/into database.
"""
from datetime import datetime, timezone
from psycopg2.extras import execute_values

from database.database_handler import DatabaseHandler
from common.dateutil import format_datetime
from common.logging_utils import get_logger
from mnm import FAILED_IMPORT_CPE, FAILED_UPDATE_CPE


class CpeStore:
    """
    Interface to store CPE metadata.
    """

    CPE_DICT_UPDATED_KEY = 'redhatcpedict:updated'
    CPE_REPO_MAP_UPDATED_KEY = 'redhatcperepomap:updated'

    def __init__(self):
        self.logger = get_logger(__name__)
        self.conn = DatabaseHandler.get_connection()
        self.cpe_label_to_id = {}
        self.cpe_label_to_name = {}

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

    def _populate_cpes(self, cpes):  # pylint: disable=too-many-branches
        to_import = []
        to_update = []
        cur = self.conn.cursor()
        cur.execute("select id, label, name from cpe")
        for cpe_id, label, name in cur.fetchall():
            self.cpe_label_to_id[label] = cpe_id
            self.cpe_label_to_name[label] = name
        cur.close()

        for label, name in cpes.items():
            if label not in self.cpe_label_to_name:
                to_import.append((label, name))
            elif self.cpe_label_to_name[label] != name:
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

    def _populate_repo_mappings(self, repo_mapping):  # pylint: disable=too-many-branches, too-many-statements
        # Make sure all CPEs are in DB, even if they are not in CPE dict
        unknown_cpes = {}
        for content_set_label in repo_mapping["data"]:
            for cpe_label in repo_mapping["data"][content_set_label]["cpes"]:
                if cpe_label not in self.cpe_label_to_id:
                    unknown_cpes[cpe_label] = None
        self._populate_cpes(unknown_cpes)

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
        unknown_content_sets = set()
        for content_set_label in repo_mapping["data"]:
            cs_id = content_set_label_to_id.get(content_set_label)
            if cs_id is None:
                self.logger.debug("Unknown content set: %s", content_set_label)
                unknown_content_sets.add(content_set_label)
                continue
            cpe_ids = set()
            for cpe_label in repo_mapping["data"][content_set_label]["cpes"]:
                cpe_id = self.cpe_label_to_id[cpe_label]
                cpe_ids.add(cpe_id)

            # Find missing pairs to import and eliminate already existing
            for cpe_id in cpe_ids:
                if cpe_id in current_associations.get(cs_id, set()):
                    current_associations[cs_id].remove(cpe_id)
                else:
                    to_import.append((cpe_id, cs_id))

        # Delete all remaining pairs
        for cs_id in current_associations:
            for cpe_id in current_associations[cs_id]:
                to_delete.append((cpe_id, cs_id))

        self.logger.debug("CPE-CS pairs to import: %s", len(to_import))
        self.logger.debug("CPE-CS pairs to delete: %s", len(to_delete))

        if unknown_content_sets:
            self.logger.warning("Unknown content sets in mapping file: %s", len(unknown_content_sets))

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


    def store(self, cpe_dict, repo_mapping):
        """
        Store CPE metadata in the database.
        """
        self._save_lastmodified(cpe_dict.lastmodified, CpeStore.CPE_DICT_UPDATED_KEY)
        self._save_lastmodified(datetime.now(timezone.utc), CpeStore.CPE_REPO_MAP_UPDATED_KEY)
        self.logger.info("Syncing CPE dictionary.")
        self._populate_cpes(cpe_dict.cpes)  # Import missing CPEs and lookup all IDs
        self.logger.info("Syncing CPE repository mapping.")
        self._populate_repo_mappings(repo_mapping)
        self.logger.debug("Syncing CPE metadata finished.")
