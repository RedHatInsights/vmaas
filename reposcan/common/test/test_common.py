"""Unit tests of common module."""
# pylint: disable=attribute-defined-outside-init, unused-argument, no-self-use

from datetime import datetime
import re
import math

import pytest

from common import string
from common import dateutil
from common.batch_list import BatchList, DEFAULT_BATCH_SIZE

DATETIME_OBJ = datetime.now()
DATETIME_ISO = datetime.now().isoformat()

RE_ISO = re.compile(r"[\d]{4}-[\d]{2}-[\d]{2}T[\d]{2}:[\d]{2}:[\d]{2}")

DATES = [("datetime_object", DATETIME_OBJ), ("datetime_iso", DATETIME_ISO)]


class TestString:
    """TestString class. Test string.py"""

    @pytest.fixture
    def setup(self):
        """String setup."""
        self.elem_none = None
        self.text = "   text   "

    def test_text_strip(self, setup):
        """Test text strip."""
        assert string.text_strip(self) == "text"

    def test_text_strip_none(self, setup):
        """Test text strip, when text is None."""
        assert not string.text_strip(None)
        self.text = None
        assert not string.text_strip(self)


class TestDateutil:
    """TestDateutil class for testing dateutil"""

    def test_parse_none(self):
        """Test parsing date = None."""
        assert dateutil.parse_datetime(None) is None

    def test_parse_string(self):
        """Test parsing datetime from string."""
        assert isinstance(dateutil.parse_datetime("2018-10-24 15:27:40.058353"), datetime)

    @pytest.mark.parametrize("date_param", DATES, ids=[d[0] for d in DATES])
    def test_datetime_to_iso(self, date_param):
        """Test formatting datetime to ISO format."""
        date = dateutil.format_datetime(date_param[1])
        assert isinstance(date, str)
        assert RE_ISO.match(date) is not None

    def test_tz_awareness(self):
        """Test if datetime is tz aware."""
        date = dateutil.now()
        assert date.tzinfo is not None
        assert date.tzinfo.utcoffset(date) is not None


class TestBatchList:
    """TestBatchList class. Test creating list of lists"""

    @pytest.fixture()
    def batchlist(self):
        """Setup for batchlist testing."""
        self.blist = BatchList()

    def test_empty_batch(self, batchlist):
        """Test empty batchlist."""
        assert not self.blist.batches

    @pytest.mark.parametrize("batch_size", [100, 150])
    def test_batch_creation(self, batchlist, batch_size):
        """Test creation of batch list."""
        for i in range(batch_size):
            self.blist.add_item(i)
        batch_num = math.ceil(batch_size / int(DEFAULT_BATCH_SIZE))
        assert len(self.blist.batches) == batch_num
        if batch_num > 1:
            num = int(DEFAULT_BATCH_SIZE)
            for i in range(batch_num):
                assert len(self.blist.batches[i]) == num
                num -= batch_size - num
        else:
            assert len(self.blist.batches[0]) == batch_size
