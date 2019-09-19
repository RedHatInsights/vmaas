"""Entry point for the application"""
from aiohttp import web

from app import create_app, init_websocket, PUBLIC_API_PORT
from common.logging_utils import init_logging, get_logger

LOGGER = get_logger(__name__)

if __name__ == '__main__':
    init_logging()
    # pylint: disable=invalid-name
    application = create_app()
    init_websocket()

    web.run_app(application.app, port=PUBLIC_API_PORT)
