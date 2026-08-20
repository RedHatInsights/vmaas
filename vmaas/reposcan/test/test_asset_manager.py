"""Unit tests for HttpAssetSource, LocalAssetSource and AssetManager (asset fetching)."""
# pylint: disable=missing-function-docstring,protected-access,invalid-name
from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import requests

from vmaas.reposcan import reposcan
from vmaas.reposcan.reposcan import AssetManager, HttpAssetSource, LocalAssetSource

MINIMAL_REPOLIST = [
    {
        "products": {
            "Red Hat Enterprise Linux Server": {
                "redhat_eng_product_id": 69,
                "content_sets": {
                    "rhel-7-server-rpms": {
                        "name": "Red Hat Enterprise Linux 7 Server (RPMs)",
                        "baseurl": "https://cdn.example.com/rhel/server/7/$basearch/os/",
                        "basearch": ["x86_64"],
                        "releasever": [],
                    }
                },
            }
        }
    }
]


class FakeAssetSource:
    """Simple in-memory AssetSource stub keyed by relative path."""

    def __init__(self, files: dict[str, str]) -> None:
        self.files = files
        self.requested: list[str] = []

    def fetch(self, path: str) -> str | None:
        self.requested.append(path)
        return self.files.get(path)


class TestHttpAssetSource:
    """Tests for HttpAssetSource.fetch."""

    def test_fetch_success(self):
        source = HttpAssetSource("http://example.com/assets", token="secrettoken")
        response = MagicMock(text="hello world")
        response.raise_for_status = MagicMock()
        with patch.object(requests, "get", return_value=response) as mock_get:
            content = source.fetch("repolist.json")

        assert content == "hello world"
        args, kwargs = mock_get.call_args
        assert args[0] == "http://example.com/assets/repolist.json"
        assert kwargs["headers"] == {"Authorization": "Bearer secrettoken"}

    def test_fetch_without_token_sends_no_auth_header(self):
        source = HttpAssetSource("http://example.com/assets")
        response = MagicMock(text="data")
        response.raise_for_status = MagicMock()
        with patch.object(requests, "get", return_value=response) as mock_get:
            source.fetch("ga_dates.json")

        assert mock_get.call_args.kwargs["headers"] == {}

    def test_fetch_joins_base_url_without_trailing_slash(self):
        source = HttpAssetSource("http://example.com/assets")
        response = MagicMock(text="data")
        response.raise_for_status = MagicMock()
        with patch.object(requests, "get", return_value=response) as mock_get:
            source.fetch("release_graphs/rhel9.json")

        assert mock_get.call_args.args[0] == "http://example.com/assets/release_graphs/rhel9.json"

    def test_fetch_returns_none_on_request_exception(self):
        source = HttpAssetSource("http://example.com/assets")
        with patch.object(requests, "get", side_effect=requests.RequestException("boom")):
            assert source.fetch("missing.json") is None

    def test_fetch_returns_none_on_http_error(self):
        source = HttpAssetSource("http://example.com/assets")
        response = MagicMock()
        response.raise_for_status.side_effect = requests.HTTPError("404")
        with patch.object(requests, "get", return_value=response):
            assert source.fetch("missing.json") is None


class TestLocalAssetSource:
    """Tests for LocalAssetSource.fetch."""

    def test_fetch_existing_file(self, tmp_path: Path):
        (tmp_path / "repolist.json").write_text("[]", encoding="utf8")
        source = LocalAssetSource(tmp_path)
        assert source.fetch("repolist.json") == "[]"

    def test_fetch_missing_file_returns_none(self, tmp_path: Path):
        source = LocalAssetSource(tmp_path)
        assert source.fetch("missing.json") is None


class TestAssetManagerGetSource:
    """Tests for AssetManager._get_source selection logic."""

    def test_fedramp_uses_local_source(self):
        with patch.object(reposcan, "IS_FEDRAMP", True):
            source = AssetManager._get_source()
        assert isinstance(source, LocalAssetSource)
        assert source.base_dir == reposcan.REPOLIST_STATIC_DIR

    def test_no_base_url_returns_none(self):
        with patch.object(reposcan, "IS_FEDRAMP", False), \
                patch.object(reposcan, "VMAAS_ASSETS_BASE_URL", ""):
            assert AssetManager._get_source() is None

    def test_base_url_uses_http_source(self):
        with patch.object(reposcan, "IS_FEDRAMP", False), \
                patch.object(reposcan, "VMAAS_ASSETS_BASE_URL", "http://example.com/assets"), \
                patch.object(reposcan, "VMAAS_ASSETS_TOKEN", "tok"):
            source = AssetManager._get_source()
        assert isinstance(source, HttpAssetSource)
        assert source.base_url == "http://example.com/assets/"
        assert source.token == "tok"


