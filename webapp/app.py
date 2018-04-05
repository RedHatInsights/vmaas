#!/usr/bin/python
"""
Main web API module
"""

import sys
import json
import traceback

from apispec import APISpec
from tornado.ioloop import IOLoop
import tornado.web

from database import Database
from cve import CveAPI
from repos import RepoAPI, RepoCache
from updates import UpdatesAPI
from errata import ErrataAPI

INTERNAL_API_PORT = 8079
PUBLIC_API_PORT = 8080

SPEC = APISpec(
    title='VMaaS Webapp',
    version='1',
    plugins=(
        'apispec.ext.tornado',
    ),
    basePath="/api/v1",
)


# pylint: disable=abstract-method
class ApiSpecHandler(tornado.web.RequestHandler):
    """Handler class providing API specification."""
    def get(self): # pylint: disable=arguments-differ
        """Get API specification.
           ---
           description: Get API specification
           responses:
             200:
               description: OpenAPI/Swagger 2.0 specification JSON returned
        """
        self.set_header("Access-Control-Allow-Origin", "*")
        self.write(SPEC.to_dict())


# pylint: disable=abstract-method
class RefreshHandler(tornado.web.RequestHandler):
    """
    Class to refresh cached data in handlers.
    """
    def get(self): # pylint: disable=arguments-differ
        # There could be authentication instead of this simple check in future
        accessed_port = int(self.request.host.split(':')[1])
        if accessed_port == INTERNAL_API_PORT:
            try:
                self.application.updatesapi.prepare()
                self.application.repocache.prepare()
                msg = "Cached data refreshed."
                print(msg)
                sys.stdout.flush()
                self.write({"success": True, "msg": msg})
            except: # pylint: disable=bare-except
                traceback.print_exc()
                self.set_status(500)
                self.write({"success": False, "msg": "Unable to refresh cached data."})
        else:
            self.set_status(403)
            self.write({"success": False, "msg": "This API can be called internally only."})
        self.flush()

# pylint: disable=abstract-method
class JsonHandler(tornado.web.RequestHandler):
    """
    Parent class to parse input json data given a a data or a file.
    """
    def process_get(self, name=None):
        """Process GET request."""
        response = self.process_string(name)
        self.write(response)
        self.flush()

    def process_post(self):
        """Process POST request."""
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


class UpdatesHandlerGet(UpdatesHandler):
    """Handler for processing /updates GET requests."""
    def get(self, nevra=None): # pylint: disable=arguments-differ
        """
        ---
        description: List security updates for single package NEVRA
        responses:
          200:
            description: Return list of security updates for single package NEVRA
        """
        self.process_get(name=nevra)


class UpdatesHandlerPost(UpdatesHandler):
    """Handler for processing /updates POST requests."""
    def post(self): # pylint: disable=arguments-differ
        """
        ---
        description: List security updates for list of package NEVRAs
        responses:
          200:
            description: Return list of security updates for list of package NEVRAs
          400:
            description: Invalid input JSON format
        """
        self.process_post()


class CVEHandler(JsonHandler):
    """ /cves API handler """
    def process_string(self, data):
        return self.application.cveapi.process_list({'cve_list': [data]})

    def process_list(self, data):
        return self.application.cveapi.process_list(data)


class CVEHandlerGet(CVEHandler):
    """Handler for processing /cves GET requests."""
    def get(self, cve=None): # pylint: disable=arguments-differ
        """
        ---
        description: Get details about single CVE
        responses:
          200:
            description: Return details about single CVE
        """
        self.process_get(name=cve)


class CVEHandlerPost(CVEHandler):
    """Handler for processing /cves POST requests."""
    def post(self): # pylint: disable=arguments-differ
        """
        ---
        description: Get details about list of CVEs
        responses:
          200:
            description: Return details about list of CVEs
          400:
            description: Invalid input JSON format
        """
        self.process_post()


class ReposHandler(JsonHandler):
    """ /repos API handler """
    def process_string(self, data):
        return self.application.repoapi.process_list({'repository_list': [data]})

    def process_list(self, data):
        return self.application.repoapi.process_list(data)


class ReposHandlerGet(ReposHandler):
    """Handler for processing /repos GET requests."""
    def get(self, repo=None): # pylint: disable=arguments-differ
        """
        ---
        description: Get details about single repository
        responses:
          200:
            description: Return details about single repository
        """
        self.process_get(name=repo)


class ReposHandlerPost(ReposHandler):
    """Handler for processing /repos POST requests."""
    def post(self): # pylint: disable=arguments-differ
        """
        ---
        description: Get details about list of repositories
        responses:
          200:
            description: Return details about list of repositories
          400:
            description: Invalid input JSON format
        """
        self.process_post()


class ErrataHandler(JsonHandler):
    """ /errata API handler """
    def process_string(self, data):
        return self.application.errataapi.process_list({'errata_list': [data]})

    def process_list(self, data):
        return self.application.errataapi.process_list(data)


class ErrataHandlerGet(ErrataHandler):
    """Handler for processing /errata GET requests."""
    def get(self, erratum=None): # pylint: disable=arguments-differ
        """
        ---
        description: Get details about single erratum
        responses:
          200:
            description: Return details about single erratum
        """
        self.process_get(name=erratum)


class ErrataHandlerPost(ErrataHandler):
    """Handler for processing /errata POST requests."""
    def post(self): # pylint: disable=arguments-differ
        """
        ---
        description: Get details about list of errata
        responses:
          200:
            description: Return details about list of errata
          400:
            description: Invalid input JSON format
        """
        self.process_post()


class Application(tornado.web.Application):
    """ main webserver application class """
    def __init__(self):
        handlers = [
            (r"/api/internal/refresh/?", RefreshHandler),  # GET request
            (r"/api/v1/apispec/?", ApiSpecHandler),
            (r"/api/v1/updates/?", UpdatesHandlerPost),
            (r"/api/v1/updates/(?P<nevra>[a-zA-Z0-9%-._:]+)", UpdatesHandlerGet),
            (r"/api/v1/cves/?", CVEHandlerPost),
            (r"/api/v1/cves/(?P<cve>[a-zA-Z0-9%*-]+)", CVEHandlerGet),
            (r"/api/v1/repos/?", ReposHandlerPost),
            (r"/api/v1/repos/(?P<repo>[a-zA-Z0-9%*-_]+)", ReposHandlerGet),
            (r"/api/v1/errata/?", ErrataHandlerPost),
            (r"/api/v1/errata/(?P<erratum>[a-zA-Z0-9%*-:]+)", ErrataHandlerGet)
        ]
        # Register public API handlers to apispec
        for handler in handlers:
            if handler[0].startswith(r"/api/v1/"):
                SPEC.add_path(urlspec=handler)
        db_instance = Database()
        cursor = db_instance.cursor()
        self.repocache = RepoCache(cursor)
        self.updatesapi = UpdatesAPI(cursor, self.repocache)
        self.cveapi = CveAPI(cursor)
        self.repoapi = RepoAPI(self.repocache)
        self.errataapi = ErrataAPI(db_instance)
        tornado.web.Application.__init__(self, handlers)


def main():
    """ Main application loop. """
    app = Application()
    app.listen(INTERNAL_API_PORT)
    app.listen(PUBLIC_API_PORT)
    IOLoop.instance().start()

if __name__ == '__main__':
    main()
