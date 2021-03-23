"""Reposcan initialization test."""

import reposcan
from common.constants import VMAAS_VERSION


def test_run_app(caplog):
    """Test reposcan init process."""

    reposcan.create_app({reposcan.DEFAULT_PATH + "/v1": "reposcan.spec.yaml",
                         reposcan.DEFAULT_PATH_API + "/v1": "reposcan.spec.yaml",
                         "": "reposcan.healthz.spec.yaml"})

    assert f"Starting (version {VMAAS_VERSION})." in caplog.messages
