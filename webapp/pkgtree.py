"""
Module to handle /pkgtree API calls.
"""


class PkgtreeAPI:
    """ Main /packages API class."""
    def __init__(self, cache):
        self.cache = cache

    def process_list(self, api_version, data): # pylint: disable=unused-argument
        """
        Returns list of NEVRAs for given packge name.

        :param data: json request parsed into data structure

        :returns: json response with list of NEVRAs
        """
        # Access any self. attribute to make travis pass.
        cc = self.cache
        names = data.get('package_name_list', None)
        pkgnamelist = {}
        if not names:
            return pkgnamelist

        for name in names:
            # TODO implement this for pkgtree.
            pkgtreedata = pkgnamelist.setdefault(name, [])

            pkgtreedata.append(
                {
                    "nevra": "kernel-rt-4.18.0-147.rt24.93.el8",
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
            'package_name_list': pkgnamelist
        }

        return response
