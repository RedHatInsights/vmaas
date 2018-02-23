"""
Module contains classes for fetching/importing CVE from/into database.
"""
from psycopg2.extras import execute_values

from cli.logger import SimpleLogger
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

    def _populate_cves(self, repo):     # pylint: disable=too-many-locals
        severity_map = self._populate_severities(repo)
        cur = self.conn.cursor()
        cve_data = {}
        for cve in repo.list_cves():
            cve_name = _dget(cve, "cve", "CVE_data_meta", "ID")

            cve_desc_list = _dget(cve, "cve", "description", "description_data")
            severity = _dget(cve, "impact", "baseMetricV3", "cvssV3", "baseSeverity")
            cwe_data = _dget(cve, "cve", "problemtype", "problemtype_data")
            cwe_desc_list = _dget(cwe_data[0], "description")

            cve_data[cve_name] = {
                "description": _desc(cve_desc_list, "lang", "en", "value"),
                "severity_id": severity_map[severity.capitalize()] if severity is not None else None,
                "cvss3_score": _dget(cve, "impact", "baseMetricV3", "cvssV3", "baseScore"),
                "cwe": _desc(cwe_desc_list, "lang", "en", "value"),
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

        to_import = [(name, values["description"], values["severity_id"],
                      values["cvss3_score"], values["cwe"], values["iava"])
                     for name, values in cve_data.items() if "id" not in values]
        self.logger.log("CVEs to import: %d" % len(to_import))
        to_update = [(values["id"], name, values["description"], values["severity_id"],
                      values["cvss3_score"], values["cwe"], values["iava"])
                     for name, values in cve_data.items() if "id" in values]
        self.logger.log("CVEs to update: %d" % len(to_update))

        if to_import:
            execute_values(cur,
                           """insert into cve (name, description, severity_id, cvss3_score, cwe, iava)
                              values %s returning id, name""",
                           list(to_import), page_size=len(to_import))
            for row in cur.fetchall():
                cve_data[row[1]]["id"] = row[0]

        if to_update:
            execute_values(cur,
                           """update cve set name = v.name,
                                             description = v.description,
                                             severity_id = v.severity_id,
                                             cvss3_score = v.cvss3_score,
                                             cwe = v.cwe,
                                             iava = v.iava
                              from (values %s)
                              as v(id, name, description, severity_id, cvss3_score, cwe, iava)
                              where cve.id = v.id """,
                           list(to_update), page_size=len(to_update))
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
