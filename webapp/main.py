import os
from aiohttp import web

from app import create_app, init_websocket, PUBLIC_API_PORT, MAX_SERVERS, VMAAS_VERSION
from common.logging_utils import init_logging, get_logger

LOGGER = get_logger(__name__)

if __name__ == '__main__':
    """Run webapp."""
    app = create_app()

    num_servers = int(os.getenv("MAX_VMAAS_SERVERS", MAX_SERVERS))

    #TODO: Implement forking behavior
    init_logging()

    LOGGER.info("Starting (version %s).", VMAAS_VERSION)
    LOGGER.info('Hotcache enabled: %s', os.getenv("HOTCACHE_ENABLED", "YES"))
    init_websocket()

    web.run_app(app.app, port=PUBLIC_API_PORT)