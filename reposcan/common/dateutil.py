"""
Utilities for date and time parsing / printing.
"""

from datetime import datetime
from dateutil import parser as dateutil_parser

def parse_datetime(date):
    """Parse date from string in ISO format."""
    if date is None:
        return None
    return dateutil_parser.parse(date)

def format_datetime(datetime_obj):
    """Try to format object to ISO 8601 if object is datetime."""
    if isinstance(datetime_obj, datetime):
        return datetime_obj.isoformat()
    return str(datetime_obj)
