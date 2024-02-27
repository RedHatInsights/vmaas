"""
Module containing models for CSAF objects.
"""
from __future__ import annotations

import csv
from dataclasses import dataclass
from dataclasses import field
from datetime import datetime
from enum import IntEnum
from typing import ItemsView, Iterator, KeysView
from typing import Optional
from typing import overload

import attr

from vmaas.common.date_utils import parse_datetime


class CsafProductStatus(IntEnum):
    """CSAF product status enum."""
    FIRST_AFFECTED = 1
    FIRST_FIXED = 2
    FIXED = 3
    KNOWN_AFFECTED = 4
    KNOWN_NOT_AFFECTED = 5
    LAST_AFFECTED = 6
    RECOMMENDED = 7
    UNDER_INVESTIGATION = 8


@dataclass
class CsafFile:
    """CSAF File model."""

    name: str
    csv_timestamp: datetime
    db_timestamp: Optional[datetime] = None
    id_: int = 0

    @property
    def out_of_date(self) -> bool:
        """Returns `True` if the file is out of date."""
        if self.db_timestamp is None:
            return True
        return self.csv_timestamp > self.db_timestamp


@attr.s(auto_attribs=True, repr=False)
class CsafFiles:
    """Collection of CSAF Files."""

    _files: dict[str, CsafFile] = attr.Factory(dict)

    @classmethod
    def from_table_map_and_csv(cls, table_map: dict[str, tuple[int, datetime]], csv_path: str) -> CsafFiles:
        """Initialize class from CsafStore.csaf_file_map table_map and changes.csv."""
        obj = cls()
        obj._update_from_table_map(table_map)
        obj._update_from_csv(csv_path)
        return obj

    def _update_from_table_map(self, table_map: dict[str, tuple[int, datetime]]) -> None:
        """Update files from `CsafStore.csaf_file_map` table_map."""
        for key, val in table_map.items():
            id_, timestamp = val
            obj = self.get(key, CsafFile(key, timestamp, timestamp, id_))
            obj.id_ = id_
            obj.db_timestamp = timestamp
            self[key] = obj

    def _update_from_csv(self, path: str) -> None:
        """Update files from CSAF changes.csv."""
        with open(path, newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile, ("name", "timestamp"))
            for row in reader:
                timestamp = parse_datetime(row["timestamp"])
                obj = self.get(row["name"], CsafFile(row["name"], timestamp))
                obj.csv_timestamp = timestamp
                self[obj.name] = obj

    @property
    def out_of_date(self) -> filter[CsafFile]:
        """Filter generator of out of date files."""
        return filter(lambda x: x.out_of_date, self)

    def to_tuples(self, attributes: tuple[str, ...]) -> list[tuple]:
        """Transform data to list of tuples with chosen attributes."""
        res = []
        for item in self:
            items = []
            for attribute in attributes:
                items.append(getattr(item, attribute))
            res.append(tuple(items))
        return res

    @overload
    def get(self, key: str, default: None = None) -> Optional[CsafFile]:
        ...

    @overload
    def get(self, key: str, default: CsafFile) -> CsafFile:
        ...

    def get(self, key, default=None):
        """Return the value for key if key is in the collection, else default."""
        return self._files.get(key, default)

    def update(self, data: CsafFiles) -> None:
        """Update data in collection - same as dict.update()."""
        self._files.update(data._files)  # pylint: disable=protected-access

    def __getitem__(self, key: str) -> CsafFile:
        return self._files[key]

    def __setitem__(self, key: str, val: CsafFile) -> None:
        self._files[key] = val

    def __contains__(self, key: str) -> bool:
        return key in self._files

    def __iter__(self) -> Iterator[CsafFile]:
        return iter(self._files.values())

    def __next__(self) -> CsafFile:
        return next(iter(self))

    def __repr__(self) -> str:
        return repr(self._files)

    def __len__(self) -> int:
        return len(self._files)


@dataclass
class CsafProduct:
    """CSAF Product object."""

    cpe: str
    package: str
    status_id: int
    module: Optional[str] = None


@attr.s(auto_attribs=True, repr=False)
class CsafCves:
    """Collection of CSAF CVEs."""

    _cves: dict[str, list[CsafProduct]] = attr.Factory(dict)

    def to_tuples(self, key: str, attributes: tuple[str, ...]) -> list[tuple]:
        """Transform data to list of tuples with chosen attributes by key.

        Example:
            > collection = CsafCves({'key1': [CsafProduct(cpe='cpe123', package='kernel', module="module:8")]})
            > collection.to_tuples("key1", ("cpe", "package", "module"))
            > [("cpe123", "kernel", "module:8")]

        """
        res = []
        for item in self[key]:
            items = []
            for attribute in attributes:
                items.append(getattr(item, attribute))
            res.append(tuple(items))
        return res

    @overload
    def get(self, key: str, default: None = None) -> Optional[list[CsafProduct]]:
        ...

    @overload
    def get(self, key: str, default: list[CsafProduct]) -> list[CsafProduct]:
        ...

    def get(self, key, default=None):
        """Return the value for key if key is in the collection, else default."""
        return self._cves.get(key, default)

    def update(self, data: CsafCves) -> None:
        """Update data in collection - same as dict.update()."""
        self._cves.update(data._cves)  # pylint: disable=protected-access

    def items(self) -> ItemsView[str, list[CsafProduct]]:
        """Returns CVEs dict key and value pairs."""
        return self._cves.items()

    def keys(self) -> KeysView:
        """Return a list of keys in the _cves dictionary."""
        return self._cves.keys()

    def __getitem__(self, key: str) -> list[CsafProduct]:
        return self._cves[key]

    def __setitem__(self, key: str, val: list[CsafProduct]) -> None:
        self._cves[key] = val

    def __iter__(self) -> Iterator[list[CsafProduct]]:
        return iter(self._cves.values())

    def __next__(self) -> list[CsafProduct]:
        return next(iter(self))

    def __contains__(self, key: str) -> bool:
        return key in self._cves

    def __repr__(self) -> str:
        return repr(self._cves)

    def __len__(self) -> int:
        return len(self._cves)


@dataclass
class CsafData:
    """CSAF Data class."""

    files: CsafFiles = field(default_factory=CsafFiles)
    cves: CsafCves = field(default_factory=CsafCves)
