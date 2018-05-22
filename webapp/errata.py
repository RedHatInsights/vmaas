"""
Module contains classes for returning errata data from DB
"""

from utils import format_datetime, parse_datetime, join_packagename


class ErrataAPI(object):
    """ Main /errata API class. """
    def __init__(self, database):
        self.cursor = database.dictcursor()

    def set_cves_for_errata(self, errata_map):
        """
        Populate the errata in the given errata_map with each erratum's
        list of cves.
        """
        cve_query = """SELECT errata_cve.errata_id as erratum_id,
                              cve.name as cve_name
                         FROM cve
                         JOIN errata_cve ON cve_id = cve.id
                        WHERE errata_cve.errata_id IN %s"""
        self.cursor.execute(cve_query, [tuple(errata_map.keys())])
        results = self.cursor.fetchall()
        for result in results:
            errata_map[result['erratum_id']]['cve_list'].append(result['cve_name'])

    def set_packages_for_errata(self, errata_map):
        """
        Populate the errata in the given errata_map with each erratum's
        list of packages.
        """
        pkg_query = """SELECT pkg_errata.errata_id as erratum_id,
                              package_name.name as name,
                              evr.epoch as epoch,
                              evr.version as version,
                              evr.release as release,
                              arch.name as arch
                         FROM pkg_errata
                         JOIN package ON package.id = pkg_errata.pkg_id
                         JOIN package_name ON package_name.id = package.name_id
                         JOIN evr ON evr.id = package.evr_id
                         JOIN arch ON arch.id = package.arch_id
                        WHERE pkg_errata.errata_id IN %s"""
        self.cursor.execute(pkg_query, [tuple(errata_map.keys())])
        results = self.cursor.fetchall()
        for result in results:
            packagename = join_packagename(result['name'],
                                           result['epoch'],
                                           result['version'],
                                           result['release'],
                                           result['arch'])
            errata_map[result['erratum_id']]['package_list'].append(packagename)

    def set_references_for_errata(self, errata_map):
        """
        Populate the errata in the given errata_map with each erratum's
        list of references (bugzilla and other).
        """
        refs_query = """SELECT errata_id as erratum_id,
                               type as ref_type,
                               name
                          FROM errata_refs
                         WHERE errata_id IN %s"""
        self.cursor.execute(refs_query, [tuple(errata_map.keys())])
        results = self.cursor.fetchall()
        for result in results:
            if result['ref_type'] == 'bugzilla':
                errata_map[result['erratum_id']]['bugzilla_list'].append(result['name'])
            else:
                errata_map[result['erratum_id']]['reference_list'].append(result['name'])

    def process_list(self, data):
        """
        This method returns details for given set of Errata.

        :param data: data obtained from api, we're interested in data["errata_list"]

        :returns: dictionary containing detailed information for given errata list}

        """

        modified_since = data.get("modified_since", None)
        errata_to_process = data.get("errata_list", None)
        response = {"errata_list": {}}
        if modified_since:
            response["modified_since"] = modified_since

        if not errata_to_process:
            return response

        errata_to_process = list(filter(None, errata_to_process))
        # Select all errata in request
        errata_query = """SELECT errata.id as oid,
                                 errata.name as name,
                                 synopsis,
                                 summary,
                                 errata_type.name as type,
                                 errata_severity.name as severity,
                                 description,
                                 solution,
                                 issued,
                                 updated
                            FROM errata
                            JOIN errata_type ON errata_type_id = errata_type.id
                            JOIN errata_severity ON severity_id = errata_severity.id
                           WHERE"""

        if len(errata_to_process) == 1:
            errata_query += " errata.name ~ %s"
            errata_query_params = errata_to_process
        else:
            errata_query += " errata.name IN %s"
            errata_query_params = [tuple(errata_to_process)]
        if modified_since:
            errata_query += " and errata.updated >= %s"
            errata_query_params.append(parse_datetime(modified_since))
        self.cursor.execute(errata_query, errata_query_params)
        errata_results = self.cursor.fetchall()

        errata_map = {} # map keyed on oid for populating lists in errata
        response_dict = {} # map keyed on erratum name to return to caller
        for erratum in errata_results:
            oid = erratum.pop('oid')
            erratum_name = erratum.pop('name')
            erratum['updated'] = format_datetime(erratum['updated'])
            erratum['issued'] = format_datetime(erratum['issued'])
            erratum['bugzilla_list'] = []
            erratum['package_list'] = []
            erratum['reference_list'] = []
            erratum['cve_list'] = []
            erratum['url'] = "https://access.redhat.com/errata/%s" % erratum_name
            errata_map[oid] = erratum
            response_dict[erratum_name] = erratum

        if errata_map:
            self.set_cves_for_errata(errata_map)
            self.set_packages_for_errata(errata_map)
            self.set_references_for_errata(errata_map)

        response["errata_list"] = response_dict
        return response
