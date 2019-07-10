"""Webapp initialization test."""

import app
from cache import Cache


def test_run_app(monkeypatch, caplog):
    """Test webapp init process."""

    monkeypatch.setattr(Cache, 'reload', lambda _: None)

    app.create_app()

    assert 'Starting (version unknown).' in caplog.messages
    assert 'Hotcache enabled: YES'
