"""
Module contains functions for returning last-modified data from the DB
"""

from vmaas.common.webapp_utils import format_datetime


class DBChange:
    """ Main /dbchange API class. """

    def __init__(self, cache):
        self.cache = cache

    def process(self):
        """
        This method returns details of last-processed-time from the VMaaS DB

        :returns: dictionary of errata_changes/cve_changes/repository_changes/last_change timestamps

        """
        answer = {}
        for key, value in self.cache.dbchange.items():
            answer[key] = format_datetime(value)

        return answer
