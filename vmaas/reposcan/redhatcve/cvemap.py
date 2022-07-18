"""
Parse informations from CVE map response.
"""

import xml.etree.ElementTree as eT
import re

from vmaas.common.date_utils import parse_datetime
from vmaas.common.string import text_strip

NS = 'http://www.w3.org/XML/1998/namespace'
CWE_RE = re.compile(r'CWE-\d+')


class CvemapHead:
    """
    Class for parsing CVE map headers.
    """

    def __init__(self, filename):
        self.data = {}
        with open(filename, 'r', encoding='utf8') as fde:
            for line in fde.readlines():
                key, val = line.strip().split(':', 1)
                self.data[key] = val

    def get_header(self, header):
        """Value of given header."""
        return self.data.get(header, None)

    def get_lastmodified(self):
        """Lastmodified time of CVE map."""
        return self.get_header('Last-Modified')


class CvemapBody:
    """Class parsing CVE map. Takes filename in the constructor."""

    def __init__(self, filename, lastmodified):
        self.lastmodified = lastmodified
        self.cves = {}
        root = None
        updated = None
        for event, elem in eT.iterparse(filename, events=("start", "end")):
            if elem.tag == "cvemap" and event == "start":
                root = elem
                updated = parse_datetime(elem.get('updated'))
            elif elem.tag == "Vulnerability" and event == "end":
                name = elem.get('name')
                self.cves[name] = {
                    'impact': text_strip(elem.find('ThreatSeverity')),
                    'published_date': parse_datetime(text_strip(elem.find('PublicDate'))),
                    'modified_date': updated,
                    'cvss2_score': text_strip(elem.find('CVSS/CVSSBaseScore')),
                    'cvss2_metrics': text_strip(elem.find('CVSS/CVSSScoringVector')),
                    'cvss3_score': text_strip(elem.find('CVSS3/CVSS3BaseScore')),
                    'cvss3_metrics': text_strip(elem.find('CVSS3/CVSS3ScoringVector')),
                    'cwe_list': self._cwe_list(text_strip(elem.find('CWE'))),
                    'description': self._cve_description(elem.findall('Details[@{%s}lang="en:us"]' % NS)),
                    'iava': text_strip(elem.find('IAVA')),
                    'redhat_url': "https://access.redhat.com/security/cve/" + str.lower(name),
                    'secondary_url': text_strip(elem.find('References'))
                }

                # Clear the XML tree continuously
                root.clear()

    @staticmethod
    def _cwe_list(cwe_text):
        cwe_names = CWE_RE.findall(cwe_text or '')

        def _link(name):
            return "http://cwe.mitre.org/data/definitions/%s.html" % name[4:]
        cwe_list = [dict(cwe_name=name, link=_link(name)) for name in cwe_names]
        return cwe_list

    @staticmethod
    def _cve_description(desc_elements):
        descriptions = {}
        description = None
        for det in desc_elements:
            source = det.get('source')
            descriptions[source] = text_strip(det)
        for source in ["Mitre", "Red Hat"]:
            desc = descriptions.get(source, None)
            if desc:
                description = desc
        return description

    def get_cve_count(self):
        """Returns count of CVEs in map."""
        return len(self.cves)

    def list_cves(self):
        """Returns list of parsed CVEs (list of dictionaries)."""
        return self.cves

    def get_lastmodified(self):
        """Lastmodified time of CVE map."""
        return self.lastmodified
