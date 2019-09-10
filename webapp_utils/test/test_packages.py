"""
Tests for the packages API in webapp_utils.
"""
from packages import PackagesAPI
from .db.dummy_db import DummyDatabase

PKG_EMPTY_JSON = {"package_list": [""]}
PKG_EMPTY_EXPECTED = {"package_list": {"": {}}}

PKG_NON_EXISTING_JSON = {"package_list": ["non-existing-package"]}
PKG_NON_EXISTING_EXPECTED = {"package_list": {"non-existing-package": {}}}

PKG_NON_EXISTING_JSON2 = {"package_list": ["non-existing-package", "nonexisting"]}
PKG_NON_EXISTING_EXPECTED2 = {"package_list": {"non-existing-package": {}, "nonexisting": {}}}

PKG_MALFORMED_JSON = {"package_list": "package"}

PKG_LEGIT = {"package_list": ["kernel-2.6.32-696.20.1.el6.x86_64"]}
PKG_LEGIT_EXPECTED = \
{"package_list": {
    "kernel-2.6.32-696.20.1.el6.x86_64": {
        "summary": "Kernel for basic OS functions.",
        "description": "Kernel description",
        "source_package": None,
        "repositories": [{"label": "rhel-6-desktop-rpms", "name":"Red Hat Enterprise Linux 6 Desktop (RPMs)",
                          "releasever": "696.20.1.el6", "arch": "x86_64"},
                         {"label": "rhel-6-server-rpms", "name":"Red Hat Enterprise Linux 6 Server (RPMs)",
                          "releasever": "696.20.1.el6", "arch": "x86_64"}],
        "binary_package_list": []
        }
    }
}

class TestPackagesAPI():
    """ Set of tests for the packages API. """
    db_handle = None
    packages_api = None

    def setup_class(self):
        """ Setup the database and connection to it. """
        self.db_handle = DummyDatabase()
        self.packages_api = PackagesAPI(dsn=self.db_handle.database.dsn())

    def test_empty_package_list(self):
        """ Test with empty package list inside the input JSON. """
        response = self.packages_api.process_list(PKG_EMPTY_JSON)
        assert response == PKG_EMPTY_EXPECTED

    def test_nonexisting_package(self):
        """ Test with non existing package inside the input JSON. """
        response = self.packages_api.process_list(PKG_NON_EXISTING_JSON)
        assert response == PKG_NON_EXISTING_EXPECTED

    def test_nonexisting_packages(self):
        """ Test with non existing packages inside the input JSON. """
        response = self.packages_api.process_list(PKG_NON_EXISTING_JSON2)
        assert response == PKG_NON_EXISTING_EXPECTED2

    def test_correct_pkg_empty(self):
        """ Test with legit input, legit package. """
        response = self.packages_api.process_list(PKG_LEGIT)
        assert response == PKG_LEGIT_EXPECTED
