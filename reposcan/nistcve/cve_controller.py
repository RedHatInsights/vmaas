"""
Module holds CVE list import workflow - downloading, unpacking, etc.
"""

import shutil
import tempfile
import time
from datetime import datetime

from cli.logger import SimpleLogger
from common.batch_list import BatchList
from database.cverepo_store import CveRepoStore
from download.downloader import FileDownloader, DownloadItem, VALID_HTTP_CODES
from download.unpacker import FileUnpacker
from nistcve.cvemeta import CveMeta
from nistcve.cverepo import CveRepo

YEAR_SINCE = 2017

class CveRepoController:
    """
    Controls import/sync of CVE lists into the DB.
    """
    def __init__(self):
        self.logger = SimpleLogger()
        self.downloader = FileDownloader()
        self.unpacker = FileUnpacker()
        self.cverepo_store = CveRepoStore()
        self.repos = set()
        self.db_lastmodified = {}

    def _download_meta(self):
        download_items = []
        for repo in self.repos:
            repo.tmp_directory = tempfile.mkdtemp(prefix="cverepo-")
            item = DownloadItem(
                source_url=repo.meta_url(),
                target_path=repo.meta_tmp()
            )
            # Save for future status code check
            download_items.append(item)
            self.downloader.add(item)
        self.downloader.run()
        # Return failed downloads
        return {item.target_path: item.status_code for item in download_items
                if item.status_code not in VALID_HTTP_CODES}

    def _read_meta(self, failed):
        """Reads downloaded meta files and checks for updates."""
        for repo in self.repos:
            meta_path = repo.meta_tmp()
            if meta_path not in failed:
                meta = CveMeta(meta_path)
                # already synced before?
                db_lastmodified = _dt_strptime(self.db_lastmodified.get(repo.label, None))
                meta_lastmodified = _dt_strptime(meta.get_lastmodified())
                # synced for the first time or has newer revision
                if (db_lastmodified is None
                        or meta_lastmodified is None
                        or meta_lastmodified > db_lastmodified):
                    repo.meta = meta
                else:
                    self.logger.log("Cve list '%s' has not been updated (since %s)." %
                                    (repo.label, str(db_lastmodified)))
            else:
                self.logger.log("Download failed: %s (HTTP CODE %d)" % (repo.meta_url(),
                                                                        failed[meta_path]))

    def _download_json(self, batch):
        for repo in batch:
            self.downloader.add(DownloadItem(source_url=repo.json_url(),
                                             target_path=repo.json_tmpgz()))
        self.downloader.run()

    def _unpack_json(self, batch):
        for repo in batch:
            self.unpacker.add(repo.json_tmpgz())
        self.unpacker.run()

    def clean_repo(self, batch):
        """Clean downloaded files for given batch."""
        for repo in batch:
            if repo.tmp_directory:
                shutil.rmtree(repo.tmp_directory)
                repo.tmp_directory = None
            self.repos.remove(repo)

    def add_repos(self):
        """Generate urls for CVE lists to download."""
        # Fetch current list of repositories from DB
        self.db_lastmodified = self.cverepo_store.list_lastmodified()

        # CVE files for single years should be used only for initial load
        labels = [str(y) for y in range(YEAR_SINCE, int(time.strftime("%Y"))+1)]
        for label in labels:
            if label not in self.db_lastmodified:
                self.repos.add(CveRepo(label))

        # always import incremental changes
        labels = ['recent', 'modified']
        for label in labels:
            self.repos.add(CveRepo(label))

    def store(self):
        """Sync all queued CVE lists. Runs in batches due to disk space and memory usage."""
        self.logger.log("Checking %d CVE lists." % len(self.repos))

        # Download all repomd files first
        failed = self._download_meta()
        self.logger.log("%d meta files failed to download." % len(failed))
        self._read_meta(failed)

        # filter out failed / unchanged lists
        batches = BatchList()
        to_skip = []
        for repo in self.repos:
            if repo.meta:
                batches.add_item(repo)
            else:
                to_skip.append(repo)
        self.clean_repo(to_skip)
        self.logger.log("%d CVE lists skipped." % len(to_skip))
        self.logger.log("Syncing %d CVE lists." % sum(len(l) for l in batches))

        # Download and process repositories in batches (unpacked metadata files can consume lot of disk space)
        for batch in batches:
            self._download_json(batch)
            self._unpack_json(batch)
            for repo in batch:
                repo.load_json()
                self.cverepo_store.store(repo)
                repo.unload_json()
            self.clean_repo(batch)

def _dt_strptime(tstr):
    # remove ':' from timezone
    if tstr is not None:
        tstr = tstr[:22] + tstr[23:]
        return datetime.strptime(tstr, "%Y-%m-%dT%H:%M:%S%z")
    return None
