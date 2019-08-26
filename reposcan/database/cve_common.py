"""
Module contains classes for fetching/importing CVE from/into database.
"""
from psycopg2.extras import execute_values

from common.logging_utils import get_logger
from database.database_handler import DatabaseHandler


class CveStoreCommon:
    """
    Class interface for listing and storing CVEs in database.
    """
    def __init__(self):
        self.logger = get_logger(__name__)
        self.conn = DatabaseHandler.get_connection()

    def _populate_cve_impacts(self):
        cve_impacts = {}
        cur = self.conn.cursor()
        cur.execute("select id, name from cve_impact")
        for row in cur.fetchall():
            cve_impacts[row[1]] = row[0]
        cur.close()
        self.conn.commit()
        return cve_impacts

    def _populate_cwes(self, cursor, cve_data):
        # pylint: disable=R0914
        # Populate CWE table
        # DB errors caught by caller
        cursor.execute("SELECT name, id FROM cwe")
        cwe_name_id = cursor.fetchall()
        cwe_name = [cwe[0] for cwe in cwe_name_id]
        cwe_list = []
        cwe_link_map = dict()
        for cve in cve_data.values():
            for cwe in cve["cwe_list"]:
                cwe_list.append(cwe['cwe_name'])
                cwe_link_map[cwe['cwe_name']] = cwe['link']

        import_set = set(cwe_list) - set(cwe_name)
        import_set = [(name, cwe_link_map[name]) for name in import_set]
        self.logger.debug("CWEs to import: %d", len(import_set))
        new_cwes = ()
        if import_set:
            execute_values(cursor, "INSERT INTO cwe (name, link) values %s returning name, id",
                           list(import_set), page_size=len(list(import_set)))
            new_cwes = cursor.fetchall()

        # Populate cve_cwe mappings
        mapping_set = []
        for entry in cve_data.values():
            if "id" in entry:
                cwe_names = [x["cwe_name"] for x in entry["cwe_list"]]
                mapping_set.extend([(entry['id'], cwe_name) for cwe_name in cwe_names])

        # Some entries are not commited to DB yet, get them from last insert
        all_cwes = dict(tuple(new_cwes) + tuple(cwe_name_id))
        # Lookup IDs for missing cwes
        cve_cwe_map = _map_name_to_id(set(mapping_set), all_cwes)
        cursor.execute("SELECT cve_id, cwe_id FROM cve_cwe")
        to_import = set(cve_cwe_map) - set(cursor.fetchall())
        self.logger.debug("CVE to CWE mapping to import: %d", len(to_import))
        if to_import:
            execute_values(cursor, "INSERT INTO cve_cwe (cve_id, cwe_id) values %s returning cve_id, cwe_id",
                           list(to_import), page_size=len(to_import))

    def _get_source_id(self, source):
        cur = self.conn.cursor()
        cur.execute("select id from cve_source where name = %s", (source,))
        source_id = cur.fetchone()[0]
        cur.close()
        return source_id

    @staticmethod
    def _process_url_list(name, url_list):
        redhat_url = None
        secondary_url = None
        url_list = [item for item in url_list if url_list is not None]
        for item in url_list:
            if not secondary_url and item["url"]: # isn't None or empty-str
                secondary_url = item["url"]
            if "redhat" in item["url"]:  # try to determine Red Hat CVE, suboptimal, but works so far
                redhat_url = "https://access.redhat.com/security/cve/" + str.lower(name)
        return redhat_url, secondary_url


def _map_name_to_id(mapping_set, result):
    cve_cwe_map = []
    # construct (cve_id,cwe_name)->(cve_id,cwe_id)
    for item in mapping_set:
        cve_cwe_map.append((item[0], result[item[1]]))
    return cve_cwe_map
