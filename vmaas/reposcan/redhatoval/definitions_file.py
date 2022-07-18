"""
Parse informations from OVAL definitions file.
"""
import xml.etree.ElementTree as eT

from vmaas.common.logging_utils import get_logger
from vmaas.common.string import text_strip, get_attr

NS = {"default": "http://oval.mitre.org/XMLSchema/oval-definitions-5",
      "ind-def": "http://oval.mitre.org/XMLSchema/oval-definitions-5#independent",
      "unix-def": "http://oval.mitre.org/XMLSchema/oval-definitions-5#unix",
      "red-def": "http://oval.mitre.org/XMLSchema/oval-definitions-5#linux"}

DEFAULT_CHECK_EXISTENCE = "at_least_one_exists"

UNSUPPORTED_TESTS = {
    "{%s}rpmverifyfile_test" % NS['red-def'],
    "{%s}uname_test" % NS['unix-def'],
}

UNSUPPORTED_TEST_CHILDS = {}

UNSUPPORTED_TEST_COMMENTS = {
    "kernel"
}

UNSUPPORTED_OBJECTS = {
    "{%s}rpmverifyfile_object" % NS['red-def'],
    "{%s}textfilecontent54_object" % NS['ind-def'],
    "{%s}uname_object" % NS['unix-def'],
}

UNSUPPORTED_OBJECT_CHILDS = {}

UNSUPPORTED_STATES = {
    "{%s}rpmverifyfile_state" % NS['red-def'],
    "{%s}textfilecontent54_state" % NS['ind-def'],
    "{%s}uname_state" % NS['unix-def'],
}

UNSUPPORTED_STATE_CHILDS = {
    "{%s}signature_keyid" % NS['red-def'],
}


