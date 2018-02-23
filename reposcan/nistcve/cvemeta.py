"""
Parse informations from NIST CVE meta file.
"""

class CveMeta:
    """
    Class for parsing NIST CVE meta file.
    """
    def __init__(self, filename):
        self.data = {}
        with open(filename, 'r') as fde:
            for line in fde.readlines():
                key, val = line.strip().split(':', 1)
                self.data[key] = val

    def get_lastmodified(self):
        """Lastmodified time of CVE list."""
        return self.data.get('lastModifiedDate', None)

    def get_sha256(self):
        """Checksum of CVE list."""
        return self.data.get('sha256', None)
