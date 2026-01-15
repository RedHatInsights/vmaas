"""
Utilities for file related functions.
"""

import os
from pathlib import Path


def remove_file_if_exists(filename: Path) -> None:
    """Remove the specified file if it exists."""
    try:
        os.remove(filename)
    except FileNotFoundError:
        pass
