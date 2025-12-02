"""Unit tests of common module."""
# pylint: disable=attribute-defined-outside-init, unused-argument

from datetime import datetime
import re
import math

import pytest

from vmaas.common import string, date_utils
from vmaas.common.batch_list import BatchList, BATCH_MAX_SIZE, BATCH_MAX_FILESIZE

DATETIME_OBJ = datetime.now()
DATETIME_ISO = datetime.now().isoformat()

RE_ISO = re.compile(r"[\d]{4}-[\d]{2}-[\d]{2}T[\d]{2}:[\d]{2}:[\d]{2}")

DATES = [("datetime_object", DATETIME_OBJ), ("datetime_iso", DATETIME_ISO)]

ITEM_FILESIZES = [1, int(BATCH_MAX_FILESIZE) // 3, int(BATCH_MAX_FILESIZE) - 1]


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
        assert date_utils.parse_datetime(None) is None

    def test_parse_string(self):
        """Test parsing datetime from string."""
        assert isinstance(date_utils.parse_datetime("2018-10-24 15:27:40.058353"), datetime)

    @pytest.mark.parametrize("date_param", DATES, ids=[d[0] for d in DATES])
    def test_datetime_to_iso(self, date_param):
        """Test formatting datetime to ISO format."""
        date = date_utils.format_datetime(date_param[1])
        assert isinstance(date, str)
        assert RE_ISO.match(date) is not None

    def test_tz_awareness(self):
        """Test if datetime is tz aware."""
        date = date_utils.now()
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

    # Assuming default is 50, 102 = 3 batches, 50/50/2 ; 150 = 50/50/50; 157 == 4, 50/50/50/7
    # move thru the batches, making sure each other than the last is at most BATCH_MAX_SIZE long
    # and each batch has cumulative file_size less than BATCH_MAX_FILESIZE
    @pytest.mark.parametrize("list_size", [102, 150, 157])
    @pytest.mark.parametrize("item_filesize", ITEM_FILESIZES)
    def test_batch_creation(self, batchlist, list_size, item_filesize):
        """Test creation of batch list."""

        for i in range(list_size):
            self.blist.add_item(i, item_filesize)

        # batch size is variable, if items are too large, the batch might contain less than BATCH_MAX_SIZE items
        batch_size = min(int(BATCH_MAX_SIZE), int(BATCH_MAX_FILESIZE) // item_filesize)

        total_batches = math.ceil(list_size / batch_size)
        last_batch_size = list_size % batch_size
        assert len(self.blist.batches) == total_batches
        for curr_batch in range(total_batches):
            if curr_batch == (total_batches - 1) and last_batch_size > 0:
                expected_num_in_batch = last_batch_size
            else:
                expected_num_in_batch = batch_size
            assert len(self.blist.batches[curr_batch]) == expected_num_in_batch

    def test_invalid_batch_size(self, batchlist):
        """
        Test creation of an invalid batch list.
        Should fail because single item is larger than max batch size
        """
        with pytest.raises(ValueError):
            self.test_batch_creation(batchlist, 102, int(BATCH_MAX_FILESIZE) + 1)