class TestAssetManagerGetProductsRepos:
    """Tests for AssetManager.get_git_products_repos."""

    def test_success_single_path(self):
        fake_source = FakeAssetSource({"repolist.json": json.dumps(MINIMAL_REPOLIST)})
        with patch.object(AssetManager, "_get_source", return_value=fake_source), \
                patch.object(reposcan, "REPOLIST_PATH", "repolist.json"):
            products, repos = AssetManager.get_git_products_repos()

        assert products is not None and repos is not None
        assert "Red Hat Enterprise Linux Server" in products
        assert len(repos) == 1
        assert repos[0][0] == "https://cdn.example.com/rhel/server/7/x86_64/os/"

    def test_success_comma_separated_paths(self):
        fake_source = FakeAssetSource({
            "repolist.json": json.dumps(MINIMAL_REPOLIST),
            "epel-repolist.json": json.dumps([]),
        })
        with patch.object(AssetManager, "_get_source", return_value=fake_source), \
                patch.object(reposcan, "REPOLIST_PATH", "repolist.json, epel-repolist.json"):
            products, repos = AssetManager.get_git_products_repos()

        # epel-repolist.json parses to no products/repos, which is treated as invalid input
        assert products is None
        assert repos is None
        assert fake_source.requested == ["repolist.json", "epel-repolist.json"]

    def test_no_source_configured(self):
        with patch.object(AssetManager, "_get_source", return_value=None):
            products, repos = AssetManager.get_git_products_repos()
        assert products is None
        assert repos is None

    def test_missing_file_returns_none(self):
        fake_source = FakeAssetSource({})
        with patch.object(AssetManager, "_get_source", return_value=fake_source), \
                patch.object(reposcan, "REPOLIST_PATH", "repolist.json"):
            products, repos = AssetManager.get_git_products_repos()
        assert products is None
        assert repos is None


class TestAssetManagerGetReleases:
    """Tests for AssetManager.get_git_releases."""

    def test_success(self):
        fake_source = FakeAssetSource({"ga_dates.json": json.dumps({"7.9": "2020-09-29"})})
        with patch.object(AssetManager, "_get_source", return_value=fake_source), \
                patch.object(reposcan, "RELEASEMAP_PATH", "ga_dates.json"):
            releases = AssetManager.get_git_releases()
        assert releases == {"7.9": "2020-09-29"}

    def test_missing_file_returns_none(self):
        fake_source = FakeAssetSource({})
        with patch.object(AssetManager, "_get_source", return_value=fake_source), \
                patch.object(reposcan, "RELEASEMAP_PATH", "ga_dates.json"):
            assert AssetManager.get_git_releases() is None

    def test_no_source_configured(self):
        with patch.object(AssetManager, "_get_source", return_value=None):
            assert AssetManager.get_git_releases() is None


class TestAssetManagerGetReleaseGraphs:
    """Tests for AssetManager.get_git_release_graphs."""

    def test_success(self):
        graph_content = json.dumps({"nodes": [], "edges": []})
        fake_source = FakeAssetSource({
            "release_graphs_index.json": json.dumps(["rhel9.json"]),
            "release_graphs/rhel9.json": graph_content,
        })
        with patch.object(AssetManager, "_get_source", return_value=fake_source), \
                patch.object(reposcan, "RELEASE_GRAPH_INDEX_PATH", "release_graphs_index.json"), \
                patch.object(reposcan, "RELEASE_GRAPH_DIR", "release_graphs"):
            release_graphs = AssetManager.get_git_release_graphs()

        assert release_graphs is not None
        assert "rhel9.json" in release_graphs
        assert release_graphs["rhel9.json"].name == "rhel9.json"

    def test_missing_index_returns_none(self):
        fake_source = FakeAssetSource({})
        with patch.object(AssetManager, "_get_source", return_value=fake_source), \
                patch.object(reposcan, "RELEASE_GRAPH_INDEX_PATH", "release_graphs_index.json"):
            assert AssetManager.get_git_release_graphs() is None

    def test_malformed_index_returns_none(self):
        fake_source = FakeAssetSource({"release_graphs_index.json": "not json"})
        with patch.object(AssetManager, "_get_source", return_value=fake_source), \
                patch.object(reposcan, "RELEASE_GRAPH_INDEX_PATH", "release_graphs_index.json"):
            assert AssetManager.get_git_release_graphs() is None

    def test_missing_listed_graph_file_returns_none(self):
        fake_source = FakeAssetSource({
            "release_graphs_index.json": json.dumps(["rhel9.json", "rhel10.json"]),
            "release_graphs/rhel9.json": json.dumps({"nodes": []}),
            # rhel10.json intentionally missing
        })
        with patch.object(AssetManager, "_get_source", return_value=fake_source), \
                patch.object(reposcan, "RELEASE_GRAPH_INDEX_PATH", "release_graphs_index.json"), \
                patch.object(reposcan, "RELEASE_GRAPH_DIR", "release_graphs"):
            assert AssetManager.get_git_release_graphs() is None

    def test_no_source_configured(self):
        with patch.object(AssetManager, "_get_source", return_value=None):
            assert AssetManager.get_git_release_graphs() is None


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
