"""Unit tests of CSAF models."""
from collections.abc import Iterable
from pathlib import Path
from datetime import datetime
from datetime import timedelta
from typing import Any

import pytest

import vmaas.reposcan.redhatcsaf.modeling as m

DictCollection = m.CsafCves | m.CsafFiles


# pylint: disable=too-many-public-methods
class TestModels:
    """Test CSAF models."""

    @pytest.fixture
    def csaf_product(self) -> m.CsafProduct:
        """Returns CSAF product."""
        return m.CsafProduct("cpe", "package", 4, "module")

    @pytest.fixture
    def csaf_product_list(self, csaf_product: m.CsafProduct) -> m.CsafProducts:
        """Returns list of CSAF products."""
        return m.CsafProducts([csaf_product])

    @pytest.fixture
    def csaf_file(self) -> m.CsafFile:
        """Returns CSAF file."""
        now = datetime.now()
        now1d = now + timedelta(days=1)
        return m.CsafFile("name", now1d, now)

    @pytest.fixture
    def csaf_cves(self, csaf_product_list: m.CsafProducts) -> m.CsafCves:
        """Returns CSAF CVEs collection."""
        return m.CsafCves({"key1": csaf_product_list, "key2": csaf_product_list})

    @pytest.fixture
    def csaf_files(self, csaf_file: m.CsafFile) -> m.CsafFiles:
        """Returns CSAF files collection."""
        return m.CsafFiles({"key1": csaf_file, "key2": csaf_file})

    @pytest.fixture
    def csaf_product_updated(self) -> m.CsafProduct:
        """Returns CSAF product."""
        return m.CsafProduct("cpe_updated", "package_updated", 4, "module_updated")

    @pytest.fixture
    def csaf_product_list_updated(self, csaf_product_updated: m.CsafProduct) -> m.CsafProducts:
        """Returns list of CSAF products."""
        return m.CsafProducts([csaf_product_updated])

    @pytest.fixture
    def csaf_file_updated(self) -> m.CsafFile:
        """Returns CSAF file."""
        now = datetime.now()
        now1d = now + timedelta(days=1)
        return m.CsafFile("name_updated", now1d, now)

    @pytest.fixture
    def csaf_cves_updated(self, csaf_product_list_updated: m.CsafProducts) -> m.CsafCves:
        """Returns CSAF CVEs collection."""
        return m.CsafCves({"key2": csaf_product_list_updated})

    @pytest.fixture
    def csaf_files_updated(self, csaf_file_updated: m.CsafFile) -> m.CsafFiles:
        """Returns CSAF files collection."""
        return m.CsafFiles({"key2": csaf_file_updated})

    @pytest.mark.parametrize(
        "collection_name, expected_arg", (("csaf_cves", "csaf_product_list"), ("csaf_files", "csaf_file"))
    )
    def test_get(self, collection_name: str, expected_arg: str, request: pytest.FixtureRequest) -> None:
        """Test get()"""
        collection = request.getfixturevalue(collection_name)
        expected = request.getfixturevalue(expected_arg)

        res = collection.get("key1")
        assert res == expected

        res = collection.get("key99")
        assert res is None

        res = collection.get("key99", "default")
        assert res == "default"

    @pytest.mark.parametrize(
        "collection_name, expected_arg", (("csaf_cves", "csaf_product_list"), ("csaf_files", "csaf_file"))
    )
    def test_getitem(self, collection_name: str, expected_arg: str, request: pytest.FixtureRequest) -> None:
        """Test __getitem__."""
        collection: DictCollection = request.getfixturevalue(collection_name)
        res = collection["key1"]
        assert res == request.getfixturevalue(expected_arg)

        with pytest.raises(KeyError):
            collection["key99"]  # pylint: disable=pointless-statement

    @pytest.mark.parametrize(
        "collection_name, expected_arg", (("csaf_cves", "csaf_cves_updated"), ("csaf_files", "csaf_files_updated"))
    )
    def test_setitem(self, collection_name: str, expected_arg: str, request: pytest.FixtureRequest) -> None:
        """Test __setitem__"""
        collection: DictCollection = request.getfixturevalue(collection_name)
        expected = request.getfixturevalue(expected_arg)
        collection["key2"] = expected["key2"]
        assert collection["key2"] == expected["key2"]

    @pytest.mark.parametrize(
        "collection_name, expected_arg", (("csaf_cves", "csaf_cves_updated"), ("csaf_files", "csaf_files_updated"))
    )
    def test_update(self, collection_name: str, expected_arg: str, request: pytest.FixtureRequest) -> None:
        """Test update()"""
        collection: DictCollection = request.getfixturevalue(collection_name)
        expected = request.getfixturevalue(expected_arg)
        collection.update(expected)
        assert collection["key2"] == expected["key2"]

    @pytest.mark.parametrize("collection_name", ("csaf_cves", "csaf_files"))
    def test_iter(self, collection_name: str, request: pytest.FixtureRequest) -> None:
        """Test __iter__"""
        collection: DictCollection = request.getfixturevalue(collection_name)
        assert isinstance(collection, Iterable)

    @pytest.mark.parametrize(
        "collection_name, expected_arg", (("csaf_cves", "csaf_product_list"), ("csaf_files", "csaf_file"))
    )
    def test_next(self, collection_name: str, expected_arg: str, request: pytest.FixtureRequest) -> None:
        """Test __next__"""
        collection: DictCollection = request.getfixturevalue(collection_name)
        expected = request.getfixturevalue(expected_arg)
        assert next(collection) == expected

    @pytest.mark.parametrize("collection_name", ("csaf_cves", "csaf_files"))
    def test_contains(self, collection_name: str, request: pytest.FixtureRequest) -> None:
        """Test __contains__"""
        collection: DictCollection = request.getfixturevalue(collection_name)
        assert "key1" in collection
        assert "key99" not in collection

    @pytest.mark.parametrize(
        "obj, expected", (("csaf_cves", "key1"), ("csaf_files", "key1"), ("csaf_product", "cpe"), ("csaf_file", "name"))
    )
    def test_repr(self, obj: str, expected: str, request: pytest.FixtureRequest) -> None:
        """Test __repr__"""
        obj = request.getfixturevalue(obj)
        res = repr(obj)
        assert isinstance(res, str)
        assert expected in res

    @pytest.mark.parametrize("collection_name", ("csaf_cves", "csaf_files"))
    def test_len(self, collection_name: str, request: pytest.FixtureRequest) -> None:
        """Test __len__"""
        collection: DictCollection = request.getfixturevalue(collection_name)
        res = len(collection)
        assert res == 2

    @pytest.mark.parametrize(
        "class_name, args",
        (
            ("CsafFile", ("x", "y")),
            ("CsafFiles", None),
            ("CsafProduct", ("x", "y", 4, "z")),
            ("CsafCves", None),
            ("CsafData", None),
        ),
    )
    def test_instantiate(self, class_name: str, args: tuple[str | int] | None) -> None:
        """Test class instantiation"""
        class_ = getattr(m, class_name)
        if args:
            class_(*args)
        else:
            class_()

    def test_csaf_file_out_of_date(self, csaf_file: m.CsafFile) -> None:
        """Test CsafFile.out_of_date"""
        assert csaf_file.out_of_date

    def test_csaf_files_out_of_date(self, csaf_file: m.CsafFile) -> None:
        """Test CsafFiles.out_of_date"""
        collection = m.CsafFiles({"x": csaf_file, "y": csaf_file})
        assert len(list(collection.out_of_date)) == 2

    def test_from_table_map_and_csv(self, tmp_path: Path) -> None:
        """Test CsafFiles.from_table_map_and_csv"""
        now = datetime.now()
        csv_file = tmp_path / "test_csaf" / "test.csv"
        csv_file.parent.mkdir(exist_ok=True)
        csv_file.touch()

        table_map = {"file1": (1, now), "file2": (2, now)}
        modified = datetime.now()
        csv_file.write_text(f"file2,{str(modified)}\r\nfile3,{str(modified)}")

        collection = m.CsafFiles.from_table_map_and_csv(table_map, csv_file)
        assert collection["file1"].csv_timestamp == collection["file1"].db_timestamp == now
        assert collection["file2"].db_timestamp is not None
        assert collection["file2"].csv_timestamp > collection["file2"].db_timestamp
        assert collection["file2"].csv_timestamp == modified
        assert collection["file3"].csv_timestamp == modified
        assert collection["file3"].db_timestamp is None

        out_of_date = list(collection.out_of_date)
        assert len(out_of_date) == 2

    @pytest.mark.parametrize(
        "collection_name, attr_tuple, by_key",
        (("csaf_cves", ("cpe", "package", "module"), "key1"), ("csaf_files", ("name",), None)),
    )
    def test_to_tuples(
        self, collection_name: str, attr_tuple: tuple[str], by_key: str | None, request: pytest.FixtureRequest
    ) -> None:
        """Test collection.to_tuples()"""
        collection: DictCollection = request.getfixturevalue(collection_name)

        def _assert_tuples(item: tuple[Any, ...]) -> None:
            assert len(item) == len(attr_tuple)
            for attr in attr_tuple:
                assert attr in item

        if by_key and isinstance(collection, m.CsafCves):
            cves_tuple, *_ = collection.to_tuples(by_key, attr_tuple)
            _assert_tuples(cves_tuple)
        elif isinstance(collection, m.CsafFiles):
            files_tuple, *_ = collection.to_tuples(attr_tuple)
            _assert_tuples(files_tuple)

    def test_to_tuples_exception(self, csaf_cves: m.CsafCves, csaf_files: m.CsafFiles) -> None:
        """Test exceptions from collection.to_tuples()"""
        with pytest.raises(AttributeError):
            csaf_files.to_tuples(("not_existing",))
        with pytest.raises(AttributeError):
            csaf_cves.to_tuples("key1", ("not_existing",))
        with pytest.raises(KeyError):
            csaf_cves.to_tuples("wrong_key", ("cpe",))

    def test_csaf_data_assignment(self, csaf_cves: m.CsafCves, csaf_file: m.CsafFile) -> None:
        """Test item assignemnt to CsafData."""
        data = m.CsafData()
        data.files[csaf_file.name] = csaf_file
        data.files.update(m.CsafFiles({csaf_file.name: csaf_file}))
        data.cves["key1"] = csaf_cves["key1"]
        data.cves.update(csaf_cves)

    def test_cves_items_method(self) -> None:
        """Test CsafCves _cves iteration with key and value pairs"""
        cves_collection = m.CsafCves(
            {
                "key1": m.CsafProducts([m.CsafProduct(cpe="cpe123", package="kernel", status_id=4, module="module:8")]),
                "key2": m.CsafProducts([m.CsafProduct(cpe="cpe456", package="nginx", status_id=4, module="web")]),
            }
        )

        expected_items = [
            ("key1", m.CsafProducts([m.CsafProduct(cpe="cpe123", package="kernel", status_id=4, module="module:8")])),
            ("key2", m.CsafProducts([m.CsafProduct(cpe="cpe456", package="nginx", status_id=4, module="web")])),
        ]

        items_result = cves_collection.items()
        assert list(items_result) == expected_items

    def test_keys_empty_dictionary(self) -> None:
        """Test the keys method with an empty dictionary"""
        csaf_cves = m.CsafCves()
        result = csaf_cves.keys()
        assert not result

    def test_keys_non_empty_dictionary(self) -> None:
        """Test the keys method with a non-empty dictionary"""
        key1 = "key1"
        key2 = "key2"
        csaf_cves = m.CsafCves({key1: m.CsafProducts(), key2: m.CsafProducts()})
        result = csaf_cves.keys()
        assert result == {key1: "", key2: ""}.keys()
