"""
Module containing models for Release objects.
"""
from dataclasses import dataclass
from datetime import date
from enum import StrEnum


class LifecyclePhase(StrEnum):
    """Lifecycle phase enumeration, has to be equal to the enum in the DB."""
    MINOR = "minor"
    EUS = "eus"
    AUS = "aus"
    E4S = "e4s"
    ELS = "els"
    TUS = "tus"


@dataclass
class Release:
    """Release object."""
    os_name: str
    major: int
    minor: int
    lifecycle_phase: LifecyclePhase
    ga_date: date
    system_profile: dict[str, str | list[str]]
