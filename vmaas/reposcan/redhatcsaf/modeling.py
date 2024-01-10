"""
Module containing models for CSAF objects.
"""
from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import datetime
from typing import Generator
from typing import Iterator
from typing import Optional

import attr

from vmaas.common.date_utils import parse_datetime


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
class CsafFileCollection:
    """Collection of CSAF Files."""

    _files: dict[str, CsafFile] = attr.Factory(dict)

    @classmethod
    def from_table_map_and_csv(cls, table_map: dict[str, tuple[int, str]], csv_path: str) -> CsafFileCollection:
        """Initialize class from CsafStore.csaf_file_map table_map and changes.csv."""
        obj = cls()
        obj._update_from_table_map(table_map)
        obj._update_from_csv(csv_path)
        return obj

    def _update_from_table_map(self, table_map: dict[str, tuple[int, str]]) -> None:
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
    def out_of_date(self) -> Generator[CsafFile, None, None]:
        """Filter generator of out of date files."""
        return filter(lambda x: x.out_of_date, self)

    def to_tuples(self, attributes: tuple[str]) -> list[tuple[str, datetime]]:
        """Transform data to list of tuples with chosen attributes."""
        res = []
        for item in self:
            items = []
            for attribute in attributes:
                items.append(getattr(item, attribute))
            res.append(tuple(items))
        return res

    def get(self, key, default=None) -> CsafFile:
        """Return the value for key if key is in the collection, else default."""
        return self._files.get(key, default)

    def __getitem__(self, key: str) -> CsafFile:
        return self._files[key]

    def __setitem__(self, key: str, val: CsafFile) -> None:
        self._files[key] = val

    def __contains__(self, val: str) -> bool:
        return val in self._files

    def __iter__(self) -> Iterator[CsafFile]:
        return iter(self._files.values())

    def __next__(self) -> CsafFile:
        return next(self)

    def __repr__(self) -> str:
        return repr(self._files)

    def __len__(self) -> int:
        return len(self._files)
