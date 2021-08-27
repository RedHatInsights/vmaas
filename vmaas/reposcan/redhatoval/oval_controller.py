"""
Module containing class for syncing set of OVAL files into the DB.
"""
import os
import shutil
import tempfile
import json
import re
from distutils.util import strtobool

from vmaas.common.batch_list import BatchList
from vmaas.common.logging_utils import get_logger
from vmaas.common.dateutil import parse_datetime

from vmaas.reposcan.database.oval_store import OvalStore
from vmaas.reposcan.download.downloader import FileDownloader, DownloadItem, VALID_HTTP_CODES
from vmaas.reposcan.download.unpacker import FileUnpacker
from vmaas.reposcan.mnm import FAILED_IMPORT_OVAL
from vmaas.reposcan.redhatoval.definitions_file import OvalDefinitions

OVAL_FEED_BASE_URL = os.getenv("OVAL_FEED_BASE_URL", "https://www.redhat.com/security/data/oval/v2/")
OVAL_WITH_UNPATCHED_FILTER = strtobool(os.getenv("OVAL_WITH_UNPATCHED_FILTER", "TRUE"))
# comma-separated keywords to filter out
OVAL_LABEL_FILTER = os.getenv("OVAL_LABEL_FILTER", "RHEL5,rhel-7-alt").split(",")


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

    @staticmethod
    def _skip_oval_definition_file(definition_file, feed_oval_files):
        for keyword in OVAL_LABEL_FILTER:
            if keyword in definition_file:
                return True
        if OVAL_WITH_UNPATCHED_FILTER:
            file_name_parts = definition_file.split(".oval.xml")
            file_name_parts[0] += "-including-unpatched"
            unpatched_file_name = ".oval.xml".join(file_name_parts)
            if unpatched_file_name in feed_oval_files:
                return True
        return False

    def _find_oval_file_by_regex(self, oval_id_regex):
        if not oval_id_regex.startswith('^'):
            oval_id_regex = '^' + oval_id_regex

        if not oval_id_regex.endswith('$'):
            oval_id_regex = oval_id_regex + '$'

        return [oval_id for oval_id in self.oval_store.oval_file_map
                if re.match(oval_id_regex, oval_id)]

    def delete_oval_file(self, oval_id_in):
        """
        Deletes oval file from DB.
        """
        oval_ids = set()
        for oval_id in oval_id_in:
            oval_ids.update(self._find_oval_file_by_regex(oval_id))
        for oval_id in oval_ids:
            self.logger.info("Deleting OVAL file: %s", oval_id)
            self.oval_store.delete_oval_file(oval_id)

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

        db_oval_files = self.oval_store.oval_file_map.copy()
        batches = BatchList()
        up_to_date = 0

        # Filter out all not updated OVAL definition files
        with open(self.feed_path, 'r') as feed_file:
            feed = json.load(feed_file)
        feed_oval_files = {entry["id"]: entry for entry in feed["feed"]["entry"]}
        for entry in feed_oval_files.values():
            if self._skip_oval_definition_file(entry['id'], feed_oval_files):
                continue
            db_timestamp = db_oval_files.get(entry['id'])
            feed_timestamp = parse_datetime(entry["updated"])
            if not db_timestamp or feed_timestamp > db_timestamp[1]:
                local_path = os.path.join(self.tmp_directory, entry["content"]["src"].replace(OVAL_FEED_BASE_URL, ""))
                oval_definitions_file = OvalDefinitions(entry["id"], feed_timestamp,
                                                        entry["content"]["src"], local_path)
                batches.add_item(oval_definitions_file)
            else:
                up_to_date += 1
            db_oval_files.pop(entry["id"], None)
        feed_updated = parse_datetime(feed["feed"]["updated"])

        self.logger.info("%d OVAL definition files are up to date.", up_to_date)
        total_oval_files = batches.get_total_items()
        completed_oval_files = 0
        self.logger.info("%d OVAL definition files need to be synced.", total_oval_files)

        for oval_definition_file in db_oval_files:
            self.logger.warning("OVAL definition file is filtered or obsolete and should be removed manually: %s",
                                oval_definition_file)

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
