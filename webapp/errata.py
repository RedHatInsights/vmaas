"""
Module contains classes for returning errata data from DB
"""

from utils import format_datetime, join_packagename


class Errata(object):
    """
    Class to hold Erratum attributes
    """

    def __init__(self, oid, name, synopsis, summary, errata_type, severity, description, solution, issued, updated):
        #pylint: disable=too-many-arguments
        self.name = name
        self.oid = oid
        self.data = {
            "type": errata_type,
            "issued": format_datetime(issued),
            "synopsis": synopsis,
            "description": description,
            "solution": solution,
            "severity": severity,
            "summary": summary,
            "updated": format_datetime(updated),
            "url": "https://access.redhat.com/errata/%s" % name,
            "bugzilla_list": [],
            "cve_list": [],
            "package_list": [],
            "reference_list": [],
        }

    def add_cve(self, cve):
        """ Put CVE into cve_list. """
        self.data["cve_list"].append(cve)

    def add_package(self, package):
        """ Put package into package_list. """
        self.data["package_list"].append(package)

    def add_bugzilla(self, bugzilla):
        """Put bugzilla into bugzilla_list. """
        self.data["bugzilla_list"].append(bugzilla)

    def add_reference(self, reference):
        """Put reference into reference_list. """
        self.data["reference_list"].append(reference)


class ErrataAPI(object):
    """ Main /errata API class. """
    def __init__(self, cursor):
        self.cursor = cursor

    def set_cves_for_errata(self, errata_map):
        """
        Populate the errata in the given errata_map with each erratum's
        list of cves.
        """
        cve_query = """SELECT errata_cve.errata_id, cve.name FROM cve
                         JOIN errata_cve ON cve_id = cve.id
                        WHERE errata_cve.errata_id IN %s"""
        self.cursor.execute(cve_query, [tuple(errata_map.keys())])
        results = self.cursor.fetchall()
        for erratum_id, cve_name in results:
            errata_map[erratum_id].add_cve(cve_name)

    def set_packages_for_errata(self, errata_map):
        """
        Populate the errata in the given errata_map with each erratum's
        list of packages.
        """
        pkg_query = """SELECT pkg_errata.errata_id, package.name, evr.epoch, evr.version, evr.release, arch.name
                         FROM pkg_errata
                         JOIN package ON package.id = pkg_errata.pkg_id
                         JOIN evr ON evr.id = package.evr_id
                         JOIN arch ON arch.id = package.arch_id
                        WHERE pkg_errata.errata_id IN %s"""
        self.cursor.execute(pkg_query, [tuple(errata_map.keys())])
        results = self.cursor.fetchall()
        for erratum_id, name, epoch, version, release, arch in results:
            errata_map[erratum_id].add_package(join_packagename(name, epoch, version, release, arch))

    def set_references_for_errata(self, errata_map):
        """
        Populate the errata in the given errata_map with each erratum's
        list of references (bugzilla and other).
        """
        refs_query = """SELECT errata_id, type, name FROM errata_refs
                        WHERE errata_id IN %s"""
        self.cursor.execute(refs_query, [tuple(errata_map.keys())])
        results = self.cursor.fetchall()
        for erratum_id, ref_type, name in results:
            if ref_type == 'bugzilla':
                errata_map[erratum_id].add_bugzilla(name)
            else:
                errata_map[erratum_id].add_reference(name)

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

        errata_map = {}
        for (oid, name, synopsis, summary, errata_type, severity,
             description, solution, issued, updated) in errata:
            new_erratum = Errata(oid, name, synopsis, summary, errata_type,
                                 severity, description, solution, issued, updated)
            errata_map[oid] = new_erratum

        if errata_map:
            self.set_cves_for_errata(errata_map)
            self.set_packages_for_errata(errata_map)
            self.set_references_for_errata(errata_map)

        response_dict = {}
        for erratum in errata_map.values():
            response_dict[erratum.name] = erratum.data
        #answer["errata_list"] = response_dict
        return {"errata_list": response_dict}
