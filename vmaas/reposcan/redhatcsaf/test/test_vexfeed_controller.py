"""Unit tests of vexfeed_controller.py."""
import pathlib
from collections.abc import Generator
from datetime import datetime

import pytest
from psycopg2.extensions import connection

import vmaas.reposcan.redhatcsaf.modeling as m
from vmaas.reposcan.conftest import reset_db
from vmaas.reposcan.redhatcsaf.csaf_controller import ComponentError
from vmaas.reposcan.redhatcsaf.modeling import DEFAULT_VARIANT
from vmaas.reposcan.redhatcsaf.vexfeed_controller import VexFeedController


EXPECTED_VEXFEED = (
    (
        "vexfeed-cve-2024-0001.json",
        m.CsafCves(
            {
                "CVE-2024-0001": m.CsafProducts(
                    [
                        # known_affected is processed first per CSAF_PRODUCT_STATUS_LIST default ordering
                        m.CsafProduct("cpe:/o:redhat:enterprise_linux:9", "testpkg", 4, None),
                        m.CsafProduct("cpe:/o:redhat:enterprise_linux:8", "nodejs", 4, "nodejs:18"),
                        m.CsafProduct(
                            "cpe:/a:redhat:rhel_eus:9.2::appstream",
                            "testpkg-0:1.2.3-4.el9.src",
                            3,
                            None,
                            "RHSA-2024:0001",
                            variant_suffix="9.2.0.z.eus",
                        ),
                        m.CsafProduct(
                            "cpe:/a:redhat:rhel_eus:8.6::appstream",
                            "nodejs-1:18.19.0-1.module+el8.6.0+20000+abc12345.src",
                            3,
                            None,
                            "RHSA-2024:0001",
                            variant_suffix="8.6.0.z.eus",
                        ),
                    ]
                )
            }
        ),
    ),
    (
        "vexfeed-cve-2024-0002.json",
        m.CsafCves(
            {
                "CVE-2024-0002": m.CsafProducts(
                    [
                        m.CsafProduct("cpe:/o:redhat:enterprise_linux:9", "vim", 4, None),
                        m.CsafProduct("cpe:/o:redhat:enterprise_linux:8", "vim", 4, None),
                    ]
                )
            }
        ),
    ),
    (
        # Container products (like rhel-8/python-eventlet) pass through as source prefixes
        # in GA format — unlike legacy, we can't structurally distinguish them from valid RPMs.
        # Harmless: they won't match actual packages during evaluation.
        "vexfeed-cve-2024-0004.json",
        m.CsafCves(
            {
                "CVE-2024-0004": m.CsafProducts(
                    [m.CsafProduct("cpe:/o:redhat:enterprise_linux:8", "python-eventlet", 4, None)]
                )
            }
        ),
    ),
)


class TestVexFeedController:
    """VexFeedController tests."""

    @pytest.fixture
    def controller(  # pylint: disable=unused-argument
        self, db_conn: connection
    ) -> Generator[VexFeedController, None, None]:
        """Fixture returning VexFeedController obj with tmp_directory set to test dir."""
        ctrl = VexFeedController()
        ctrl.tmp_directory = pathlib.Path(__file__).parent.resolve()
        yield ctrl
        reset_db(ctrl.csaf_store.conn)

    @pytest.mark.parametrize("data", EXPECTED_VEXFEED, ids=[x[0] for x in EXPECTED_VEXFEED])
    def test_parse_vexfeed_file(self, data: tuple[str, m.CsafCves], controller: VexFeedController) -> None:
        """Test GA VEX feed JSON file parsing."""
        json_file, expected = data
        csaf_file = m.CsafFile(json_file, datetime.now())
        parsed = controller.parse_csaf_file(csaf_file)
        assert parsed == expected

    @pytest.mark.parametrize("data", EXPECTED_VEXFEED, ids=[x[0] for x in EXPECTED_VEXFEED])
    def test_vexfeed_store(self, data: tuple[str, m.CsafCves], controller: VexFeedController) -> None:
        """Parse GA VEX feed JSON and store its data to DB."""
        json_file, _ = data
        csaf_file = m.CsafFile(json_file, datetime(2024, 1, 15, 10, 0))
        csaf_cves = controller.parse_csaf_file(csaf_file)
        csaf_data = m.CsafData()
        csaf_file.cves = list(csaf_cves.keys())
        csaf_data.files[csaf_file.name] = csaf_file
        csaf_data.cves.update(csaf_cves)
        controller.csaf_store.store(csaf_data)


