"""
Utilities for file related functions.
"""

import os

def remove_file_if_exists(filename):
    """Remove the specified file if it exists."""
    try:
        os.remove(filename)
    except FileNotFoundError:
        pass
