"""
Module containing class for UpdateInfo XML metadata.
"""
# pylint: disable=too-many-nested-blocks, too-many-branches
# I really don't want to do that but, the way how updateinfo XML is done it's unfortuntately needed
from datetime import datetime
from distutils.util import strtobool
import re
import xml.etree.ElementTree as eT

from vmaas.common.string import text_strip
from vmaas.common.utc import UTC

DATETIME_PATTERNS = {
    "%Y-%m-%d %H:%M:%S": re.compile(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$"),
    "%Y-%m-%d %H:%M:%S UTC": re.compile(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} UTC$"),
    "%Y-%m-%d": re.compile(r"^\d{4}-\d{2}-\d{2}$"),
}


class UpdateInfoMD:
    """Class parsing UpdateInfo XML. Takes filename in the constructor."""
    def __init__(self, filename):
        self.updates = []
        root = None
        for event, elem in eT.iterparse(filename, events=("start", "end")):
            if elem.tag == "updates" and event == "start":
                root = elem
            elif elem.tag == "update" and event == "end":
                update = {}
                update["from"] = elem.get("from")
                update["status"] = elem.get("status")
                update["version"] = elem.get("version")
                update["type"] = elem.get("type")
                update["id"] = text_strip(elem.find("id"))
                update["title"] = text_strip(elem.find("title"))
                # Is the false here good choice ? Shouldn't the default be true ?
                update["reboot"] = False

                # Optional fields
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
                    update["references"].append({
                        "href": reference.get("href"),
                        "id": reference.get("id"),
                        "type": reference.get("type"),
                        "title": reference.get("title")
                    })

                pkglist = elem.find("pkglist")
                update["pkglist"] = []
                if pkglist is not None:
                    for collection in pkglist.findall("collection"):
                        module = collection.find("module")
                        for pkg in collection.findall("package"):
                            if strtobool(pkg.get("reboot_suggested", 'False')):
                                update["reboot"] = True

                            rec = self._process_package(pkg, module)
                            if rec not in update["pkglist"]:
                                update["pkglist"].append(rec)

                self.updates.append(update)
                # Clear the XML tree continuously
                root.clear()

    @staticmethod
    def _process_package(pkg, module):
        rec = {
            "name": pkg.get("name"),
            "epoch": pkg.get("epoch", "0"),
            "ver": pkg.get("version"),
            "rel": pkg.get("release"),
            "arch": pkg.get("arch")
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
