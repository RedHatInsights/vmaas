"""
Module contains functions and CVE class for returning data from DB
"""

from utils import format_datetime, parse_datetime


class CVE(object):
    """
    Class to hold CVE attributes
    """
    cve_cwe_map = None

    def __init__(self, cve_entry, column_names):
        for col_name in column_names:
            setattr(self, col_name, cve_entry[column_names.index(col_name)])
        self.cwe = self.associate_cwes()

    def associate_cwes(self):
        """
        Assigns cve to cwe and creates a list
        :return:
        """
        cwe_map = []
        if CVE.cve_cwe_map is not None:
            cwe_map = [item[1] for item in CVE.cve_cwe_map if self.get_val("cve.id") == item[0]]
        return cwe_map

    def get_val(self, attr_name):
        """
        Return CVE attribute or None
        :param attr_name: attr_name
        :return: attribute
        """
        value = getattr(self, attr_name, "")
        return value if value is not None else ""


class CveAPI(object):
    """ Main /cves API class. """
    def __init__(self, cursor, items_per_page=5000):
        self.cursor = cursor
        self.page_size = items_per_page
        self.pages = 1
        self.page = 1

    def process_list(self, data):
        """
        This method returns details for given set of CVEs.

        :param data: data obtained from api, we're interested in data["cve_list"]

        :returns: list of dictionaries containing detailed information for given cve list}

        """

        cves_to_process = data.get("cve_list", None)
        modified_since = data.get("modified_since", None)
        self.page = data.get("page", self.page)
        self.page_size = data.get("page_size", self.page_size)
        cve_list = []

        if not cves_to_process or self.page <= 0:
            return self.construct_answer(cve_list, modified_since)

        cves_to_process = filter(None, cves_to_process)
        # Select all cves in request
        column_names = ["cve.id", "redhat_url", "secondary_url", "cve.name", "cvss3_score", "cve_impact.name",
                        "published_date", "modified_date", "iava", "description"]
        cve_query = """SELECT {columns}
                         FROM cve
                         LEFT JOIN cve_impact ON cve.impact_id = cve_impact.id
                        WHERE""".format(columns=', '.join(column_names))

        # Count number of CVEs in the DB
        cve_number_query = """SELECT count(cve.id)
                         FROM cve
                         LEFT JOIN cve_impact ON cve.impact_id = cve_impact.id
                        WHERE"""

        if len(cves_to_process) == 1:
            cve_query += " cve.name ~ %s"
            cve_number_query += " cve.name ~ %s"
            cve_query_params = cves_to_process
        else:
            cve_query += " cve.name IN %s"
            cve_number_query += " cve.name IN %s"
            cve_query_params = [tuple(cves_to_process)]

        if modified_since:
            cve_query += " and (cve.modified_date >= %s or cve.published_date >= %s)"
            cve_number_query += " and (cve.modified_date >= %s or cve.published_date >= %s)"
            cve_query_params.append(parse_datetime(modified_since))
            cve_query_params.append(parse_datetime(modified_since))

        # count number of pages in response
        self.cursor.execute(cve_number_query, cve_query_params)
        cves = self.cursor.fetchall()[0][0]  # get entire number of CVEs in the DB
        self.pages = cves / self.page_size   # update number of pages
        if cves % self.page_size > 0:
            self.pages += 1

        if self.page > self.pages:
            return self.construct_answer(cve_list, modified_since)
        else:
            cve_query += " ORDER BY cve.id LIMIT %s OFFSET %s"
            cve_query_params.append(self.page_size)
            cve_query_params.append(self.page_size * (self.page - 1))

        self.cursor.execute(cve_query, cve_query_params)
        cves = self.cursor.fetchall()
        CVE.cve_cwe_map = self.get_cve_cwe_map([cve[column_names.index("cve.id")] for cve in cves])  # generate cve ids

        for cve_entry in cves:
            cve = CVE(cve_entry, column_names)
            cve_list.append(cve)

        return self.construct_answer(cve_list, modified_since)

    def get_cve_cwe_map(self, ids):
        """
        For givers CVE ids find CWE in DB
        :param ids: CVE ids
        :return: cve_cwe mapping
        """
        if not ids:
            return []
        query = """SELECT cve_id, cwe.name, cwe.link
                     FROM cve_cwe map
                     JOIN cwe ON map.cwe_id = cwe.id
                    WHERE map.cve_id IN %s"""
        self.cursor.execute(query, [tuple(ids)])
        return self.cursor.fetchall()

    def construct_answer(self, cve_list, modified_since):
        """
        Final dictionary generation
        :param cve_list: which cves to show
        :return: JSON ready dictionary
        """
        resp_cve_list = {}
        for cve in cve_list:
            resp_cve_list[cve.get_val("cve.name")] = {
                "redhat_url": cve.get_val("redhat_url"),
                "secondary_url": cve.get_val("secondary_url"),
                "synopsis": cve.get_val("cve.name"),
                "impact": cve.get_val("cve_impact.name"),
                "public_date": format_datetime(cve.get_val("published_date")),
                "modified_date": format_datetime(cve.get_val("modified_date")),
                "cwe_list": cve.get_val("cwe"),
                "cvss3_score": str(cve.get_val("cvss3_score")),
                "description": cve.get_val("description"),
            }
        response = {"cve_list": resp_cve_list}
        if modified_since:
            response["modified_since"] = modified_since

        response["page"] = self.page
        response["pages"] = self.pages
        response["page_size"] = self.page_size
        return response
