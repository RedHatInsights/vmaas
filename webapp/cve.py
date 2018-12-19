"""
Module contains functions and CVE class for returning data from DB
"""

import re
from jsonschema import validate

from utils import format_datetime, parse_datetime, none2empty, paginate, \
                  pkgidlist2packages
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

    def process_list(self, api_version, data): # pylint: disable=unused-argument
        """
        This method returns details for given set of CVEs.

        :param data: data obtained from api, we're interested in data["cve_list"]

        :returns: list of dictionaries containing detailed information for given cve list}

        """
        validate(data, JSON_SCHEMA)

        cves_to_process = data.get("cve_list", None)
        modified_since = data.get("modified_since", None)
        rh_only = data.get('rh_only', False)
        modified_since_dt = parse_datetime(modified_since)
        page = data.get("page", None)
        page_size = data.get("page_size", None)

        answer = {}
        if not cves_to_process:
            return answer

        cves_to_process = list(filter(None, cves_to_process))
        if len(cves_to_process) == 1:
            # treat single-label like a regex, get all matching names
            cves_to_process = self.find_cves_by_regex(cves_to_process[0])

        cve_list = {}
        cve_page_to_process, pagination_response = paginate(cves_to_process, page, page_size)
        for cve in cve_page_to_process:
            cve_detail = self.cache.cve_detail.get(cve, None)
            if not cve_detail:
                continue

            # if we have information about modified/published dates and receive "modified_since" in request,
            # compare the dates
            if modified_since:
                if cve_detail[CVE_MODIFIED_DATE] and cve_detail[CVE_MODIFIED_DATE] < modified_since_dt:
                    continue
                elif not cve_detail[CVE_MODIFIED_DATE] and cve_detail[CVE_PUBLISHED_DATE] and \
                                cve_detail[CVE_PUBLISHED_DATE] < modified_since_dt:
                    continue

            if rh_only:
                if cve_detail[CVE_SOURCE] != 'Red Hat':
                    continue

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
                "package_list": pkgidlist2packages(self.cache, cve_detail[CVE_PID]),
                "errata_list": [self.cache.errataid2name[eid] for eid in cve_detail[CVE_EID]],

            }
        response = {"cve_list": cve_list}
        response.update(pagination_response)
        if modified_since:
            response["modified_since"] = modified_since
        return response
