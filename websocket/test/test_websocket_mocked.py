"""Test mocked VMaaS websocket."""
import tornado.testing
import tornado.websocket
import tornado.web

from websocket import websocket as ws


class NotificationHandlerMock(ws.NotificationHandler):
    """Mock NotificationHandler for testing."""

    @classmethod
    def send_message(cls, target_client_type, message):
        """Modify method not to send messages to
        given components but back to testing code."""
        if target_client_type == "webapp":
            ws.NotificationHandler.send_message("reposcan", message)
        elif target_client_type == "listener":
            ws.NotificationHandler.send_message("webapp", message)


class TestVMaaSWebSocket(tornado.testing.AsyncHTTPTestCase):
    """Test mocked VMaaS websocket."""

    def get_app(self):
        app = tornado.web.Application([(r'/', NotificationHandlerMock)])
        return app

    def _init_ws_client(self):
        ws_url = f"ws://localhost:{self.get_http_port()}/"
        return tornado.websocket.websocket_connect(ws_url, ping_interval=5, ping_timeout=10)

    @tornado.testing.gen_test
    def test_reposcan_invalidate_cache(self):
        """Test reposcan invalidate cache notification."""
        ws_client = yield self._init_ws_client()
        ws_client.write_message("subscribe-reposcan")
        ws_client.write_message("invalidate-cache")
        received_msg = yield ws_client.read_message()
        self.assertEqual(received_msg, "refresh-cache")

    @tornado.testing.gen_test()
    def test_webapp_refreshed(self):
        """Test webapp refreshed notification."""
        ws_client = yield self._init_ws_client()
        ws_client.write_message("subscribe-webapp")
        ws_client.write_message("refreshed 2019-07-11T01:02:03")
        received_msg = yield ws_client.read_message()
        self.assertEqual(received_msg, "webapps-refreshed")
