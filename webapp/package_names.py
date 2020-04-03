"""
Module contains classes for matching RPM name by SRPM name and Content Set
"""
import re

from cache import REPO_LABEL
from common.webapp_utils import format_datetime


class PackageNamesAPI:
    """Main /package_names API class"""

    def __init__(self, cache):
        self.cache = cache

    def process_list(self, api_version, data):  # pylint: disable=unused-argument
        """
        This method returns RPM names for given SRPM list and content set for given RPM list filtered by content set
        :param data: data from api - SRPM name list RPM name list and content set
        :returns: list of RPM names for given content set and SRPM and content set for given RPM list
        """
        srpm_list = data.get('srpm_name_list', None)
        rpm_list = data.get('rpm_name_list', None)
        content_set_list = data.get('content_set_list', None)
        response = {}

        if not srpm_list and not rpm_list:
            return response

        response['last_change'] = format_datetime(self.cache.dbchange['last_change'])
        rpm_data = {}
        if srpm_list:
            for srpm in srpm_list:
                if srpm in self.cache.packagename2id:
                    pkg_ids = self.cache.pkg_name2pkg_ids[srpm]
                    src_pkg_ids = [pid for pid in pkg_ids if pid in self.cache.src_pkg_id2pkg_ids]
                    rpms = {}
                    for src_pkg_id in src_pkg_ids:
                        rpms.setdefault(src_pkg_id, []).extend(self.cache.src_pkg_id2pkg_ids[src_pkg_id])

                    repo_labels_tmp = []
                    repo_ids_tmp = []
                    if content_set_list:
                        for content_set in content_set_list:
                            repo_ids, repo_labels = self._process_content_set(content_set)
                            repo_ids_tmp.extend(repo_ids)
                            repo_labels_tmp.extend(repo_labels)
                    else:
                        repo_ids, repo_labels = self._process_content_set('')
                        repo_ids_tmp.extend(repo_ids)
                        repo_labels_tmp.extend(repo_labels)

                    repo_ids_with_pkg_ids = {}
                    for repo_id in repo_ids_tmp:
                        packages = []
                        for pkg in rpms.values():
                            packages.extend(pkg)
                        repo_ids_with_pkg_ids.setdefault(
                            self.cache.repo_detail[repo_id][REPO_LABEL], []).extend(
                            pid for pid in packages if repo_id in self.cache.pkgid2repoids[pid])

                    for label in repo_labels_tmp:
                        if repo_ids_with_pkg_ids[label]:
                            rpm_data.setdefault(srpm, {}).update(
                                {label: self._packageids2names(repo_ids_with_pkg_ids[label])})

        if rpm_data:
            response['srpm_name_list'] = rpm_data

        content_data = {}
        if rpm_list:
            for rpm in rpm_list:
                if rpm in self.cache.packagename2id:
                    pkg_ids = self.cache.pkg_name2pkg_ids[rpm]
                    repo_ids = []
                    for pid in pkg_ids:
                        if pid in self.cache.pkgid2repoids:
                            repo_ids.extend(self.cache.pkgid2repoids[pid])
                    for rid in repo_ids:
                        label = self.cache.repo_detail[rid][REPO_LABEL]
                        content_data.setdefault(rpm, [])
                        if label not in content_data[rpm]:
                            content_data[rpm].append(label)
        if content_data:
            response['rpm_name_list'] = content_data

        return response

    def _process_content_set(self, content_set):
        """Returns list of available repo_ids for given content sets."""
        repo_labels = [label for label in self.cache.repolabel2ids if re.match(content_set + ".*", label)]
        repo_ids = []
        for label in repo_labels:
            repo_ids.extend(self.cache.repolabel2ids[label])
        return repo_ids, repo_labels

    def _packageids2names(self, pkg_id_list):
        """For given list of pkg_ids returns list of package names"""
        package_names = set()
        for pkg_id in pkg_id_list:
            pkg_name = self.cache.pkg_id2pkg_name[pkg_id]
            package_names.add(pkg_name)
        return list(package_names)
