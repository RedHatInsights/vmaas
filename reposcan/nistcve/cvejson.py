"""
Parse data from NIST CVE json format.
"""

import json


class CveJson:
    """
    Class for parsing NIST CVE json format.
    """
    def __init__(self, filename):
        self.data = []
        with open(filename, 'r', encoding='utf-8') as fde:
            self.data = json.load(fde)

    def get_count(self):
        """Number of CVEs in json."""
        return int(self.data['CVE_data_numberOfCVEs'])

    def list_cves(self):
        """List of CVEs in json."""
        return self.data['CVE_Items']
