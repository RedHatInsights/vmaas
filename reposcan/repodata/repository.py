"""
Module containing class for aggregating repository metadata.
"""
from cli.logger import SimpleLogger
from repodata.primary import PrimaryMD
from repodata.primary_db import PrimaryDatabaseMD
from repodata.updateinfo import UpdateInfoMD


class Repository:
    """
    Class aggregating information about metadata files available in repository.
    """
    def __init__(self, repo_url):
        self.logger = SimpleLogger()
        self.repo_url = repo_url
        self.repomd = None
        self.primary = None
        self.updateinfo = None
        self.md_files = {}
        self.tmp_directory = None

    def get_package_count(self):
        """Returns package count in repository (from primary XML or SQLite if available)."""
        if self.primary:
            return self.primary.get_package_count()
        return 0

    def get_update_count(self, update_type=None):
        """Returns updates count in repository (from updateinfo XML if available)."""
        return len(self.list_updates(update_type=update_type))

    def list_packages(self):
        """List packages in repository (from primary XML or SQLite if available)"""
        if self.primary:
            return self.primary.list_packages()
        return []

    def list_updates(self, update_type=None):
        """Returns updates in repository (from updateinfo XML if available)."""
        if self.updateinfo:
            if update_type:
                return [u for u in self.updateinfo.list_updates() if u["type"] == update_type]
            return self.updateinfo.list_updates()
        return []

    def load_metadata(self):
        """Parse available metadata files into memory."""
        for md_type in self.md_files:
            if md_type == "primary_db":
                self.primary = PrimaryDatabaseMD(self.md_files["primary_db"])
            elif md_type == "primary":
                self.primary = PrimaryMD(self.md_files["primary"])
            elif md_type == "updateinfo":
                self.updateinfo = UpdateInfoMD(self.md_files["updateinfo"])

    def unload_metadata(self):
        """Unset previously loaded metadata files from this object."""
        self.primary = None
        self.updateinfo = None
