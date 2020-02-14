""""
Module containing classes for fetching/importing cvemap metadata from/into database.
"""
from psycopg2.extras import execute_values

from database.cve_common import CveStoreCommon
from common.dateutil import format_datetime
from mnm import FAILED_IMPORT_CVE, FAILED_UPDATE_CVE


class CvemapStore(CveStoreCommon):
    """
    Interface to store cve list metadata (e.g lastmodified).
    """
    UPDATED_KEY = 'redhatcve:updated'

    def lastmodified(self):
        """
        Fetch lastmodified date for cvemap we've downloaded in the past.
        """
        cur = self.conn.cursor()
        cur.execute("select value from metadata where key = %s", (self.UPDATED_KEY,))
        row = cur.fetchone()
        lastmodified = row[0] if row else None
        cur.close()
        return lastmodified

    def _save_lastmodified(self, lastmodified):
        lastmodified = format_datetime(lastmodified)
        cur = self.conn.cursor()
        # Update timestamp
        cur.execute("update metadata set value = %s where key = %s",
                    (lastmodified, self.UPDATED_KEY,))
        if cur.rowcount < 1:
            cur.execute("insert into metadata (key, value) values (%s, %s)",
                        (self.UPDATED_KEY, lastmodified))
        cur.close()
        self.conn.commit()

    def _import_cves(self, to_import, cve_data):
        if to_import:
            cur = self.conn.cursor()
            try:
                execute_values(cur, """insert into cve (name, description, impact_id,
                                                        published_date, modified_date,
                                                        cvss3_score, cvss3_metrics, iava,
                                                        redhat_url, secondary_url, source_id,
                                                        cvss2_score, cvss2_metrics)
                                              values %s returning id, name""",
                               list(to_import), page_size=len(to_import))
                for row in cur.fetchall():
                    cve_data[row[1]]["id"] = row[0]
                self.conn.commit()
            except Exception:  # pylint: disable=broad-except
                self.logger.exception("Failure while importing CVEs")
                FAILED_IMPORT_CVE.inc()
                self.conn.rollback()
            finally:
                cur.close()

    def _update_cves(self, to_update):
        if to_update:
            cur = self.conn.cursor()
            try:
                tmpl_str = b"(%s, %s, %s, %s::int, %s, %s, %s::numeric, %s, %s, %s, %s, %s::int, %s::numeric, %s)"
                execute_values(cur,
                               """update cve set name = v.name,
                                                 description = v.description,
                                                 impact_id = v.impact_id,
                                                 published_date = v.published_date,
                                                 modified_date = v.modified_date,
                                                 redhat_url = v.redhat_url,
                                                 secondary_url = v.secondary_url,
                                                 cvss2_score = v.cvss2_score,
                                                 cvss2_metrics = v.cvss2_metrics,
                                                 cvss3_score = v.cvss3_score,
                                                 cvss3_metrics = v.cvss3_metrics,
                                                 iava = v.iava,
                                                 source_id = v.source_id
                                  from (values %s)
                                  as v(id, name, description, impact_id, published_date, modified_date,
                                  cvss3_score, cvss3_metrics, iava, redhat_url, secondary_url, source_id,
                                  cvss2_score, cvss2_metrics)
                                  where cve.id = v.id """,
                               list(to_update), page_size=len(to_update), template=tmpl_str)
            except Exception: # pylint: disable=broad-except
                self.logger.exception("Failure while updating CVEs")
                FAILED_UPDATE_CVE.inc()
                self.conn.rollback()
            finally:
                cur.close()

    def _set_null_source_cves(self, to_delete):
        if to_delete:
            cur = self.conn.cursor()
            try:
                execute_values(cur, """update cve set source_id = null where id in (%s)""",
                               to_delete, page_size=len(to_delete))
                self.conn.commit()
            except Exception:  # pylint: disable=broad-except
                self.logger.exception("Failure while deleting CVEs")
                self.conn.rollback()
            finally:
                cur.close()

    def _populate_cves(self, cvemap):  # pylint: disable=too-many-branches
        cve_impact_map = self._populate_cve_impacts()
        rh_source_id = self._get_source_id('Red Hat')
        cur = self.conn.cursor()

        cve_data = cvemap.list_cves()
        cur.execute("""select id, name, source_id,
                                 description, impact_id,
                                 published_date, modified_date,
                                 cvss3_score, cvss3_metrics,
                                 iava, redhat_url,
                                 secondary_url, source_id,
                                 cvss2_score, cvss2_metrics
                                 from cve""")
        #
        # find and merge cves that have already been loaded
        #
        # fields we care about potentially merging include:
        # [3]description,
        # [5]published_date, [6]modified_date,
        # [7]cvss3_score, [8]cvss3_metrics,
        # [9]iava, [10]redhat_url, [11]secondary_url,
        # [13]cvss2_score, [14]cvss2_metrics,
        cols = {
            'description': 3,
            'published_date': 5,
            'modified_date': 6,
            'cvss3_score': 7,
            'cvss3_metrics': 8,
            'iava': 9,
            'redhat_url': 10,
            'secondary_url': 11,
            'cvss2_score': 13,
            'cvss2_metrics': 14}

        to_delete = []
        for a_db_row in cur.fetchall():
            # cve_data[row[1]] = incoming-cve-with-same-name-as-from-db
            # skip id, name, source_id (they are *always* filled in
            # for rest, use incoming unless null, then use from-db
            db_name = a_db_row[1]
            db_id = a_db_row[0]
            if db_name in cve_data:
                cve_data[db_name]["id"] = db_id
                for a_key in cols:
                    if not a_key in cve_data[db_name]:
                        cve_data[db_name][a_key] = None
                    if not cve_data[db_name][a_key]:
                        cve_data[db_name][a_key] = a_db_row[cols[a_key]]
            else:
                to_delete.append((db_id,))

        to_import = []
        to_update = []
        # now, deal with all items
        for name, values in cve_data.items():
            values["impact_id"] = cve_impact_map[values["impact"].capitalize()] \
                        if values["impact"] is not None else cve_impact_map["None"]
            # make sure everyting has all the keys, even if val is empty
            for a_key in cols:
                if not a_key in values:
                    values[a_key] = None

            item = (name, values["description"], values["impact_id"], values["published_date"],
                    values["modified_date"], values["cvss3_score"], values["cvss3_metrics"], values["iava"],
                    values["redhat_url"], values["secondary_url"], rh_source_id,
                    values["cvss2_score"], values["cvss2_metrics"])
            # if we have an 'id', it means we're already in the db
            if "id" in values:
                to_update.append((values["id"],) + item)
            else:
                to_import.append(item)
        cur.close()
        self.logger.debug("CVEs to import: %d", len(to_import))
        self.logger.debug("CVEs to update: %d", len(to_update))
        self.logger.debug("CVEs to delete: %d", len(to_delete))

        self._import_cves(to_import, cve_data)

        self._update_cves(to_update)

        self._set_null_source_cves(to_delete)

        cur = self.conn.cursor()
        try:
            self._populate_cwes(cur, cve_data)
            self.conn.commit()
        except Exception:  # pylint: disable=broad-except
            self.logger.exception("Failure when populating CWEs")
            self.conn.rollback()
        finally:
            cur.close()

    def store(self, cvemap):
        """
        Store list of CVEs in the database.
        """
        self.logger.info("Syncing CVE map.")
        self._save_lastmodified(cvemap.get_lastmodified())
        self.logger.debug("Syncing CVEs: %s", cvemap.get_cve_count())
        self._populate_cves(cvemap)
        self.logger.debug("Syncing CVEs finished.")
