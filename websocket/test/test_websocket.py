"""Test VMaaS websocket."""
import http

import tornado.testing
import tornado.web

from websocket import websocket as ws  # pylint: disable=no-name-in-module


class TestWebSocket(tornado.testing.AsyncHTTPTestCase):
    """Test VMaaS websocket."""

    def get_app(self):
        app = ws.WebsocketApplication()
        return app

    def test_monitoring_health(self):
        """Test reposcan invalidate cache notification."""
        resp = self.fetch("/api/v1/monitoring/health/", method="GET")
        self.assertEqual(resp.code, http.HTTPStatus.OK)
