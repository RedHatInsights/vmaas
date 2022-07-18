"""
Module containing implementation of tzinfo UTC object.
"""
from datetime import tzinfo, timedelta

ZERO = timedelta(0)


class UtcTz(tzinfo):
    """UTC"""

    def utcoffset(self, dt):
        return ZERO

    def tzname(self, dt):
        return "UTC"

    def dst(self, dt):
        return ZERO


UTC = UtcTz()
