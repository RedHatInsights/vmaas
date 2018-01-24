import os
import shutil
import tempfile
from urllib.parse import urljoin

from cli.logger import SimpleLogger
from database.repository_store import RepositoryStore
from download.downloader import FileDownloader, DownloadItem
from download.unpacker import FileUnpacker
from repodata.repomd import RepoMD, RepoMDTypeNotFound
from repodata.primary import PrimaryMD
from repodata.primary_db import PrimaryDatabaseMD
from repodata.updateinfo import UpdateInfoMD
from repodata.repository import Repository

REPOMD_PATH = "repodata/repomd.xml"


class RepositoryController:
    def __init__(self):
        self.logger = SimpleLogger()
        self.downloader = FileDownloader()
        self.unpacker = FileUnpacker()
        self.repo_store = RepositoryStore()
        self.repositories = []

    def _download_repomds(self):
        for repository in self.repositories:
            repomd_url = urljoin(repository.repo_url, REPOMD_PATH)
            repository.tmp_directory = tempfile.mkdtemp(prefix="repo-")
            self.downloader.add(DownloadItem(
                source_url=repomd_url,
                target_path=os.path.join(repository.tmp_directory, "repomd.xml")
            ))
        self.downloader.run()

    def _read_repomds(self):
        for repository in self.repositories:
            repository.repomd = RepoMD(os.path.join(repository.tmp_directory, "repomd.xml"))

    def _download_metadata(self):
        for repository in self.repositories:
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

    def _unpack_metadata(self):
        for repository in self.repositories:
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

    def clean_repodata(self):
        for repository in self.repositories:
            if repository.tmp_directory:
                shutil.rmtree(repository.tmp_directory)
                repository.tmp_directory = None

    def add_repository(self, repo_url):
        if not repo_url.endswith("/"):
            repo_url += "/"
        self.repositories.append(Repository(repo_url))

    def store(self):
        self._download_repomds()
        self._read_repomds()
        self._download_metadata()
        self._unpack_metadata()
        for repository in self.repositories:
            self._load_metadata(repository)
            self.repo_store.store(repository)
            self._unload_metadata(repository)
        self.clean_repodata()
