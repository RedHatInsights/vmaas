"""
Module to handle /pkgtree API calls.
"""

# TODO FIXME - suggested SPEC.yaml and examples does not contain arch.
#              how to handle arch? should it be returned or ust use 'nevr' without arch?
#            - 'nevr' is usually built for every architecture?
#            - how is it returned from reposcan pkgtree? Also it includes architecture?

from cache import PKG_NAME_ID

from common.webapp_utils import format_datetime, join_packagename, none2empty


# TODO add test - to check pkgtree order that is generated
# TODO add test with 'my-pkg',
# TODO - create file ./webapp/test/data/cache_pkgtree.yml that will contain
#        data for pkgtree tests - right ordering atp.
#      - create that file from vmaas.dbm
# TODO how to work with vmaas.dbm files? python 'shelve' module?
class PkgtreeAPI:
    """ Main /packages API class."""
    def __init__(self, cache):
        self.cache = cache

    def _get_packages(self, pkgname_id):
        pkg_ids = set()
        for pkg_id, pkg_val in self.cache.package_details.items():
            if pkgname_id == pkg_val[PKG_NAME_ID]:
                pkg_ids.update(pkg_id)

    def _build_nevra(self, pkg_id):
        name_id, evr_id, arch_id, _, _, _ = self.db_cache.package_details[pkg_id]
        name = self.db_cache.id2packagename[name_id]
        epoch, ver, rel = self.db_cache.id2evr[evr_id]
        arch = self.db_cache.id2arch[arch_id]
        return join_packagename(name, epoch, ver, rel, arch)

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
                pkg_ids = self._get_packages(name_id)
                # TODO implement formating nevra from pkg

                pkgtreedata.append(
                    {
                        "nevra": "kernel-rt-4.18.0-147.rt24.93.el8.x86_64",
                        "first_published": "2020-01-13T17:31:41+00:00",
                        "repositories": [
                            {
                                "label": "rhel-8-for-s390x-appstream-rpms",
                                "name": "Red Hat Enterprise Linux 8 for IBM z Systems - AppStream (RPMs)",
                                "basearch": "x86_64",
                                "releasever": "6.9",
                                "revision": "2019-11-19T09:41:05+00:00",
                                "module_name": "postgresql",
                                "module_stream": "9.6"
                            }
                        ],
                        "errata": [
                            {
                                "name": "RHSA-2019:2730",
                                "issued": "2019-11-19T09:41:05+00:00",
                                "cve_list": [
                                    "CVE-2018-13405"
                                ]
                            }
                        ]
                    }
                )

        response = {
            'package_name_list': pkgnamelist,
            # TODO read this value properly as it is in DBCHANGE api
            'last_change': last_change,
        }

        return response
