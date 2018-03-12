#!/usr/bin/python

from tornado.ioloop import IOLoop
import tornado.web
import ujson
import os

from database import Database
from cve import CveAPI
from repos import RepoAPI
from updates import UpdatesAPI


class DocHandler(tornado.web.RequestHandler):
    DOC_MSG = """Example of passing input data as a file: <br />
                 curl -F file=@/path/to/json_file http://hostname:8080/api/v1/updates/ <br /> <br />

                 Example of passing imput data as a body of POST request: <br />
                 curl -d "@/path/to/json_file" -H "Content-Type: application/json" -X POST http://hostname:8080/api/v1/updates/
              """
    def get(self):
        self.write(self.DOC_MSG)


class JsonHandler(tornado.web.RequestHandler):
    def get(self):
        index = self.request.uri.rfind('/')
        name = self.request.uri[index + 1:]

        response = self.process_string(name)
        self.write(ujson.dumps(response))

    def post(self):
        # extract input JSON from POST request
        json_data = ''
        # check if JSON is passed as a file or as a body of POST request
        if self.request.files:
            json_data = self.request.files['file'][0]['body']  # pick up only first file (index 0)
        elif self.request.body:
            json_data = self.request.body

        # fill response with packages
        try:
            data = ujson.loads(json_data)
            response = self.process_list(data)
            self.write(ujson.dumps(response))
        except ValueError:
            self.set_status(400, reason='Error: malformed input JSON.')


class UpdatesHandler(JsonHandler):
    def process_string(self, data):
        return self.application.updatesapi.process_list({'package_list': [data]})

    def process_list(self, data):
        return self.application.updatesapi.process_list(data)

class CVEHandler(JsonHandler):
    def process_string(self, data):
        return self.application.cveapi.process_list({'cve_list': [data]})

    def process_list(self, data):
        return self.application.cveapi.process_list(data)

class ReposHandler(JsonHandler):
    def process_string(self, data):
        return self.application.repoapi.process_list({'repository_list': [data]})

    def process_list(self, data):
        return self.application.repoapi.process_list(data)


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/?", DocHandler),
            (r"/api/v1/updates/?", UpdatesHandler),  # POST request
            (r"/api/v1/updates/[a-zA-Z0-9-._:]+", UpdatesHandler),  # GET request with package name
            (r"/api/v1/cves/?", CVEHandler),
            (r"/api/v1/cves/[a-zA-Z0-9*-]+/?", CVEHandler),
            (r"/api/v1/repos/?", ReposHandler),
            (r"/api/v1/repos/[a-zA-Z0-9*-_]+/?", ReposHandler)
        ]
        cursor = Database().cursor()
        self.updatesapi = UpdatesAPI(cursor)
        self.cveapi = CveAPI(cursor)
        self.repoapi = RepoAPI(cursor)
        tornado.web.Application.__init__(self, handlers)


def main():
    app = Application()
    app.listen(8080)
    IOLoop.instance().start()

if __name__ == '__main__':
    main()
