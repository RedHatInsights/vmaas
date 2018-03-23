"""
Unit test classes for repository module.
"""
import unittest
from repodata.primary import PrimaryMD
from repodata.primary_db import PrimaryDatabaseMD
from repodata.updateinfo import UpdateInfoMD
from repodata.repository import Repository
from repodata.test.test_updateinfo import KNOWN_UPDATE_TYPES


class TestRepository(unittest.TestCase):
    """Test Repository class."""
    def setUp(self):
        """Setup example files."""
        primary_db = PrimaryDatabaseMD("test_data/repodata/primary_db.sqlite")
        primary = PrimaryMD("test_data/repodata/primary.xml")
        updateinfo = UpdateInfoMD("test_data/repodata/updateinfo.xml")

        self.repository = Repository("repo_url", "content_set", "x86_64", "27")
        self.repository.primary = primary_db
        self.repository.updateinfo = updateinfo
        self.repository_without_updateinfo = Repository("repo_url", "content_set", "x86_64", "27")
        self.repository_without_updateinfo.primary = primary_db
        self.repository_primary_xml = Repository("repo_url", "content_set", "x86_64", "27")
        self.repository_primary_xml.primary = primary
        self.repository_primary_xml.updateinfo = updateinfo

    def test_counting(self):
        """Test counts of packages from parsed primary and primary_db."""
        # Package count should be same in all repositories
        self.assertGreater(self.repository.get_package_count(), 0)
        self.assertGreater(self.repository_without_updateinfo.get_package_count(), 0)
        self.assertEqual(self.repository.get_package_count(), self.repository_primary_xml.get_package_count())
        self.assertEqual(self.repository.get_package_count(), self.repository_without_updateinfo.get_package_count())

        # Only repository with updateinfo has more than 0 updates
        self.assertGreater(self.repository.get_update_count(), 0)
        self.assertEqual(self.repository_without_updateinfo.get_update_count(), 0)

        # Re-count updates of all known types
        update_sum = 0
        for update_type in KNOWN_UPDATE_TYPES:
            cnt = self.repository.get_update_count(update_type=update_type)
            update_sum += cnt
        self.assertEqual(update_sum, self.repository.get_update_count())

        # Repository without updateinfo returns 0 regardless of specified update type
        for update_type in KNOWN_UPDATE_TYPES:
            self.assertEqual(self.repository_without_updateinfo.get_update_count(update_type=update_type), 0)

    def test_listing(self):
        """Test package and update methods."""
        self.assertEqual(len(self.repository.list_packages()), self.repository.get_package_count())
        self.assertEqual(len(self.repository.list_updates()), self.repository.get_update_count())
