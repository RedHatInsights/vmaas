"""Entry point for the application"""
from aiohttp import web
from app import create_app, DEFAULT_PATH, DEFAULT_PATH_API
from app import init_websocket

from common.config import Config
from common.logging_utils import get_logger
from common.logging_utils import init_logging

LOGGER = get_logger(__name__)

if __name__ == '__main__':
    init_logging()
    # pylint: disable=invalid-name
    application = create_app({DEFAULT_PATH + "/v1": "webapp.v1.spec.yaml",
                              DEFAULT_PATH + "/v2": "webapp.v2.spec.yaml",
                              DEFAULT_PATH + "/v3": "webapp.v3.spec.yaml",
                              DEFAULT_PATH_API + "/v1": "webapp.v1.spec.yaml",
                              DEFAULT_PATH_API + "/v2": "webapp.v2.spec.yaml",
                              DEFAULT_PATH_API + "/v3": "webapp.v3.spec.yaml"})
    init_websocket()
    cfg = Config()
    port = cfg.web_port or cfg.webapp_port

    web.run_app(application.app, port=port, access_log_format="%s %r (%a) %Tfs")
