"""Unit tests for utils module."""
# pylint: disable=no-self-use

import re

from test.conftest import TestBase

import utils


class TestUtils(TestBase):
    """Unit test utils."""

    NEVRA_RE = re.compile(r"(.*)-(([0-9]+):)?([^-]+)-([^-]+)\.([a-z0-9_]+)")

    def _is_nevra(self, nevra):
        """Check is provided nevra string is nevra."""
        return bool(self.NEVRA_RE.match(nevra))

    def test_join_pkgname(self):
        """Test joining package name"""
        pkg_name = utils.join_packagename("test", "2", "1.2", "4.el7", "x86_64")
        assert pkg_name == "test-2:1.2-4.el7.x86_64"

    # pylint: disable=unused-argument
    # load_cache is pytest fixture
    def test_pkgidlist2packages(self, load_cache):
        """Test making NEVRA from package id."""
        pkgid_list = [1, 2]
        nevras = utils.pkgidlist2packages(self.cache, pkgid_list)
        for nevra in nevras:
            assert self._is_nevra(nevra)

    def test_split_packagename(self):
        """Test splitting package name into N,E,V,R,A."""
        pkg_name = "bash-0:4.2.46-20.el7_2.x86_64.rpm"
        name, epoch, version, release, arch = utils.split_packagename(pkg_name)
        assert name == "bash"
        assert epoch == "0"
        assert version == "4.2.46"
        assert release == "20.el7_2"
        assert arch == "x86_64"

    def test_none2empty(self):
        """Test 'None' to "" conversion."""
        assert utils.none2empty(None) == ""

    def test_none_page_number(self):
        """Test pagination - page=page_size=None."""
        __, page_info = utils.paginate([], None, None)
        assert page_info["page"] == utils.DEFAULT_PAGE
        assert page_info["page_size"] == utils.DEFAULT_PAGE_SIZE

    def test_negative_page_number(self):
        """Test pagination - page=-1 page_size=0."""
        __, page_info = utils.paginate([], -1, 0)
        assert page_info["page"] == utils.DEFAULT_PAGE
        assert page_info["page_size"] == utils.DEFAULT_PAGE_SIZE

    def test_page_number(self):
        """Test pagination."""
        __, page_info = utils.paginate([], 2, 5)
        assert page_info["page"] == 2
        assert page_info["page_size"] == 5
