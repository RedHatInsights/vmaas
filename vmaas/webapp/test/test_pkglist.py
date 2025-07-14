"""Unit tests for pkglist module."""
# pylint: disable=unused-argument

import pytest

from vmaas.webapp.test import schemas
from vmaas.webapp.test.conftest import TestBase
from vmaas.webapp.pkglist import PkgListAPI


class TestPkgListAPI(TestBase):
    """Test PkgListAPI api class."""

    pkglist_api = None

    @pytest.fixture(autouse=True)
    def setup_api(self, load_cache):
        """Setup PkgListAPI object."""
        self.pkglist_api = PkgListAPI(self.cache)

    def test_schema(self):
        """Test response schema."""
        response = self.pkglist_api.process_list(3, {})
        schemas.pkglist_list_schema.validate(response)

    def test_fetch_all_packages(self):
        """Test response without 'modified_since' input argument."""
        response = self.pkglist_api.process_list(3, {})
        assert len(response['package_list']) == 13
        assert response['total'] == 13
        assert response['page'] == 1
        assert response['pages'] == 1
        assert response['page_size'] == 13

    def test_fetch_with_modified_since(self):
        """Test response with 'modified_since' input argument."""
        response = self.pkglist_api.process_list(3, {'modified_since': '2020-10-15T00:00:00+00:00'})
        pkg_list = response['package_list']
        assert len(pkg_list) == 3
        assert pkg_list[0]['nevra'] == 'my-pkg-1.2.0-1.el8.i686'
        assert pkg_list[1]['nevra'] == 'my-pkg-1.1.0-1.el8.src'
        assert pkg_list[2]['nevra'] == 'kernel-4.18.0-80.el8.x86_64'
        assert 'modified' not in pkg_list[0]  # 'modified' attribute not included by default
        assert response['total'] == 3
        assert response['page'] == 1
        assert response['pages'] == 1
        assert response['page_size'] == 3

    def test_page_size(self):
        """Test pagination usage."""
        response = self.pkglist_api.process_list(3, {'page_size': 4})
        assert len(response['package_list']) == 4
        assert response['total'] == 13
        assert response['page'] == 1
        assert response['pages'] == 4
        assert response['page_size'] == 4

    def test_return_modified(self):
        """Test optional "modified" attribute return."""
        response = self.pkglist_api.process_list(3, {'return_modified': True})
        assert response['package_list'][0]['modified'] == '2020-10-10T01:02:03+00:00'
