from threading import Thread
from queue import Queue, Empty
import requests
from cli.logger import SimpleLogger

CHUNK_SIZE = 1048576
THREADS = 8


class DownloadItem:
    def __init__(self, source_url=None, target_path=None):
        self.source_url = source_url
        self.target_path = target_path


class FileDownloadThread(Thread):
    def __init__(self, queue, logger):
        Thread.__init__(self)
        self.queue = queue
        self.session = requests.Session()
        self.logger = logger

    def _download(self, source_url, target_path):
        with open(target_path, "wb") as file_handle:
            with self.session.get(source_url, stream=True) as response:
                while True:
                    chunk = response.raw.read(CHUNK_SIZE, decode_content=False)
                    if chunk == b"":
                        break
                    file_handle.write(chunk)

    def run(self):
        while not self.queue.empty():
            try:
                download_item = self.queue.get(block=False)
            except Empty:
                break
            self._download(download_item.source_url, download_item.target_path)
            self.queue.task_done()
            self.logger.log("%s -> %s" % (download_item.source_url, download_item.target_path))

        self.session.close()


class FileDownloader:
    def __init__(self):
        self.queue = Queue()
        self.logger = SimpleLogger()

    def add(self, download_item):
        self.queue.put(download_item)

    def run(self):
        self.logger.log("Downloading started.")
        threads = []
        for i in range(min(THREADS, self.queue.qsize())):
            self.logger.log("Starting thread %d." % i)
            thread = FileDownloadThread(self.queue, self.logger)
            thread.setDaemon(True)
            thread.start()
            threads.append(thread)

        for i, t in enumerate(threads):
            t.join()
            self.logger.log("Stopping thread %d." % i)
        self.logger.log("Downloading finished.")
