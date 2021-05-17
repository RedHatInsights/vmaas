"""
Module contains classes for matching Content Set by RPM name
"""
from natsort import natsorted  # pylint: disable=E0401

from vmaas.common.webapp_utils import format_datetime


class RPMPkgNamesAPI:
    """Main /package_names/rpms API class"""

    def __init__(self, cache):
        self.cache = cache

    def process_list(self, api_version, data):  # pylint: disable=unused-argument
        """
        This method returns content sets for given RPM list filtered by content set
        :param data: data from api - RPM name list and content set
        :returns: list of content sets for given content set and RPM list
        """
        rpm_list = data.get('rpm_name_list', [])
        content_set_list = data.get('content_set_list', [])
        response = {}
        if not rpm_list:
            return response

        response['last_change'] = format_datetime(self.cache.dbchange['last_change'])
        content_data = {}
        for rpm in set(rpm_list):
            content_set_labels = []
            if rpm in self.cache.packagename2id:
                pkg_name_id = self.cache.packagename2id[rpm]
                content_set_ids = self._get_content_set_ids(pkg_name_id)
                content_set_labels.extend(self._get_content_set_labels(content_set_ids, content_set_list))
                content_data.setdefault(rpm, []).extend(natsorted(content_set_labels))

        response['rpm_name_list'] = content_data
        return response

    def _get_content_set_ids(self, pkg_name_id):
        """Returns list of content set ids for given package name id"""
        return (csid for csid in self.cache.content_set_id2pkg_name_ids if
                pkg_name_id in self.cache.content_set_id2pkg_name_ids[csid])

    def _get_content_set_labels(self, content_set_ids, content_set_list=None):
        """Returns list of content set labels for given content set ids and list"""
        if content_set_list:
            labels = [self.cache.content_set_id2label[csid] for csid in content_set_ids if
                      csid in self.cache.content_set_id2label and self.cache.content_set_id2label[
                          csid] in content_set_list]
        else:
            labels = [self.cache.content_set_id2label[csid] for csid in content_set_ids if
                      csid in self.cache.content_set_id2label]
        return labels
