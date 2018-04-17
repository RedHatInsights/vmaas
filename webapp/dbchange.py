"""
Module contains functions for returning last-modified data from the DB
"""

from utils import format_datetime

class DBChange(object):
    """ Main /dbchange API class. """
    # pylint: disable=too-few-public-methods
    def __init__(self, database):
        self.cursor = database.dictcursor()

    def process(self):
        """
        This method returns details of last-processed-time from the VMaaS DB

        :returns: dictionary of errata_changes/cve_changes/repository_changes/last_change timestamps

        """
        query = 'SELECT * from dbchange'
        self.cursor.execute(query)
        updates = self.cursor.fetchall()

        answer = {}
        for row in updates:
            for key, value in row.items():
                answer[key] = format_datetime(value)

        return answer
