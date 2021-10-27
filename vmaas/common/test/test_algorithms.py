"""
Tests for "common.algorithms" module.
"""
from vmaas.common import algorithms


class TestAlgorithms:
    """Tests for "common.algorithms" module."""

    @staticmethod
    def test_find_index_1():
        """Test algorithms.find_index method."""
        arr = [1, 2, 3, 3, 4, 5, 6]
        i = algorithms.find_index(arr, 0)
        assert i == 0

    @staticmethod
    def test_find_index_2():
        """Test algorithms.find_index method."""
        arr = [1, 2, 3, 3, 4, 5, 6]
        i = algorithms.find_index(arr, 10)
        assert i == 7

    @staticmethod
    def test_find_index_3():
        """Test algorithms.find_index method."""
        arr = [1, 2, 3, 3, 4, 5, 6]
        i = algorithms.find_index(arr, 2.5)
        assert i == 2

    @staticmethod
    def test_find_index_4():
        """Test algorithms.find_index method."""
        arr = [1, 2, 3, 3, 4, 5, 6]
        i = algorithms.find_index(arr, 3)
        assert i == 2
