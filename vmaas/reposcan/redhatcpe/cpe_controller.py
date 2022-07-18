"""
Module holds CPE metadata import workflow - downloading, unpacking, etc.
"""

import json
import os
import shutil
import tempfile

from vmaas.common.logging_utils import get_logger
from vmaas.reposcan.database.cpe_store import CpeStore
from vmaas.reposcan.download.downloader import FileDownloader, DownloadItem, VALID_HTTP_CODES
from vmaas.reposcan.mnm import FAILED_CPE_METADATA
from vmaas.reposcan.redhatcpe.cpe_dict import CpeDict

CPE_DICT_URL = os.getenv('CPE_DICT_URL', 'https://www.redhat.com/security/data/metrics/cpe-dictionary.xml')
REPO_TO_CPE_URL = os.getenv('REPO_TO_CPE_URL', 'https://www.redhat.com/security/data/metrics/repository-to-cpe.json')


class CpeController:
    """
    Controls import/sync of CPE metadata into the DB.
    """

    def __init__(self):
        self.logger = get_logger(__name__)
        self.downloader = FileDownloader()
        self.cpe_store = CpeStore()
        self.tmp_directory = tempfile.mkdtemp(prefix="cpe-")

    def _cpe_dict_path(self):
        return os.path.join(self.tmp_directory, 'cpe-dictionary.xml')

    def _repo_mapping_path(self):
        return os.path.join(self.tmp_directory, 'repository-to-cpe.json')

    def _download(self):
        cpe_dict_item = DownloadItem(source_url=CPE_DICT_URL,
                                     target_path=self._cpe_dict_path())
        repo_mapping_item = DownloadItem(source_url=REPO_TO_CPE_URL,
                                         target_path=self._repo_mapping_path())
        download_items = [cpe_dict_item, repo_mapping_item]
        for item in download_items:
            self.downloader.add(item)
        self.downloader.run()
        return {item.target_path: item.status_code for item in download_items
                if item.status_code not in VALID_HTTP_CODES}

    def _load(self):
        cpe_dict = CpeDict(self._cpe_dict_path())
        with open(self._repo_mapping_path(), 'r', encoding='utf8') as repo_mapping_file:
            repo_mapping = json.load(repo_mapping_file)
        return cpe_dict, repo_mapping

    def clean(self):
        """Clean downloaded files for given batch."""
        if self.tmp_directory:
            shutil.rmtree(self.tmp_directory)
            self.tmp_directory = None

    def store(self):
        """Sync CPE metadata."""
        self.logger.info("Checking CPE metadata.")
        try:
            # Download all files first
            failed = self._download()
            for path in failed:
                FAILED_CPE_METADATA.inc()
                self.logger.warning("Download failed: %s (HTTP CODE %d)", path, failed[path])

            cpe_dict, repo_mapping = self._load()
            self.cpe_store.store(cpe_dict, repo_mapping)
        finally:
            self.clean()
