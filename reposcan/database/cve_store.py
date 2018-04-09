"""
Module contains classes for fetching/importing CVE from/into database.
"""
from psycopg2.extras import execute_values

from cli.logger import SimpleLogger
from common.dateutil import parse_datetime
from database.database_handler import DatabaseHandler

class CveStore:
    """
    Class interface for listing and storing CVEs in database.
    """
    def __init__(self):
        self.logger = SimpleLogger()
        self.conn = DatabaseHandler.get_connection()

    def list_lastmodified(self):
        """
        List lastmodified times from database.
        """
        lastmodified = {}
        cur = self.conn.cursor()
        cur.execute("select key, value from metadata where key like 'nistcve:'")
        for row in cur.fetchall():
            label = row[0][8:]        # strip nistcve: prefix
            lastmodified[label] = row[1]
        cur.close()
        return lastmodified

    def _populate_severities(self, repo):
        severities = {}
        cur = self.conn.cursor()
        cur.execute("select id, name from severity")
        for row in cur.fetchall():
            severities[row[1]] = row[0]
        missing_severities = set()
        for cve in repo.list_cves():
            severity = _dget(cve, "impact", "baseMetricV3", "cvssV3", "baseSeverity")
            if severity is not None:
                severity = severity.capitalize()
                if severity not in severities:
                    missing_severities.add((severity,))
        self.logger.log("Severities missing in DB: %d" % len(missing_severities))
        if missing_severities:
            execute_values(cur, "insert into severity (name) values %s returning id, name",
                           missing_severities, page_size=len(missing_severities))
            for row in cur.fetchall():
                severities[row[1]] = row[0]
        cur.close()
        self.conn.commit()
        return severities

    def _populate_cwes(self, cursor, cve_data):
        # pylint: disable=R0914
        # Populate CWE table
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
        self.logger.log("CWEs to import: %d" % len(import_set))
        new_cwes = ()
        if import_set:
            execute_values(cursor, "INSERT INTO cwe (name, link) values %s returning name, id",
                           list(import_set), page_size=len(list(import_set)))
            new_cwes = cursor.fetchall()

        # Populate cve_cwe mappings
        mapping_set = []
        for entry in cve_data.values():
            cwe_names = [x["cwe_name"] for x in entry["cwe_list"]]
            mapping_set.extend([(entry['id'], cwe_name) for cwe_name in cwe_names])

        # Some entries are not commited to DB yet, get them from last insert
        all_cwes = dict(tuple(new_cwes) + tuple(cwe_name_id))
        # Lookup IDs for missing cwes
        cve_cwe_map = _map_name_to_id(set(mapping_set), all_cwes)
        cursor.execute("SELECT cve_id, cwe_id FROM cve_cwe")
        to_import = set(cve_cwe_map) - set(cursor.fetchall())
        self.logger.log("CVE to CWE mapping to import: %d" % len(to_import))
        if to_import:
            execute_values(cursor, "INSERT INTO cve_cwe (cve_id, cwe_id) values %s returning cve_id, cwe_id",
                           list(to_import), page_size=len(to_import))

    def _populate_cves(self, repo):     # pylint: disable=too-many-locals
        severity_map = self._populate_severities(repo)
        cur = self.conn.cursor()
        cve_data = {}
        for cve in repo.list_cves():
            cve_name = _dget(cve, "cve", "CVE_data_meta", "ID")

            cve_desc_list = _dget(cve, "cve", "description", "description_data")
            severity = _dget(cve, "impact", "baseMetricV3", "cvssV3", "baseSeverity")
            url_list = _dget(cve, "cve", "references", "reference_data")
            modified_date = parse_datetime(_dget(cve, "lastModifiedDate"))
            published_date = parse_datetime(_dget(cve, "publishedDate"))
            cwe_data = _dget(cve, "cve", "problemtype", "problemtype_data")
            cwe_list = _process_cwe_list(cwe_data)
            redhat_url, secondary_url = _process_url_list(cve_name, url_list)
            cve_data[cve_name] = {
                "description": _desc(cve_desc_list, "lang", "en", "value"),
                "severity_id": severity_map[severity.capitalize()] if severity is not None else None,
                "cvss3_score": _dget(cve, "impact", "baseMetricV3", "cvssV3", "baseScore"),
                "redhat_url": redhat_url,
                "cwe_list": cwe_list,
                "secondary_url": secondary_url,
                "published_date": published_date,
                "modified_date": modified_date,
                "iava": None,
            }


        if cve_data:
            names = [(key,) for key in cve_data]
            execute_values(cur,
                           """select id, name from cve
                              inner join (values %s) t(name)
                              using (name)
                           """, names, page_size=len(names))
            for row in cur.fetchall():
                cve_data[row[1]]["id"] = row[0]
                # Remove to not insert this CVE

        to_import = [(name, values["description"], values["severity_id"], values["published_date"],
                      values["modified_date"], values["cvss3_score"], values["iava"],
                      values["redhat_url"], values["secondary_url"])
                     for name, values in cve_data.items() if "id" not in values]
        self.logger.log("CVEs to import: %d" % len(to_import))
        to_update = [(values["id"], name, values["description"], values["severity_id"], values["published_date"],
                      values["modified_date"], values["cvss3_score"], values["iava"],
                      values["redhat_url"], values["secondary_url"])
                     for name, values in cve_data.items() if "id" in values]

        self.logger.log("CVEs to update: %d" % len(to_update))

        if to_import:
            execute_values(cur,
                           """insert into cve (name, description, severity_id, published_date, modified_date,
                              cvss3_score, iava, redhat_url, secondary_url) values %s returning id, name""",
                           list(to_import), page_size=len(to_import))
            for row in cur.fetchall():
                cve_data[row[1]]["id"] = row[0]

        if to_update:
            execute_values(cur,
                           """update cve set name = v.name,
                                             description = v.description,
                                             severity_id = v.severity_id,
                                             published_date = v.published_date,
                                             modified_date = v.modified_date,
                                             redhat_url = v.redhat_url,
                                             secondary_url = v.secondary_url,
                                             cvss3_score = v.cvss3_score,
                                             iava = v.iava
                              from (values %s)
                              as v(id, name, description, severity_id, published_date, modified_date, cvss3_score,
                              iava, redhat_url, secondary_url)
                              where cve.id = v.id """,
                           list(to_update), page_size=len(to_update),
                           template=b"(%s, %s, %s, %s::int, %s, %s, %s::numeric, %s, %s, %s)")
        self._populate_cwes(cur, cve_data)
        cur.close()
        self.conn.commit()
        return cve_data

    def store(self, repo):
        """
        Store / update cve information in database.
        """
        self.logger.log("Syncing %d CVEs." % repo.get_count())
        self._populate_cves(repo)
        self.logger.log("Syncing CVEs finished.")