# pylint: disable=protected-access
class TestVexFeedParseProduct:
    """Unit tests for VexFeedController._parse_product and helpers."""

    @pytest.fixture
    def controller(self, db_conn: connection) -> VexFeedController:  # pylint: disable=unused-argument
        """Fixture returning VexFeedController."""
        ctrl = VexFeedController()
        ctrl.tmp_directory = pathlib.Path(__file__).parent.resolve()
        return ctrl

    def test_fixed_channel_src(self, controller: VexFeedController) -> None:
        """Fixed product with :: channel and source/ prefix."""
        product_cpe = {
            "rhel-9.2.0.z.eus::appstream": "cpe:/a:redhat:rhel_eus:9.2::appstream",
        }
        product_purl = {
            "testpkg/testpkg-0:1.2.3-4.el9.src": "pkg:rpm/redhat/testpkg@1.2.3-4.el9?arch=src",
        }
        branch, pkg, module, variant = controller._parse_product(
            "rhel-9.2.0.z.eus::appstream:testpkg/testpkg-0:1.2.3-4.el9.src",
            "fixed",
            product_cpe,
            product_purl,
        )
        assert branch == "rhel-9.2.0.z.eus::appstream"
        assert pkg == "testpkg-0:1.2.3-4.el9.src"
        assert module is None
        assert variant == "9.2.0.z.eus"

    def test_fixed_encoded_plus(self, controller: VexFeedController) -> None:
        """Fixed product with %2B encoding in release string."""
        product_cpe = {
            "rhel-8.6.0.z.eus::appstream": "cpe:/a:redhat:rhel_eus:8.6::appstream",
        }
        product_purl = {
            "nodejs/nodejs-1:18.19.0-1.module+el8.6.0+20000+abc12345.src":
                "pkg:rpm/redhat/nodejs@18.19.0-1.module%2Bel8.6.0%2B20000%2Babc12345?arch=src&epoch=1",
        }
        branch, pkg, module, variant = controller._parse_product(
            "rhel-8.6.0.z.eus::appstream:nodejs/nodejs-1:18.19.0-1.module%2Bel8.6.0%2B20000%2Babc12345.src",
            "fixed",
            product_cpe,
            product_purl,
        )
        assert branch == "rhel-8.6.0.z.eus::appstream"
        assert pkg == "nodejs-1:18.19.0-1.module+el8.6.0+20000+abc12345.src"
        assert module is None
        assert variant == "8.6.0.z.eus"

    def test_known_affected_no_mod(self, controller: VexFeedController) -> None:
        """Known affected product without module."""
        product_cpe = {"rhel-9": "cpe:/o:redhat:enterprise_linux:9"}
        branch, pkg, module, variant = controller._parse_product(
            "rhel-9:testpkg/testpkg", "known_affected", product_cpe, {}
        )
        assert branch == "rhel-9"
        assert pkg == "testpkg"
        assert module is None
        assert variant == "N/A"

    def test_known_affected_mod(self, controller: VexFeedController) -> None:
        """Known affected product with module:stream."""
        product_cpe = {"rhel-8": "cpe:/o:redhat:enterprise_linux:8"}
        branch, pkg, module, variant = controller._parse_product(
            "rhel-8:nodejs:18:8080020240101000000:abc12345/nodejs",
            "known_affected",
            product_cpe,
            {},
        )
        assert branch == "rhel-8"
        assert pkg == "nodejs"
        assert module == "nodejs:18"
        assert variant == "N/A"

    def test_no_colon_raises(self, controller: VexFeedController) -> None:
        """Product without colon raises ComponentError."""
        with pytest.raises(ComponentError):
            controller._parse_product("rhel9", "fixed", {}, {})

    def test_known_affected_src(self, controller: VexFeedController) -> None:
        """known_affected without / but with .src package (e.g., vim.src, kubevirt.src)."""
        product_cpe = {"rhel-9": "cpe:/o:redhat:enterprise_linux:9"}
        branch, pkg, module, variant = controller._parse_product(
            "rhel-9:vim.src", "known_affected", product_cpe, {}
        )
        assert branch == "rhel-9"
        assert pkg == "vim.src"
        assert module is None
        assert variant == "N/A"

    def test_no_cpe_raises(self, controller: VexFeedController) -> None:
        """known_affected without / and no CPE match raises ComponentError."""
        product_cpe = {"rhel-9": "cpe:/o:redhat:enterprise_linux:9"}
        with pytest.raises(ComponentError):
            controller._parse_product("unknown-1:testpkg", "known_affected", product_cpe, {})

    def test_empty_pkg_raises(self, controller: VexFeedController) -> None:
        """known_affected where branch_product consumes the whole string raises ComponentError."""
        product_cpe = {"rhel-9": "cpe:/o:redhat:enterprise_linux:9"}
        with pytest.raises(ComponentError):
            controller._parse_product("rhel-9:", "known_affected", product_cpe, {})

    def test_fixed_hardcoded_arch(self, controller: VexFeedController) -> None:
        """Fixed product without arch suffix gets .x86_64 appended."""
        product_cpe = {
            "openshift-4.13::el8": "cpe:/a:redhat:openshift:4.13::el8",
        }
        product_purl = {
            "runc/runc-4:1.1.12-1.rhaos4.13.el8": "pkg:rpm/redhat/runc@1.1.12-1.rhaos4.13.el8?epoch=4",
        }
        branch, pkg, module, _ = controller._parse_product(
            "openshift-4.13::el8:runc/runc-4:1.1.12-1.rhaos4.13.el8",
            "fixed",
            product_cpe,
            product_purl,
        )
        assert branch == "openshift-4.13::el8"
        assert pkg == "runc-4:1.1.12-1.rhaos4.13.el8.x86_64"
        assert module is None

    def test_fixed_src_no_arch(self, controller: VexFeedController) -> None:
        """Fixed product with .src should NOT get .x86_64 appended."""
        product_cpe = {
            "openshift-4.11::el8": "cpe:/a:redhat:openshift:4.11::el8",
        }
        product_purl = {
            "runc-3:1.1.2-3.1.rhaos4.11.el8.src": "pkg:rpm/redhat/runc@1.1.2-3.1.rhaos4.11.el8?arch=src&epoch=3",
        }
        _, pkg, _, _ = controller._parse_product(
            "openshift-4.11::el8:runc-3:1.1.2-3.1.rhaos4.11.el8.src",
            "fixed",
            product_cpe,
            product_purl,
        )
        assert pkg == "runc-3:1.1.2-3.1.rhaos4.11.el8.src"
        assert pkg.endswith(".src")

    def test_unsupported_status(self, controller: VexFeedController) -> None:
        """Unsupported product status raises NotImplementedError."""
        with pytest.raises(NotImplementedError):
            controller._parse_product("rhel-9:pkg/pkg", "under_investigation", {}, {})


