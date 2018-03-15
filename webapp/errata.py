"""
Module contains classes for returning errata data from DB
"""

class Errata(object):
    """
    Class to hold Erratum attributes
    """

    def __init__(self, oid, name, synopsis, summary, errata_type, severity, description, solution, issued, updated):
        #pylint: disable=too-many-arguments
        setattr(self, "name", name)
        setattr(self, "id", oid)
        mydict = {}
        mydict["type"] = errata_type
        mydict["issued"] = str(issued)
        mydict["synopsis"] = synopsis
        mydict["description"] = description
        mydict["solution"] = solution
        mydict["severity"] = severity
        mydict["summary"] = summary
        mydict["updated"] = str(updated)
        mydict["url"] = "https://access.redhat.com/errata/%s" % name
        mydict["bugzilla_list"] = []
        mydict["cve_list"] = []
        mydict["package_list"] = []
        mydict["reference_list"] = []
        setattr(self, "mydict", mydict)

    def set_cve_names(self, cve_name_list):
        """ Put CVE list into erratum. """
        mydict = self.get_val("mydict")
        mydict["cve_list"] = cve_name_list

    def set_packages(self, package_list):
        """ Put package list into erratum. """
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

class ErrataAPI(object):
    """ Main /errata API class. """
    def __init__(self, cursor):
        self.cursor = cursor

    def get_cve_names_for_erratum_id(self, oid):
        """
        Get the list of cves for the given erratum id
        """
        cve_query = """SELECT name FROM cve
                         JOIN errata_cve ON cve_id = cve.id
                        WHERE errata_cve.errata_id = %s"""
        self.cursor.execute(cve_query, (oid,))
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

    def get_package_list_for_erratum_id(self, oid):
        """
        Get the list of packages for the given erratum id
        """
        pkg_query = """SELECT package.name, evr.epoch, evr.version, evr.release, arch.name
                         FROM pkg_errata
                         JOIN package ON package.id = pkg_errata.pkg_id
                         JOIN evr ON evr.id = package.evr_id
                         JOIN arch ON arch.id = package.arch_id
                        WHERE pkg_errata.errata_id = %s"""
        self.cursor.execute(pkg_query, (oid,))
        result = self.cursor.fetchall()
        package_list = []
        for name, epoch, version, release, arch in result:
            package_list.append(self.build_package_name(name, epoch, version, release, arch))
        return package_list

    def process_list(self, data):
        #pylint: disable=too-many-locals
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
        errata_query = """SELECT errata.id, errata.name, synopsis, summary, errata_type.name,
                                 severity.name, description, solution, issued, updated
                            FROM errata
                            JOIN errata_type ON errata_type_id = errata_type.id
                            JOIN severity ON severity_id = severity.id
                           WHERE errata.name IN %s"""
        self.cursor.execute(errata_query, [tuple(errata_to_process)])
        errata = self.cursor.fetchall()

        erratum_list = []
        for (oid, name, synopsis, summary, errata_type, severity,
             description, solution, issued, updated) in errata:
            new_erratum = Errata(oid, name, synopsis, summary, errata_type,
                                 severity, description, solution, issued, updated)
            new_erratum.set_cve_names(self.get_cve_names_for_erratum_id(oid))
            new_erratum.set_packages(self.get_package_list_for_erratum_id(oid))
            erratum_list.append(new_erratum)

        errata_dict = {}
        for erratum in erratum_list:
            errata_dict[erratum.get_val("name")] = erratum.get_val("mydict")
        answer["errata_list"] = errata_dict
        return answer
