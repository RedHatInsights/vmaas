"""Entry point for the application"""
from aiohttp import web
from app import create_app
from app import init_websocket

from common.config import Config
from common.logging_utils import get_logger
from common.logging_utils import init_logging

LOGGER = get_logger(__name__)

if __name__ == '__main__':
    init_logging()
    # pylint: disable=invalid-name
    application = create_app()
    init_websocket()
    cfg = Config()
    port = cfg.web_port or cfg.webapp_port

    web.run_app(application.app, port=port, access_log_format="%s %r (%a) %Tfs")
