"""
Module containing models for Release objects.
"""
from dataclasses import dataclass
from datetime import date


@dataclass
class Release:
    """Release object."""
    os_name: str
    major: int
    minor: int
    ga_date: date
