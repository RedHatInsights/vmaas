"""
Module to handle /vulnerabilities API calls.
"""

from vmaas.webapp.cache import ERRATA_CVE
from vmaas.webapp.repos import REPO_PREFIXES
from vmaas.common.webapp_utils import format_datetime, strip_prefixes


class VulnerabilitiesAPI:
    """Main /vulnerabilities API class"""

    def __init__(self, db_cache, updates_api):
        self.db_cache = db_cache
        self.updates_api = updates_api

    @staticmethod
    def _serialize_dict(input_dict, extended=False):
        return [{k: list(v) if isinstance(v, set) else v for k, v in cve.items()} for cve in input_dict.values()] \
            if extended else list(input_dict.keys())

    # pylint: disable=unused-argument,too-many-branches,too-many-nested-blocks
    def process_list(self, api_version, data):
        """Return list of potential security issues"""
        strip_prefixes(data, REPO_PREFIXES)
        extended = data.get("extended", False)
        cve_dict = {}
        manually_fixable_cve_dict = {}
        unpatched_cve_dict = {}

        # Repositories
        updates = self.updates_api.process_list(api_version, data)
        for package in updates['update_list']:
            for update in updates['update_list'][package].get('available_updates', []):
                for cve in self.db_cache.errata_detail[update['erratum']][ERRATA_CVE]:
                    if cve not in unpatched_cve_dict:  # Skip CVEs found as unpatched
                        cve_dict.setdefault(cve, {})["cve"] = cve
                        cve_dict[cve].setdefault("affected_packages", set()).add(package)
                        cve_dict[cve].setdefault("errata", set()).add(update['erratum'])

        return {'cve_list': self._serialize_dict(cve_dict, extended=extended),
                'manually_fixable_cve_list': self._serialize_dict(manually_fixable_cve_dict, extended=extended),
                'unpatched_cve_list': self._serialize_dict(unpatched_cve_dict, extended=extended),
                'last_change': format_datetime(self.db_cache.dbchange['last_change'])}
