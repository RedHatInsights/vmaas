"""
Module contains functions and CVE class for returning data from DB
"""

import re
from jsonschema import validate

from common.webapp_utils import format_datetime, parse_datetime, none2empty, paginate, \
                  pkgidlist2packages, filter_item_if_exists
from cache import CVE_REDHAT_URL, CVE_SECONDARY_URL, CVE_IMPACT, CVE_PUBLISHED_DATE, \
                  CVE_MODIFIED_DATE, CVE_CWE, CVE_CVSS3_SCORE, CVE_CVSS3_METRICS, \
                  CVE_DESCRIPTION, CVE_PID, CVE_EID, CVE_CVSS2_SCORE, CVE_CVSS2_METRICS, CVE_SOURCE

JSON_SCHEMA = {
    'type' : 'object',
    'required': ['cve_list'],
    'properties' : {
        'cve_list': {
            'type': 'array', 'items': {'type': 'string'}, 'minItems' : 1
            },
        'modified_since' : {'type' : 'string'},
        'published_since' : {'type' : 'string'},
        'page_size' : {'type' : 'number'},
        'page' : {'type' : 'number'},
        'rh_only' : {'type' : 'boolean'}
    }
}


class CveAPI:
    """ Main /cves API class. """
    def __init__(self, cache):
        self.cache = cache

    def find_cves_by_regex(self, regex):
        """Returns list of CVEs matching a provided regex."""
        if not regex.startswith('^'):
            regex = '^' + regex

        if not regex.endswith('$'):
            regex = regex + '$'

        return [label for label in self.cache.cve_detail if re.match(regex, label)]

    def _filter_redhat_only(self, cves_to_process):
        return [cve for cve in cves_to_process if self.cache.cve_detail.get(cve)
                and self.cache.cve_detail.get(cve)[CVE_SOURCE] == 'Red Hat']

    def _filter_modified_since(self, cves_to_process, modified_since_dt):
        filtered_cves_to_process = []
        for cve in cves_to_process:
            cve_detail = self.cache.cve_detail.get(cve)
            if not cve_detail:
                continue
            if cve_detail[CVE_MODIFIED_DATE]:
                if cve_detail[CVE_MODIFIED_DATE] >= modified_since_dt:
                    filtered_cves_to_process.append(cve)
            elif cve_detail[CVE_PUBLISHED_DATE] and cve_detail[CVE_PUBLISHED_DATE] >= modified_since_dt:
                filtered_cves_to_process.append(cve)
        return filtered_cves_to_process

    def _filter_published_since(self, cves_to_process, published_since_dt):
        filtered_cves_to_process = []

        for cve in cves_to_process:
            cve_detail = self.cache.cve_detail.get(cve)
            if not cve_detail:
                continue
            if cve_detail[CVE_PUBLISHED_DATE]:
                if cve_detail[CVE_PUBLISHED_DATE] >= published_since_dt:
                    filtered_cves_to_process.append(cve)

        return filtered_cves_to_process

    def process_list(self, api_version, data): # pylint: disable=unused-argument
        """
        This method returns details for given set of CVEs.

        :param data: data obtained from api, we're interested in data["cve_list"]

        :returns: list of dictionaries containing detailed information for given cve list}

        """
        validate(data, JSON_SCHEMA)

        cves_to_process = data.get("cve_list", None)
        modified_since = data.get("modified_since", None)
        published_since = data.get("published_since", None)
        rh_only = data.get('rh_only', False)
        modified_since_dt = parse_datetime(modified_since)
        published_since_dt = parse_datetime(published_since)
        page = data.get("page", None)
        page_size = data.get("page_size", None)

        answer = {}
        if not cves_to_process:
            return answer

        cves_to_process = list(filter(None, cves_to_process))
        if len(cves_to_process) == 1:
            # treat single-label like a regex, get all matching names
            cves_to_process = self.find_cves_by_regex(cves_to_process[0])

        filters = [(filter_item_if_exists, [self.cache.cve_detail])]
        if rh_only:
            filters.append((self._filter_redhat_only, []))
        # if we have information about modified/published dates and receive "modified_since"
        # or "published_since" in request,
        # compare the dates
        if modified_since:
            filters.append((self._filter_modified_since, [modified_since_dt]))

        if published_since:
            filters.append((self._filter_published_since, [published_since_dt]))

        cve_list = {}
        cve_page_to_process, pagination_response = paginate(cves_to_process, page, page_size, filters=filters)
        for cve in cve_page_to_process:
            cve_detail = self.cache.cve_detail.get(cve, None)
            if not cve_detail:
                continue

            bin_pkg_list, src_pkg_list = pkgidlist2packages(self.cache, cve_detail[CVE_PID])
            cve_list[cve] = {
                "redhat_url": none2empty(cve_detail[CVE_REDHAT_URL]),
                "secondary_url": none2empty(cve_detail[CVE_SECONDARY_URL]),
                "synopsis": cve,
                "impact": none2empty(cve_detail[CVE_IMPACT]),
                "public_date": none2empty(format_datetime(cve_detail[CVE_PUBLISHED_DATE])),
                "modified_date": none2empty(format_datetime(cve_detail[CVE_MODIFIED_DATE])),
                "cwe_list": none2empty(cve_detail[CVE_CWE]),
                "cvss3_score": str(none2empty(cve_detail[CVE_CVSS3_SCORE])),
                "cvss3_metrics": str(none2empty(cve_detail[CVE_CVSS3_METRICS])),
                "cvss2_score": str(none2empty(cve_detail[CVE_CVSS2_SCORE])),
                "cvss2_metrics": str(none2empty(cve_detail[CVE_CVSS2_METRICS])),
                "description": none2empty(cve_detail[CVE_DESCRIPTION]),
                "package_list": bin_pkg_list,
                "source_package_list": src_pkg_list,
                "errata_list": [self.cache.errataid2name[eid] for eid in cve_detail[CVE_EID]],

            }
        response = {"cve_list": cve_list}
        response.update(pagination_response)
        if modified_since:
            response["modified_since"] = modified_since
        if published_since:
            response["published_since"] = published_since
        return response
