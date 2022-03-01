"""
Module to handle /updates API calls.
"""
import redis
import rpm

from vmaas.common.rpm_utils import parse_rpm_name


def _process_package_updates(installed_evra: tuple, nevra_erratum_updates: list) -> list:
    out_updates = []
    for nevra_erratum_update in nevra_erratum_updates:
        if not nevra_erratum_update:
            continue

        nevra, erratum = nevra_erratum_update.decode().split(' ')
        _, epoch, ver, rel, _ = parse_rpm_name(nevra)
        ver_cmp = rpm.labelCompare((epoch, ver, rel), installed_evra)
        if ver_cmp > 0:
            out_updates.append([nevra, erratum])
    return out_updates


def _filter_updates(package_list: list, nevra_erratum_updates: list, evrs: list,
                    updates_counts: list) -> dict:
    update_list = {}
    i = 0
    for nevra, inst_evr, updates_count in zip(package_list, evrs, updates_counts):
        package_updates = nevra_erratum_updates[i:updates_count]
        i += updates_count
        update_result = _process_package_updates(inst_evr, package_updates)
        update_list[nevra] = update_result
    return update_list


class UpdatesRedisAPI:
    """ Main /updates API class."""

    def __init__(self, redis_conn: redis.Redis):
        self.redis_conn = redis_conn

    def _get_repos_key(self, data: dict) -> list:
        repos = ['r:%s' % repo for repo in data.get('repository_list', [])]
        repos_key = '+'.join(sorted(repos))
        if not repos_key:
            return []
        if not self.redis_conn.exists(repos_key):
            self.redis_conn.sunionstore(repos_key, repos)
            self.redis_conn.expire(repos_key, 5)
        return [repos_key]

    def _get_nevra_updates(self, nevra: str, data: dict) -> tuple:
        name, epoch, ver, rel, arch = parse_rpm_name(nevra)
        sinter_keys = ['u:%s' % name, 'a:%s' % arch]
        repos_key = self._get_repos_key(data)
        sinter_keys.extend(repos_key)
        package_ids = self.redis_conn.sinter(sinter_keys)
        pkg_updates_ids = sorted(package_ids) if package_ids else [-1]
        return pkg_updates_ids, (epoch, ver, rel)

    def _get_nevra_erratum_updates(self, package_list: list, data: dict) -> tuple:
        updates_ids = []
        updates_counts = []
        evrs = []
        for nevra in package_list:
            pkg_updates_ids, pkg_evr = self._get_nevra_updates(nevra, data)
            updates_ids.extend(pkg_updates_ids)
            updates_counts.append(len(pkg_updates_ids))
            evrs.append(pkg_evr)
        nevra_erratum_updates = self.redis_conn.mget(updates_ids)
        return nevra_erratum_updates, evrs, updates_counts

    def process_list(self, data: dict) -> dict:
        """Find updates for package list with repository list.

        :param data: {"package_list": ["pA-1.x86", "pB-1.i686"],
                      "repository_list": ["repo1", "repo2"]}

        :returns: {"update_list": {"pA-1.x86": [["pA-2.x86", "ERA2"],["pA-3.x86", "ERA3"]],
                                   "pB-1.i686": []}
        """

        package_list = data.get('package_list', None)
        response = {'update_list': {}}
        if not package_list:
            return response

        nevra_erratum_updates, evrs, updates_counts = self._get_nevra_erratum_updates(package_list, data)
        update_list = _filter_updates(package_list, nevra_erratum_updates, evrs, updates_counts)
        response['update_list'] = update_list
        return response
