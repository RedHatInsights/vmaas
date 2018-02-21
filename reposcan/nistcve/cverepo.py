import os.path

from cli.logger import SimpleLogger
from nistcve.cvejson import CveJson

API_VERSION = '1.0'
URL = 'https://static.nvd.nist.gov/feeds/json/cve/{apiver}/nvdcve-{apiver}-{label}.{ext}'

class CveRepo:
    def __init__(self, label):
        self.logger = SimpleLogger()
        self.label = label
        self.meta = None
        self.json = None
        self.tmp_directory = None

    def get_count(self):
        if self.json:
            return self.json.get_count()
        return 0

    def list_cves(self):
        if self.json:
            return self.json.list_cves()
        return []

    def load_json(self):
        self.json = CveJson(self.json_tmp())

    def unload_json(self):
        self.json = None

    def meta_url(self):
        return URL.format(apiver=API_VERSION, label=self.label, ext='meta')

    def json_url(self):
        return URL.format(apiver=API_VERSION, label=self.label, ext='json.gz')

    def meta_tmp(self):
        return os.path.join(self.tmp_directory, 'data.meta')

    def json_tmp(self):
        return os.path.join(self.tmp_directory, 'data.json')

    def json_tmpgz(self):
        return os.path.join(self.tmp_directory, 'data.json.gz')
