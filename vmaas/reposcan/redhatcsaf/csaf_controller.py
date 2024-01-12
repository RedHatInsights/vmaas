"""
Module containing class for syncing set of CSAF files into the DB.
"""
import os
import shutil
import tempfile
from pathlib import Path

from vmaas.common.batch_list import BatchList
from vmaas.common.logging_utils import get_logger
from vmaas.common.strtobool import strtobool
from vmaas.reposcan.database.csaf_store import CsafStore
from vmaas.reposcan.download.downloader import DownloadItem
from vmaas.reposcan.download.downloader import FileDownloader
from vmaas.reposcan.download.downloader import VALID_HTTP_CODES
from vmaas.reposcan.mnm import CSAF_FAILED_DOWNLOAD
from vmaas.reposcan.redhatcsaf.modeling import CsafFileCollection

CSAF_VEX_BASE_URL = os.getenv("CSAF_VEX_BASE_URL", "https://access.redhat.com/security/data/csaf/beta/vex/")
CSAF_VEX_INDEX_CSV = os.getenv("CSAF_VEX_INDEX_CSV", "changes.csv")
CSAF_SYNC_ALL_FILES = strtobool(os.getenv("CSAF_SYNC_ALL_FILES", "true"))


class CsafController:
    """Class for importing/syncing set of CSAF files into DB."""

    def __init__(self):
        self.logger = get_logger(__name__)
        self.downloader = FileDownloader()
        self.downloader.num_threads = 1  # rh.com returns 403 when downloading too quickly (DDoS protection?)
        self.csaf_store = CsafStore()
        self.tmp_directory = Path(tempfile.mkdtemp(prefix="csaf-"))
        self.index_path = self.tmp_directory / CSAF_VEX_INDEX_CSV

    def _download_index(self) -> dict[str, int]:
        """Download CSAF index changes.csv file."""
        item = DownloadItem(source_url=CSAF_VEX_BASE_URL + CSAF_VEX_INDEX_CSV, target_path=self.index_path)
        self.downloader.add(item)
        self.downloader.run()
        # return failed download
        if item.status_code not in VALID_HTTP_CODES:
            return {item.target_path: item.status_code}
        return {}

    def _download_csaf_files(self, batch) -> dict[str, int]:
        """Download CSAF files."""
        download_items = []
        for csaf_file in batch:
            local_path = self.tmp_directory / csaf_file.name
            os.makedirs(os.path.dirname(local_path), exist_ok=True)  # Make sure subdirs exist
            item = DownloadItem(source_url=CSAF_VEX_BASE_URL + csaf_file.name, target_path=local_path)
            # Save for future status code check
            download_items.append(item)
            self.downloader.add(item)
        self.downloader.run()
        # Return failed downloads
        return {
            item.target_path: item.status_code for item in download_items if item.status_code not in VALID_HTTP_CODES
        }

    def clean(self):
        """Clean downloaded files for given batch."""
        if self.tmp_directory:
            shutil.rmtree(self.tmp_directory)
            self.tmp_directory = None

    def store(self):
        """Process and store CSAF objects to DB."""
        self.logger.info("Checking CSAF index.")
        failed = self._download_index()
        if failed:
            CSAF_FAILED_DOWNLOAD.inc()
            target, status = failed.popitem()
            self.logger.warning("CSAF index failed to download, %s (HTTP CODE %d).", target, status)
            self.clean()
            return

        db_csaf_files = self.csaf_store.csaf_file_map.copy()
        batches = BatchList()
        csaf_files = CsafFileCollection.from_table_map_and_csv(db_csaf_files, self.index_path)
        files_to_sync = csaf_files
        if not CSAF_SYNC_ALL_FILES:
            files_to_sync = csaf_files.out_of_date

        for csaf_file in files_to_sync:
            batches.add_item(csaf_file)

        self.logger.info("%d CSAF files.", len(csaf_files))
        self.logger.info("%d CSAF files need to be synced.", len(list(files_to_sync)))

        try:
            for i, batch in enumerate(batches, 1):
                self.logger.info("Syncing a batch of %d CSAF files [%d/%d]", len(batch), i, len(batches))
                failed = self._download_csaf_files(batch)
                if failed:
                    CSAF_FAILED_DOWNLOAD.inc(len(failed))
                    self.logger.warning("%d CSAF files failed to download.", len(failed))
                    batch = [f for f in batch if (self.tmp_directory / f.name) not in failed]

                to_store = CsafFileCollection()
                for csaf_file in batch:
                    to_store[csaf_file.name] = csaf_file
                    # TODO: processing of files

                self.csaf_store.store(to_store)
        finally:
            self.clean()
