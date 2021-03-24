"""
Module containing class for syncing set of OVAL files into the DB.
"""
import os
import shutil
import tempfile
import json

from common.batch_list import BatchList
from common.logging_utils import get_logger
from common.dateutil import parse_datetime

from database.oval_store import OvalStore
from download.downloader import FileDownloader, DownloadItem, VALID_HTTP_CODES
from download.unpacker import FileUnpacker
from mnm import FAILED_IMPORT_OVAL
from redhatoval.definitions_file import OvalDefinitions

OVAL_FEED_BASE_URL = os.getenv("OVAL_FEED_BASE_URL", "https://www.redhat.com/security/data/oval/v2/")


class OvalController:
    """
    Class for importing/syncing set of OVAL files into the DB.
    First, OVAL data from repository are downloaded and parsed.
    Second, they are synced to the DB.
    """

    def __init__(self):
        self.logger = get_logger(__name__)
        self.downloader = FileDownloader()
        self.downloader.num_threads = 1  # rh.com returns 403 when downloading too quickly (DDoS protection?)
        self.unpacker = FileUnpacker()
        self.oval_store = OvalStore()
        self.tmp_directory = tempfile.mkdtemp(prefix="oval-")
        self.feed_path = os.path.join(self.tmp_directory, "feed.json")

    def _download_feed(self):
        item = DownloadItem(
            source_url=f"{OVAL_FEED_BASE_URL}feed.json",
            target_path=self.feed_path
        )
        # Save for future status code check
        download_items = [item]
        self.downloader.add(item)
        self.downloader.run()
        # Return failed downloads
        return {item.target_path: item.status_code for item in download_items
                if item.status_code not in VALID_HTTP_CODES}

    def _download_definitions(self, batch):
        download_items = []
        for oval_file in batch:
            os.makedirs(os.path.dirname(oval_file.local_path), exist_ok=True)  # Make sure subdirs exist
            item = DownloadItem(
                source_url=oval_file.url,
                target_path=oval_file.local_path
            )
            # Save for future status code check
            download_items.append(item)
            self.downloader.add(item)
        self.downloader.run()
        # Return failed downloads
        return {item.target_path: item.status_code for item in download_items
                if item.status_code not in VALID_HTTP_CODES}

    def _unpack_definitions(self, batch):
        for oval_file in batch:
            self.unpacker.add(oval_file.local_path)
            oval_file.local_path = self.unpacker.get_unpacked_file_path(oval_file.local_path)
        self.unpacker.run()

    def clean(self):
        """Clean downloaded files for given batch."""
        if self.tmp_directory:
            shutil.rmtree(self.tmp_directory)
            self.tmp_directory = None

    def store(self):  # pylint: disable=too-many-branches,too-many-statements
        """Sync all OVAL feeds. Process files in batches due to disk space and memory usage."""
        self.logger.info("Checking OVAL feed.")
        failed = self._download_feed()
        if failed:
            for path in failed:
                FAILED_IMPORT_OVAL.inc()
                self.logger.warning("OVAL feed failed to download, %s (HTTP CODE %d).", path, failed[path])
            self.clean()
            return

        db_oval_definitions = self.oval_store.list_oval_definitions()
        batches = BatchList()
        up_to_date = 0

        # Filter out all not updated OVAL definition files
        with open(self.feed_path, 'r') as feed_file:
            feed = json.load(feed_file)
        for entry in feed["feed"]["entry"]:
            db_timestamp = db_oval_definitions.get(entry['id'])
            feed_timestamp = parse_datetime(entry["updated"])
            if not db_timestamp or feed_timestamp > db_timestamp:
                local_path = os.path.join(self.tmp_directory, entry["content"]["src"].replace(OVAL_FEED_BASE_URL, ""))
                oval_definitions_file = OvalDefinitions(entry["id"], feed_timestamp,
                                                        entry["content"]["src"], local_path)
                batches.add_item(oval_definitions_file)
            else:
                up_to_date += 1
        feed_updated = parse_datetime(feed["feed"]["updated"])

        self.logger.info("%d OVAL definition files are up to date.", up_to_date)
        total_oval_files = batches.get_total_items()
        completed_oval_files = 0
        self.logger.info("%d OVAL definition files need to be synced.", total_oval_files)

        try:
            for batch in batches:
                self.logger.info("Syncing a batch of %d OVAL definition files", len(batch))
                failed = self._download_definitions(batch)
                if failed:
                    self.logger.warning("%d OVAL definition files failed to download.", len(failed))
                    batch = [oval_file for oval_file in batch if oval_file.local_path not in failed]
                self._unpack_definitions(batch)
                for oval_definitions_file in batch:
                    completed_oval_files += 1
                    try:
                        oval_definitions_file.load_metadata()
                        self.logger.info("Syncing OVAL definition file: %s [%s/%s]", oval_definitions_file.oval_id,
                                         completed_oval_files, total_oval_files)
                        self.oval_store.store(oval_definitions_file)
                    finally:
                        oval_definitions_file.unload_metadata()
            # Timestamp of main feed file
            self.oval_store.save_lastmodified(feed_updated)
        finally:
            self.clean()