class OvalDefinitions:
    """Class parsing OVAL definitions file."""
    # pylint: disable=too-many-instance-attributes

    def __init__(self, oval_id, updated, url, local_path):
        self.logger = get_logger(__name__)
        self.oval_id = oval_id
        self.updated = updated
        self.url = url
        self.local_path = local_path
        self.root = None

        self.definitions = []
        self.tests = []
        self.module_tests = []
        self.objects = []
        self.states = []

    def _xfind(self, tag):
        """Helper method to return empty list if tag is not found."""
        if not self.root:
            return []
        elem = self.root.find(tag, NS)
        return elem if elem is not None else []

    def _parse_criteria(self, criteria):
        if criteria is None:
            return None
        criteria_obj = {"operator": criteria.get("operator"), "criterions": [], "criteria": []}
        for child in criteria:
            if child.tag == "{%s}criteria" % NS['default']:  # <criteria>
                criteria_obj["criteria"].append(self._parse_criteria(child))
            elif child.tag == "{%s}criterion" % NS['default']:  # <criterion>
                criteria_obj["criterions"].append(child.get("test_ref"))
            else:
                self.logger.warning("Unknown tag: %s", child.tag)

        return criteria_obj

    def _parse_definitions(self):
        # pylint: disable=too-many-nested-blocks, too-many-branches
        for definition in self._xfind("default:definitions"):  # <definitions>
            if definition.tag == "{%s}definition" % NS['default']:  # <definition>
                cves = []
                advisories = []
                cpes = []
                metadata = definition.find("default:metadata", NS)
                if metadata is not None:
                    for child in metadata.findall("default:reference", NS):
                        if child.get("source") == "CVE":
                            cves.append(child.get("ref_id"))
                        elif child.get("source") == "RHSA":
                            advisories.append(child.get("ref_id"))
                        else:
                            self.logger.warning("Unknown reference source: %s", child.get("source"))

                    advisory = metadata.find("default:advisory", NS)
                    if advisory is not None:
                        affected_cpe_list = advisory.find("default:affected_cpe_list", NS)
                        if affected_cpe_list is not None:
                            for child in affected_cpe_list.findall("default:cpe", NS):
                                cpes.append(text_strip(child))
                criteria = self._parse_criteria(definition.find("default:criteria", NS))  # <criteria> 0..1

                # Parse tests
                tests = []
                crit = criteria
                criteria_stack = []
                while crit is not None:
                    tests.extend(crit["criterions"])
                    criteria_stack.extend(crit["criteria"])
                    if criteria_stack:
                        crit = criteria_stack.pop()
                    else:
                        crit = None

                self.definitions.append({"id": definition.get("id"),
                                         "type": definition.get("class"),
                                         "cves": cves,
                                         "advisories": advisories,
                                         "cpes": cpes,
                                         "criteria": criteria,
                                         "tests": tests,
                                         "version": int(definition.get("version"))})
            else:  # Other unparsed tags
                self.logger.warning("Unknown definition: %s", definition.tag)

    def _parse_tests(self):
        # pylint: disable=too-many-branches
        for test in self._xfind("default:tests"):  # <tests>
            if test.tag == "{%s}rpminfo_test" % NS['red-def']:  # <red-def:rpminfo_test>
                obj = None
                states = []
                for child in test:
                    if child.tag == "{%s}object" % NS['red-def']:  # <red-def:object> 1..1
                        obj = child
                    elif child.tag == "{%s}state" % NS['red-def']:  # <red-def:state> 0..n
                        states.append(child)
                    elif child.tag in UNSUPPORTED_TEST_CHILDS:  # Not supported, skip
                        pass
                    else:  # Other unparsed tags
                        self.logger.warning("Unknown tag: %s", child.tag)
                self.tests.append({"id": test.get("id"),
                                   "object": get_attr(obj, "object_ref"),
                                   "states": [get_attr(state, "state_ref") for state in states],
                                   "check": test.get("check"),
                                   "check_existence": test.get("check_existence", DEFAULT_CHECK_EXISTENCE),
                                   "version": int(test.get("version"))})
            elif test.tag == "{%s}textfilecontent54_test" % NS['ind-def']:  # <ind-def:textfilecontent54_test>
                # Can't use <ind-def:textfilecontent54_test>, parse required module from comment,
                # not optimal, but better than parsing <ind-def:textfilecontent54_state> regex
                comment = test.get("comment", "")
                parts = comment.split()
                if parts and parts[0] == "Module" and parts[-1] == "enabled":
                    self.module_tests.append({"id": test.get("id"),
                                              "module_stream": parts[1],
                                              "version": int(test.get("version"))})
                elif comment.startswith(tuple(UNSUPPORTED_TEST_COMMENTS)):  # Not supported, skip
                    pass
                else:
                    self.logger.warning("Unknown <ind-def:textfilecontent54_test> comment: %s", test.get("comment"))
            elif test.tag in UNSUPPORTED_TESTS:  # Not supported, skip
                pass
            else:  # Other unparsed tags
                self.logger.warning("Unknown test: %s", test.tag)

    def _parse_objects(self):
        for obj in self._xfind("default:objects"):  # <objects>
            if obj.tag == "{%s}rpminfo_object" % NS['red-def']:  # <red-def:rpminfo_object>
                name = None
                for child in obj:
                    if child.tag == "{%s}name" % NS['red-def']:  # <red-def:name> 1..1
                        name = child
                    elif child.tag in UNSUPPORTED_OBJECT_CHILDS:  # Not supported, skip
                        pass
                    else:  # Other unparsed tags
                        self.logger.warning("Unknown tag: %s", child.tag)
                self.objects.append({"id": obj.get("id"),
                                     "name": text_strip(name),
                                     "version": int(obj.get("version"))})
            elif obj.tag in UNSUPPORTED_OBJECTS:  # Not supported, skip
                pass
            else:  # Other unparsed tags
                self.logger.warning("Unknown object: %s", obj.tag)

    def _parse_states(self):
        for state in self._xfind("default:states"):  # <states>
            if state.tag == "{%s}rpminfo_state" % NS['red-def']:  # <red-def:rpminfo_state>
                evr = arch = None
                for child in state:
                    if child.tag == "{%s}evr" % NS['red-def']:  # <red-def:evr> 0..1
                        evr = child
                    elif child.tag == "{%s}arch" % NS['red-def']:  # <red-def:arch> 0..1
                        arch = child
                    elif child.tag in UNSUPPORTED_STATE_CHILDS:  # Not supported, skip
                        pass
                    else:  # Other unparsed tags
                        self.logger.warning("Unknown tag: %s", child.tag)
                self.states.append({"id": state.get("id"),
                                    "evr": text_strip(evr),
                                    "evr_operation": get_attr(evr, "operation"),
                                    "arch": text_strip(arch),
                                    "arch_operation": get_attr(arch, "operation"),
                                    "version": int(state.get("version"))})
            elif state.tag in UNSUPPORTED_STATES:  # Not supported, skip
                pass
            else:  # Other unparsed tags
                self.logger.warning("Unknown state: %s", state.tag)

    def load_metadata(self):
        """Parse available metadata files into memory."""
        self.root = eT.parse(self.local_path).getroot()  # <oval_definitions>

        self._parse_definitions()
        self._parse_tests()
        self._parse_objects()
        self._parse_states()

    def unload_metadata(self):
        """Unset previously loaded metadata files from this object."""
        self.definitions = []
        self.tests = []
        self.objects = []
        self.states = []
        self.root = None
