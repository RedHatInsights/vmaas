"""
Module containing class for UpdateInfo XML metadata.
"""
# pylint: disable=too-many-nested-blocks, too-many-branches
# I really don't want to do that but, the way how updateinfo XML is done it's unfortuntately needed
from datetime import datetime
import re
import xml.etree.ElementTree as eT

from vmaas.common.string import text_strip
from vmaas.common.utc import UTC
from vmaas.common.strtobool import strtobool
from vmaas.common.logging_utils import get_logger
from vmaas.reposcan.repodata.metadata_validators import validate_field, ValidationError
from vmaas.reposcan.mnm import VALIDATION_FAILED_ITEMS, VALIDATION_TOTAL_ITEMS

DATETIME_PATTERNS = {
    "%Y-%m-%d %H:%M:%S": re.compile(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$"),
    "%Y-%m-%d %H:%M:%S UTC": re.compile(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} UTC$"),
    "%Y-%m-%d": re.compile(r"^\d{4}-\d{2}-\d{2}$"),
}


class UpdateInfoMD:
    """Class parsing UpdateInfo XML. Takes filename in the constructor."""

    def __init__(self, filename):
        self.logger = get_logger(__name__)
        self.updates = []
        root = None
        for event, elem in eT.iterparse(filename, events=("start", "end")):
            if elem.tag == "updates" and event == "start":
                root = elem
            elif elem.tag == "update" and event == "end":
                VALIDATION_TOTAL_ITEMS.labels(metadata_type='updateinfo').inc()
                try:
                    update = self._parse_update(elem)
                    self.updates.append(update)
                except ValidationError as err:
                    self.logger.warning("Validation failed, skipped: %s", str(err))
                # Clear the XML tree continuously
                root.clear()

    def _validate(self, value, field_type):
        """Validate a field and track metrics on failure."""
        try:
            return validate_field(value, field_type)
        except ValidationError:
            VALIDATION_FAILED_ITEMS.labels(metadata_type='updateinfo', field=field_type).inc()
            raise

    def _parse_update(self, elem):
        """Parse and validate a single update/errata element.

        Errata header and text fields are stored as-is. Validation is applied to
        pkglist NEVRA (package matching) and reference ids by type (cve, bugzilla).
        ValidationError from those checks propagates to the caller.
        """
        update = {
            "from": elem.get("from"),
            "status": elem.get("status"),
            "version": elem.get("version"),
            "type": elem.get("type"),
            "id": text_strip(elem.find("id")),
            "title": text_strip(elem.find("title")),
            "reboot": self._parse_reboot_suggested(elem),
        }

        # Optional fields - store as-is, no validation
        text_elements = ["summary", "rights", "description", "release", "solution", "severity"]
        date_elements = ["issued", "updated"]
        for field in text_elements + date_elements:
            found = elem.find(field)
            if found is not None and field in text_elements:
                content = text_strip(found)
                update[field] = content if content else None
            elif found is not None and field in date_elements:
                update[field] = self._get_dt(found.get("date"))
            else:
                update[field] = None

        references = elem.find("references")
        update["references"] = []
        for reference in references.findall("reference"):
            update["references"].append(self._parse_reference(reference))

        pkglist = elem.find("pkglist")
        update["pkglist"] = []
        if pkglist is not None:
            for collection in pkglist.findall("collection"):
                module = collection.find("module")
                for pkg in collection.findall("package"):
                    rec = self._process_package(pkg, module)
                    if rec not in update["pkglist"]:
                        update["pkglist"].append(rec)

        return update

    def _parse_reference(self, reference):
        """Parse a reference; validate id by reference type."""
        ref_id = reference.get("id")
        ref_type = reference.get("type")

        if ref_type == "cve":
            ref_id = self._validate(ref_id, 'cve_id')
        elif ref_type == "bugzilla":
            ref_id = self._validate(ref_id, 'bugzilla_id')

        return {
            "href": reference.get("href"),
            "id": ref_id,
            "type": ref_type,
            "title": reference.get("title")
        }

    @staticmethod
    def _parse_reboot_suggested(elem) -> bool:
        """Try to parse bool from <reboot_suggested> tag. Return False by default."""
        found = elem.find("reboot_suggested")
        if found is None:
            return False
        parsed = text_strip(found)
        parsed_bool = bool(strtobool(parsed))  # strtobool returns 1 or 0, we need bool type
        return parsed_bool

    def _process_package(self, pkg, module):
        """Parse and validate pkglist entry NEVRA used for package matching."""
        rec = {
            "name": self._validate(pkg.get("name"), 'name'),
            "epoch": pkg.get("epoch", "0"),
            "ver": self._validate(pkg.get("version"), 'version'),
            "rel": self._validate(pkg.get("release"), 'release'),
            "arch": self._validate(pkg.get("arch"), 'arch')
        }
        if module is not None:
            rec["module_name"] = module.get("name")
            rec["module_stream"] = module.get("stream")
            rec["module_version"] = int(module.get("version"))
            rec["module_context"] = module.get("context")
            rec["module_arch"] = module.get("arch")
        return rec

    @staticmethod
    def _get_dt(str_value):
        for datetime_format, pattern in DATETIME_PATTERNS.items():
            if pattern.match(str_value):
                return datetime.strptime(str_value, datetime_format).replace(tzinfo=UTC)
        raise ValueError("Unknown datetime format: %s" % str_value)

    def list_updates(self):
        """Returns list of parsed updates (list of dictionaries)."""
        return self.updates
