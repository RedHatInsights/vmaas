"""
Module containing models for CSAF objects.
"""
from __future__ import annotations

import csv
import typing as t
from dataclasses import dataclass
from dataclasses import field
from datetime import datetime
from enum import IntEnum
from pathlib import Path

import attr

from vmaas.common.date_utils import parse_datetime


DEFAULT_VARIANT = "N/A"


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
    db_timestamp: datetime | None = None
    csv: bool = False
    id_: int = 0
    # it should be 1:1 mapping between file and cve
    # but the json in file contains list of cves so add the whole list
    cves: list[str] | None = None

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
    def from_table_map_and_csv(cls, table_map: dict[str, tuple[int, datetime]], csv_path: Path) -> CsafFiles:
        """Initialize class from CsafStore.csaf_file_map table_map and changes.csv."""
        obj = cls()
        obj._update_from_table_map(table_map)
        obj._update_from_csv(csv_path)
        return obj

    def _update_from_table_map(self, table_map: dict[str, tuple[int, datetime]]) -> None:
        """Update files from `CsafStore.csaf_file_map` table_map."""
        for key, val in table_map.items():
            id_, timestamp = val
            obj = self.get(key, CsafFile(key, timestamp, db_timestamp=timestamp, id_=id_))
            obj.id_ = id_
            obj.db_timestamp = timestamp
            self[key] = obj

    def _update_from_csv(self, path: Path) -> None:
        """Update files from CSAF changes.csv."""
        with open(path, newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile, ("name", "timestamp"))
            for row in reader:
                timestamp = parse_datetime(row["timestamp"])
                obj = self.get(row["name"], CsafFile(row["name"], timestamp, csv=True))
                obj.csv_timestamp = timestamp
                obj.csv = True
                self[obj.name] = obj

    @property
    def out_of_date(self) -> filter[CsafFile]:
        """Filter generator of out of date files."""
        return filter(lambda x: x.out_of_date, self)

    @property
    def csv_files(self) -> filter[CsafFile]:
        """Files from csv."""
        return filter(lambda x: x.csv, self)

    @property
    def not_csv_files(self) -> filter[CsafFile]:
        """Files not in csv."""
        return filter(lambda x: not x.csv, self)

    def to_tuples(self, attributes: tuple[str, ...]) -> list[tuple[int | str | datetime | None, ...]]:
        """Transform data to list of tuples with chosen attributes."""
        res = []
        for item in self:
            items = []
            for attribute in attributes:
                items.append(getattr(item, attribute))
            res.append(tuple(items))
        return res

    @t.overload
    def get(self, key: str, default: None = None) -> CsafFile | None:
        ...

    @t.overload
    def get(self, key: str, default: CsafFile) -> CsafFile:
        ...

    def get(self, key: str, default: CsafFile | None = None) -> CsafFile | None:
        """Return the value for key if key is in the collection, else default."""
        return self._files.get(key, default)

    def get_by_id(self, id_: int, default: CsafFile | None = None) -> CsafFile | None:
        """Return the value for id_ if id_ is in the collection, else default."""
        for csaf_file in self:
            if csaf_file.id_ == id_:
                return csaf_file
        return default

    def update(self, data: CsafFiles) -> None:
        """Update data in collection - same as dict.update()."""
        self._files.update(data._files)  # pylint: disable=protected-access

    def __getitem__(self, key: str) -> CsafFile:
        return self._files[key]

    def __setitem__(self, key: str, val: CsafFile) -> None:
        self._files[key] = val

    def __contains__(self, key: str) -> bool:
        return key in self._files

    def __iter__(self) -> t.Iterator[CsafFile]:
        return iter(self._files.values())

    def __next__(self) -> CsafFile:
        return next(iter(self))

    def __repr__(self) -> str:
        return repr(self._files)

    def __len__(self) -> int:
        return len(self._files)

    def __bool__(self) -> bool:
        return bool(self._files)


@dataclass
class CsafProduct:
    """CSAF Product object."""

    cpe: str
    package: str
    status_id: int
    module: str | None = None
    erratum: str | None = None
    id_: int | None = None
    cpe_id: int | None = None
    package_name_id: int | None = None
    package_id: int | None = None
    variant_suffix: str = DEFAULT_VARIANT


