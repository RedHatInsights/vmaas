"""
Unit test classes for repository module.
"""
import unittest
from repodata.primary import PrimaryMD
from repodata.primary_db import PrimaryDatabaseMD
from repodata.updateinfo import UpdateInfoMD
from repodata.modules import ModuleMD
from repodata.repository import Repository
from repodata.test.test_updateinfo import KNOWN_UPDATE_TYPES

PRIMARY_SQLITE_PATH = "test_data/repodata/primary_db.sqlite"
PRIMARY_XML_PATH = "test_data/repodata/primary.xml"
UPDATEINFO_XML_PATH = "test_data/repodata/updateinfo.xml"
MODULES_YAML_PATH = "test_data/repodata/modules.yaml"


class TestRepository(unittest.TestCase):
    """Test Repository class."""
    def setUp(self):
        """Setup example files."""
        primary_db = PrimaryDatabaseMD(PRIMARY_SQLITE_PATH)
        primary = PrimaryMD(PRIMARY_XML_PATH)
        updateinfo = UpdateInfoMD(UPDATEINFO_XML_PATH)
        modules = ModuleMD(MODULES_YAML_PATH)

        self.repository = Repository("repo_url", "content_set", "x86_64", "27")
        self.repository.primary = primary_db
        self.repository.updateinfo = updateinfo
        self.repository.modules = modules
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
        self.assertEqual(12, len(self.repository.list_packages()))
        self.assertEqual(12, self.repository.get_package_count())

        self.assertEqual(9, len(self.repository.list_updates()))
        self.assertEqual(9, self.repository.get_update_count())

        self.assertEqual(2, len(self.repository.list_modules()))

    def test_load_metadata(self):
        """Test package and update methods."""
        repo = Repository(repo_url='', content_set='', basearch='', releasever='')
        self.assertEqual(repo.md_files, {})
        self.assertIsNone(repo.primary)
        self.assertIsNone(repo.updateinfo)
        self.assertIsNone(repo.modules)
        repo.md_files = dict(primary_db=PRIMARY_SQLITE_PATH, primary=PRIMARY_XML_PATH, updateinfo=UPDATEINFO_XML_PATH,
                             modules=MODULES_YAML_PATH)
        repo.load_metadata()
        self.assertIsNotNone(repo.primary)
        self.assertIsNotNone(repo.updateinfo)
        self.assertIsNotNone(repo.modules)

        repo.unload_metadata()
        self.assertIsNone(repo.primary)
        self.assertIsNone(repo.updateinfo)
        self.assertIsNone(repo.modules)
