"""
Custom middlewares for connexion/starlette.
"""
import json
import time

from starlette.datastructures import MutableHeaders

from vmaas.common.logging_utils import get_logger
from vmaas.common.probes import REQUEST_COUNTS
from vmaas.common.probes import REQUEST_TIME

LOGGER = get_logger(__name__)


class ErrorHandlerMiddleware:
    """Middleware to wrap error message in JSON struct."""
    def __init__(self, app):
        self.app = app

    def _format_error(self, detail, status):
        res = {}
        res["type"] = "about:blank"
        res["detail"] = detail
        res["status"] = status
        return res

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        start_message = {}

        async def send_with_formatted_error(message):
            nonlocal start_message
            if message["type"] == "http.response.start":
                start_message = message
            elif message["type"] == "http.response.body":
                if start_message["status"] >= 400:
                    headers = MutableHeaders(raw=start_message["headers"])
                    error = message["body"].decode("utf-8").strip().replace('"', '')
                    better_error = json.dumps(self._format_error(error, start_message["status"])).encode("utf-8")
                    headers["Content-Length"] = str(len(better_error))
                    message["body"] = better_error
                await send(start_message)
                await send(message)

        await self.app(scope, receive, send_with_formatted_error)


class TimingLoggingMiddleware:
    """Middleware to measure duration of requests to each endpoint and exporting it as Prometheus metric."""
    def __init__(self, app, vmaas_component):
        self.app = app
        self.vmaas_component = vmaas_component

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        start_message = {}
        start_time = time.time()

        async def send_finished(message):
            nonlocal start_message
            if message["type"] == "http.response.start":
                start_message = message
            elif message["type"] == "http.response.body":
                duration = time.time() - start_time
                method = scope["method"]
                path_parts = scope["path"].split('/')
                if self.vmaas_component == "webapp":
                    #                    (0) (1)  (2)     (3)
                    # / api / vmaas / v1  /  cves  /  CVE-XXXX-YYYY
                    path_parts = path_parts[:2]
                const_path = '/'.join(path_parts)
                REQUEST_TIME.labels(method, const_path).observe(duration)
                REQUEST_COUNTS.labels(method, const_path, start_message["status"]).inc()

                # Log request as access/error log
                LOGGER.info("%s %s %s HTTP/%s %.6fs",
                            start_message["status"],
                            scope["method"],
                            scope["path"],
                            scope["http_version"],
                            duration)
            await send(message)

        await self.app(scope, receive, send_finished)
