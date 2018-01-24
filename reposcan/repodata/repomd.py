import xml.etree.ElementTree as eT

NS = {"repo": "http://linux.duke.edu/metadata/repo"}


class RepoMDTypeNotFound(Exception):
    """Raised when certain data type was not parsed from repomd file.  
    """
    pass


class RepoMD:
    def __init__(self, filename):
        tree = eT.parse(filename)
        root = tree.getroot()
        self.data = {}
        for child in root.findall("repo:data", NS):
            data_type = child.get("type")
            location = child.find("repo:location", NS).get("href")
            size = int(child.find("repo:size", NS).text)
            checksum_type = child.find("repo:checksum", NS).get("type")
            checksum = child.find("repo:checksum", NS).text
            self.data[data_type] = {"location": location, "size": size,
                                    "checksum_type": checksum_type, "checksum": checksum}

    def get_metadata(self, data_type):
        if data_type not in self.data:
            raise RepoMDTypeNotFound(data_type)
        return self.data[data_type]
