"""
Module contains classes for fetching/importing CVE from/into database.
"""
from psycopg2.extras import execute_values

from common.dateutil import parse_datetime
from database.cve_common import CveStoreCommon

class CveStore(CveStoreCommon):
    """
    Class interface for listing and storing CVEs in database.
    """
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

    def _populate_cves(self, repo):
        cve_impact_map = self._populate_cve_impacts()
        nist_source_id = self._get_source_id('NIST')
        cur = self.conn.cursor()
        cve_data = {}
        for cve in repo.list_cves():
            cve_name = _dget(cve, "cve", "CVE_data_meta", "ID")

            cve_desc_list = _dget(cve, "cve", "description", "description_data")
            impact = _dget(cve, "impact", "baseMetricV3", "cvssV3", "baseSeverity")
            if impact is None:
                impact = _dget(cve, "impact", "baseMetricV2", "severity")
            url_list = _dget(cve, "cve", "references", "reference_data")
            modified_date = parse_datetime(_dget(cve, "lastModifiedDate"))
            published_date = parse_datetime(_dget(cve, "publishedDate"))
            cwe_data = _dget(cve, "cve", "problemtype", "problemtype_data")
            cwe_list = _process_cwe_list(cwe_data)
            redhat_url, secondary_url = self._process_url_list(cve_name, url_list)
            cve_data[cve_name] = {
                "description": _desc(cve_desc_list, "lang", "en", "value"),
                "impact_id": cve_impact_map[impact.capitalize()] if impact is not None else cve_impact_map['NotSet'],
                "cvss2_score": _dget(cve, "impact", "baseMetricV2", "cvssV2", "baseScore"),
                "cvss2_metrics": _dget(cve, "impact", "baseMetricV2", "cvssV2", "vectorString"),
                "cvss3_score": _dget(cve, "impact", "baseMetricV3", "cvssV3", "baseScore"),
                "cvss3_metrics": _dget(cve, "impact", "baseMetricV3", "cvssV3", "vectorString"),
                "redhat_url": redhat_url,
                "cwe_list": cwe_list,
                "secondary_url": secondary_url,
                "published_date": published_date,
                "modified_date": modified_date,
                "iava": None,
                "source_id": nist_source_id,
            }


        if cve_data:
            names = [(key,) for key in cve_data]
            execute_values(cur,
                           """select id, name, source_id from cve
                              inner join (values %s) t(name)
                              using (name)
                           """, names, page_size=len(names))
            for row in cur.fetchall():
                if row[2] is not None and row[2] != nist_source_id:
                    # different source, do not touch!
                    del cve_data[row[1]]
                    continue
                cve_data[row[1]]["id"] = row[0]
        to_import = [(name, values["description"], values["impact_id"], values["published_date"],
                      values["modified_date"], values["cvss3_score"], values["cvss3_metrics"], values["iava"],
                      values["redhat_url"], values["secondary_url"], values["source_id"],
                      values["cvss2_score"], values["cvss2_metrics"],)
                     for name, values in cve_data.items() if "id" not in values]
        self.logger.debug("CVEs to import: %d", len(to_import))
        to_update = [(values["id"], name, values["description"], values["impact_id"], values["published_date"],
                      values["modified_date"], values["cvss3_score"], values["cvss3_metrics"], values["iava"],
                      values["redhat_url"], values["secondary_url"], values["source_id"],
                      values["cvss2_score"], values["cvss2_metrics"])
                     for name, values in cve_data.items() if "id" in values]

        self.logger.debug("CVEs to update: %d", len(to_update))

        if to_import:
            execute_values(cur,
                           """insert into cve (name, description, impact_id, published_date, modified_date,
                              cvss3_score, cvss3_metrics, iava, redhat_url, secondary_url, source_id,
                              cvss2_score, cvss2_metrics)
                              values %s returning id, name""",
                           list(to_import), page_size=len(to_import))
            for row in cur.fetchall():
                cve_data[row[1]]["id"] = row[0]

        if to_update:
            tmpl_str = b"(%s, %s, %s, %s::int, %s, %s, %s::numeric, %s, %s, %s, %s, %s::int, %s::numeric, %s)"
            execute_values(cur,
                           """update cve set name = v.name,
                                             description = v.description,
                                             impact_id = v.impact_id,
                                             published_date = v.published_date,
                                             modified_date = v.modified_date,
                                             redhat_url = v.redhat_url,
                                             secondary_url = v.secondary_url,
                                             cvss3_score = v.cvss3_score,
                                             cvss3_metrics = v.cvss3_metrics,
                                             iava = v.iava,
                                             source_id = v.source_id,
                                             cvss2_score = v.cvss2_score,
                                             cvss2_metrics = v.cvss2_metrics
                              from (values %s)
                              as v(id, name, description, impact_id, published_date,
                              modified_date, cvss3_score, cvss3_metrics, iava, redhat_url,
                              secondary_url, source_id, cvss2_score, cvss2_metrics)
                              where cve.id = v.id """,
                           list(to_update), page_size=len(to_update), template=tmpl_str)
        self._populate_cwes(cur, cve_data)
        cur.close()
        self.conn.commit()
        return cve_data

    def store(self, repo):
        """
        Store / update cve information in database.
        """
        self.logger.info("Syncing %d CVEs.", repo.get_count())
        self._populate_cves(repo)
        self.logger.info("Syncing CVEs finished.")


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
