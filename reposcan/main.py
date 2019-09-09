"""Entry point for the reposcan component"""

from tornado.ioloop import IOLoop
from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer

from reposcan import create_app

# pylint: disable=invalid-name
application = create_app()

if __name__ == '__main__':
    server = HTTPServer(WSGIContainer(application))
    server.listen(8081)
    IOLoop.instance().start()
