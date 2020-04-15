"""
Module to handle /patches API calls.
"""

#from cache import ERRATA_CVE


class PatchesAPI:
    """Main /patches API class"""

    def __init__(self, db_cache, updates_api):
        self.db_cache = db_cache
        self.updates_api = updates_api

    def process_list(self, api_version, data):  # pylint: disable=unused-argument
        """Return list of potential security issues"""
        updates = self.updates_api.process_list(2, data)
        errata_list = set()
        for package in updates['update_list']:
            for update in updates['update_list'][package].get('available_updates', []):
                errata_list.add(update['erratum'])
        return {'errata_list': list(errata_list)}
