"""
Module contains classes for returning errata data from DB
"""

class Errata:
    """
    Class to hold Erratum attributes
    """

    def __init__(self, id, name, synopsis, severity, description, solution, issued, updated):
        setattr(self, "name", name)
        setattr(self, "id", id)
        mydict = {}
        mydict["type"] = None
        mydict["issued"] = str(issued)
        mydict["synopsis"] = synopsis
        mydict["description"] = description
        mydict["solution"] = solution
        mydict["severity"] = severity
        mydict["summary"] = None
        mydict["updated"] = str(updated)
        mydict["url"] = "https://access.redhat.com/errata/%s" % name
        mydict["bugzilla_list"] = []
        mydict["cve_list"] = []
        mydict["package_list"] = []
        mydict["reference_list"] = []
        setattr(self, "mydict", mydict)

    def set_cve_names(self, cve_name_list):
        mydict = self.get_val("mydict")
        mydict["cve_list"] = cve_name_list

    def set_packages(self, package_list):
        mydict = self.get_val("mydict")
        mydict["package_list"] = package_list

    def get_val(self, attr_name):
        """
        Return Erratum attribute or None
        :param attr_name: attr_name
        :return: attribute
        """
        value = None
        if attr_name in vars(self):
            value = getattr(self, attr_name)
        return value

class ErrataAPI:
    def __init__(self, cursor):
        self.cursor = cursor

    def get_cve_names_for_erratum_id(self, id):
        """
        Get the list of cves for the given erratum id
        """
        cve_query = "SELECT name FROM cve"
        cve_query += " JOIN errata_cve ON cve_id = cve.id"
        cve_query += " WHERE errata_cve.errata_id = %s" % str(id)
        self.cursor.execute(cve_query)
        cve_names = self.cursor.fetchall()
        cve_name_list = []
        for cve_name in cve_names:
            cve_name_list.append(cve_name[0])
        return cve_name_list

    @staticmethod
    def build_package_name(name, epoch, version, release, arch):
        """
        Build a package name from the separate NEVRA parts
        """
        package_name = name + "-"
        if int(epoch) > 0:
            package_name += "%s:" % epoch
        package_name += "%s-%s.%s" % (version, release, arch)
        return package_name

    def get_package_list_for_erratum_id(self, id):
        """
        Get the list of packages for the given erratum id
        """
        pkg_query = "SELECT package.name, evr.epoch, evr.version, evr.release, arch.name"
        pkg_query += " FROM pkg_errata"
        pkg_query += " JOIN package ON package.id = pkg_errata.pkg_id"
        pkg_query += " JOIN evr ON evr.id = package.evr_id"
        pkg_query += " JOIN arch ON arch.id = package.arch_id"
        pkg_query += " WHERE pkg_errata.errata_id = %s" % str(id)
        self.cursor.execute(pkg_query)
        result = self.cursor.fetchall()
        package_list = []
        for name, epoch, version, release, arch in result:
            package_list.append(self.build_package_name(name, epoch, version, release, arch))
        return package_list

    def process_list(self, data):
        """
        This method returns details for given set of Errata.

        :param cursor: psycopg2 connection cursor
        :param data: data obtained from api, we're interested in data["errata_list"]

        :returns: dictionary containing detailed information for given errata list}

        """

        errata_to_process = data["errata_list"]
        errata_to_process = filter(None, errata_to_process)
        answer = {}

        if not errata_to_process:
            return answer

        # Select all errata in request
        errata_query = "SELECT errata.id, errata.name, synopsis, severity.name, description,"
        errata_query += " solution, issued, updated"
        errata_query += " FROM errata"
        errata_query += " LEFT JOIN severity ON severity_id = severity.id"
        errata_query += " WHERE errata.name IN %s"
        self.cursor.execute(errata_query, [tuple(errata_to_process)])
        errata = self.cursor.fetchall()

        erratum_list = []
        for id, name, synopsis, severity, description, solution, issued, updated in errata:
            new_erratum = Errata(id, name, synopsis, severity, description, solution, issued, updated)
            new_erratum.set_cve_names(self.get_cve_names_for_erratum_id(id))
            new_erratum.set_packages(self.get_package_list_for_erratum_id(id))
            erratum_list.append(new_erratum)

        errata_dict = {}
        for e in erratum_list:
            errata_dict[e.get_val("name")] = e.get_val("mydict")
        answer["errata_list"] = errata_dict
        return answer
