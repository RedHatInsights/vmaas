"""
Tests for batch list module.
"""
import pytest
from common.batch_list import BatchList


class TestBatchList:
    """ Batch list tests group. """
    batch_list = None
    DUMMY_ITEMS = [{"item": 1}, {"item": 2}, {"item": 3}]

    @pytest.fixture(autouse=True)
    def setup_batch_list(self):
        """ Fixture for creating batch list. """
        self.batch_list = BatchList()

    def test_empty(self):
        """ Test for empty batch list. """
        assert self.batch_list.get_total_items() == 0

    def test_insert_few(self):
        """ Test for inserton of one item. """
        for item in self.DUMMY_ITEMS:
            self.batch_list.add_item(item)

        assert self.batch_list.get_total_items() == len(self.DUMMY_ITEMS)

    def test_insert_full_batch(self):
        """ Test for insertion of multiple items, until new batch needs to be created. """
        for count in range(0, 51):
            self.batch_list.add_item({"item": count})

        assert self.batch_list.get_total_items() == 51
        assert len(self.batch_list.batches) == 2
        assert len(self.batch_list.batches[0]) == 50
        assert len(self.batch_list.batches[1]) == 1

    def test_clear(self):
        """ Test for clearing the list. """
        for item in self.DUMMY_ITEMS:
            self.batch_list.add_item(item)

        self.batch_list.clear()
        assert self.batch_list.batches == []
