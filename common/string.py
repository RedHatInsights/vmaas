"""
Utilities for string operations.
"""


def text_strip(elem):
    """Stripped text of element but check if it's None."""
    if elem is None or elem.text is None:
        return None
    return elem.text.strip()
