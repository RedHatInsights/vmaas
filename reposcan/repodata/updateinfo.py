"""
Module containing class for UpdateInfo XML metadata.
"""
import xml.etree.ElementTree as eT


class UpdateInfoMD: # pylint: disable=too-few-public-methods
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
                update["id"] = elem.find("id").text.strip()
                update["title"] = elem.find("title").text.strip()

                # Optional fields
                text_elements = ["summary", "rights", "description", "release", "solution", "severity"]
                date_elements = ["issued", "updated"]
                for field in text_elements + date_elements:
                    found = elem.find(field)
                    if found is not None and field in text_elements:
                        update[field] = found.text.strip()
                    elif found is not None and field in date_elements:
                        update[field] = found.get("date")
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
                for pkg in pkglist.find("collection").findall("package"):
                    update["pkglist"].append({
                        "name": pkg.get("name"),
                        "epoch": pkg.get("epoch"),
                        "ver": pkg.get("version"),
                        "rel": pkg.get("release"),
                        "arch": pkg.get("arch")
                    })

                self.updates.append(update)
                # Clear the XML tree continuously
                root.clear()

    def list_updates(self):
        """Returns list of parsed updates (list of dictionaries)."""
        return self.updates