@attr.s(auto_attribs=True, repr=False)
class CsafProducts:
    """List like collection of CSAF products with lookup by ids."""

    _products: list[CsafProduct] = attr.Factory(list)
    _lookup: dict[tuple[int, int | None, int | None, str | None], CsafProduct] = attr.Factory(dict)

    def to_tuples(
        self,
        attributes: tuple[str, ...],
        *,
        missing_only: bool = False,
        with_id: bool = False,
        with_cpe_id: bool = False,
        with_pkg_id: bool = False,
    ) -> list[tuple[int | str | None, ...]]:
        """Transform data to list of tuples with chosen attributes by key.

        :param tuple attributes: Attributes included in the response
        :param bool missing_only: Include only products not present in DB (id_=None)
        :param bool with_id: Include only products which have product id
        :param bool with_cpe_id: Include only products which have cpe_id
        :param bool with_pkg_id: Include only products which have either package_name_id or package_id

        Example:
            > collection = CsafProducts([CsafProduct(cpe='cpe123', package='kernel', module="module:8", status_id=4)])
            > collection.to_tuples(("cpe", "package", "module"))
            > [("cpe123", "kernel", "module:8")]

        """
        res = []
        products: t.Iterable[CsafProduct] = self
        if missing_only:
            products = filter(lambda x: x.id_ is None, products)
        if with_id:
            products = filter(lambda x: x.id_, products)
        if with_cpe_id:
            products = filter(lambda x: x.cpe_id, products)
        if with_pkg_id:
            products = filter(lambda x: x.package_name_id or x.package_id, products)

        for item in products:
            items = []
            for attribute in attributes:
                items.append(getattr(item, attribute))
            res.append(tuple(items))
        return res

    def get_by_ids_and_module(
        self,
        cpe_id: int,
        package_name_id: int | None,
        package_id: int | None,
        module: str | None,
    ) -> CsafProduct | None:
        """Return product by (cpe_id, package_name_id, package_id, module)."""
        key = (cpe_id, package_name_id, package_id, module)
        product = self._lookup.get(key)
        if product is None:
            # not found in _lookup, try to find in _products and add to _lookup
            for prod in self:
                if (prod.cpe_id, prod.package_name_id, prod.package_id, module) == key:
                    self.add_to_lookup(prod)
                    return prod
        return product

    def add_to_lookup(self, val: CsafProduct) -> None:
        """Add `val` to internal lookup dict."""
        if val.cpe_id is not None:
            key = (val.cpe_id, val.package_name_id, val.package_id, val.module)
            self._lookup[key] = val

    def append(self, val: CsafProduct) -> None:
        """Append `val` to CsafProducts."""
        self._products.append(val)
        self.add_to_lookup(val)

    def remove(self, val: CsafProduct) -> None:
        """Remove `val` from CsafProducts."""
        if val.cpe_id is not None:
            key = (val.cpe_id, val.package_name_id, val.package_id, val.module)
            self._lookup.pop(key, None)
        self._products.remove(val)

    def __getitem__(self, idx: int) -> CsafProduct:
        return self._products[idx]

    def __setitem__(self, idx: int, val: CsafProduct) -> None:
        self._products[idx] = val
        self.add_to_lookup(val)

    def __iter__(self) -> t.Iterator[CsafProduct]:
        return iter(self._products)

    def __next__(self) -> CsafProduct:
        return next(iter(self))

    def __contains__(self, val: CsafProduct) -> bool:
        return val in self._products

    def __repr__(self) -> str:
        return repr(self._products)

    def __len__(self) -> int:
        return len(self._products)

    def __bool__(self) -> bool:
        return bool(self._products)


@attr.s(auto_attribs=True, repr=False)
class CsafCves:
    """Collection of CSAF CVEs."""

    _cves: dict[str, CsafProducts] = attr.Factory(dict)

    def to_tuples(self, key: str, attributes: tuple[str, ...]) -> list[tuple[int | str | None, ...]]:
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

    @t.overload
    def get(self, key: str, default: None = None) -> CsafProducts | None:
        ...

    @t.overload
    def get(self, key: str, default: CsafProducts) -> CsafProducts:
        ...

    def get(self, key: str, default: CsafProducts | None = None) -> CsafProducts | None:
        """Return the value for key if key is in the collection, else default."""
        return self._cves.get(key, default)

    def update(self, data: CsafCves) -> None:
        """Update data in collection - same as dict.update()."""
        self._cves.update(data._cves)  # pylint: disable=protected-access

    def items(self) -> t.ItemsView[str, CsafProducts]:
        """Returns CVEs dict key and value pairs."""
        return self._cves.items()

    def keys(self) -> t.KeysView[str]:
        """Return a list of keys in the _cves dictionary."""
        return self._cves.keys()

    def __getitem__(self, key: str) -> CsafProducts:
        return self._cves[key]

    def __setitem__(self, key: str, val: CsafProducts) -> None:
        self._cves[key] = val

    def __iter__(self) -> t.Iterator[CsafProducts]:
        return iter(self._cves.values())

    def __next__(self) -> CsafProducts:
        return next(iter(self))

    def __contains__(self, key: str) -> bool:
        return key in self._cves

    def __repr__(self) -> str:
        return repr(self._cves)

    def __len__(self) -> int:
        return len(self._cves)

    def __bool__(self) -> bool:
        return bool(self._cves)


@dataclass
class CsafData:
    """CSAF Data class."""

    files: CsafFiles = field(default_factory=CsafFiles)
    cves: CsafCves = field(default_factory=CsafCves)

    def __bool__(self) -> bool:
        return bool(self.files) and bool(self.cves)
