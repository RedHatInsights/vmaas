"""Webapp initialization test."""

from vmaas.webapp import app
from vmaas.webapp.cache import Cache
from vmaas.common.constants import VMAAS_VERSION


def test_run_app(monkeypatch, caplog):
    """Test webapp init process."""

    monkeypatch.setattr(Cache, 'reload', lambda _: None)

    app.create_app({app.DEFAULT_PATH + "/v1": "webapp.v1.spec.yaml",
                    app.DEFAULT_PATH + "/v2": "webapp.v2.spec.yaml",
                    app.DEFAULT_PATH + "/v3": "webapp.v3.spec.yaml",
                    app.DEFAULT_PATH_API + "/v1": "webapp.v1.spec.yaml",
                    app.DEFAULT_PATH_API + "/v2": "webapp.v2.spec.yaml",
                    app.DEFAULT_PATH_API + "/v3": "webapp.v3.spec.yaml"})

    assert f'Starting (version {VMAAS_VERSION}).' in caplog.messages
