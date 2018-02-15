"""
Module containing classes for logging to stdout/stderr/files.
"""

import sys
from threading import Lock


class SimpleLogger:
    """Print thread-safely input text to stdout.
    """
    def __init__(self):
        self.lock = Lock()

    @staticmethod
    def _write(text, stream):
        stream.write("%s\n" % text)
        stream.flush()

    def log(self, text):
        """Log given string to stdout."""
        self.lock.acquire()
        self._write(text, sys.stdout)
        self.lock.release()

    def errlog(self, text):
        """Log given string to stderr."""
        self.lock.acquire()
        self._write(text, sys.stderr)
        self.lock.release()
