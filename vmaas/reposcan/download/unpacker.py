"""
Module containing classes for decompressing files.
"""
import os
import gzip
import lzma
import bz2
import tarfile
from pathlib import Path

import zstandard as zstd

from vmaas.common.logging_utils import ProgressLogger, get_logger
from vmaas.common.fileutil import remove_file_if_exists


DEFAULT_CHUNK_SIZE = "1048576"


class FileUnpacker:
    """
    Class unpacking queued files.
    Files to unpack are collected and then all unpacked at once into their locations.
    Gz, Xz, Bz2, Zst formats are supported.
    """

    def __init__(self):
        self.queue = []
        self.logger = get_logger(__name__)
        self.chunk_size = int(os.getenv('CHUNK_SIZE', DEFAULT_CHUNK_SIZE))
        self.progress_logger = ProgressLogger(self.logger, 0)

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
        if file_path.endswith(".zst"):
            return zstd.open
        return None

    @staticmethod
    def get_unpacked_file_path(file_path):
        """Get unpacked file path for supported archive type."""
        file_path_endings = (".gz", ".xz", ".bz2", ".zst")
        if file_path.endswith(file_path_endings):
            file_path = file_path.rsplit(".", maxsplit=1)[0]
        return file_path

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
            remove_file_if_exists(file_path)
            self.progress_logger.update(source=file_path, target=unpacked_file_path)
        else:
            self.progress_logger.update(source=file_path, target="(unknown archive format)")

    def run(self):
        """Unpack all queued file paths."""
        self.progress_logger.reset(len(self.queue))
        self.logger.info("Unpacking started.")
        for file_path in self.queue:
            self._unpack(file_path)
        # Make queue empty to be able to reuse this class multiple times in one run
        self.queue = []
        self.logger.info("Unpacking finished.")


class TarZstUnpacker:
    """
    Class unpacking single .tar.zst archive. Supports specifying list of files to unpack for very large archives.
    """

    def __init__(self, archive_path: Path):
        self.logger = get_logger(__name__)
        self.archive_path = archive_path
        self.output_dir = os.path.dirname(archive_path)

    def _extract(self, tar, member, files_to_extract: set = None):
        if files_to_extract is None or member.name in files_to_extract:
            tar.extract(member, path=self.output_dir, filter="data")
            self.logger.debug("Extracting: %s", member.name)
            if files_to_extract is not None:
                files_to_extract.remove(member.name)

    def run(self, files_to_extract: set = None):
        """Unpack all files or specified files from tar."""
        self.logger.info("Unpacking started.")
        decompressor = zstd.ZstdDecompressor()
        with open(self.archive_path, 'rb') as file_h:
            with decompressor.stream_reader(file_h) as decompressed_file_h:
                with tarfile.open(fileobj=decompressed_file_h, mode='r|') as tar:
                    for member in tar:
                        self._extract(tar, member, files_to_extract=files_to_extract)
                        if files_to_extract is not None and len(files_to_extract) == 0:
                            break

        if files_to_extract:
            self.logger.debug("Files not found in archive: %s", files_to_extract)
        self.logger.info("Unpacking finished.")