def _dget(struct, *keys):
    """ Get value from multilevel dictionary structure.
        Similar to dict.get('key').
    """
    for key in keys:
        if key in struct:
            struct = struct[key]
        else:
            return None
    return struct

def _desc(dlist, lang_key, lang_val, desc_key):
    """ In list of descriptions locate the one with given lang.
    """
    for item in dlist:
        if item[lang_key] == lang_val:
            return item[desc_key]
    return None

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


def _process_cwe_list(cwe_data):
    cwe_list = []
    cwe_exclusion_list = ["NVD-CWE-noinfo", "NVD-CWE-Other"]
    for cwe in cwe_data:
        description_list = cwe["description"]
        for description in description_list:
            if all(x != description["value"] for x in cwe_exclusion_list):
                cwe_id = int(description["value"][4:])  # strip CWE-
                cwe_link = "http://cwe.mitre.org/data/definitions/%i.html" % cwe_id
                cwe_name = "CWE-%i" % cwe_id
                cwe_list.append(dict(cwe_name=cwe_name, link=cwe_link))
    return cwe_list

def _map_name_to_id(mapping_set, result):
    cve_cwe_map = []
    # construct (cve_id,cwe_name)->(cve_id,cwe_id)
    for item in mapping_set:
        cve_cwe_map.append((item[0], result[item[1]]))
    return cve_cwe_map
