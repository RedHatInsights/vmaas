"""Websocket initialization test."""

from websocket import websocket as ws  # pylint: disable=no-name-in-module


def test_run_app():
    """Test websocket init process."""
    ws.create_app()
