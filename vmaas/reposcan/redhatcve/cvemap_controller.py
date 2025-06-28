"""
Module holds CVE map import workflow - downloading, unpacking, etc.
"""

import os
import shutil
import tempfile

from vmaas.common.date_utils import parse_datetime, now
from vmaas.common.logging_utils import get_logger
from vmaas.reposcan.database.cvemap_store import CvemapStore
from vmaas.reposcan.download.downloader import FileDownloader, DownloadItem, VALID_HTTP_CODES
from vmaas.reposcan.katello import KATELLO_URL, KATELLO_CA_CERT_PATH
from vmaas.reposcan.mnm import FAILED_CVEMAP
from vmaas.reposcan.redhatcve.cvemap import CvemapHead, CvemapBody

URL = os.getenv('REDHAT_CVEMAP_URL',
                'https://www.redhat.com/security/data/metrics/cvemap.xml')


class CvemapController:
    """
    Controls import/sync of CVE map into the DB.
    """

    def __init__(self):
        self.logger = get_logger(__name__)
        self.downloader = FileDownloader()
        self.cvemap_store = CvemapStore()
        self.updated = False
        self.lastmodified = None
        self.tmp_directory = tempfile.mkdtemp(prefix="cvemap-")

    def _tmp_head(self):
        return os.path.join(self.tmp_directory, 'cvemap.head')

    def _tmp_xml(self):
        return os.path.join(self.tmp_directory, 'cvemap.xml')

    @staticmethod
    def _get_ca_cert() -> str | None:
        if KATELLO_URL and URL.startswith(KATELLO_URL) and os.path.isfile(KATELLO_CA_CERT_PATH):
            return KATELLO_CA_CERT_PATH
        return None

    def _download_head(self):
        item = DownloadItem(source_url=URL,
                            target_path=self._tmp_head(),
                            ca_cert=self._get_ca_cert())
        download_items = [item]
        self.downloader.add(item)
        self.downloader.run(headers_only=True)
        return {item.target_path: item.status_code for item in download_items
                if item.status_code not in VALID_HTTP_CODES}

    def _read_head(self, failed):
        """Reads downloaded meta files and checks for updates."""
        header_path = self._tmp_head()
        if not failed:
            header = CvemapHead(header_path)
            # already synced before?
            db_lastmodified = parse_datetime(self.cvemap_store.lastmodified())
            self.lastmodified = parse_datetime(header.get_lastmodified())
            # if header doesn't have last-modified
            if self.lastmodified is None:
                self.lastmodified = now()
            # synced for the first time or has newer revision
            if (db_lastmodified is None
                    or self.lastmodified > db_lastmodified):
                self.updated = True
            else:
                self.logger.info("Cve map has not been updated (since %s).",
                                 str(db_lastmodified))
        else:
            FAILED_CVEMAP.inc()
            self.logger.warning("Download failed: %s (HTTP CODE %d)", URL, failed[header_path])

    def _download_xml(self):
        self.downloader.add(DownloadItem(source_url=URL,
                                         target_path=self._tmp_xml(),
                                         ca_cert=self._get_ca_cert()))
        self.downloader.run()

    def _load_xml(self, lastmodified):
        return CvemapBody(self._tmp_xml(), lastmodified)

    def clean(self):
        """Clean downloaded files for given batch."""
        if self.tmp_directory:
            shutil.rmtree(self.tmp_directory)
            self.tmp_directory = None

    def store(self):
        """Sync CVE map."""
        self.logger.info("Checking CVE map.")

        # Download all repomd files first
        failed = self._download_head()
        if failed:
            FAILED_CVEMAP.inc()
            self.logger.warning("Cve map failed to download.")
        self._read_head(failed)

        try:
            if self.updated:
                # Download and process cvemap
                self._download_xml()
                cvemap = self._load_xml(self.lastmodified)
                self.cvemap_store.store(cvemap)
        finally:
            self.clean()
