"""
Module containing class for Primary XML metadata.
"""

import xml.etree.ElementTree as eT

from common.string import strip

NS = {"primary": "http://linux.duke.edu/metadata/common"}


class PrimaryMD:
    """Class parsing Primary XML. Takes filename in the constructor."""
    def __init__(self, filename):
        self.package_count = 0
        self.packages = []
        root = None
        for event, elem in eT.iterparse(filename, events=("start", "end")):
            if elem.tag == "{%s}metadata" % NS["primary"] and event == "start":
                root = elem
                self.package_count = int(elem.get("packages"))
            elif elem.tag == "{%s}package" % NS["primary"] and event == "end":
                if elem.get("type") == "rpm":
                    package = {}
                    package["name"] = strip(elem.find("primary:name", NS).text)
                    evr = elem.find("primary:version", NS)
                    package["epoch"] = evr.get("epoch")
                    package["ver"] = evr.get("ver")
                    package["rel"] = evr.get("rel")
                    package["arch"] = strip(elem.find("primary:arch", NS).text)
                    package["summary"] = strip(elem.find("primary:summary", NS).text)
                    package["description"] = strip(elem.find("primary:description", NS).text)
                    checksum = elem.find("primary:checksum", NS)
                    package["checksum_type"] = checksum.get("type")
                    package["checksum"] = strip(checksum.text)
                    self.packages.append(package)
                    # Clear the XML tree continuously
                    root.clear()

    def get_package_count(self):
        """Returns count of packages in Primary file."""
        return self.package_count

    def list_packages(self):
        """Returns list of parsed packages (list of dictionaries)."""
        return self.packages
