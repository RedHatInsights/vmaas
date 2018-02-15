"""
Module containing classes for logging to stdout/stderr/files.
"""

from threading import Lock


class SimpleLogger:
    """Print thread-safely input text to stdout.
    """

    def __init__(self):
        self.lock = Lock()

    def log(self, text):
        """Log given string to stdout."""
        self.lock.acquire()
        print(text)
        self.lock.release()
