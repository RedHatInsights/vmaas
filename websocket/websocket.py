#!/usr/bin/env python3
"""
Main entrypoint of websocket server.
"""
import signal

from tornado.ioloop import IOLoop, PeriodicCallback
from tornado.web import Application, RequestHandler
from tornado.websocket import WebSocketHandler

from common.logging_utils import get_logger, init_logging

WEBSOCKET_PING_INTERVAL = 5
WEBSOCKET_TIMEOUT = 60

LOGGER = get_logger("websocket")


class NotificationHandler(WebSocketHandler):
    """Websocket handler to send messages to subscribed clients."""
    connections = {}
    # What is the freshest data each webapp has
    webapp_export_timestamps = {}
    # What time did we advertise last
    last_refresh_sent = None

    def __init__(self, application, request, **kwargs):
        super(NotificationHandler, self).__init__(application, request, **kwargs)
        self.last_pong = None
        self.timeout_callback = None

    def open(self, *args, **kwargs):
        self.connections[self] = None
        # Set last pong timestamp to current timestamp and ping client
        self.last_pong = IOLoop.current().time()
        self.ping(b"")
        # Start periodic callback checking time since last received pong
        self.timeout_callback = PeriodicCallback(self.timeout_check, WEBSOCKET_PING_INTERVAL * 1000)
        self.timeout_callback.start()

    def data_received(self, chunk):
        pass

    @classmethod
    def poll_notify(cls):
        """Check and possibly send updates to listeners"""
        refresh_time = list(set(cls.webapp_export_timestamps))[0] if len(cls.webapp_export_timestamps) > 0 else None
        if cls.webapps_ready() and cls.last_refresh_sent != refresh_time:
            LOGGER.info("All webapps have fresh data")
            cls.send_message("listener", "webapps-refreshed")
            cls.last_refresh_sent = refresh_time

    @classmethod
    def webapps_ready(cls):
        """Check whether all of available webapps are ready"""
        app_count = len([c for c in cls.connections.values() if c == "webapp"])
        return app_count == len(cls.webapp_export_timestamps) and len(set(cls.webapp_export_timestamps.values())) == 1

    def on_message(self, message):
        if self.connections[self]:
            LOGGER.info("Received message from %s: %s", self.connections[self], message)
        else:
            LOGGER.info("Received message from unsubscribed client: %s", message)
        if message == "subscribe-webapp":
            self.connections[self] = "webapp"
        elif message == "subscribe-reposcan":
            self.connections[self] = "reposcan"
        elif message == "subscribe-listener":
            self.connections[self] = "listener"
        elif message == "invalidate-cache" and self.connections[self] == "reposcan":
            self.webapp_export_timestamps.clear()
            self.send_message("webapp", "refresh-cache")
        elif message.startswith("refreshed") and self.connections[self] == "webapp":
            _, timestamp = message.split()
            self.webapp_export_timestamps[self] = timestamp
            # All webapp connections are refreshed with same dump version
        self.poll_notify()

    def on_close(self):
        self.timeout_callback.stop()
        del self.connections[self]
        del self.webapp_export_timestamps[self]

    def timeout_check(self):
        """Check time since we received last pong. Send ping again."""
        now = IOLoop.current().time()
        if now - self.last_pong > WEBSOCKET_TIMEOUT:
            self.close(1000, "Connection timed out.")
            return
        self.ping(b"")

    def on_ping(self, data):
        super().on_ping(data)
        self.poll_notify()

    def on_pong(self, data):
        """Pong received from client."""
        self.last_pong = IOLoop.current().time()
        self.poll_notify()

    @classmethod
    def send_message(cls, target_client_type, message):
        """Send message to selected group of connected clients."""
        for client, client_type in cls.connections.items():
            if client_type == target_client_type:
                client.write_message(message)
                LOGGER.info("Sent message to %s: %s", target_client_type, message)


class HealthHandler(RequestHandler):
    """Handler class providing health status."""

    def data_received(self, chunk):
        pass

    def get(self):
        """Get API status.
           ---
           description: Return API status
           responses:
             200:
               description: Application is alive
        """
        self.flush()


class WebsocketApplication(Application):
    """Class defining API handlers."""
    def __init__(self):
        handlers = [
            (r"/?", NotificationHandler),
            (r"/api/v1/monitoring/health/?", HealthHandler),
        ]

        Application.__init__(self, handlers)

    @staticmethod
    def stop():
        """Stop the websocket"""
        IOLoop.instance().stop()


def create_app():
    """Create websocket tornado app."""
    app = WebsocketApplication()

    def terminate(*_):
        """Trigger shutdown."""
        IOLoop.instance().add_callback_from_signal(app.stop)

    signals = (signal.SIGHUP, signal.SIGTERM, signal.SIGINT)
    for sig in signals:
        signal.signal(sig, terminate)

    app.listen(8082)


def main():
    """Main entrypoint."""
    init_logging()
    create_app()
    IOLoop.instance().start()


if __name__ == '__main__':
    main()
