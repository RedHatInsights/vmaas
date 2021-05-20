"""
Module to handle /vulnerabilities API calls.
"""

from vmaas.webapp.cache import ERRATA_CVE

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

    @staticmethod
    def _get_num_tuple(text):
        return tuple(int(part) if part.isdigit() else part for part in text.split("."))

    def _evaluate_state(self, state, epoch, ver, rel, arch):
        oval_state_id, evr_id, oval_operation_evr = state
        matched = False

        candidate_epoch, candidate_ver, candidate_rel = self.db_cache.id2evr[evr_id]
        if oval_operation_evr == OVAL_OPERATION_EVR_EQUALS:
            matched = epoch == candidate_epoch and ver == candidate_ver and rel == candidate_rel
        elif oval_operation_evr == OVAL_OPERATION_EVR_LESS_THAN:
            epoch = self._get_num_tuple(epoch)
            candidate_epoch = self._get_num_tuple(candidate_epoch)
            ver = self._get_num_tuple(ver)
            candidate_ver = self._get_num_tuple(candidate_ver)
            rel = self._get_num_tuple(rel)
            candidate_rel = self._get_num_tuple(candidate_rel)

            matched = ((epoch < candidate_epoch) or
                       (epoch == candidate_epoch and ver < candidate_ver) or
                       (epoch == candidate_epoch and ver == candidate_ver and rel < candidate_rel))
        else:
            raise ValueError("Unsupported oval_operation_evr: %s" % oval_operation_evr)

        candidate_arches = self.db_cache.ovalstate_id2arches.get(oval_state_id, [])
        if candidate_arches:
            matched = matched and self.db_cache.arch2id[arch] in candidate_arches

        #LOGGER.info("Evaluated state id=%s, candidate_evr_id=%s, operation=%s, matched=%s",
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

        #LOGGER.info("Evaluated test id=%s, package=%s, candidate_package=%s, check_existence=%s, matched=%s",
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

        #LOGGER.info("Evaluated criteria id=%s, type=%s, matched=%s", criteria_id, criteria_type,
        #            matches >= required_matches)
        return matches >= required_matches

    def _content_sets_to_definitions(self, content_set_list):
        # TODO: some CPEs are not matching because they are substrings/subtrees
        content_set_ids = {self.db_cache.label2content_set_id[label]
                           for label in content_set_list
                           if label in self.db_cache.label2content_set_id}
        cpe_ids = set()
        for content_set_id in content_set_ids:
            if content_set_id in self.db_cache.content_set_id2cpe_ids:
                cpe_ids.update(self.db_cache.content_set_id2cpe_ids[content_set_id])
        candidate_definitions = set()
        for cpe_id in cpe_ids:
            if cpe_id in self.db_cache.cpe_id2ovaldefinition_ids:
                candidate_definitions.update(self.db_cache.cpe_id2ovaldefinition_ids[cpe_id])
        return candidate_definitions


    def process_list(self, api_version, data):  # pylint: disable=unused-argument
        """Return list of potential security issues"""
        evaluate_oval = data.get("oval", False)
        evaluate_oval_only = data.get("oval_only", False)
        cve_list = set()
        unpatched_cve_list = set()

        if not evaluate_oval_only:
            updates = self.updates_api.process_list(2, data)
            errata_list = set()
            for package in updates['update_list']:
                for update in updates['update_list'][package].get('available_updates', []):
                    errata_list.add(update['erratum'])
            for errata in errata_list:
                cve_list.update(self.db_cache.errata_detail[errata][ERRATA_CVE])

        if evaluate_oval:
            # TODO: re-factor, double parsing input packages
            packages_to_process, _ = self.updates_api.process_input_packages(data)
            modules_list = {f"{x['module_name']}:{x['module_stream']}" for x in data.get('modules_list', [])}

            # Get CPEs for affected repos/content sets
            # TODO: currently OVAL doesn't evaluate when there is not correct input repo list mapped to CPEs
            #       there needs to be better fallback at least to guess correctly RHEL version,
            #       use old VMaaS repo guessing?
            candidate_definitions = self._content_sets_to_definitions(data.get('repository_list', []))

            for package in packages_to_process.values():
                name, epoch, ver, rel, arch = package["parsed_nevra"]
                package_name_id = self.db_cache.packagename2id[name]
                definition_ids = candidate_definitions.intersection(
                    self.db_cache.packagename_id2definition_ids.get(package_name_id, []))
                #LOGGER.info("OVAL definitions found for package_name=%s, count=%s", name, len(definition_ids))
                for definition_id in definition_ids:
                    definition_type, criteria_id = self.db_cache.ovaldefinition_detail[definition_id]
                    cves = self.db_cache.ovaldefinition_id2cves.get(definition_id, [])
                    if (
                            (definition_type == OVAL_DEFINITION_TYPE_PATCH
                             and not [cve for cve in cves if cve not in cve_list])
                         or (definition_type == OVAL_DEFINITION_TYPE_VULNERABILITY
                             and not [cve for cve in cves if cve not in unpatched_cve_list])
                       ):
                        continue

                    if self._evaluate_criteria(criteria_id, (package_name_id, epoch, ver, rel, arch), modules_list):
                        # Vulnerable
                        #LOGGER.info("Definition id=%s, type=%s matched! Adding CVEs.", definition_id, definition_type)
                        if definition_type == OVAL_DEFINITION_TYPE_PATCH:
                            cve_list.update(cves)
                        elif definition_type == OVAL_DEFINITION_TYPE_VULNERABILITY:
                            unpatched_cve_list.update(cves)
                        else:
                            raise ValueError("Unsupported definition type: %s" % definition_type)

        return {'cve_list': list(cve_list), 'unpatched_cve_list': list(unpatched_cve_list)}
