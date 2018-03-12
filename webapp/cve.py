"""
Module contains functions and CVE class for returning data from DB
"""


class CVE:
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
        value = None
        if attr_name in vars(self):
            value = getattr(self, attr_name)
        return value

class CveAPI:
    def __init__(self, cursor):
        self.cursor = cursor

    def process_list(self, data):
        """
        This method returns details for given set of CVEs.

        :param data: data obtained from api, we're interested in data["cve_list"]

        :returns: list of dictionaries containing detailed information for given cve list}

        """

        cves_to_process = data["cve_list"]
        cves_to_process = filter(None, cves_to_process)
        answer = {}
        if not cves_to_process:
            return answer

        # Select all cves in request
        column_names = ["cve.id", "redhat_url", "secondary_url", "cve.name", "severity.name", "published_date",
                        "modified_date", "iava", "description"]
        cve_query = "SELECT %s from cve" % ', '.join(column for column in column_names)
        cve_query = cve_query + " LEFT JOIN severity ON severity_id = severity.id"
        cve_query = cve_query + " WHERE cve.name IN %s"
        self.cursor.execute(cve_query, [tuple(cves_to_process)])
        cves = self.cursor.fetchall()
        cwe_map = self.get_cve_cwe_map([cve[column_names.index("cve.id")] for cve in cves])  # generate cve ids
        CVE.cve_cwe_map = cwe_map
        cve_list = []
        for cve_entry in cves:
            cve = CVE(cve_entry, column_names)
            cve_list.append(cve)

        return self.construct_answer(cve_list)


    def get_cve_cwe_map(self, ids):
        """
        For givers CVE ids find CWE in DB
        :param ids: CVE ids
        :return: cve_cwe mapping
        """
        if not ids:
            return []
        query = "SELECT cve_id, cwe.name, cwe.link FROM cve_cwe map JOIN cwe ON map.cwe_id = cwe.id WHERE map.cve_id IN %s"
        self.cursor.execute(query, [tuple(ids)])
        return self.cursor.fetchall()


    @staticmethod
    def construct_answer(cve_list):
        """
        Final dictionary generation
        :param cve_list: which cves to show
        :return: JSON ready dictionary
        """
        response = {}
        for cve in cve_list:
            response[cve.get_val("cve.name")] = {
                "redhat_url": cve.get_val("redhat_url"),
                "secondary_url": cve.get_val("secondary_url"),
                "synopsis": cve.get_val("cve.name"),
                "impact": cve.get_val("severity.name"),
                "public_date": cve.get_val("published_date"),
                "modified_date": cve.get_val("modified_date"),
                "iava": cve.get_val("iava"),
                "cwe_list": cve.get_val("cwe"),
                "description": cve.get_val("description"),
            }
        return response
