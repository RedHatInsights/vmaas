import os
import shutil
import tempfile
from datetime import datetime, timezone
from urllib.parse import urljoin

from cli.logger import SimpleLogger
from database.repository_store import RepositoryStore
from download.downloader import FileDownloader, DownloadItem, VALID_HTTP_CODES
from download.unpacker import FileUnpacker
from repodata.repomd import RepoMD, RepoMDTypeNotFound
from repodata.primary import PrimaryMD
from repodata.primary_db import PrimaryDatabaseMD
from repodata.updateinfo import UpdateInfoMD
from repodata.repository import Repository

REPOMD_PATH = "repodata/repomd.xml"
BATCH_SIZE = 100


class RepositoryController:
    def __init__(self):
        self.logger = SimpleLogger()
        self.downloader = FileDownloader()
        self.unpacker = FileUnpacker()
        self.repo_store = RepositoryStore()
        self.repository_batches = [[]]
        self.db_repositories = {}

    def _download_repomds(self, batch):
        download_items = []
        for repository in batch:
            repomd_url = urljoin(repository.repo_url, REPOMD_PATH)
            repository.tmp_directory = tempfile.mkdtemp(prefix="repo-")
            item = DownloadItem(
                source_url=repomd_url,
                target_path=os.path.join(repository.tmp_directory, "repomd.xml")
            )
            # Save for future status code check
            download_items.append(item)
            self.downloader.add(item)
        self.downloader.run()
        # Return failed downloads
        return {item.target_path: item.status_code for item in download_items
                if item.status_code not in VALID_HTTP_CODES}

    def _read_repomds(self, batch, failed):
        for repository in batch:
            repomd_path = os.path.join(repository.tmp_directory, "repomd.xml")
            if repomd_path not in failed:
                repomd = RepoMD(repomd_path)
                db_revision = self.db_repositories[repository.repo_url]["revision"]
                downloaded_revision = datetime.fromtimestamp(repomd.get_revision(), tz=timezone.utc)
                if downloaded_revision > db_revision:
                    repository.repomd = repomd
                else:
                    self.logger.log("Downloaded repo %s (%s) is not newer than repo in DB (%s)." %
                                    (repository.repo_url, str(downloaded_revision), str(db_revision)))
            else:
                self.logger.log("Download failed: %s (HTTP CODE %d)" % (urljoin(repository.repo_url, REPOMD_PATH),
                                failed[repomd_path]))

    def _download_metadata(self, batch):
        for repository in batch:
            if repository.repomd:
                try:
                    repository.md_files["primary_db"] = repository.repomd.get_metadata("primary_db")["location"]
                except RepoMDTypeNotFound:
                    repository.md_files["primary"] = repository.repomd.get_metadata("primary")["location"]
                try:
                    repository.md_files["updateinfo"] = repository.repomd.get_metadata("updateinfo")["location"]
                except RepoMDTypeNotFound:
                    pass

            for md_location in repository.md_files.values():
                self.downloader.add(DownloadItem(
                    source_url=urljoin(repository.repo_url, md_location),
                    target_path=os.path.join(repository.tmp_directory, os.path.basename(md_location))
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

    @staticmethod
    def _load_metadata(repository):
        for md_type in repository.md_files:
            if md_type == "primary_db":
                repository.primary = PrimaryDatabaseMD(repository.md_files["primary_db"])
            elif md_type == "primary":
                repository.primary = PrimaryMD(repository.md_files["primary"])
            elif md_type == "updateinfo":
                repository.updateinfo = UpdateInfoMD(repository.md_files["updateinfo"])

    @staticmethod
    def _unload_metadata(repository):
        repository.primary = None
        repository.updateinfo = None

    def clean_repodata(self, batch):
        for repository in batch:
            if repository.tmp_directory:
                shutil.rmtree(repository.tmp_directory)
                repository.tmp_directory = None

    def add_repository(self, repo_url):
        repo_url = repo_url.strip()
        if not repo_url.endswith("/"):
            repo_url += "/"
        # Get last batch and append repository to it
        last_batch = self.repository_batches[-1]
        if len(last_batch) >= BATCH_SIZE:
            last_batch = []
            self.repository_batches.append(last_batch)
        last_batch.append(Repository(repo_url))

    def store(self):
        # Fetch current list of repositories from DB
        self.db_repositories = self.repo_store.list_repositories()
        for batch in self.repository_batches:
            failed = self._download_repomds(batch)
            self._read_repomds(batch, failed)
            self._download_metadata(batch)
            self._unpack_metadata(batch)
            for repository in batch:
                self._load_metadata(repository)
                self.repo_store.store(repository)
                self._unload_metadata(repository)
            self.clean_repodata(batch)
