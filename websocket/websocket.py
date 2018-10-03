#!/usr/bin/python3
"""
Main entrypoint of websocket server.
"""
from tornado.ioloop import IOLoop, PeriodicCallback
from tornado.web import Application, RequestHandler
from tornado.websocket import WebSocketHandler

WEBSOCKET_PING_INTERVAL = 60
WEBSOCKET_TIMEOUT = 300


class NotificationHandler(WebSocketHandler):
    """Websocket handler to send messages to subscribed clients."""
    connections = {}
    webapp_export_timestamps = {}

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

    def on_message(self, message):
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
            if (len([c for c in self.connections.values() if c == "webapp"]) == len(self.webapp_export_timestamps)
                    and len(set(self.webapp_export_timestamps.values())) == 1):
                self.send_message("listener", "webapps-refreshed")

    def on_close(self):
        self.timeout_callback.stop()
        del self.connections[self]

    def timeout_check(self):
        """Check time since we received last pong. Send ping again."""
        now = IOLoop.current().time()
        if now - self.last_pong > WEBSOCKET_TIMEOUT:
            self.close(1000, "Connection timed out.")
            return
        self.ping(b"")

    def on_pong(self, data):
        """Pong received from client."""
        self.last_pong = IOLoop.current().time()

    @staticmethod
    def send_message(target_client_type, message):
        """Send message to selected group of connected clients."""
        for client, client_type in NotificationHandler.connections.items():
            if client_type == target_client_type:
                client.write_message(message)


class HealthHandler(RequestHandler):
    """Handler class providing health status."""

    def data_received(self, chunk):
        pass

    def get(self):  # pylint: disable=arguments-differ
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


def main():
    """Main entrypoint."""
    app = WebsocketApplication()
    app.listen(8082)
    IOLoop.instance().start()

if __name__ == '__main__':
    main()
