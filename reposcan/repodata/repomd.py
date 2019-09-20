"""
Module containing class for Repo XML metadata.
"""
from datetime import datetime
import xml.etree.ElementTree as eT

from common.string import text_strip
from common.utc import UTC

NS = {"repo": "http://linux.duke.edu/metadata/repo"}


class RepoMDTypeNotFound(Exception):
    """Raised when certain data type was not parsed from repomd file."""


class RepoMD:
    """Class parsing Repo XML. Takes filename in the constructor."""
    def __init__(self, filename):
        tree = eT.parse(filename)
        root = tree.getroot()
        revision = root.find("repo:revision", NS)
        if revision is not None:
            revision = int(text_strip(revision))
        else:
            revision = 0
        self.revision = datetime.fromtimestamp(revision, tz=UTC)
        self.data = {}
        for child in root.findall("repo:data", NS):
            data_type = child.get("type")
            location = child.find("repo:location", NS).get("href")
            checksum_type = child.find("repo:checksum", NS).get("type")
            checksum = text_strip(child.find("repo:checksum", NS))
            size = child.find("repo:size", NS)
            open_size = child.find("repo:open-size", NS)

            self.data[data_type] = {
                "location": location,
                "checksum_type": checksum_type,
                "checksum": checksum,
            }

            if size:
                self.data[data_type]["size"] = int(size.text)
            if open_size:
                self.data[data_type]["open-size"] = int(open_size.text)

    def get_revision(self):
        """Returns revision field of parsed repomd file. This is in format of Unix timestamp."""
        return self.revision

    def get_metadata(self, data_type):
        """Returns info about given metadata type available in repository. E.g. primary, updateinfo etc."""
        if data_type not in self.data:
            raise RepoMDTypeNotFound(data_type)
        return self.data[data_type]
