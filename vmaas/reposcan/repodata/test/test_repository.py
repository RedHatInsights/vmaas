"""
Unit test classes for repository module.
"""
from vmaas.reposcan.repodata.primary import PrimaryMD
from vmaas.reposcan.repodata.primary_db import PrimaryDatabaseMD
from vmaas.reposcan.repodata.updateinfo import UpdateInfoMD
from vmaas.reposcan.repodata.modules import ModuleMD
from vmaas.reposcan.repodata.repository import Repository
from vmaas.reposcan.repodata.test.test_updateinfo import KNOWN_UPDATE_TYPES
from vmaas.reposcan.reposcan import DEFAULT_ORG_NAME

PRIMARY_SQLITE_PATH = "test_data/repodata/primary_db.sqlite"
PRIMARY_XML_PATH = "test_data/repodata/primary.xml"
UPDATEINFO_XML_PATH = "test_data/repodata/updateinfo.xml"
MODULES_YAML_PATH = "test_data/repodata/modules.yaml"


class TestRepository:
    """Test Repository class."""

    PRIMARY_DB = PrimaryDatabaseMD(PRIMARY_SQLITE_PATH)
    PRIMARY = PrimaryMD(PRIMARY_XML_PATH)
    UPDATEINFO = UpdateInfoMD(UPDATEINFO_XML_PATH)
    MODULES = ModuleMD(MODULES_YAML_PATH)

    REPOSITORY = Repository("repo_url", "content_set", "x86_64", "27", DEFAULT_ORG_NAME)
    REPOSITORY.primary = PRIMARY_DB
    REPOSITORY.updateinfo = UPDATEINFO
    REPOSITORY.modules = MODULES
    REPOSITORY_WITHOUT_UPDATEINFO = Repository("repo_url", "content_set", "x86_64", "27", DEFAULT_ORG_NAME)
    REPOSITORY_WITHOUT_UPDATEINFO.primary = PRIMARY_DB
    REPOSITORY_PRIMARY_XML = Repository("repo_url", "content_set", "x86_64", "27", DEFAULT_ORG_NAME)
    REPOSITORY_PRIMARY_XML.primary = PRIMARY
    REPOSITORY_PRIMARY_XML.updateinfo = UPDATEINFO

    def test_counting(self):
        """Test counts of packages from parsed primary and primary_db."""
        # Package count should be same in all repositories
        assert self.REPOSITORY.get_package_count() > 0
        assert self.REPOSITORY_WITHOUT_UPDATEINFO.get_package_count() > 0
        assert self.REPOSITORY.get_package_count() == self.REPOSITORY_PRIMARY_XML.get_package_count()
        assert self.REPOSITORY.get_package_count() == self.REPOSITORY_WITHOUT_UPDATEINFO.get_package_count()

        # Only repository with updateinfo has more than 0 updates
        assert self.REPOSITORY.get_update_count() > 0
        assert self.REPOSITORY_WITHOUT_UPDATEINFO.get_update_count() == 0

        # Re-count updates of all known types
        update_sum = 0
        for update_type in KNOWN_UPDATE_TYPES:
            cnt = self.REPOSITORY.get_update_count(update_type=update_type)
            update_sum += cnt
        assert update_sum == self.REPOSITORY.get_update_count()

        # Repository without updateinfo returns 0 regardless of specified update type
        for update_type in KNOWN_UPDATE_TYPES:
            assert self.REPOSITORY_WITHOUT_UPDATEINFO.get_update_count(update_type=update_type) == 0

    def test_listing(self):
        """Test package and update methods."""
        assert len(self.REPOSITORY.list_packages()) == 12
        assert self.REPOSITORY.get_package_count() == 12

        assert len(self.REPOSITORY.list_updates()) == 9
        assert self.REPOSITORY.get_update_count() == 9

        assert len(self.REPOSITORY.list_modules()) == 2

    def test_load_metadata(self):
        """Test package and update methods."""
        repo = Repository(repo_url="", content_set="", basearch="", releasever="", organization=DEFAULT_ORG_NAME)
        assert not repo.md_files
        assert repo.primary is None
        assert repo.updateinfo is None
        assert repo.modules is None
        repo.md_files = {
            "primary_db": PRIMARY_SQLITE_PATH,
            "primary": PRIMARY_XML_PATH,
            "updateinfo": UPDATEINFO_XML_PATH,
            "modules": MODULES_YAML_PATH,
        }
        repo.load_metadata()
        assert repo.primary is not None
        assert repo.updateinfo is not None
        assert repo.modules is not None

        repo.unload_metadata()
        assert repo.primary is None
        assert repo.updateinfo is None
        assert repo.modules is None
