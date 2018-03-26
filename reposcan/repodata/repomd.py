"""
Module containing class for Repo XML metadata.
"""
from datetime import datetime
import xml.etree.ElementTree as eT

from common.utc import UTC

NS = {"repo": "http://linux.duke.edu/metadata/repo"}


class RepoMDTypeNotFound(Exception):
    """Raised when certain data type was not parsed from repomd file."""
    pass


class RepoMD:
    """Class parsing Repo XML. Takes filename in the constructor."""
    def __init__(self, filename):
        tree = eT.parse(filename)
        root = tree.getroot()
        self.revision = datetime.fromtimestamp(int(root.find("repo:revision", NS).text.strip()), tz=UTC)
        self.data = {}
        for child in root.findall("repo:data", NS):
            data_type = child.get("type")
            location = child.find("repo:location", NS).get("href")
            size = int(child.find("repo:size", NS).text.strip())
            checksum_type = child.find("repo:checksum", NS).get("type")
            checksum = child.find("repo:checksum", NS).text.strip()
            self.data[data_type] = {"location": location, "size": size,
                                    "checksum_type": checksum_type, "checksum": checksum}

    def get_revision(self):
        """Returns revision field of parsed repomd file. This is in format of Unix timestamp."""
        return self.revision

    def get_metadata(self, data_type):
        """Returns info about given metadata type available in repository. E.g. primary, updateinfo etc."""
        if data_type not in self.data:
            raise RepoMDTypeNotFound(data_type)
        return self.data[data_type]
