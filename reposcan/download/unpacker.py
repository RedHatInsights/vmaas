import os
import gzip
import lzma
import bz2
from cli.logger import SimpleLogger

CHUNK_SIZE = 1048576


class FileUnpacker:
    def __init__(self):
        self.queue = []
        self.logger = SimpleLogger()

    def add(self, file_path):
        self.queue.append(file_path)

    @staticmethod
    def _get_unpack_func(file_path):
        if file_path.endswith(".gz"):
            return gzip.open
        elif file_path.endswith(".xz"):
            return lzma.open
        elif file_path.endswith(".bz2"):
            return bz2.open
        else:
            return None

    def _unpack(self, file_path):
        unpack_func = self._get_unpack_func(file_path)
        if unpack_func:
            with unpack_func(file_path, "rb") as packed:
                unpacked_file_path = file_path.rsplit(".", maxsplit=1)[0]
                with open(unpacked_file_path, "wb") as unpacked:
                    while True:
                        chunk = packed.read(CHUNK_SIZE)
                        if chunk == b"":
                            break
                        unpacked.write(chunk)
            os.unlink(file_path)
            self.logger.log("%s -> %s" % (file_path, unpacked_file_path))
        else:
            self.logger.log("%s skipped.")

    def run(self):
        self.logger.log("Unpacking started.")
        for file_path in self.queue:
            self._unpack(file_path)
        self.logger.log("Unpacking finished.")
