"""
Module to handle /pkglist API calls.
"""
import datetime

import vmaas.common.webapp_utils as utils
from vmaas.common.webapp_utils import parse_datetime, paginate, format_datetime
from vmaas.common import algorithms
from vmaas.webapp.cache import PKG_MODIFIED_ID, PKG_DESC_ID, PKG_SUMMARY_ID

UTC = datetime.timezone.utc


class PkgListAPI:
    """ Main /pkglist API class."""

    def __init__(self, cache):
        self.cache = cache

    def _get_package_ids(self, modified_since_int) -> list:
        if modified_since_int is None:
            return self.cache.package_details_modified_index[:]

        i = algorithms.find_index(self.cache.package_details_modified_index, modified_since_int,
                                  key=lambda id: self.cache.package_details[id][PKG_MODIFIED_ID])
        return self.cache.package_details_modified_index[i:]

    def _build_package_list(self, package_ids: list, opts):
        package_list = []
        for package_id in package_ids:
            pkg = {}
            pkg_detail = self.cache.package_details[package_id]
            pkg['nevra'] = utils.pkg_detail2nevra(self.cache, pkg_detail)
            pkg['description'] = self.cache.strings.get(pkg_detail[PKG_DESC_ID], None)
            pkg['summary'] = self.cache.strings.get(pkg_detail[PKG_SUMMARY_ID], None)

            package_list.append(pkg)

        if opts['return_modified']:  # For debugging enable to return "modified" value for each package
            for i, package_id in enumerate(package_ids):
                pkg_detail = self.cache.package_details[package_id]
                package_list[i]['modified'] = format_datetime(
                    datetime.datetime.fromtimestamp(pkg_detail[PKG_MODIFIED_ID], tz=UTC))

        return package_list

    @staticmethod
    def modify_since_dt2int(modify_since_dt):
        """Convert datetime type to unix-timestamp int."""

        if modify_since_dt is None:
            return None
        modified_since_int = int(modify_since_dt.astimezone(UTC).timestamp())
        return modified_since_int

    def process_list(self, api_version, data):  # pylint: disable=unused-argument
        """
        Returns info about all packages.

        :param data: json request parsed into data structure
        :returns: json response with package details
        """

        page = data.get("page", None)
        page_size = data.get("page_size", None)
        opts = {"return_modified": data.get("return_modified", False)}
        modified_since = parse_datetime(data.get("modified_since", None))
        modified_since_int = self.modify_since_dt2int(modified_since)
        package_ids = self._get_package_ids(modified_since_int)
        page_package_ids, response = paginate(package_ids, page, page_size, sort_input=False)
        package_list = self._build_package_list(page_package_ids, opts)
        response['package_list'] = package_list
        response['last_change'] = utils.format_datetime(self.cache.dbchange['last_change'])
        response['total'] = len(package_ids)
        return response
