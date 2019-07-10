"""Reposcan initialization test."""

import reposcan


def test_run_app(caplog):
    """Test reposcan init process."""

    reposcan.create_app()

    assert "Starting (version unknown)." in caplog.messages
