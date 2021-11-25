#!/usr/bin/env python3
"""
Main entrypoint of websocket server.
"""
import signal
import uuid

from tornado.ioloop import IOLoop
from tornado.web import Application, RequestHandler
from tornado.websocket import WebSocketHandler

from vmaas.common.config import Config
from vmaas.common.logging_utils import get_logger
from vmaas.common.logging_utils import init_logging

WEBSOCKET_PING_INTERVAL = 5
WEBSOCKET_TIMEOUT = 60

LOGGER = get_logger("websocket")


class NotificationHandler(WebSocketHandler):
    """Websocket handler to send messages to subscribed clients."""
    connections = {}
    # Timestamp of the last data dump reported by reposcan
    last_dump_version = None
    last_advertised_version = None
    # What is the freshest data each webapp has
    webapp_export_timestamps = {}
    webapp_statuses = {}

    def open(self, *args, **kwargs):
        # Uuid just for reference in logs
        self.connections[self] = [uuid.uuid4().hex[:8], "unsubscribed"]
        LOGGER.info("New connection: %s", self.connections[self][0])

    def data_received(self, chunk):
        pass

    @classmethod
    def poll_notify(cls):
        """Check and possibly send updates to webapps and listeners"""
        total_count = cls.webapps_count()
        ready_count = cls.webapps_ready_count()
        updated_count = cls.webapps_updated_count()
        outdated_count = total_count - cls.webapps_updated_count()

        # At least one webapp is outdated
        if total_count != updated_count:

            # Outdated, but currently not updating webapps
            updatable = [conn for conn, val in cls.connections.items() if val[1] == "webapp"
                         and cls.webapp_export_timestamps.get(conn) != cls.last_dump_version
                         and cls.webapp_statuses.get(conn) == "ready"]

            # If we have 1 webapp left to update, perform the update, if more, keep at least one
            # in its current state
            to_update = 1 if outdated_count == 1 else min(ready_count, outdated_count) - 1
            updatable = updatable[:to_update]
            if len(updatable) > 0:
                LOGGER.info("Updating %d webapps: %s", len(updatable),
                            ", ".join([cls.connections[conn][0] for conn in updatable]))

            # Send refresh message to webapps, removing status, since from this point their
            # status is indeterminate (They should start updating themselves, but we don't know that until
            # the status is reported by webapps)
            for conn in updatable:
                conn.write_message("refresh-cache")
                del cls.webapp_statuses[conn]

        # We have all webapps up to date, but advertised version is outdated
        if cls.last_dump_version != cls.last_advertised_version and cls.webapps_count() == cls.webapps_ready_count() \
                and cls.webapps_count() > 0 and str(cls.last_dump_version) != "None":
            LOGGER.info("Advertising dump version %s to listeners", cls.last_dump_version)
            cls.last_advertised_version = cls.last_dump_version
            cls.send_message("listener", "webapps-refreshed")

    @classmethod
    def webapps_count(cls):
        """ count of webapps"""
        return len([c for c in cls.connections.values() if c[1] == "webapp"])

    @classmethod
    def webapps_ready_count(cls):
        """ All webapps report ready state, and have the same export timestamp"""
        return len([s for s in cls.webapp_statuses.values() if s == "ready"])

    @classmethod
    def webapps_updated_count(cls):
        """ Count of webapps serving latest data """
        return len([s for s in cls.webapp_export_timestamps.values() if s == cls.last_dump_version])

    def on_message(self, message):
        LOGGER.info("Received message from %s (%s): %s", self.connections[self][1], self.connections[self][0], message)
        if message == "subscribe-webapp":
            self.connections[self][1] = "webapp"
        elif message == "subscribe-reposcan":
            self.connections[self][1] = "reposcan"
        elif message == "subscribe-listener":
            self.connections[self][1] = "listener"
        elif message.startswith("version") and self.connections[self][1] == "reposcan":
            _, timestamp = message.split()
            self.__class__.last_dump_version = timestamp
        elif message.startswith("version") and self.connections[self][1] == "webapp":
            _, timestamp = message.split()
            self.webapp_export_timestamps[self] = timestamp
        elif message.startswith("status") and self.connections[self][1] == "webapp":
            _, status = message.split("-")
            self.webapp_statuses[self] = status
        self.poll_notify()

    def on_close(self):
        super().on_close()
        LOGGER.warning("Closing connection: %s", self.connections[self][0])
        del self.connections[self]
        if self in self.webapp_export_timestamps:
            del self.webapp_export_timestamps[self]
        if self in self.webapp_statuses:
            del self.webapp_statuses[self]

    @classmethod
    def send_message(cls, target_client_type, message):
        """Send message to selected group of connected clients."""
        for client, (client_id, client_type) in cls.connections.items():
            if client_type == target_client_type:
                client.write_message(message)
                LOGGER.info("Sent message to %s (%s): %s", target_client_type, client_id, message)


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
            (r"/healthz/?", HealthHandler)
        ]

        Application.__init__(self, handlers, websocket_ping_interval=WEBSOCKET_PING_INTERVAL,
                             websocket_ping_timeout=WEBSOCKET_TIMEOUT)

    @staticmethod
    def stop():
        """Stop the websocket"""
        IOLoop.instance().stop()


def create_app():
    """Create websocket tornado app."""
    app = WebsocketApplication()
    cfg = Config()

    def terminate(*_):
        """Trigger shutdown."""
        IOLoop.instance().add_callback_from_signal(app.stop)

    signals = (signal.SIGHUP, signal.SIGTERM, signal.SIGINT)
    for sig in signals:
        signal.signal(sig, terminate)

    port = cfg.private_port or cfg.websocket_port
    LOGGER.info("Websocket is listening on port %s", port)
    app.listen(port)


def main():
    """Main entrypoint."""
    init_logging()
    create_app()
    IOLoop.instance().start()


if __name__ == '__main__':
    main()
