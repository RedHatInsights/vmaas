"""
Module to handle /vulnerabilities API calls.
"""

from cache import ERRATA_CVE
from updates import UpdatesAPI


class VulnerabilitiesAPI:
    """Main /vulnerabilities API class"""

    def __init__(self, db_cache):
        self.db_cache = db_cache

    def process_list(self, api_version, data):  # pylint: disable=unused-argument
        """Return list of potential security issues"""
        updates = UpdatesAPI(self.db_cache).process_list(2, data)
        errata_list = set()
        cve_list = set()
        for package in updates['update_list']:
            for update in updates['update_list'][package].get('available_updates', []):
                errata_list.add(update['erratum'])
        for errata in errata_list:
            cve_list.update(self.db_cache.errata_detail[errata][ERRATA_CVE])
        return {'cve_list': list(cve_list)}
