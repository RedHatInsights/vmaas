"""
Parse informations from CPE dict XML.
"""

import xml.etree.ElementTree as eT

from common.dateutil import parse_datetime
from common.string import text_strip

NS = {'cpe': 'http://cpe.mitre.org/dictionary/2.0'}


class CpeDict:
    """Class parsing CPE dict. Takes filename in the constructor."""
    def __init__(self, filename):
        self.lastmodified = None
        self.cpes = {}
        root = None
        for event, elem in eT.iterparse(filename, events=("start", "end")):
            if elem.tag == "{%s}cpe-list" % NS["cpe"] and event == "start":
                root = elem
            elif elem.tag == "{%s}generator" % NS["cpe"] and event == "end":
                self.lastmodified = parse_datetime(text_strip(elem.find('cpe:timestamp', NS)))
            elif elem.tag == "{%s}cpe-item" % NS["cpe"] and event == "end":
                name = elem.get('name')
                self.cpes[name] = text_strip(elem.find('cpe:title', NS))

                # Clear the XML tree continuously
                root.clear()
