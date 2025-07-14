"""
Module to handle /patches API calls.
"""

from vmaas.common.webapp_utils import format_datetime


class PatchesAPI:
    """Main /patches API class"""

    def __init__(self, db_cache, updates_api):
        self.db_cache = db_cache
        self.updates_api = updates_api

    def process_list(self, api_version, data):  # pylint: disable=unused-argument
        """Return list of potential security issues"""
        data['security_only'] = False
        updates = self.updates_api.process_list(3, data)
        errata_list = set()
        for package in updates['update_list']:
            for update in updates['update_list'][package].get('available_updates', []):
                errata_list.add(update['erratum'])
        return {'errata_list': list(errata_list),
                'last_change': format_datetime(self.db_cache.dbchange['last_change'])}
