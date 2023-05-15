"""
Module to handle /vulnerabilities API calls.
"""

from vmaas.webapp.cache import ERRATA_CVE, CFG, REPO_BASEARCH, REPO_RELEASEVER
from vmaas.webapp.repos import REPO_PREFIXES
from vmaas.common.rpm_utils import rpmver2array
from vmaas.common.webapp_utils import format_datetime, strip_prefixes

OVAL_OPERATION_EVR_EQUALS = 1
OVAL_OPERATION_EVR_LESS_THAN = 2

OVAL_CHECK_EXISTENCE_AT_LEAST_ONE = 1
OVAL_CHECK_EXISTENCE_NONE = 2

OVAL_DEFINITION_TYPE_PATCH = 1
OVAL_DEFINITION_TYPE_VULNERABILITY = 2

OVAL_CRITERIA_OPERATOR_AND = 1
OVAL_CRITERIA_OPERATOR_OR = 2


class VulnerabilitiesAPI:
    """Main /vulnerabilities API class"""

    def __init__(self, db_cache, updates_api):
        self.db_cache = db_cache
        self.updates_api = updates_api

    def _evaluate_state(self, state, epoch, ver, rel, arch):
        oval_state_id, evr_id, oval_operation_evr = state
        matched = False

        candidate_epoch, candidate_ver, candidate_rel = self.db_cache.id2evr[evr_id]
        if oval_operation_evr == OVAL_OPERATION_EVR_EQUALS:
            matched = epoch == candidate_epoch and ver == candidate_ver and rel == candidate_rel
        elif oval_operation_evr == OVAL_OPERATION_EVR_LESS_THAN:
            epoch = rpmver2array(epoch)
            candidate_epoch = rpmver2array(candidate_epoch)
            ver = rpmver2array(ver)
            candidate_ver = rpmver2array(candidate_ver)
            rel = rpmver2array(rel)
            candidate_rel = rpmver2array(candidate_rel)

            matched = ((epoch < candidate_epoch) or
                       (epoch == candidate_epoch and ver < candidate_ver) or
                       (epoch == candidate_epoch and ver == candidate_ver and rel < candidate_rel))
        else:
            raise ValueError("Unsupported oval_operation_evr: %s" % oval_operation_evr)

        candidate_arches = self.db_cache.ovalstate_id2arches.get(oval_state_id, [])
        if candidate_arches:
            if arch in self.db_cache.arch2id:
                matched = matched and self.db_cache.arch2id[arch] in candidate_arches
            else:
                raise ValueError("Invalid arch name: %s" % arch)

        # LOGGER.info("Evaluated state id=%s, candidate_evr_id=%s, operation=%s, matched=%s",
        #            oval_state_id, evr_id, oval_operation_evr, matched)
        return matched

    def _evaluate_module_test(self, module_test_id, modules_list):
        return self.db_cache.ovalmoduletest_detail[module_test_id] in modules_list

    def _evaluate_test(self, test_id, nevra):
        package_name_id, epoch, ver, rel, arch = nevra
        candidate_package_name_id, check_existence = self.db_cache.ovaltest_detail[test_id]

        matched = False
        package_name_matched = package_name_id == candidate_package_name_id
        if check_existence == OVAL_CHECK_EXISTENCE_AT_LEAST_ONE:
            states = self.db_cache.ovaltest_id2states.get(test_id, [])
            if package_name_matched and states:
                for state in states:
                    if self._evaluate_state(state, epoch, ver, rel, arch):
                        matched = True
                        break  # at least one
            else:
                matched = package_name_matched
        elif check_existence == OVAL_CHECK_EXISTENCE_NONE:
            matched = not package_name_matched
        else:
            raise ValueError("Unsupported check_existence: %s" % check_existence)

        # LOGGER.info("Evaluated test id=%s, package=%s, candidate_package=%s, check_existence=%s, matched=%s",
        #            test_id, package_name_id, candidate_package_name_id, check_existence, matched)
        return matched

    def _evaluate_criteria(self, criteria_id, nevra, modules_list):
        # pylint: disable=too-many-branches
        module_test_deps = self.db_cache.ovalcriteria_id2depmoduletest_ids.get(criteria_id, [])
        test_deps = self.db_cache.ovalcriteria_id2deptest_ids.get(criteria_id, [])
        criteria_deps = self.db_cache.ovalcriteria_id2depcriteria_ids.get(criteria_id, [])

        criteria_type = self.db_cache.ovalcriteria_id2type[criteria_id]
        if criteria_type == OVAL_CRITERIA_OPERATOR_AND:
            required_matches = len(module_test_deps) + len(test_deps) + len(criteria_deps)
            must_match = True
        elif criteria_type == OVAL_CRITERIA_OPERATOR_OR:
            required_matches = min(1, (len(module_test_deps) + len(test_deps) + len(criteria_deps)))
            must_match = False
        else:
            raise ValueError("Unsupported operator: %s" % criteria_type)

        matches = 0

        for module_test_id in module_test_deps:
            if matches >= required_matches:
                break
            if self._evaluate_module_test(module_test_id, modules_list):
                matches += 1
            elif must_match:  # AND
                break

        for test_id in test_deps:
            if matches >= required_matches:
                break
            if self._evaluate_test(test_id, nevra):
                matches += 1
            elif must_match:  # AND
                break

        for dep_criteria_id in criteria_deps:
            if matches >= required_matches:
                break
            if self._evaluate_criteria(dep_criteria_id, nevra, modules_list):
                matches += 1
            elif must_match:  # AND
                break

        # LOGGER.info("Evaluated criteria id=%s, type=%s, matched=%s", criteria_id, criteria_type,
        #            matches >= required_matches)
        return matches >= required_matches

    def _repos_to_definitions(self, content_set_list, basearch, releasever):  # pylint: disable=too-many-branches
        # TODO: some CPEs are not matching because they are substrings/subtrees
        if content_set_list is None:
            return set(), set()

        repo_ids = set()
        content_set_ids = set()
        # Try to identify repos (CS+basearch+releasever) or at least CS
        for label in content_set_list:
            if basearch or releasever:
                for repo_id in self.db_cache.repolabel2ids.get(label, []):
                    if basearch and self.db_cache.repo_detail[repo_id][REPO_BASEARCH] != basearch:
                        continue
                    if releasever and self.db_cache.repo_detail[repo_id][REPO_RELEASEVER] != releasever:
                        continue
                    repo_ids.add(repo_id)
            if label in self.db_cache.label2content_set_id:
                content_set_ids.add(self.db_cache.label2content_set_id[label])

        cpe_ids = set()
        if repo_ids:  # Check CPE-Repo mapping first
            for repo_id in repo_ids:
                if repo_id in self.db_cache.repo_id2cpe_ids:
                    cpe_ids.update(self.db_cache.repo_id2cpe_ids[repo_id])

        if not cpe_ids:  # No CPE-Repo mapping? Use CPE-CS mapping
            for content_set_id in content_set_ids:
                if content_set_id in self.db_cache.content_set_id2cpe_ids:
                    cpe_ids.update(self.db_cache.content_set_id2cpe_ids[content_set_id])

        candidate_patch_definitions = set()
        candidate_vuln_definitions = set()
        for cpe_id in cpe_ids:
            for definition_id in self.db_cache.cpe_id2ovaldefinition_ids.get(cpe_id, []):
                definition_type, _ = self.db_cache.ovaldefinition_detail[definition_id]
                if definition_type == OVAL_DEFINITION_TYPE_PATCH:
                    candidate_patch_definitions.add(definition_id)
                elif definition_type == OVAL_DEFINITION_TYPE_VULNERABILITY:
                    candidate_vuln_definitions.add(definition_id)
                else:
                    raise ValueError("Unsupported definition type: %s" % definition_type)
        return candidate_patch_definitions, candidate_vuln_definitions

    @staticmethod
    def _serialize_dict(input_dict, extended=False):
        return [{k: list(v) if isinstance(v, set) else v for k, v in cve.items()} for cve in input_dict.values()] \
            if extended else list(input_dict.keys())

    # pylint: disable=unused-argument,too-many-branches,too-many-nested-blocks
    def process_list(self, api_version, data):
        """Return list of potential security issues"""
        strip_prefixes(data, REPO_PREFIXES)
        extended = data.get("extended", False)
        cve_dict = {}
        manually_fixable_cve_dict = {}
        unpatched_cve_dict = {}

        # OVAL
        # TODO: re-factor, double parsing input packages
        packages_to_process, _ = self.updates_api.process_input_packages(data)
        modules_list = {f"{x['module_name']}:{x['module_stream']}" for x in data.get('modules_list', [])}

        # Get CPEs for affected repos/content sets
        # TODO: currently OVAL doesn't evaluate when there is not correct input repo list mapped to CPEs
        #       there needs to be better fallback at least to guess correctly RHEL version,
        #       use old VMaaS repo guessing?
        candidate_patch_definitions, candidate_vuln_definitions = \
            self._repos_to_definitions(data.get('repository_list'),
                                       data.get('basearch'),
                                       data.get('releasever'))

        if CFG.oval_unfixed_eval_enabled and candidate_vuln_definitions:
            for package, parsed_package in packages_to_process.items():
                name, epoch, ver, rel, arch = parsed_package["parsed_nevra"]
                package_name_id = self.db_cache.packagename2id[name]
                definition_ids = candidate_vuln_definitions.intersection(
                    self.db_cache.packagename_id2definition_ids.get(package_name_id, []))
                # LOGGER.info("OVAL definitions found for package_name=%s, count=%s", name, len(definition_ids))
                for definition_id in definition_ids:
                    _, criteria_id = self.db_cache.ovaldefinition_detail[definition_id]
                    cves = self.db_cache.ovaldefinition_id2cves.get(definition_id, [])
                    # Skip if all CVEs from definition were already found somewhere
                    if not [cve for cve in cves if cve not in unpatched_cve_dict]:
                        continue

                    if self._evaluate_criteria(criteria_id, (package_name_id, epoch, ver, rel, arch), modules_list):
                        # Vulnerable
                        # LOGGER.info("Definition id=%s, type=%s matched! Adding CVEs.", definition_id, definition_type)
                        for cve in cves:
                            unpatched_cve_dict.setdefault(cve, {})["cve"] = cve
                            unpatched_cve_dict[cve].setdefault("affected_packages", set()).add(package)
                            # no erratum for unpatched CVEs
                            unpatched_cve_dict[cve].setdefault("errata", set())

        # Repositories
        updates = self.updates_api.process_list(2, data)
        for package in updates['update_list']:
            for update in updates['update_list'][package].get('available_updates', []):
                for cve in self.db_cache.errata_detail[update['erratum']][ERRATA_CVE]:
                    if cve not in unpatched_cve_dict:  # Skip CVEs found as unpatched
                        cve_dict.setdefault(cve, {})["cve"] = cve
                        cve_dict[cve].setdefault("affected_packages", set()).add(package)
                        cve_dict[cve].setdefault("errata", set()).add(update['erratum'])

        if candidate_patch_definitions:
            for package, parsed_package in packages_to_process.items():
                name, epoch, ver, rel, arch = parsed_package["parsed_nevra"]
                package_name_id = self.db_cache.packagename2id[name]
                definition_ids = candidate_patch_definitions.intersection(
                    self.db_cache.packagename_id2definition_ids.get(package_name_id, []))
                # LOGGER.info("OVAL definitions found for package_name=%s, count=%s", name, len(definition_ids))
                for definition_id in definition_ids:
                    _, criteria_id = self.db_cache.ovaldefinition_detail[definition_id]
                    cves = self.db_cache.ovaldefinition_id2cves.get(definition_id, [])
                    # Skip if all CVEs from definition were already found somewhere
                    if not [cve for cve in cves
                            if cve not in unpatched_cve_dict and
                            cve not in cve_dict]:
                        continue

                    if self._evaluate_criteria(criteria_id, (package_name_id, epoch, ver, rel, arch), modules_list):
                        # Vulnerable
                        # LOGGER.info("Definition id=%s, type=%s matched! Adding CVEs.", definition_id, definition_type)
                        for cve in cves:
                            # Skip CVEs found in repos or in unpatched
                            if cve in unpatched_cve_dict or cve in cve_dict:
                                continue
                            manually_fixable_cve_dict.setdefault(cve, {})["cve"] = cve
                            manually_fixable_cve_dict[cve].setdefault("affected_packages", set()).add(package)
                            errata_ids = self.db_cache.ovaldefinition_id2errata_id.get(definition_id, [])
                            errata_names = [res for e in errata_ids if (res := self.db_cache.errataid2name.get(e))]
                            manually_fixable_cve_dict[cve].setdefault("errata", set()).update(errata_names)

        return {'cve_list': self._serialize_dict(cve_dict, extended=extended),
                'manually_fixable_cve_list': self._serialize_dict(manually_fixable_cve_dict, extended=extended),
                'unpatched_cve_list': self._serialize_dict(unpatched_cve_dict, extended=extended),
                'last_change': format_datetime(self.db_cache.dbchange['last_change'])}
