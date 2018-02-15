"""
Unit test classes for logger module.
"""
import sys
import unittest
from io import StringIO

from cli.logger import SimpleLogger


class TestSimpleLogger(unittest.TestCase):
    """Test writing messages to stdout and stderr using SimpleLogger."""
    def setUp(self):
        self.logger = SimpleLogger()
        self.old_stdout = sys.stdout
        self.old_stderr = sys.stderr
        sys.stdout = StringIO()
        sys.stderr = StringIO()

    def test_stdout(self):
        """Write message to stdout and read it back."""
        msg = "test message to stdout"
        self.logger.log(msg)
        sys.stdout.seek(0)
        output = sys.stdout.read().strip()
        self.assertEqual(msg, output)

    def test_stderr(self):
        """Write message to stderr and read it back."""
        msg = "test message to stderr"
        self.logger.errlog(msg)
        sys.stderr.seek(0)
        output = sys.stderr.read().strip()
        self.assertEqual(msg, output)

    def tearDown(self):
        sys.stdout = self.old_stdout
        sys.stderr = self.old_stderr
