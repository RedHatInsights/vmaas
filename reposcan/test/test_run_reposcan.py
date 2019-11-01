"""Reposcan initialization test."""

import reposcan
from common.constants import VMAAS_VERSION


def test_run_app(caplog):
    """Test reposcan init process."""

    reposcan.create_app()

    assert f"Starting (version {VMAAS_VERSION})." in caplog.messages
