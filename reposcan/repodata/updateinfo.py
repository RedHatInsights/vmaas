"""
Module containing class for UpdateInfo XML metadata.
"""
import xml.etree.ElementTree as eT


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
                update["id"] = elem.find("id").text.strip()
                update["title"] = elem.find("title").text.strip()

                # Optional fields
                summary = elem.find("summary")
                if summary is not None:
                    update["summary"] = summary.text.strip()
                else:
                    update["summary"] = None

                rights = elem.find("rights")
                if rights is not None:
                    update["rights"] = rights.text.strip()
                else:
                    update["rights"] = None

                description = elem.find("description")
                if description is not None:
                    update["description"] = description.text.strip()
                else:
                    update["description"] = None

                issued = elem.find("issued")
                if issued is not None:
                    update["issued"] = issued.get("date")
                else:
                    update["issued"] = None

                updated = elem.find("updated")
                if updated is not None:
                    update["updated"] = updated.get("date")
                else:
                    update["updated"] = None

                release = elem.find("release")
                if release is not None:
                    update["release"] = release.text.strip()
                else:
                    update["release"] = None

                solution = elem.find("solution")
                if solution is not None:
                    update["solution"] = solution.text.strip()
                else:
                    update["solution"] = None

                severity = elem.find("severity")
                if severity is not None:
                    update["severity"] = severity.text.strip()
                else:
                    update["severity"] = None

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
