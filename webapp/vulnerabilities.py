"""
Module to handle /vulnerabilities API calls.
"""

from cache import ERRATA_CVE


class VulnerabilitiesAPI:
    """Main /vulnerabilities API class"""

    def __init__(self, db_cache, updates_api):
        self.db_cache = db_cache
        self.updates_api = updates_api

    def process_list(self, api_version, data):  # pylint: disable=unused-argument
        """Return list of potential security issues"""
        updates = self.updates_api.process_list(2, data)
        errata_list = set()
        cve_errata = {}
        for package in updates['update_list']:
            for update in updates['update_list'][package].get('available_updates', []):
                errata_list.add(update['erratum'])
        for errata in errata_list:
            for cve in self.db_cache.errata_detail[errata][ERRATA_CVE]:
                cve_errata.setdefault(cve, set()).add(errata)
        cv_er = {cve: list(er) for cve, er in cve_errata.items()}
        return {'cve_list': cv_er}
