"""
Module contains classes for returning errata data from DB
"""

import re
from jsonschema import validate

from utils import format_datetime, parse_datetime, none2empty, paginate, \
                  pkgidlist2packages
from cache import ERRATA_SYNOPSIS, ERRATA_SUMMARY, ERRATA_TYPE, \
                  ERRATA_SEVERITY, ERRATA_DESCRIPTION, ERRATA_SOLUTION, \
                  ERRATA_ISSUED, ERRATA_UPDATED, ERRATA_CVE, ERRATA_PKGIDS, \
                  ERRATA_BUGZILLA, ERRATA_REFERENCE, ERRATA_URL

JSON_SCHEMA = {
    'type' : 'object',
    'required': ['errata_list'],
    'properties' : {
        'errata_list': {
            'type': 'array', 'items': {'type': 'string'}, 'minItems' : 1
            },
        'modified_since' : {'type' : 'string'},
        'page_size' : {'type' : 'number'},
        'page' : {'type' : 'number'}
    }
}


class ErrataAPI:
    """ Main /errata API class. """
    def __init__(self, cache):
        self.cache = cache

    def find_errata_by_regex(self, regex):
        """Returns list of errata matching a provided regex."""
        if not regex.startswith('^'):
            regex = '^' + regex

        if not regex.endswith('$'):
            regex = regex + '$'

        return [label for label in self.cache.errata_detail
                if re.match(regex, label)]

    def _filter_modified_since(self, errata_to_process, modified_since_dt):
        filtered_errata_to_process = []
        for errata in errata_to_process:
            errata_detail = self.cache.errata_detail.get(errata)
            if not errata_detail:
                continue
            if errata_detail[ERRATA_UPDATED]:
                if errata_detail[ERRATA_UPDATED] >= modified_since_dt:
                    filtered_errata_to_process.append(errata)
            elif errata_detail[ERRATA_ISSUED] and errata_detail[ERRATA_ISSUED] >= modified_since_dt:
                filtered_errata_to_process.append(errata)
        return filtered_errata_to_process

    def process_list(self, api_version, data): # pylint: disable=unused-argument
        """
        This method returns details for given set of Errata.

        :param data: data obtained from api, we're interested in data["errata_list"]

        :returns: dictionary containing detailed information for given errata list}

        """
        validate(data, JSON_SCHEMA)

        modified_since = data.get("modified_since", None)
        modified_since_dt = parse_datetime(modified_since)
        errata_to_process = data.get("errata_list", None)
        page = data.get("page", None)
        page_size = data.get("page_size", None)

        response = {"errata_list": {}}
        if modified_since:
            response["modified_since"] = modified_since

        if not errata_to_process:
            return response

        if len(errata_to_process) == 1:
            # treat single-label like a regex, get all matching names
            errata_to_process = self.find_errata_by_regex(errata_to_process[0])

        filters = []
        # if we have information about modified/published dates and receive "modified_since" in request,
        # compare the dates
        if modified_since:
            filters.append((self._filter_modified_since, [modified_since_dt]))

        errata_list = {}
        errata_page_to_process, pagination_response = paginate(errata_to_process, page, page_size, filters=filters)
        for errata in errata_page_to_process:
            errata_detail = self.cache.errata_detail.get(errata, None)
            if not errata_detail:
                continue

            errata_list[errata] = {
                "synopsis": none2empty(errata_detail[ERRATA_SYNOPSIS]),
                "summary": none2empty(errata_detail[ERRATA_SUMMARY]),
                "type": none2empty(errata_detail[ERRATA_TYPE]),
                "severity": none2empty(errata_detail[ERRATA_SEVERITY]),
                "description": none2empty(errata_detail[ERRATA_DESCRIPTION]),
                "solution": none2empty(errata_detail[ERRATA_SOLUTION]),
                "issued": none2empty(format_datetime(errata_detail[ERRATA_ISSUED])),
                "updated": none2empty(format_datetime(errata_detail[ERRATA_UPDATED])),
                "cve_list": errata_detail[ERRATA_CVE],
                "package_list": pkgidlist2packages(self.cache, errata_detail[ERRATA_PKGIDS]),
                "bugzilla_list": errata_detail[ERRATA_BUGZILLA],
                "reference_list": errata_detail[ERRATA_REFERENCE],
                "url": none2empty(errata_detail[ERRATA_URL])
                }
        response["errata_list"] = errata_list
        response.update(pagination_response)
        return response
