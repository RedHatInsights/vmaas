"""Webapp initialization test."""

import app
from cache import Cache
from common.constants import VMAAS_VERSION


def test_run_app(monkeypatch, caplog):
    """Test webapp init process."""

    monkeypatch.setattr(Cache, 'reload', lambda _: None)

    app.create_app()

    assert f'Starting (version {VMAAS_VERSION}).' in caplog.messages
