"""
Module to handle /pkgtree API calls.
"""

# TODO FIXME - suggested SPEC.yaml and examples does not contain arch.
#              how to handle arch? should it be returned or ust use 'nevr' without arch?
#            - 'nevr' is usually built for every architecture?
#            - how is it returned from reposcan pkgtree? Also it includes architecture?

from cache import PKG_NAME_ID, ERRATA_ISSUED, ERRATA_CVE, REPO_LABEL, REPO_NAME, \
    REPO_BASEARCH, REPO_RELEASEVER, REPO_REVISION
from common.webapp_utils import format_datetime, join_packagename, none2empty


# TODO add test - to check pkgtree order that is generated
# TODO add test with 'my-pkg',
# TODO - create file ./webapp/test/data/cache_pkgtree.yml that will contain
#        data for pkgtree tests - right ordering atp.
#      - create that file from vmaas.dbm
# TODO how to work with vmaas.dbm files? python 'shelve' module?
# TODO add tests to test right order of returned PKG trees.
class PkgtreeAPI:
    """ Main /packages API class."""
    def __init__(self, cache):
        self.cache = cache

    def _get_packages(self, pkgname_id):
        pkg_ids = set()
        # FIXME this implementation is not effecitve to traverse all items in package_details.
        #       Better implementation would require updates in the vmaas.dbm file format
        #       to contain some mapping from package_name to NEVRA or EVR or package_details.
        for pkg_id, pkg_val in self.cache.package_details.items():
            if pkgname_id == pkg_val[PKG_NAME_ID]:
                pkg_ids.add(pkg_id)
        return pkg_ids

    def _build_nevra(self, pkg_id):
        name_id, evr_id, arch_id, _, _, _ = self.cache.package_details[pkg_id]
        name = self.cache.id2packagename[name_id]
        epoch, ver, rel = self.cache.id2evr[evr_id]
        arch = self.cache.id2arch[arch_id]
        return join_packagename(name, epoch, ver, rel, arch)

    def _get_erratas(self, pkg_id):
        # TODO sort erratas by date from newest to oldest? Is it sorted in reposcan pkgtree?
        erratas = []
        if pkg_id in self.cache.pkgid2errataids:
            errata_ids = self.cache.pkgid2errataids[pkg_id]
            for err_id in errata_ids:
                name = self.cache.errataid2name[err_id]
                issued = format_datetime(self.cache.errata_detail[name][ERRATA_ISSUED])
                cves = self.cache.errata_detail[name][ERRATA_CVE]
                errata = {'name': name, 'issued': issued}
                if cves:
                    errata['cve_list'] = cves
                erratas.append(errata)
        return erratas

    def _get_repositories(self, pkg_id):
        # TODO Add support for modules and streams.
        # TODO sort repositories by date from newest to oldest? Is it sorted in reposcan pkgtree?
        repos = []
        if pkg_id in self.cache.pkgid2repoids:
            for repo_id in self.cache.pkgid2repoids[pkg_id]:
                detail = self.cache.repo_detail[repo_id]
                repos.append({
                    'label': detail[REPO_LABEL],
                    'name': detail[REPO_NAME],
                    'basearch': none2empty(detail[REPO_BASEARCH]),
                    'releasever': none2empty(detail[REPO_RELEASEVER]),
                    'revision': format_datetime(detail[REPO_REVISION])
                })
        return repos

    def process_list(self, api_version, data): # pylint: disable=unused-argument,R0201
        """
        Returns list of NEVRAs for given packge name.

        :param data: json request parsed into data structure

        :returns: json response with list of NEVRAs
        """
        # Date and time of last data change in the VMaaS DB
        last_change = format_datetime(self.cache.dbchange['last_change'])

        names = data.get('package_name_list', None)
        pkgnamelist = {}
        if not names:
            return pkgnamelist

        for name in names:
            pkgtreedata = pkgnamelist.setdefault(name, [])
            if name in self.cache.packagename2id:
                name_id = self.cache.packagename2id[name]
                # TODO right sorting of nevras according to pkgtree algorithm
                pkg_ids = self._get_packages(name_id)
                for pkg_id in pkg_ids:
                    pkg_nevra = self._build_nevra(pkg_id)
                    # TODO Where does it come from this date? It is not in cache.
                    #      It looks like it is the date of the oldest errata. Is it oldest repo where it was published?
                    #      Check it out with related vmaas PR or bug report from jsvoboda
                    first_published = "2020-01-13T17:31:41+00:00"
                    errata = self._get_erratas(pkg_id)
                    repositories = self._get_repositories(pkg_id)
                    pkgtreedata.append(
                        {
                            "nevra": pkg_nevra,
                            "first_published": first_published,
                            "repositories": repositories,
                            "errata": errata,
                        }
                    )

        response = {
            'package_name_list': pkgnamelist,
            'last_change': last_change,
        }

        return response
