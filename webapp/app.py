#!/usr/bin/python

from tornado.ioloop import IOLoop
import tornado.web
import ujson
import falcon
import errata
import sys
import os

EXAMPLE_MSG = """Example: <br /> curl -F file=@/path/to/plaintext_file http://hostname:8080/api/v1/plain/ <br />
                 curl -F file=@/path/to/json_file http://hostname:8080/api/v1/json/
              """

cursor = errata.init_db(os.getenv('POSTGRES_DB', errata.DEFAULT_DB_NAME), 
                        os.getenv('POSTGRES_USER', errata.DEFAULT_DB_USER),
                        os.getenv('POSTGRES_PASSWORD', errata.DEFAULT_DB_PASSWORD),
                        os.getenv('POSTGRES_HOST', 'vmaas_db'), 
                        os.getenv('POSTGRES_PORT', errata.DEFAULT_DB_PORT))


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write(EXAMPLE_MSG)


class PlaintextHandler(tornado.web.RequestHandler):
    def get(self):
        self.write('')

    def post(self):
        plaintext_file = self.request.files['file'][0]['body']
        contents = plaintext_file.split('\n')
        for line in sorted(set(contents)):
            if line and line.strip():
                self.write(str(errata.process(line, cursor)))


class JsonHandler(tornado.web.RequestHandler):
    def get(self):
        self.write('')

    def post(self):
        json_data = self.request.files['file'][0]['body']
        try:
            data = ujson.loads(json_data)
            for pkg in sorted(set(data['package_list'])):
                if pkg and pkg.strip():
                    self.write(str(errata.process(pkg, cursor)))
        except ValueError:
            self.set_status(400, reason='Error: malformed input JSON.')


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/?", MainHandler),
            (r"/api/v1/plain/?", PlaintextHandler),
            (r"/api/v1/json/?", JsonHandler)
        ]
        tornado.web.Application.__init__(self, handlers)


def main():
    app = Application()
    app.listen(8080)
    IOLoop.instance().start()

if __name__ == '__main__':
    main()
