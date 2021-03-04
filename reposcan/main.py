"""Entry point for the reposcan component"""
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.wsgi import WSGIContainer

from common.config import Config
from reposcan import create_app

# pylint: disable=invalid-name
application = create_app()

if __name__ == '__main__':
    cfg = Config()
    server = HTTPServer(WSGIContainer(application))
    server.listen(cfg.public_port or cfg.reposcan_port)
    IOLoop.instance().start()
