"""
Module for different commonly usable algorithms.
"""


def find_index(data: list, item, key=lambda m: m):
    """
    Find index for a new item in a ascended sorted list
    :param data: Collection to search in
    :param item: New data item
    :param key: Function to get value for a data collection member, by default a member itself.
    :return: Result index
    """

    i = _find_index_range(data, 0, len(data), item, key)
    return i


def _find_index_range(data: list, i_start: int, i_end: int, item, key=lambda m: m):
    if i_start >= i_end:
        return i_start

    if key(data[i_start]) >= item:
        return i_start

    i_mid = (i_start + i_end) // 2
    if key(data[i_mid]) >= item:
        return _find_index_range(data, i_start, i_mid, item, key)
    return _find_index_range(data, i_mid + 1, i_end, item, key)
