"""
Module contains classes for matching RPM name by SRPM name and Content Set
"""
from natsort import natsorted  # pylint: disable=E0401

from cache import PKG_NAME_ID
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
        srpm_list = data.get('srpm_name_list', [])
        rpm_list = data.get('rpm_name_list', [])
        content_set_list = data.get('content_set_list', [])
        response = {}

        if not srpm_list and not rpm_list:
            return response

        response['last_change'] = format_datetime(self.cache.dbchange['last_change'])
        rpm_data = {}
        for srpm in srpm_list:
            if srpm in self.cache.packagename2id:
                src_pkg_name_id = self.cache.packagename2id[srpm]
                content_set_ids = self._get_content_set_ids(src_pkg_name_id)
                src_pkg_ids = set(pkg_id for (name_id, _, _), pkg_id in self.cache.nevra2pkgid.items() if
                                  src_pkg_name_id == name_id and pkg_id in self.cache.src_pkg_id2pkg_ids)

                src2pkgid = {}
                for src_pkg_id in src_pkg_ids:
                    src2pkgid.setdefault(src_pkg_id, []).extend(self.cache.src_pkg_id2pkg_ids[src_pkg_id])

                content_set_labels = []
                if content_set_list:
                    content_set_labels.extend([label for label in content_set_list if
                                               self.cache.label2content_set_id[label] in content_set_ids])
                    label2name_ids = self._process_content_set(content_set_labels)
                else:
                    content_set_labels = self._get_content_set_labels(content_set_ids)
                    label2name_ids = self._process_content_set(content_set_labels)

                pkg_ids = []
                for pkg in src2pkgid.values():
                    pkg_ids.extend(pkg)

                label2pkg_name_filtered = {}
                for label in content_set_labels:
                    pkg_names = set(
                        self.cache.id2packagename[self.cache.package_details[pid][PKG_NAME_ID]] for pid in pkg_ids if
                        self.cache.package_details[pid][PKG_NAME_ID] in label2name_ids[label])
                    label2pkg_name_filtered.setdefault(label, []).extend(natsorted(pkg_names))
                rpm_data.setdefault(srpm, {}).update(label2pkg_name_filtered)

        if rpm_data:
            response['srpm_name_list'] = rpm_data

        content_data = {}
        for rpm in rpm_list:
            if rpm in self.cache.packagename2id:
                pkg_name_id = self.cache.packagename2id[rpm]
                content_set_ids = self._get_content_set_ids(pkg_name_id)
                content_set_labels = self._get_content_set_labels(content_set_ids)
                content_data.setdefault(rpm, []).extend(natsorted(content_set_labels))

        if content_data:
            response['rpm_name_list'] = content_data

        return response

    def _get_content_set_ids(self, pkg_name_id):
        """Returns list of content set ids for given package name id"""
        return (csid for csid in self.cache.content_set_id2pkg_name_ids if
                pkg_name_id in self.cache.content_set_id2pkg_name_ids[csid])

    def _get_content_set_labels(self, content_set_ids):
        """Returns list of content set labels for given content set ids"""
        return [self.cache.content_set_id2label[csid] for csid in content_set_ids if
                csid in self.cache.content_set_id2label]

    def _process_content_set(self, content_set_labels):
        """Returns dict of name ids for given content sets."""
        label2name_ids = {}
        for label in content_set_labels:
            if label in self.cache.label2content_set_id:
                label2name_ids.setdefault(label, []).extend(
                    self.cache.content_set_id2pkg_name_ids[self.cache.label2content_set_id[label]])
        return label2name_ids
