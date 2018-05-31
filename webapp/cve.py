"""
Module contains functions and CVE class for returning data from DB
"""

import re

from utils import format_datetime, parse_datetime, none2empty
from cache import CVE_REDHAT_URL, CVE_SECONDARY_URL, CVE_IMPACT, CVE_PUBLISHED_DATE, \
                  CVE_MODIFIED_DATE, CVE_CWE, CVE_CVSS3_SCORE, CVE_DESCRIPTION


class CveAPI(object):
    """ Main /cves API class. """
    def __init__(self, cache):
        self.cache = cache

    def find_cves_by_regex(self, regex):
        """Returns list of CVEs matching a provided regex."""
        return [label for label in self.cache.cve_detail if re.match(regex, label)]

    @staticmethod
    def filter_by_modified_since(cve_list, modified_since):
        """Filter CVEs according to modified/published date."""
        return [cve for cve in cve_list
                if cve["modified_date"] >= modified_since or cve["published_date"] >= modified_since]

    def process_list(self, data):
        """
        This method returns details for given set of CVEs.

        :param data: data obtained from api, we're interested in data["cve_list"]

        :returns: list of dictionaries containing detailed information for given cve list}

        """

        cves_to_process = data.get("cve_list", None)
        modified_since = data.get("modified_since", None)
        modified_since_dt = parse_datetime(modified_since)

        answer = {}
        if not cves_to_process:
            return answer

        cves_to_process = list(filter(None, cves_to_process))
        if len(cves_to_process) == 1:
            # treat single-label like a regex, get all matching names
            cves_to_process = self.find_cves_by_regex(cves_to_process[0])

        cve_list = {}
        for cve in cves_to_process:
            cve_detail = self.cache.cve_detail.get(cve, None)
            if not cve_detail:
                continue
            if modified_since and (cve_detail[CVE_MODIFIED_DATE] < modified_since_dt
                                   and cve_detail[CVE_PUBLISHED_DATE] < modified_since_dt):
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
                "description": none2empty(cve_detail[CVE_DESCRIPTION]),
            }
        response = {"cve_list": cve_list}
        if modified_since:
            response["modified_since"] = modified_since
        return response
