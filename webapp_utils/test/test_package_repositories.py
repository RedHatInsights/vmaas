"""
Tests for the packages API in webapp_utils.
"""
from package_repositories import PackagesRepositoriesAPI
from .db.dummy_db import DummyDatabase

EMPTY_JSON = {"package_list":[]}
EMPTY_JSON_RESPONSE = {"data":{}}

CORRECT_JSON = {"package_list":["kernel-2.6.32-696.20.1.el6.x86_64"]}
CORRECT_JSON_RESPONSE = {"data":{"kernel-2.6.32-696.20.1.el6.x86_64":[
    {"repo_name": "Red Hat Enterprise Linux 6 Desktop (RPMs)", "repo_label": "rhel-6-desktop-rpms"},
    {"repo_name": "Red Hat Enterprise Linux 6 Server (RPMs)", "repo_label": "rhel-6-server-rpms"}]}}

NONEXISTING_PACKAGE_JSON = {"package_list":["non-existing-package"]}
NONEXISTING_PACKAGE_JSON_RESPONSE = {"data":{"non-existing-package":[]}}

NONEXISTING_PACKAGES_JSON = {"package_list":["non-existing-package", "non-existing-package2"]}
NONEXISTING_PACKAGES_JSON_RESPONSE = {"data":{"non-existing-package":[], "non-existing-package2":[]}}

EXISTING_NONEXISTING_PACKAGES_JSON = {"package_list":["kernel-2.6.32-696.20.1.el6.x86_64", "non-existing-package"]}
EXISTING_NONEXISTING_PACKAGES_JSON_RESPONSE = {"data":{"kernel-2.6.32-696.20.1.el6.x86_64":[
    {"repo_name": "Red Hat Enterprise Linux 6 Desktop (RPMs)", "repo_label": "rhel-6-desktop-rpms"},
    {"repo_name": "Red Hat Enterprise Linux 6 Server (RPMs)", "repo_label": "rhel-6-server-rpms"}],
                                                       "non-existing-package":[]}}

class TestPackageRepositories:
    """ Set of tests for the package repositories API. """
    db_handle = None
    repository_packages_api = None

    def setup_class(self):
        """ Setup the database and connection to it. """
        self.db_handle = DummyDatabase()
        self.repository_packages_api = PackagesRepositoriesAPI(dsn=self.db_handle.database.dsn())

    def test_empty_list(self):
        """ Test with empty package_list. """
        response = self.repository_packages_api.process_nevras(EMPTY_JSON)
        assert response == EMPTY_JSON_RESPONSE

    def test_correct_package(self):
        """ Test with correct package and correct repositories. """
        response = self.repository_packages_api.process_nevras(CORRECT_JSON)
        assert response == CORRECT_JSON_RESPONSE

    def test_nonexisting_package(self):
        """ Test with nonexisting package. """
        response = self.repository_packages_api.process_nevras(NONEXISTING_PACKAGE_JSON)
        assert response == NONEXISTING_PACKAGE_JSON_RESPONSE

    def test_nonexisting_packages(self):
        """ Test with nonexisting packages. """
        response = self.repository_packages_api.process_nevras(NONEXISTING_PACKAGES_JSON)
        assert response == NONEXISTING_PACKAGES_JSON_RESPONSE

    def test_existnonexisting_packages(self):
        """ Test with existing and nonexisting packages. """
        response = self.repository_packages_api.process_nevras(EXISTING_NONEXISTING_PACKAGES_JSON)
        assert response == EXISTING_NONEXISTING_PACKAGES_JSON_RESPONSE