# pylint: disable=protected-access
class TestVexFeedExtractVariant:
    """Tests for variant suffix extraction."""

    def test_simple_version(self) -> None:
        """Simple RHEL version."""
        assert VexFeedController._extract_variant_suffix("rhel-8") == "8"

    def test_eus_version(self) -> None:
        """EUS version string."""
        assert VexFeedController._extract_variant_suffix("rhel-9.2.0.z.eus") == "9.2.0.z.eus"

    def test_with_channel(self) -> None:
        """Version with :: channel suffix."""
        assert VexFeedController._extract_variant_suffix("rhel-8.6.0.z.eus::appstream") == "8.6.0.z.eus"

    def test_br_prefix(self) -> None:
        """Branch prefix (rhel-br-)."""
        assert VexFeedController._extract_variant_suffix("rhel-br-8.8.0.z::appstream") == "8.8.0.z"

    def test_rhscl(self) -> None:
        """RHSCL version."""
        assert VexFeedController._extract_variant_suffix("rhscl-3.5.0::el7") == "3.5.0"

    def test_no_dash(self) -> None:
        """Branch without dash returns default."""
        assert VexFeedController._extract_variant_suffix("rhel") == DEFAULT_VARIANT


# pylint: disable=protected-access
class TestVexFeedFindBranchProduct:
    """Tests for _find_branch_product helper."""

    @pytest.fixture
    def controller(self, db_conn: connection) -> VexFeedController:  # pylint: disable=unused-argument
        """Fixture returning VexFeedController."""
        ctrl = VexFeedController()
        return ctrl

    def test_longest_match(self, controller: VexFeedController) -> None:
        """Should prefer longest matching prefix."""
        product_cpe = {
            "rhel-8": "cpe:/o:redhat:enterprise_linux:8",
            "rhel-8.6.0.z.eus::appstream": "cpe:/a:redhat:rhel_eus:8.6::appstream",
        }
        result = controller._find_branch_product(
            "rhel-8.6.0.z.eus::appstream:pkg/pkg-0:1-1.el8.src", product_cpe
        )
        assert result == "rhel-8.6.0.z.eus::appstream"

    def test_no_match(self, controller: VexFeedController) -> None:
        """Should return None when no prefix matches."""
        product_cpe = {"rhel-9": "cpe:/o:redhat:enterprise_linux:9"}
        result = controller._find_branch_product("rhel-8:pkg/pkg", product_cpe)
        assert result is None

    def test_separator_check(self, controller: VexFeedController) -> None:
        """Should not match partial prefixes (e.g. rhel-8 should not match rhel-8.6...)."""
        product_cpe = {
            "rhel-8": "cpe:/o:redhat:enterprise_linux:8",
        }
        result = controller._find_branch_product(
            "rhel-8.6.0.z.eus::appstream:pkg/pkg-0:1-1.el8.src", product_cpe
        )
        # "rhel-8" is followed by "." which is not ":" or "/", so should not match
        assert result is None
