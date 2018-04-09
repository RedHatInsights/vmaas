"""
Utilities for date and time parsing / printing.
"""

from dateutil import parser as dateutil_parser

def parse_datetime(date):
    """Parse date from string in ISO format."""
    if date is None:
        return None
    return dateutil_parser.parse(date)
