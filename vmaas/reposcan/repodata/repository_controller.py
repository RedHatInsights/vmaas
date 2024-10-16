"""
Module containing class for syncing set of repositories into the DB.
"""
import os
import shutil
import tempfile
from datetime import datetime
from urllib.parse import urljoin
import re
from operator import attrgetter
from prometheus_client import Counter
from OpenSSL import crypto

from vmaas.common.batch_list import BatchList
from vmaas.common.logging_utils import get_logger

from vmaas.reposcan.database.repository_store import RepositoryStore
from vmaas.reposcan.download.downloader import FileDownloader, DownloadItem, VALID_HTTP_CODES
from vmaas.reposcan.download.unpacker import FileUnpacker
from vmaas.reposcan.mnm import FAILED_REPOMD, FAILED_IMPORT_REPO, FAILED_REPO_WITH_HTTP_CODE

from vmaas.reposcan.repodata.repomd import RepoMD, RepoMDTypeNotFound
from vmaas.reposcan.repodata.repository import Repository

REPOMD_PATH = "repodata/repomd.xml"
EXPIRATION_WARNING = Counter("certificate_expiration_warning", "Certificate expiration warning")


class RepositoryController:
    """
    Class for importing/syncing set of repositories into the DB.
    First, repomd from all repositories are downloaded and parsed.
    Second, primary and updateinfo repodata from repositories needing update are downloaded, parsed and imported.
    """

    def __init__(self):
        self.logger = get_logger(__name__)
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
        certs_tmp_dict = {}
        for repository in sorted(self.repositories, key=attrgetter("repo_url")):
            repomd_url = urljoin(repository.repo_url, REPOMD_PATH)
            repository.tmp_directory = tempfile.mkdtemp(prefix="repo-")
            ca_cert, cert, key = self._get_certs_tuple(repository.cert_name)
            # Check certificate expiration date
            if repository.cert_name:
                certs_tmp_dict[repository.cert_name] = repository.cert

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

        for cert_name, cert in certs_tmp_dict.items():
            self._check_cert_expiration_date(cert_name, cert)
        self.downloader.run()
        # Return failed downloads
        return {item.target_path: item.status_code for item in download_items
                if item.status_code not in VALID_HTTP_CODES}

    def _check_cert_expiration_date(self, cert_name, cert):
        try:
            # Load certificate
            loaded_cert = crypto.load_certificate(crypto.FILETYPE_PEM, cert)
            # Get expiration date and parse it to datetime object
            valid_to_dt = datetime.strptime(loaded_cert.get_notAfter().decode("utf-8"), "%Y%m%d%H%M%SZ")
            expire_in_days_td = (valid_to_dt - datetime.utcnow()).days
            if 30 >= expire_in_days_td > 0:
                self.logger.warning('Certificate %s will expire in %s days!', cert_name, expire_in_days_td)
                EXPIRATION_WARNING.inc()
            elif expire_in_days_td <= 0:
                self.logger.error('Certificate %s expired!', cert_name)
                EXPIRATION_WARNING.inc()
            else:
                self.logger.info('Certificate %s will expire in %s days.', cert_name, expire_in_days_td)
        except crypto.Error:
            self.logger.error('Certificate not provided or incorrect: %s', cert_name if cert_name else 'None')
            EXPIRATION_WARNING.inc()

    def _read_repomds(self):
        """Reads all downloaded repomd files. Checks if their download failed and checks if their metadata are
           newer than metadata currently in DB.
        """
        # Fetch current list of repositories from DB
        db_repositories = self.repo_store.list_repositories()
        for repository in sorted(self.repositories, key=attrgetter("repo_url")):
            repomd_path = os.path.join(repository.tmp_directory, "repomd.xml")
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
                self.logger.debug("Downloaded repo %s (%s) is not newer than repo in DB (%s).",
                                  ", ".join(filter(None, repository_key)), str(downloaded_revision), str(db_revision))

    def _repo_download_failed(self, repo, failed_items):
        failed = False
        for md_path in list(repo.md_files.values()) + [REPOMD_PATH]:
            local_path = os.path.join(repo.tmp_directory, os.path.basename(md_path))
            if local_path in failed_items:
                failed = True
                # Download errors with no HTTP code are logged in downloader, deduplicate error msgs
                if failed_items[local_path] > 0:
                    self.logger.warning("Download failed: LABEL: %s URL: %s (HTTP CODE %d)",
                                        repo.content_set, urljoin(repo.repo_url, md_path),
                                        failed_items[local_path])
                    FAILED_REPO_WITH_HTTP_CODE.labels(failed_items[local_path]).inc()
        return failed

    def _download_metadata(self, batch):
        download_items = []
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
            try:
                repository.md_files["modules"] = repository.repomd.get_metadata("modules")["location"]
            except RepoMDTypeNotFound:
                pass

            # queue metadata files for download
            for md_location in repository.md_files.values():
                ca_cert, cert, key = self._get_certs_tuple(repository.cert_name)
                item = DownloadItem(
                    source_url=urljoin(repository.repo_url, md_location),
                    target_path=os.path.join(repository.tmp_directory, os.path.basename(md_location)),
                    ca_cert=ca_cert,
                    cert=cert,
                    key=key
                )
                download_items.append(item)
                self.downloader.add(item)
        self.downloader.run()
        # Return failed downloads
        return {item.target_path: item.status_code for item in download_items
                if item.status_code not in VALID_HTTP_CODES}

    def _unpack_metadata(self, batch):
        for repository in batch:
            for md_type in repository.md_files:
                local_path = os.path.join(repository.tmp_directory, os.path.basename(repository.md_files[md_type]))
                self.unpacker.add(local_path)
                repository.md_files[md_type] = self.unpacker.get_unpacked_file_path(local_path)
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

    def add_db_repositories(self):
        """Queue all previously imported repositories."""
        repos = self.repo_store.list_repositories()
        for (content_set, basearch, releasever), repo_dict in repos.items():
            # Reference content_set_label -> content set id
            self.repo_store.content_set_to_db_id[content_set] = repo_dict["content_set_id"]
            self.repositories.add(Repository(repo_dict["url"], content_set, basearch, releasever,
                                             cert_name=repo_dict["cert_name"], ca_cert=repo_dict["ca_cert"],
                                             cert=repo_dict["cert"], key=repo_dict["key"]))

    def add_repository(self, repo_url, content_set, basearch, releasever, *,
                       cert_name=None, ca_cert=None, cert=None, key=None):
        """Queue repository to import/check updates."""
        repo_url = repo_url.strip()
        if not repo_url.endswith("/"):
            repo_url += "/"
        self.repositories.add(Repository(repo_url, content_set, basearch, releasever, cert_name=cert_name,
                                         ca_cert=ca_cert, cert=cert, key=key))

    def _write_certificate_cache(self):
        certs = {}
        for repository in sorted(self.repositories, key=attrgetter("repo_url")):
            if repository.cert_name:
                certs[repository.cert_name] = {"ca_cert": repository.ca_cert, "cert": repository.cert,
                                               "key": repository.key}
        if certs:
            self.certs_tmp_directory = tempfile.mkdtemp(prefix="certs-")
            for cert_name, cert_dict in certs.items():
                self.certs_files[cert_name] = {}
                for cert_type in ["ca_cert", "cert", "key"]:
                    # Cert is not None
                    if cert_dict[cert_type]:
                        cert_path = os.path.join(self.certs_tmp_directory, "%s.%s" % (cert_name, cert_type))
                        with open(cert_path, "w", encoding='utf8') as cert_file:
                            cert_file.write(cert_dict[cert_type])
                        self.certs_files[cert_name][cert_type] = cert_path
                    else:
                        self.certs_files[cert_name][cert_type] = None

    def _find_content_sets_by_regex(self, content_set_regex):
        if not content_set_regex.startswith('^'):
            content_set_regex = '^' + content_set_regex

        if not content_set_regex.endswith('$'):
            content_set_regex = content_set_regex + '$'

        return [content_set_label for content_set_label in self.repo_store.content_set_to_db_id
                if re.match(content_set_regex, content_set_label)]

    def delete_content_set(self, content_set_regex):
        """Deletes content sets described by given regex from DB."""
        for content_set_label in self._find_content_sets_by_regex(content_set_regex):
            self.logger.info("Deleting content set: %s", content_set_label)
            self.repo_store.delete_content_set(content_set_label, whole_content_set=True)
        self.repo_store.cleanup_unused_data()

    def delete_repos(self, repos):
        """Deletes repos (cs+basearch+releasever) from DB."""
        for content_set, basearch, releasever in repos:
            self.logger.info("Deleting repository: %s", ", ".join(
                filter(None, (content_set, basearch, releasever))))
            self.repo_store.delete_content_set(content_set, basearch=basearch, releasever=releasever)
        self.repo_store.cleanup_unused_data()

    def import_repositories(self):
        """Create or update repository records in the DB."""
        self.logger.info("Importing %d repositories.", len(self.repositories))
        failures = 0
        for repository in sorted(self.repositories, key=attrgetter("repo_url")):
            try:
                self.repo_store.import_repository(repository)
            except Exception:  # pylint: disable=broad-except
                failures += 1
        if failures > 0:
            self.logger.warning("Failed to import %d repositories.", failures)
            FAILED_IMPORT_REPO.inc(failures)

    # TODO: refactor - split to smaller functions
    def store(self):  # pylint: disable=too-many-branches,too-many-statements
        """Sync all queued repositories. Process repositories in batches due to disk space and memory usage."""
        self.logger.info("Checking %d repositories.", len(self.repositories))

        self._write_certificate_cache()

        # Download all repomd files first
        failed = self._download_repomds()
        if failed:
            FAILED_REPOMD.inc(len(failed))
            failed_repos = [repo for repo in sorted(self.repositories, key=attrgetter("repo_url"))
                            if self._repo_download_failed(repo, failed)]
            self.logger.warning("%d repomd.xml files failed to download.", len(failed))
            self.clean_repodata(failed_repos)

        self._read_repomds()
        # Filter all repositories without repomd attribute set (downloaded repomd is not newer)
        batches = BatchList()
        up_to_date = []

        def md_size(repomd, data_type):
            try:
                mdata = repomd.get_metadata(data_type)
                # open-size is not present for uncompressed files
                return int(mdata.get('size', 0)) + int(mdata.get('open-size', '0'))
            except RepoMDTypeNotFound:
                return 0

        for repository in sorted(self.repositories, key=attrgetter("repo_url")):
            if repository.repomd:

                repo_size = md_size(repository.repomd, 'primary_db')
                # If we use primary_db, we don't even download primary data xml
                if repo_size == 0:
                    repo_size += md_size(repository.repomd, 'primary')

                repo_size += md_size(repository.repomd, 'updateinfo')
                repo_size += md_size(repository.repomd, 'modules')

                batches.add_item(repository, repo_size)
            else:
                up_to_date.append(repository)

        self.clean_repodata(up_to_date)
        self.logger.info("%d repositories are up to date.", len(up_to_date))
        total_repositories = batches.get_total_items()
        completed_repositories = 0
        self.logger.info("%d repositories need to be synced.", total_repositories)

        # Download and process repositories in batches (unpacked metadata files can consume lot of disk space)
        try:  # pylint: disable=too-many-nested-blocks
            for batch in batches:
                self.logger.info("Syncing a batch of %d repositories", len(batch))
                try:
                    failed = self._download_metadata(batch)
                    if failed:
                        self.logger.warning("%d metadata files failed to download.", len(failed))
                        failed_repos = [repo for repo in batch if self._repo_download_failed(repo, failed)]
                        self.clean_repodata(failed_repos)
                        batch = [repo for repo in batch if repo not in failed_repos]
                    self._unpack_metadata(batch)
                    for repository in batch:
                        completed_repositories += 1
                        try:
                            repository.load_metadata()
                            self.logger.info("Syncing repository: %s [%s/%s]", ", ".join(
                                filter(None, (repository.content_set, repository.basearch, repository.releasever))),
                                completed_repositories, total_repositories)
                            self.repo_store.store(repository)
                        except Exception:  # pylint: disable=broad-except
                            self.logger.warning("Syncing repository failed: %s [%s/%s]", ", ".join(
                                filter(None, (repository.content_set, repository.basearch, repository.releasever))),
                                completed_repositories, total_repositories)
                            self.logger.exception("Exception: ")
                            FAILED_IMPORT_REPO.inc()
                        finally:
                            repository.unload_metadata()
                finally:
                    self.clean_repodata(batch)
        finally:
            self.repo_store.cleanup_unused_data()
            self._clean_certificate_cache()
