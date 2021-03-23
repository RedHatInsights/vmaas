"""Entry point for the reposcan component"""
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.wsgi import WSGIContainer

from common.config import Config
from reposcan import create_app, DEFAULT_PATH, DEFAULT_PATH_API

# pylint: disable=invalid-name
application = create_app({DEFAULT_PATH + "/v1": "reposcan.spec.yaml",
                          DEFAULT_PATH_API + "/v1": "reposcan.spec.yaml",
                          "": "reposcan.healthz.spec.yaml"})

if __name__ == '__main__':
    cfg = Config()
    server = HTTPServer(WSGIContainer(application))
    server.listen(cfg.public_port or cfg.reposcan_port)
    IOLoop.instance().start()
