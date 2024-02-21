"""Unit tests of CSAF models."""
from collections.abc import Iterable
from datetime import datetime
from datetime import timedelta

import pytest

import vmaas.reposcan.redhatcsaf.modeling as model


# pylint: disable=too-many-public-methods
class TestModels:
    """Test CSAF models."""

    @pytest.fixture
    def csaf_product(self):
        """Returns CSAF product."""
        return model.CsafProduct("cpe", "package", 4, "module")

    @pytest.fixture
    def csaf_product_list(self, csaf_product):
        """Returns list of CSAF products."""
        return [csaf_product]

    @pytest.fixture
    def csaf_file(self):
        """Returns CSAF file."""
        now = datetime.now()
        now1d = now + timedelta(days=1)
        return model.CsafFile("name", now1d, now)

    @pytest.fixture
    def csaf_cves(self, csaf_product_list):
        """Returns CSAF CVEs collection."""
        return model.CsafCves({"key1": csaf_product_list, "key2": csaf_product_list})

    @pytest.fixture
    def csaf_files(self, csaf_file):
        """Returns CSAF files collection."""
        return model.CsafFiles({"key1": csaf_file, "key2": csaf_file})

    @pytest.fixture
    def csaf_product_updated(self):
        """Returns CSAF product."""
        return model.CsafProduct("cpe_updated", "package_updated", "module_updated")

    @pytest.fixture
    def csaf_product_list_updated(self, csaf_product_updated):
        """Returns list of CSAF products."""
        return [csaf_product_updated]

    @pytest.fixture
    def csaf_file_updated(self):
        """Returns CSAF file."""
        now = datetime.now()
        now1d = now + timedelta(days=1)
        return model.CsafFile("name_updated", now1d, now)

    @pytest.fixture
    def csaf_cves_updated(self, csaf_product_list_updated):
        """Returns CSAF CVEs collection."""
        return model.CsafCves({"key2": csaf_product_list_updated})

    @pytest.fixture
    def csaf_files_updated(self, csaf_file_updated):
        """Returns CSAF files collection."""
        return model.CsafFiles({"key2": csaf_file_updated})

    @pytest.mark.parametrize("collection, expected", (("csaf_cves", "csaf_product_list"), ("csaf_files", "csaf_file")))
    def test_get(self, collection, expected, request):
        """Test get()"""
        collection = request.getfixturevalue(collection)
        expected = request.getfixturevalue(expected)

        res = collection.get("key1")
        assert res == expected

        res = collection.get("key99")
        assert res is None

        res = collection.get("key99", "default")
        assert res == "default"

    @pytest.mark.parametrize("collection, expected", (("csaf_cves", "csaf_product_list"), ("csaf_files", "csaf_file")))
    def test_getitem(self, collection, expected, request):
        """Test __getitem__."""
        collection = request.getfixturevalue(collection)
        res = collection["key1"]
        assert res == request.getfixturevalue(expected)

        with pytest.raises(KeyError):
            collection["key99"]  # pylint: disable=pointless-statement

    @pytest.mark.parametrize(
        "collection, expected", (("csaf_cves", "csaf_cves_updated"), ("csaf_files", "csaf_files_updated"))
    )
    def test_setitem(self, collection, expected, request):
        """Test __setitem__"""
        collection = request.getfixturevalue(collection)
        expected = request.getfixturevalue(expected)
        collection["key2"] = expected["key2"]
        assert collection["key2"] == expected["key2"]

    @pytest.mark.parametrize(
        "collection, expected", (("csaf_cves", "csaf_cves_updated"), ("csaf_files", "csaf_files_updated"))
    )
    def test_update(self, collection, expected, request):
        """Test update()"""
        collection = request.getfixturevalue(collection)
        expected = request.getfixturevalue(expected)
        collection.update(expected)
        assert collection["key2"] == expected["key2"]

    @pytest.mark.parametrize("collection", ("csaf_cves", "csaf_files"))
    def test_iter(self, collection, request):
        """Test __iter__"""
        collection = request.getfixturevalue(collection)
        assert isinstance(collection, Iterable)

    @pytest.mark.parametrize("collection, expected", (("csaf_cves", "csaf_product_list"), ("csaf_files", "csaf_file")))
    def test_next(self, collection, expected, request):
        """Test __next__"""
        collection = request.getfixturevalue(collection)
        expected = request.getfixturevalue(expected)
        assert next(collection) == expected

    @pytest.mark.parametrize("collection", ("csaf_cves", "csaf_files"))
    def test_contains(self, collection, request):
        """Test __contains__"""
        collection = request.getfixturevalue(collection)
        assert "key1" in collection
        assert "key99" not in collection

    @pytest.mark.parametrize(
        "obj, expected", (("csaf_cves", "key1"), ("csaf_files", "key1"), ("csaf_product", "cpe"), ("csaf_file", "name"))
    )
    def test_repr(self, obj, expected, request):
        """Test __repr__"""
        obj = request.getfixturevalue(obj)
        res = repr(obj)
        assert isinstance(res, str)
        assert expected in res

    @pytest.mark.parametrize("collection", ("csaf_cves", "csaf_files"))
    def test_len(self, collection, request):
        """Test __len__"""
        collection = request.getfixturevalue(collection)
        res = len(collection)
        assert res == 2

    @pytest.mark.parametrize(
        "class_name, args",
        (
            ("CsafFile", ("x", "y")),
            ("CsafFiles", None),
            ("CsafProduct", ("x", "y", "z")),
            ("CsafCves", None),
            ("CsafData", None),
        ),
    )
    def test_instantiate(self, class_name, args):
        """Test class instantiation"""
        class_ = getattr(model, class_name)
        if args:
            class_(*args)
        else:
            class_()

    def test_csaf_file_out_of_date(self, csaf_file):
        """Test CsafFile.out_of_date"""
        assert csaf_file.out_of_date

    def test_csaf_files_out_of_date(self, csaf_file):
        """Test CsafFiles.out_of_date"""
        collection = model.CsafFiles({"x": csaf_file, "y": csaf_file})
        assert len(list(collection.out_of_date)) == 2

    def test_from_table_map_and_csv(self, tmp_path):
        """Test CsafFiles.from_table_map_and_csv"""
        now = datetime.now()
        csv_file = tmp_path / "test_csaf" / "test.csv"
        csv_file.parent.mkdir(exist_ok=True)
        csv_file.touch()

        table_map = {"file1": (1, now), "file2": (2, now)}
        modified = datetime.now()
        csv_file.write_text(f"file2,{str(modified)}\r\nfile3,{str(modified)}")

        collection = model.CsafFiles.from_table_map_and_csv(table_map, csv_file)
        assert collection["file1"].csv_timestamp == collection["file1"].db_timestamp == now
        assert collection["file2"].csv_timestamp > collection["file2"].db_timestamp
        assert collection["file2"].csv_timestamp == modified
        assert collection["file3"].csv_timestamp == modified
        assert collection["file3"].db_timestamp is None

        out_of_date = list(collection.out_of_date)
        assert len(out_of_date) == 2

    @pytest.mark.parametrize(
        "collection, attr_tuple, by_key",
        (("csaf_cves", ("cpe", "package", "module"), "key1"), ("csaf_files", ("name",), None)),
    )
    def test_to_tuples(self, collection, attr_tuple, by_key, request):
        """Test collection.to_tuples()"""
        collection = request.getfixturevalue(collection)

        def _assert_tuples(item):
            assert len(item) == len(attr_tuple)
            for attr in attr_tuple:
                assert attr in item

        if by_key:
            res, *_ = collection.to_tuples(by_key, attr_tuple)
            _assert_tuples(res)
        else:
            res, *_ = collection.to_tuples(attr_tuple)
            _assert_tuples(res)

    def test_to_tuples_exception(self, csaf_cves, csaf_files):
        """Test exceptions from collection.to_tuples()"""
        with pytest.raises(AttributeError):
            csaf_files.to_tuples(("not_existing",))
        with pytest.raises(AttributeError):
            csaf_cves.to_tuples("key1", ("not_existing",))
        with pytest.raises(KeyError):
            csaf_cves.to_tuples("wrong_key", ("cpe",))

    def test_csaf_data_assignment(self, csaf_cves, csaf_file):
        """Test item assignemnt to CsafData."""
        data = model.CsafData()
        data.files[csaf_file.name] = csaf_file
        data.files.update(model.CsafFiles({csaf_file.name: csaf_file}))
        data.cves["key1"] = csaf_cves["key1"]
        data.cves.update(csaf_cves)
