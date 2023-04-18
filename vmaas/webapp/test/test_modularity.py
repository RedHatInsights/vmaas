"""Unit tests for modularity"""
# pylint: disable=protected-access
# pylint: disable=unused-argument

import pytest

from vmaas.webapp.test.conftest import TestBase
from vmaas.webapp.updates import UpdatesAPI

PKG_NEVRAS = ['my-pkg-1.1.0-1.el8.i686',
              'my-pkg-1.2.0-1.el8.i686',
              'my-pkg-2.0.0-1.el8.i686',
              'my-pkg-2.1.0-1.el8.i686']

MODULE_JSONS = [{'module_name': 'my-pkg', 'module_stream': '1'},
                {'module_name': 'my-pkg', 'module_stream': '2'},
                {'module_name': 'rhn-tools', 'module_stream': '1.0'},
                {'module_name': 'sharks', 'module_stream': 'are_dangerous'}]

OLD_OLD = [
    ('without_modularity', None, set()),
    ('with_modularity', [MODULE_JSONS[0]], {PKG_NEVRAS[1]}),
    ('multiple_modules', MODULE_JSONS, {PKG_NEVRAS[1], PKG_NEVRAS[2], PKG_NEVRAS[3]})
]

NEW_OLD = [
    ('without_modularity', None, set()),
    ('correct_stream_enabled', [MODULE_JSONS[0]], None),
    ('incorrect_stream_enabled', [MODULE_JSONS[1]], {PKG_NEVRAS[2], PKG_NEVRAS[3]})
]

NEW_MODULE = [
    ('without_modularity', None, set()),
    ('with_modularity', [MODULE_JSONS[1]], {PKG_NEVRAS[3]})
]

NO_MODULES = [
    ('no_enabled_modules', []),
    ('different_enabled', [MODULE_JSONS[2]]),
    ('module_not_in_db', [MODULE_JSONS[3]])
]


class TestModularity(TestBase):
    """Test /updates modularity"""

    updates_api = None

    @staticmethod
    def gen_pkg_json(nevra, modules=None):
        """Prepares a request to VMaaS"""
        retval = {'package_list': [nevra]}
        if modules is not None:
            retval['modules_list'] = modules
        return retval

    @pytest.fixture(autouse=True)
    def setup_api(self, load_cache):
        """Setup UpdatesAPI object."""
        self.updates_api = UpdatesAPI(self.cache)

    @pytest.mark.parametrize('test_data', OLD_OLD, ids=[x[0] for x in OLD_OLD])
    def test_old_pkg_old_module(self, test_data):
        """
        Test with my-pkg-1.1.0-1.el8.i686
        Test without modularity info provided, should find 3 updates:
          my-pkg-1.2.0-1.el8.i686
          my-pkg-2.0.0-1.el8.i686
          my-pkg-2.1.0-1.el8.i686
        Test with modularity info provided, should find one update:
          my-pkg-1.2.0-1.el8.i686
        """
        pkg = PKG_NEVRAS[0]
        mode, modules, expected_update_pkgs = test_data  # pylint:disable=unused-variable
        updates = self.updates_api.process_list(2, self.gen_pkg_json(pkg, modules))
        assert updates
        available_updates = updates['update_list'][pkg]['available_updates']
        package_updates = {rec['package'] for rec in available_updates}
        assert len(package_updates) == len(expected_update_pkgs)
        assert expected_update_pkgs == package_updates

    @pytest.mark.parametrize('test_data', NEW_OLD, ids=[x[0] for x in NEW_OLD])
    def test_new_pkg_old_module(self, test_data):
        """Test with my-pkg-1.2.0-1.el8.i686
        Test without modularity info enabled, should find two updates
          my-pkg-2.0.0-1.el8.i686
          my-pkg-2.1.0-1.el8.i686
        With correct modularity stream enabled there should be no upates
        Test with incorrect modularity information, should find two (incorrect) update:
          my-pkg-2.0.0-1.el8.i686
          my-pkg-2.1.0-1.el8.i686
          DNF on the client should never let this happen
        """
        pkg = PKG_NEVRAS[1]
        mode, modules, expected_update_pkgs = test_data  # pylint:disable=unused-variable
        updates = self.updates_api.process_list(2, self.gen_pkg_json(pkg, modules))
        assert updates
        available_updates = updates['update_list'][pkg]['available_updates']
        if mode == 'correct_stream_enabled':  # with correct stream enabled there should be no updates
            assert not available_updates
            return
        package_updates = {rec['package'] for rec in available_updates}
        assert len(package_updates) == len(expected_update_pkgs)
        assert expected_update_pkgs == package_updates

    @pytest.mark.parametrize('test_data', NEW_MODULE, ids=[x[0] for x in NEW_MODULE])
    def test_old_pkg_new_module(self, test_data):
        """
        Test with my-pkg-2.0.0-1.el8.i686
        Both tests with, or without modularity should find one update
          my-pkg-2.1.0-1.el8.i686
        """
        pkg = PKG_NEVRAS[2]
        mode, modules, expected_update_pkgs = test_data  # pylint:disable=unused-variable
        updates = self.updates_api.process_list(2, self.gen_pkg_json(pkg, modules))
        assert updates
        available_updates = updates['update_list'][pkg]['available_updates']
        assert len(available_updates) == len(expected_update_pkgs)
        assert expected_update_pkgs == {rec['package'] for rec in available_updates}

    @pytest.mark.parametrize('test_data', NEW_MODULE, ids=[x[0] for x in NEW_MODULE])
    def test_new_pkg_new_module(self, test_data):
        """
        Test with my-pkg-2.1.0-1.el8.i686 which is the latest package and has no updates
        There should be zero updates with or without modularity
        """

        pkg = PKG_NEVRAS[3]
        mode, modules, expected_update_pkgs = test_data  # pylint:disable=unused-variable
        updates = self.updates_api.process_list(2, self.gen_pkg_json(pkg, modules))
        assert updates
        assert not updates['update_list'][pkg].get('available_updates')

    @pytest.mark.parametrize('test_data', NO_MODULES, ids=[x[0] for x in NO_MODULES])
    def test_no_enabled_modules(self, test_data):
        """
        Tests with modularity functionaility enabled witout needed module (my-pkg 1) enabled
        Scenarios: no modules enabled at all, only rhn-tools module enabled, module not present in the database enabled
        All of these should result in no updates found
        """
        pkg = PKG_NEVRAS[0]
        mode, modules = test_data  # pylint:disable=unused-variable
        updates = self.updates_api.process_list(2, self.gen_pkg_json(pkg, modules))
        assert updates
        assert not updates['update_list'][pkg].get('available_updates')
