"""
Module containing class for syncing set of repositories into the DB.
"""
import os
import shutil
import tempfile
from urllib.parse import urljoin

from cli.logger import SimpleLogger
from common.batch_list import BatchList

from database.repository_store import RepositoryStore
from download.downloader import FileDownloader, DownloadItem, VALID_HTTP_CODES
from download.unpacker import FileUnpacker
from repodata.repomd import RepoMD, RepoMDTypeNotFound
from repodata.repository import Repository

REPOMD_PATH = "repodata/repomd.xml"


class RepositoryController:
    """
    Class for importing/syncing set of repositories into the DB.
    First, repomd from all repositories are downloaded and parsed.
    Second, primary and updateinfo repodata from repositories needing update are downloaded, parsed and imported.
    """
    def __init__(self):
        self.logger = SimpleLogger()
        self.downloader = FileDownloader()
        self.unpacker = FileUnpacker()
        self.repo_store = RepositoryStore()
        self.repositories = set()
        self.certs_tmp_directory = None
        self.certs_files = {}

    def _get_certs_tuple(self, name):
        if name in self.certs_files:
            return self.certs_files[name]["ca_cert"], self.certs_files[name]["cert"], self.certs_files[name]["key"]
        return None, None, None

    def _download_repomds(self):
        download_items = []
        for repository in self.repositories:
            repomd_url = urljoin(repository.repo_url, REPOMD_PATH)
            repository.tmp_directory = tempfile.mkdtemp(prefix="repo-")
            ca_cert, cert, key = self._get_certs_tuple(repository.cert_name)
            item = DownloadItem(
                source_url=repomd_url,
                target_path=os.path.join(repository.tmp_directory, "repomd.xml"),
                ca_cert=ca_cert,
                cert=cert,
                key=key
            )
            # Save for future status code check
            download_items.append(item)
            self.downloader.add(item)
        self.downloader.run()
        # Return failed downloads
        return {item.target_path: item.status_code for item in download_items
                if item.status_code not in VALID_HTTP_CODES}

    def _read_repomds(self, failed):
        """Reads all downloaded repomd files. Checks if their download failed and checks if their metadata are
           newer than metadata currently in DB.
        """
        # Fetch current list of repositories from DB
        db_repositories = self.repo_store.list_repositories()
        for repository in self.repositories:
            repomd_path = os.path.join(repository.tmp_directory, "repomd.xml")
            if repomd_path not in failed:
                repomd = RepoMD(repomd_path)
                # Was repository already synced before?
                repository_key = (repository.content_set, repository.basearch, repository.releasever)
                if repository_key in db_repositories:
                    db_revision = db_repositories[repository_key]["revision"]
                else:
                    db_revision = None
                downloaded_revision = repomd.get_revision()
                # Repository is synced for the first time or has newer revision
                if db_revision is None or downloaded_revision > db_revision:
                    repository.repomd = repomd
                else:
                    self.logger.log("Downloaded repo %s (%s) is not newer than repo in DB (%s)." %
                                    (", ".join(repository_key), str(downloaded_revision), str(db_revision)))
            else:
                self.logger.log("Download failed: %s (HTTP CODE %d)" % (urljoin(repository.repo_url, REPOMD_PATH),
                                                                        failed[repomd_path]))

    def _download_metadata(self, batch):
        for repository in batch:
            # primary_db has higher priority, use primary.xml if not found
            try:
                repository.md_files["primary_db"] = repository.repomd.get_metadata("primary_db")["location"]
            except RepoMDTypeNotFound:
                repository.md_files["primary"] = repository.repomd.get_metadata("primary")["location"]
            # updateinfo.xml may be missing completely
            try:
                repository.md_files["updateinfo"] = repository.repomd.get_metadata("updateinfo")["location"]
            except RepoMDTypeNotFound:
                pass

            # queue metadata files for download
            for md_location in repository.md_files.values():
                ca_cert, cert, key = self._get_certs_tuple(repository.cert_name)
                self.downloader.add(DownloadItem(
                    source_url=urljoin(repository.repo_url, md_location),
                    target_path=os.path.join(repository.tmp_directory, os.path.basename(md_location)),
                    ca_cert=ca_cert,
                    cert=cert,
                    key=key
                ))
        self.downloader.run()

    def _unpack_metadata(self, batch):
        for repository in batch:
            for md_type in repository.md_files:
                self.unpacker.add(os.path.join(repository.tmp_directory,
                                               os.path.basename(repository.md_files[md_type])))
                # FIXME: this should be done in different place?
                repository.md_files[md_type] = os.path.join(
                    repository.tmp_directory,
                    os.path.basename(repository.md_files[md_type])).rsplit(".", maxsplit=1)[0]
        self.unpacker.run()

    def clean_repodata(self, batch):
        """Clean downloaded repodata of all repositories in batch."""
        for repository in batch:
            if repository.tmp_directory:
                shutil.rmtree(repository.tmp_directory)
                repository.tmp_directory = None
            self.repositories.remove(repository)

    def _clean_certificate_cache(self):
        if self.certs_tmp_directory:
            shutil.rmtree(self.certs_tmp_directory)
            self.certs_tmp_directory = None
            self.certs_files = {}

    def add_synced_repositories(self):
        """Queue all previously synced repositories."""
        repos = self.repo_store.list_repositories()
        for (content_set, basearch, releasever), repo_dict in repos.items():
            # Reference content_set_label -> content set id
            self.repo_store.content_set_to_db_id[content_set] = repo_dict["content_set_id"]
            self.repositories.add(Repository(repo_dict["url"], content_set, basearch, releasever,
                                             cert_name=repo_dict["cert_name"], ca_cert=repo_dict["ca_cert"],
                                             cert=repo_dict["cert"], key=repo_dict["key"]))

    # pylint: disable=too-many-arguments
    def add_repository(self, repo_url, content_set, basearch, releasever,
                       cert_name=None, ca_cert=None, cert=None, key=None):
        """Queue repository to import/check updates."""
        repo_url = repo_url.strip()
        if not repo_url.endswith("/"):
            repo_url += "/"
        self.repositories.add(Repository(repo_url, content_set, basearch, releasever, cert_name=cert_name,
                                         ca_cert=ca_cert, cert=cert, key=key))

    def _write_certificate_cache(self):
        certs = {}
        for repository in self.repositories:
            if repository.cert_name:
                certs[repository.cert_name] = {"ca_cert": repository.ca_cert, "cert": repository.cert,
                                               "key": repository.key}
        if certs:
            self.certs_tmp_directory = tempfile.mkdtemp(prefix="certs-")
            for cert_name in certs:
                self.certs_files[cert_name] = {}
                for cert_type in ["ca_cert", "cert", "key"]:
                    # Cert is not None
                    if certs[cert_name][cert_type]:
                        cert_path = os.path.join(self.certs_tmp_directory, "%s.%s" % (cert_name, cert_type))
                        with open(cert_path, "w") as cert_file:
                            cert_file.write(certs[cert_name][cert_type])
                        self.certs_files[cert_name][cert_type] = cert_path
                    else:
                        self.certs_files[cert_name][cert_type] = None

    def store(self):
        """Sync all queued repositories. Process repositories in batches due to disk space and memory usage."""
        self.logger.log("Checking %d repositories." % len(self.repositories))

        self._write_certificate_cache()

        # Download all repomd files first
        failed = self._download_repomds()
        self.logger.log("%d repomd.xml files failed to download." % len(failed))
        self._read_repomds(failed)

        # Filter all repositories without repomd attribute set (failed download, downloaded repomd is not newer)
        batches = BatchList()
        to_skip = []
        for repository in self.repositories:
            if repository.repomd:
                batches.add_item(repository)
            else:
                to_skip.append(repository)
        self.clean_repodata(to_skip)
        self.logger.log("%d repositories skipped." % len(to_skip))
        self.logger.log("Syncing %d repositories." % sum(len(l) for l in batches))

        # Download and process repositories in batches (unpacked metadata files can consume lot of disk space)
        for batch in batches:
            self._download_metadata(batch)
            self._unpack_metadata(batch)
            for repository in batch:
                repository.load_metadata()
                self.repo_store.store(repository)
                repository.unload_metadata()
            self.clean_repodata(batch)

        self._clean_certificate_cache()
