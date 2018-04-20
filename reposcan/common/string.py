"""
Utilities for string operations.
"""


def strip(text):
    """Strip text but check if it's None."""
    if text is None:
        return None
    return text.strip()
