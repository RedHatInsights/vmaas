"""
Module containing classes for decompressing files.
"""
import os
import gzip
import lzma
import bz2

from common.logging import get_logger

DEFAULT_CHUNK_SIZE = "1048576"



class FileUnpacker:
    """
    Class unpacking queued files.
    Files to unpack are collected and then all unpacked at once into their locations.
    Gz, Xz, Bz2 formats are supported.
    """
    def __init__(self):
        self.queue = []
        self.logger = get_logger(__name__)
        self.chunk_size = int(os.getenv('CHUNK_SIZE', DEFAULT_CHUNK_SIZE))

    def add(self, file_path):
        """Add compressed file path to queue."""
        self.queue.append(file_path)

    @staticmethod
    def _get_unpack_func(file_path):
        if file_path.endswith(".gz"):
            return gzip.open
        if file_path.endswith(".xz"):
            return lzma.open
        if file_path.endswith(".bz2"):
            return bz2.open
        return None

    def _unpack(self, file_path):
        unpack_func = self._get_unpack_func(file_path)
        if unpack_func:
            with unpack_func(file_path, "rb") as packed:
                unpacked_file_path = file_path.rsplit(".", maxsplit=1)[0]
                with open(unpacked_file_path, "wb") as unpacked:
                    while True:
                        chunk = packed.read(self.chunk_size)
                        if chunk == b"":
                            break
                        unpacked.write(chunk)
            os.unlink(file_path)
            self.logger.info("%s -> %s", file_path, unpacked_file_path)
        else:
            self.logger.info("%s skipped.", file_path)

    def run(self):
        """Unpack all queued file paths."""
        self.logger.info("Unpacking started.")
        for file_path in self.queue:
            self._unpack(file_path)
        # Make queue empty to be able to reuse this class multiple times in one run
        self.queue = []
        self.logger.info("Unpacking finished.")
