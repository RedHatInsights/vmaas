"""
Module containing class for aggregating repository metadata.
"""
from vmaas.reposcan.repodata.modules import ModuleMD
from vmaas.reposcan.repodata.primary import PrimaryMD
from vmaas.reposcan.repodata.primary_db import PrimaryDatabaseMD
from vmaas.reposcan.repodata.updateinfo import UpdateInfoMD


class Repository:
    """
    Class aggregating information about metadata files available in repository.
    """
    # pylint: disable=too-many-instance-attributes

    def __init__(self, repo_url, content_set, basearch, releasever, organization, *,  # pylint: disable=too-many-positional-arguments
                 cert_name=None, ca_cert=None, cert=None, key=None):
        self.repo_url = repo_url
        self.repomd = None
        self.primary = None
        self.updateinfo = None
        self.modules = None
        self.md_files = {}
        self.tmp_directory = None
        self.content_set = content_set
        self.basearch = basearch
        self.releasever = releasever
        self.organization = organization
        self.cert_name = cert_name
        self.ca_cert = ca_cert
        self.cert = cert
        self.key = key

    def get_package_count(self):
        """Returns package count in repository (from primary XML or SQLite if available)."""
        if self.primary:
            return self.primary.get_package_count()
        return 0

    def get_update_count(self, update_type=None):
        """Returns updates count in repository (from updateinfo XML if available)."""
        return len(self.list_updates(update_type=update_type))

    def list_modules(self):
        """List modules in repository (from modules.yaml if available)"""
        if self.modules:
            return self.modules.list_modules()
        return []

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
            elif md_type == "modules":
                self.modules = ModuleMD(self.md_files["modules"])

    def unload_metadata(self):
        """Unset previously loaded metadata files from this object."""
        self.primary = None
        self.updateinfo = None
        self.modules = None

    def get_revision(self):
        """Returns revision field of parsed repomd file if available."""
        if self.repomd:
            return self.repomd.get_revision()
        return None
