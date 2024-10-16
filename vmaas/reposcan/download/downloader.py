"""
Module containing classes for downloading files using HTTP.
"""
import os
from threading import Thread
from queue import Queue, Empty
from pathlib import Path

from urllib3.exceptions import ProtocolError

import requests

from requests.exceptions import ConnectionError  # pylint: disable=redefined-builtin

from vmaas.common.logging_utils import ProgressLogger, get_logger

DEFAULT_CHUNK_SIZE = "1048576"
DEFAULT_THREADS = "8"
DEFAULT_RETRY_COUNT = "3"
VALID_HTTP_CODES = [200]

FAILED_THRESHOLD = 5


class DownloadItem:
    """
    Basic download structure storing source HTTP URL, target file path where to save downloaded file
    and result HTTP status code of the download operation.
    """

    def __init__(self, *, source_url: str | None = None, target_path: Path | None = None,
                 ca_cert: str | None = None, cert: str | None = None, key: str | None = None) -> None:
        self.source_url = source_url
        self.target_path = target_path
        self.ca_cert = ca_cert
        self.cert = cert
        self.key = key
        self.status_code = -2


class FileDownloadThread(Thread):
    """
    Single thread for downloading files. After it's created, it processes DownloadItem objects from queue shared
    between all threads. Thread will end when shared queue is empty.
    """

    def __init__(self, queue, logger, progress_logger, headers_only=False):
        Thread.__init__(self)
        self.queue = queue
        self.session = requests.Session()
        self.logger = logger
        self.progress_logger = progress_logger
        self.chunk_size = int(os.getenv('CHUNK_SIZE', DEFAULT_CHUNK_SIZE))
        self.retry_count = int(os.getenv('RETRY_COUNT', DEFAULT_RETRY_COUNT))
        self.headers_only = headers_only

    def _download(self, download_item):
        with open(download_item.target_path, "wb") as file_handle:
            # Specify the CA bundle file or use the default value - True
            if download_item.ca_cert:
                verify = download_item.ca_cert
            else:
                verify = True
            if download_item.cert:
                if download_item.key:
                    cert = (download_item.cert, download_item.key)
                else:
                    cert = download_item.cert
            else:
                cert = None

            req_args = {'url': download_item.source_url, 'verify': verify, 'cert': cert, 'stream': True,
                        'allow_redirects': True}
            if self.headers_only:
                with self.session.head(**req_args) as response:
                    headers = ["%s:%s" % (key, value)
                               for key, value in response.headers.items()]
                    file_handle.write(bytearray("\n".join(headers).encode('utf8')))
                    download_item.status_code = response.status_code
            else:
                with self.session.get(**req_args) as response:
                    while True:
                        chunk = response.raw.read(self.chunk_size, decode_content=True)
                        if chunk == b"":
                            break
                        file_handle.write(chunk)
                    download_item.status_code = response.status_code

    def _retry_download(self, download_item):
        for _ in range(self.retry_count):
            try:
                self._download(download_item)
                break
            except (ProtocolError, ConnectionError):
                self.logger.exception("Download of '%s' failed: ", download_item.source_url)
                download_item.status_code = -1

    def run(self):
        """Method executed after thread start. Downloads items from shared queue as long as there are any."""
        failed = 0
        while not self.queue.empty():
            try:
                download_item = self.queue.get(block=False)
            except Empty:
                break
            self._retry_download(download_item)
            self.progress_logger.update(source=download_item.source_url, target=download_item.target_path)
            self.queue.task_done()

            # Add mechanism to interrupt downloading when FAILED_THRESHOLD number of items failed to download.
            if download_item.status_code < 0:
                failed += 1
            else:
                failed = 0
            if failed >= FAILED_THRESHOLD:
                self.logger.error("Failed %d downloads in a row, interrupting download.", failed)
                break

        self.session.close()


class FileDownloader:
    """
    Main downloader class. Contains queue of items to download. Once download is triggered, certain number
    of download threads is created. Downloader is waiting until download queue is empty and all child threads
    are finished.
    """

    def __init__(self) -> None:
        self.queue = Queue()
        self.logger = get_logger(__name__)
        self.num_threads = int(os.getenv('THREADS', DEFAULT_THREADS))

    def add(self, download_item: DownloadItem) -> None:
        """Add DownloadItem object into the queue."""
        self.queue.put(download_item)

    def run(self, headers_only: bool = False) -> None:
        """Start processing download queue using multiple threads."""
        progress_logger = ProgressLogger(self.logger, self.queue.qsize())
        self.logger.info("Downloading started.")
        threads = []
        for i in range(min(self.num_threads, self.queue.qsize())):
            self.logger.debug("Starting thread %d.", i)
            thread = FileDownloadThread(self.queue, self.logger, progress_logger, headers_only)
            thread.daemon = True
            thread.start()
            threads.append(thread)

        for i, thread in enumerate(threads):
            thread.join()
            self.logger.debug("Stopping thread %d.", i)
        self.logger.info("Downloading finished.")
