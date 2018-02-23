"""
Module aggregating CVE list metadata.
"""

import os.path

from cli.logger import SimpleLogger
from nistcve.cvejson import CveJson

API_VERSION = '1.0'
URL = 'https://static.nvd.nist.gov/feeds/json/cve/{apiver}/nvdcve-{apiver}-{label}.{ext}'

class CveRepo:
    """
    Class aggregating CVE list metadata.
    """
    def __init__(self, label):
        self.logger = SimpleLogger()
        self.label = label
        self.meta = None
        self.json = None
        self.tmp_directory = None

    def get_count(self):
        """Nomber of CVEs in the list."""
        if self.json:
            return self.json.get_count()
        return 0

    def list_cves(self):
        """List of associated CVEs."""
        if self.json:
            return self.json.list_cves()
        return []

    def load_json(self):
        """Parse CVE json into memmory."""
        self.json = CveJson(self.json_tmp())

    def unload_json(self):
        """Free memory taken by json data."""
        self.json = None

    def meta_url(self):
        """Format URL of meta file."""
        return URL.format(apiver=API_VERSION, label=self.label, ext='meta')

    def json_url(self):
        """Format URL of json file."""
        return URL.format(apiver=API_VERSION, label=self.label, ext='json.gz')

    def meta_tmp(self):
        """Local path to cached meta file."""
        return os.path.join(self.tmp_directory, 'data.meta')

    def json_tmp(self):
        """Local path to cached uncompressed json file."""
        return os.path.join(self.tmp_directory, 'data.json')

    def json_tmpgz(self):
        """Local path to cached compressed json file."""
        return os.path.join(self.tmp_directory, 'data.json.gz')
