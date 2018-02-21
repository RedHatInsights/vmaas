import json


class CveJson:
    def __init__(self, filename):
        self.data = []
        with open(filename, 'r') as fde:
            self.data = json.load(fde)

    def get_count(self):
        return int(self.data['CVE_data_numberOfCVEs'])

    def list_cves(self):
        return self.data['CVE_Items']
