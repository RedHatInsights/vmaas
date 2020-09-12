"""Test mocked VMaaS websocket."""
import tornado.testing
import tornado.websocket
import tornado.web

from websocket import websocket as ws  # pylint: disable=no-name-in-module


class NotificationHandlerMock(ws.NotificationHandler):
    """Mock NotificationHandler for testing."""


class WebsocketTestCase(tornado.testing.AsyncHTTPTestCase):
    """Shared test case for testing the websocket implementation"""

    def get_app(self):
        app = tornado.web.Application([(r'/', NotificationHandlerMock)])
        return app

    def _init_ws_client(self):
        ws_url = f"ws://localhost:{self.get_http_port()}/"
        return tornado.websocket.websocket_connect(ws_url, ping_interval=5, ping_timeout=10)

    @staticmethod
    def _process():
        return tornado.testing.gen.sleep(0.1)


class TestVMaaSWebSocket(WebsocketTestCase):
    """Test mocked VMaaS websocket."""

    @tornado.testing.gen_test
    def test_reposcan_messages(self):
        """Test reposcan invalidate cache notification."""
        ws_client = yield self._init_ws_client()
        ws_client.write_message("subscribe-reposcan")
        ws_client.write_message("version 2019-07-11T01:02:03")

        yield self._process()

        self.assertEqual(NotificationHandlerMock.last_dump_version, "2019-07-11T01:02:03")

        ws_client.close()

    @tornado.testing.gen_test
    def test_webapp_messages(self):
        """Test webapp refreshed notification."""
        ws_client = yield self._init_ws_client()
        ws_client.write_message("subscribe-webapp")
        ws_client.write_message("version 2019-07-11T01:02:03")
        ws_client.write_message("status-ready")

        yield self._process()

        self.assertEqual(list(NotificationHandlerMock.webapp_export_timestamps.values())[0], "2019-07-11T01:02:03")
        self.assertEqual(list(NotificationHandlerMock.webapp_statuses.values())[0], "ready")

        ws_client.close()


class TestVMaaSWebsocketE2E(WebsocketTestCase):
    """ Test websocket behavior using multiple clients """

    def make_reposcan(self):
        """ Crate a sample reposcan client """
        reposcan = yield self._init_ws_client()
        reposcan.write_message("subscribe-reposcan")
        reposcan.write_message("version 2019-07-11T01:02:03")
        yield self._process()
        return reposcan

    def make_webapp(self):
        """ Create a sample webapp client"""
        webapp = yield self._init_ws_client()
        webapp.write_message("subscribe-webapp")
        webapp.write_message("version 2019-07-11T01:02:03")
        webapp.write_message("status-ready")
        yield self._process()
        return webapp

    @tornado.testing.gen_test
    def test_e2e_single(self):
        """ Test behavior of websocket with both reposcan and single webapp running """
        reposcan = yield from self.make_reposcan()
        webapp = yield from self.make_webapp()

        # Change version
        reposcan.write_message("version 2019-07-11T01:02:04")
        yield self._process()

        self.assertEqual(NotificationHandlerMock.last_dump_version, "2019-07-11T01:02:04")

        msg = yield webapp.read_message()
        # We expect to receive a refresh message
        self.assertEqual(msg, "refresh-cache")

        webapp.close()
        reposcan.close()

    @tornado.testing.gen_test
    def test_e2e_multi(self):
        """ Test behavior of websocket with both reposcan and multiple webapps running """
        reposcan = yield from self.make_reposcan()
        webapp1 = yield from self.make_webapp()
        webapp2 = yield from self.make_webapp()

        self.assertEqual(NotificationHandlerMock.webapps_ready_count(), 2)
        self.assertEqual(NotificationHandlerMock.webapps_updated_count(), 2)
        # Change version
        reposcan.write_message("version 2019-07-11T01:02:04")
        yield self._process()
        # Reposcan is supposed to start updating 1 webapp, so we have 1 ready and none up to date
        self.assertEqual(NotificationHandlerMock.webapps_ready_count(), 1)
        self.assertEqual(NotificationHandlerMock.webapps_updated_count(), 0)
        self.assertEqual(NotificationHandlerMock.last_dump_version, "2019-07-11T01:02:04")
        self.assertEqual(NotificationHandlerMock.last_advertised_version, "2019-07-11T01:02:03")
        # Websocket is supposed to update first webapp
        msg = yield webapp1.read_message()
        # We expect to receive a refresh message
        self.assertEqual(msg, "refresh-cache")
        webapp1.write_message("status-refresh")
        yield self._process()
        webapp1.write_message("version 2019-07-11T01:02:04")
        webapp1.write_message("status-ready")
        yield self._process()
        self.assertEqual(NotificationHandlerMock.webapps_ready_count(), 1)
        self.assertEqual(NotificationHandlerMock.webapps_updated_count(), 1)

        # Update second webapp
        msg = yield webapp2.read_message()
        self.assertEqual(msg, "refresh-cache")
        webapp2.write_message("version 2019-07-11T01:02:04")
        webapp2.write_message("status-ready")
        yield self._process()

        self.assertEqual(NotificationHandlerMock.webapps_ready_count(), 2)
        self.assertEqual(NotificationHandlerMock.webapps_updated_count(), 2)
        self.assertEqual(NotificationHandlerMock.last_advertised_version, "2019-07-11T01:02:04")

        webapp1.close()
        webapp2.close()
        reposcan.close()
