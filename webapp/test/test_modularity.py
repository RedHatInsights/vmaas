"""Unit tests for modularity"""
# pylint: disable=protected-access
# pylint: disable=unused-argument

from test.conftest import TestBase

import pytest

from updates import UpdatesAPI

PKG_NEVRAS = ['postgresql-9.6.10-1.el8+1547+210b7007.x86_64',
              'postgresql-9.6.10-1.module+el8+2470+d1bafa0e.x86_64',
              'postgresql-10.5-1.el8+1546+27ad5f8e.x86_64',
              'postgresql-10.6-1.module+el8+2469+5ecd5aae.x86_64']
MODULE_JSONS = [{'module_name': 'postgresql', 'module_stream': '9.6'},
                {'module_name': 'postgresql', 'module_stream': '10'},
                {'module_name': 'rhn-tools', 'module_stream': '1.0'},
                {'module_name': 'sharks', 'module_stream': 'are_dangerous'}]

OLD_OLD = [
    ('without_modularity', None, {PKG_NEVRAS[1], PKG_NEVRAS[3]}),
    ('with_modularity', [MODULE_JSONS[0]], {PKG_NEVRAS[1]}),
    ('multiple_modules', MODULE_JSONS, {PKG_NEVRAS[1], PKG_NEVRAS[3]})
]

NEW_OLD = [
    ('without_modularity', None, {PKG_NEVRAS[3]}),
    ('correct_stream_enabled', [MODULE_JSONS[0]], None),
    ('incorrect_stream_enabled', [MODULE_JSONS[1]], {PKG_NEVRAS[3]})
]

NEW_MODULE = [
    ('without_modularity', None, {PKG_NEVRAS[3]}),
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
        Test with postgresql-9.6.10-1.el8+1547+210b7007.x86_64
        Test without modularity info provided, should find 2 updates:
          postgresql-9.6.10-1.module+el8+2470+d1bafa0e.x86_64.rpm
          postgresql-10.6-1.module+el8+2469+5ecd5aae.x86_64.rpm
        Test with modularity info provided, should find one update:
          postgresql-9.6.10-1.module+el8+2470+d1bafa0e.x86_64.rpm
        """
        updates = self.updates_api.process_list(2, self.gen_pkg_json(PKG_NEVRAS[0], test_data[1]))
        assert updates
        available_updates = updates['update_list'][PKG_NEVRAS[0]]['available_updates']
        assert len(available_updates) == len(test_data[2])
        assert test_data[2] == {rec['package'] for rec in available_updates}

    @pytest.mark.parametrize('test_data', NEW_OLD, ids=[x[0] for x in NEW_OLD])
    def test_new_pkg_old_module(self, test_data):
        """Test with postgresql-9.6.10-1.module+el8+2470+d1bafa0e.x86_64
        Test without modularity info enabled, should find one update
          postgresql-10.6-1.module+el8+2469+5ecd5aae.x86_64.rpm
        With correct modularity stream enabled there should be no upates
        Test with incorrect modularity information, should find one (incorrect) update:
          postgresql-10.6-1.module+el8+2469+5ecd5aae.x86_64
          DNF on the client should never let this happen
        """
        updates = self.updates_api.process_list(2, self.gen_pkg_json(PKG_NEVRAS[1], test_data[1]))
        assert updates
        available_updates = updates['update_list'][PKG_NEVRAS[1]]['available_updates']
        if test_data[0] == 'correct_stream_enabled':  # with correct stream enabled there should be no updates
            assert not available_updates
            return
        assert len(available_updates) == len(test_data[2])
        assert test_data[2] == {rec['package'] for rec in available_updates}

    @pytest.mark.parametrize('test_data', NEW_MODULE, ids=[x[0] for x in NEW_MODULE])
    def test_old_pkg_new_module(self, test_data):
        """
        Test with postgresql-10.5-1.el8+1546+27ad5f8e.x86_64
        Both tests with, or without modularity should find one update
          postgresql-10.6-1.module+el8+2469+5ecd5aae.x86_64
        """
        updates = self.updates_api.process_list(2, self.gen_pkg_json(PKG_NEVRAS[2], test_data[1]))
        assert updates
        available_updates = updates['update_list'][PKG_NEVRAS[2]]['available_updates']
        assert len(available_updates) == len(test_data[2])
        assert test_data[2] == {rec['package'] for rec in available_updates}

    @pytest.mark.parametrize('test_data', NEW_MODULE, ids=[x[0] for x in NEW_MODULE])
    def test_new_pkg_new_module(self, test_data):
        """
        Test with postgresql-10.6-1.module+el8+2469+5ecd5aae.x86_64 which is the latest package and has no updates
        There should be zero updates with or without modularity
        """
        updates = self.updates_api.process_list(2, self.gen_pkg_json(PKG_NEVRAS[3], test_data[1]))
        assert updates
        assert not updates['update_list'][PKG_NEVRAS[3]]['available_updates']

    @pytest.mark.parametrize('test_data', NO_MODULES, ids=[x[0] for x in NO_MODULES])
    def test_no_enabled_modules(self, test_data):
        """
        Tests with modularity functionaility enabled witout needed module (postgresql 9.6) enabled
        Scenarios: no modules enabled at all, only rhn-tools module enabled, module not present in the database enabled
        All of these should result in no updates found
        """
        updates = self.updates_api.process_list(2, self.gen_pkg_json(PKG_NEVRAS[0], test_data[1]))
        assert updates
        assert not updates['update_list'][PKG_NEVRAS[0]]['available_updates']
