"""
Module used for pagination inside webapp-utils.
"""

import math

DEFAULT_PAGE = 1
DEFAULT_PAGE_SIZE = 1000
MAX_PAGE_SIZE = 2000


def paginate(input_list, page, page_size):
    """Split input list into pages and return only requested page."""
    def _validate_num(num, default):
        try:
            num = int(num)
            if num <= 0:
                num = default
            if num >= MAX_PAGE_SIZE:
                num = MAX_PAGE_SIZE
        except (TypeError, ValueError):
            num = default
        return num
    page = _validate_num(page, DEFAULT_PAGE)
    page_size = _validate_num(page_size, DEFAULT_PAGE_SIZE)
    input_list.sort()
    start = (page-1)*page_size
    end = page*page_size
    pages = int(math.ceil(float(len(input_list))/page_size))
    result_list = input_list[start:end]
    return result_list, {"page": page, "page_size": len(result_list), "pages": pages}
