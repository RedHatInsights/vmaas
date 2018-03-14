#!/usr/bin/python
"""
Main web API module
"""

import json
import traceback

from tornado.ioloop import IOLoop
import tornado.web

from database import Database
from cve import CveAPI
from repos import RepoAPI
from updates import UpdatesAPI
from errata import ErrataAPI


# pylint: disable=abstract-method
class JsonHandler(tornado.web.RequestHandler):
    """
    Parent class to parse input json data given a a data or a file.
    """
    def get(self, *args, **kwargs):
        index = self.request.uri.rfind('/')
        name = self.request.uri[index + 1:]

        response = self.process_string(name)
        self.write(response)
        self.flush()

    def post(self, *args, **kwargs):
        # extract input JSON from POST request
        json_data = ''
        # check if JSON is passed as a file or as a body of POST request
        if self.request.files:
            json_data = self.request.files['file'][0]['body']  # pick up only first file (index 0)
        elif self.request.body:
            json_data = self.request.body

        # fill response with packages
        try:
            data = json.loads(json_data)
            response = self.process_list(data)
            self.write(response)
            self.flush()
        except ValueError:
            traceback.print_exc()
            self.set_status(400, reason='Error: malformed input JSON.')

    def process_list(self, data):
        """ Method to process list of input data. """
        raise NotImplementedError("abstract method")

    def process_string(self, data):
        """ Method to process a single input data. """
        raise NotImplementedError("abstract method")

class UpdatesHandler(JsonHandler):
    """ /updates API handler """
    def process_string(self, data):
        return self.application.updatesapi.process_list({'package_list': [data]})

    def process_list(self, data):
        return self.application.updatesapi.process_list(data)

class CVEHandler(JsonHandler):
    """ /cves API handler """
    def process_string(self, data):
        return self.application.cveapi.process_list({'cve_list': [data]})

    def process_list(self, data):
        return self.application.cveapi.process_list(data)

class ReposHandler(JsonHandler):
    """ /repos API handler """
    def process_string(self, data):
        return self.application.repoapi.process_list({'repository_list': [data]})

    def process_list(self, data):
        return self.application.repoapi.process_list(data)

class ErrataHandler(JsonHandler):
    """ /errata API handler """
    def process_string(self, data):
        return self.application.errataapi.process_list({'errata_list': [data]})

    def process_list(self, data):
        return self.application.errataapi.process_list(data)


class Application(tornado.web.Application):
    """ main webserver application class """
    def __init__(self):
        handlers = [
            (r"/api/v1/updates/?", UpdatesHandler),  # POST request
            (r"/api/v1/updates/[a-zA-Z0-9-._:]+", UpdatesHandler),  # GET request with package name
            (r"/api/v1/cves/?", CVEHandler),
            (r"/api/v1/cves/[a-zA-Z0-9*-]+", CVEHandler),
            (r"/api/v1/repos/?", ReposHandler),
            (r"/api/v1/repos/[a-zA-Z0-9*-_]+", ReposHandler),
            (r"/api/v1/errata/?", ErrataHandler),  # POST request
            (r"/api/v1/errata/[a-zA-Z0-9*-:]+", ErrataHandler) # GET request
        ]
        cursor = Database().cursor()
        self.updatesapi = UpdatesAPI(cursor)
        self.cveapi = CveAPI(cursor)
        self.repoapi = RepoAPI(cursor)
        self.errataapi = ErrataAPI(cursor)
        tornado.web.Application.__init__(self, handlers)


def main():
    """ Main application loop. """
    app = Application()
    app.listen(8080)
    IOLoop.instance().start()

if __name__ == '__main__':
    main()
