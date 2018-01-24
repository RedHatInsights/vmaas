import xml.etree.ElementTree as eT

NS = {"primary": "http://linux.duke.edu/metadata/common"}


class PrimaryMD:
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
                    package["name"] = elem.find("primary:name", NS).text
                    evr = elem.find("primary:version", NS)
                    package["epoch"] = evr.get("epoch")
                    package["ver"] = evr.get("ver")
                    package["rel"] = evr.get("rel")
                    package["arch"] = elem.find("primary:arch", NS).text
                    checksum = elem.find("primary:checksum", NS)
                    package["checksum_type"] = checksum.get("type")
                    package["checksum"] = checksum.text
                    self.packages.append(package)
                    # Clear the XML tree continuously
                    root.clear()

    def get_package_count(self):
        return self.package_count

    def list_packages(self):
        return self.packages
