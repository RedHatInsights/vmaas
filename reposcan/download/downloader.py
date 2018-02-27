"""
Module containing classes for downloading files using HTTP.
"""
from threading import Thread
from queue import Queue, Empty
import requests
from cli.logger import SimpleLogger

CHUNK_SIZE = 1048576
THREADS = 8
VALID_HTTP_CODES = [200]


class DownloadItem: # pylint: disable=too-few-public-methods
    """
    Basic download structure storing source HTTP URL, target file path where to save downloaded file
    and result HTTP status code of the download operation.
    """
    # pylint: disable=too-many-arguments
    def __init__(self, source_url=None, target_path=None, ca_cert=None, cert=None, key=None):
        self.source_url = source_url
        self.target_path = target_path
        self.ca_cert = ca_cert
        self.cert = cert
        self.key = key
        self.status_code = None


class FileDownloadThread(Thread):
    """
    Single thread for downloading files. After it's created, it processes DownloadItem objects from queue shared
    between all threads. Thread will end when shared queue is empty.
    """
    def __init__(self, queue, logger):
        Thread.__init__(self)
        self.queue = queue
        self.session = requests.Session()
        self.logger = logger

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
            with self.session.get(download_item.source_url, verify=verify, cert=cert, stream=True) as response:
                while True:
                    chunk = response.raw.read(CHUNK_SIZE, decode_content=False)
                    if chunk == b"":
                        break
                    file_handle.write(chunk)
                download_item.status_code = response.status_code

    def run(self):
        """Method executed after thread start. Downloads items from shared queue as long as there are any."""
        while not self.queue.empty():
            try:
                download_item = self.queue.get(block=False)
            except Empty:
                break
            self._download(download_item)
            self.queue.task_done()
            self.logger.log("%s -> %s" % (download_item.source_url, download_item.target_path))

        self.session.close()


class FileDownloader:
    """
    Main downloader class. Contains queue of items to download. Once download is triggered, certain number
    of download threads is created. Downloader is waiting until download queue is empty and all child threads
    are finished.
    """
    def __init__(self):
        self.queue = Queue()
        self.logger = SimpleLogger()

    def add(self, download_item):
        """Add DownloadItem object into the queue."""
        self.queue.put(download_item)

    def run(self):
        """Start processing download queue using multiple threads."""
        self.logger.log("Downloading started.")
        threads = []
        for i in range(min(THREADS, self.queue.qsize())):
            self.logger.log("Starting thread %d." % i)
            thread = FileDownloadThread(self.queue, self.logger)
            thread.setDaemon(True)
            thread.start()
            threads.append(thread)

        for i, thread in enumerate(threads):
            thread.join()
            self.logger.log("Stopping thread %d." % i)
        self.logger.log("Downloading finished.")
