"""
Module containing class for Primary XML metadata.
"""


import xml.etree.ElementTree as eT
from vmaas.common.string import text_strip
from vmaas.common.logging_utils import get_logger
from vmaas.reposcan.repodata.metadata_validators import validate_field, ValidationError
from vmaas.reposcan.mnm import VALIDATION_FAILED_ITEMS, VALIDATION_TOTAL_ITEMS

NS = {"primary": "http://linux.duke.edu/metadata/common", "rpm": "http://linux.duke.edu/metadata/rpm"}


class PrimaryMD:
    """Class parsing Primary XML. Takes filename in the constructor."""

    def __init__(self, filename):
        self.logger = get_logger(__name__)
        self.package_count = 0
        self.packages = []
        root = None
        for event, elem in eT.iterparse(filename, events=("start", "end")):
            if elem.tag == "{%s}metadata" % NS["primary"] and event == "start":
                root = elem
                self.package_count = int(elem.get("packages"))
            elif elem.tag == "{%s}package" % NS["primary"] and event == "end":
                if elem.get("type") == "rpm":
                    VALIDATION_TOTAL_ITEMS.labels(metadata_type='primary').inc()
                    try:
                        package = self._parse_package(elem)
                        self.packages.append(package)
                    except ValidationError as err:
                        self.logger.warning("Validation failed, skipped package: %s", str(err))
                    # Clear the XML tree continuously
                    root.clear()

    def _validate(self, value, field_type):
        """Validate a field and track metrics on failure."""
        try:
            return validate_field(value, field_type)
        except ValidationError:
            VALIDATION_FAILED_ITEMS.labels(metadata_type='primary', field=field_type).inc()
            raise

    def _parse_package(self, elem):
        """Parse and validate a single package element."""
        # Parse raw values
        name_raw = text_strip(elem.find("primary:name", NS))
        evr = elem.find("primary:version", NS)
        arch_raw = text_strip(elem.find("primary:arch", NS))
        summary_raw = text_strip(elem.find("primary:summary", NS))
        description_raw = text_strip(elem.find("primary:description", NS))
        srpm_raw = elem.find("primary:format", NS).find("rpm:sourcerpm", NS).text

        # Validate and build package dict
        package = {
            "name": self._validate(name_raw, 'name'),
            "epoch": evr.get("epoch"),
            "ver": self._validate(evr.get("ver"), 'version'),
            "rel": self._validate(evr.get("rel"), 'release'),
            "arch": self._validate(arch_raw, 'arch'),
            "summary": summary_raw,
            "description": description_raw,
            "srpm": srpm_raw,
        }

        return package

    def get_package_count(self):
        """Returns count of packages in Primary file."""
        return self.package_count

    def list_packages(self):
        """Returns list of parsed packages (list of dictionaries)."""
        return self.packages
