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
    schemes=["http"],
)


class BaseHandler(tornado.web.RequestHandler):
    """Base handler setting CORS headers."""
    def data_received(self, chunk):
        pass

    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "Content-Type")

    def options(self): # pylint: disable=arguments-differ
        self.finish()


class ApiSpecHandler(BaseHandler):
    """Handler class providing API specification."""
    def get(self): # pylint: disable=arguments-differ
        """Get API specification.
           ---
           description: Get API specification
           responses:
             200:
               description: OpenAPI/Swagger 2.0 specification JSON returned
        """
        self.write(SPEC.to_dict())


class RefreshHandler(BaseHandler):
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


class JsonHandler(BaseHandler):
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
        parameters:
          - name: nevra
            description: Package NEVRA
            required: True
            type: string
            in: path
            example: kernel-2.6.32-696.20.1.el6.x86_64
        responses:
          200:
            description: Return list of security updates for single package NEVRA
            schema:
              $ref: "#/definitions/UpdatesResponse"
        tags:
          - updates
        """
        self.process_get(name=nevra)


class UpdatesHandlerPost(UpdatesHandler):
    """Handler for processing /updates POST requests."""
    def post(self): # pylint: disable=arguments-differ
        """
        ---
        description: List security updates for list of package NEVRAs
        parameters:
          - name: body
            description: Input JSON
            required: True
            in: body
            schema:
              type: object
              properties:
                package_list:
                  type: array
                  items:
                    type: string
                    example: kernel-2.6.32-696.20.1.el6.x86_64
                repository_list:
                  type: array
                  items:
                    type: string
                    example: rhel-6-server-rpms
                releasever:
                  type: string
                  example: 6Server
                basearch:
                  type: string
                  example: x86_64
              required:
                - package_list
        responses:
          200:
            description: Return list of security updates for list of package NEVRAs
            schema:
              $ref: "#/definitions/UpdatesResponse"
          400:
            description: Invalid input JSON format
        tags:
          - updates
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
        parameters:
          - name: cve
            description: CVE name
            required: True
            type: string
            in: path
            example: CVE-2017-5715
        responses:
          200:
            description: Return details about single CVE
            schema:
              $ref: "#/definitions/CvesResponse"
        tags:
          - cves
        """
        self.process_get(name=cve)


class CVEHandlerPost(CVEHandler):
    """Handler for processing /cves POST requests."""
    def post(self): # pylint: disable=arguments-differ
        """
        ---
        description: Get details about list of CVEs
        parameters:
          - name: body
            description: Input JSON
            required: True
            in: body
            schema:
              type: object
              properties:
                cve_list:
                  type: array
                  items:
                    type: string
                    example: CVE-2017-5715
                modified_since:
                  type: string
                  example: "2018-04-05T01:23:45+02:00"
              required:
                - cve_list
        responses:
          200:
            description: Return details about list of CVEs
            schema:
              $ref: "#/definitions/CvesResponse"
          400:
            description: Invalid input JSON format
        tags:
          - cves
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
        parameters:
          - name: repo
            description: Repository name
            required: True
            type: string
            in: path
            example: rhel-6-server-rpms
        responses:
          200:
            description: Return details about single repository
            schema:
              $ref: "#/definitions/ReposResponse"
        tags:
          - repos
        """
        self.process_get(name=repo)


class ReposHandlerPost(ReposHandler):
    """Handler for processing /repos POST requests."""
    def post(self): # pylint: disable=arguments-differ
        """
        ---
        description: Get details about list of repositories
        parameters:
          - name: body
            description: Input JSON
            required: True
            in: body
            schema:
              type: object
              properties:
                repository_list:
                  type: array
                  items:
                    type: string
                    example: rhel-6-server-rpms
              required:
                - repository_list
        responses:
          200:
            description: Return details about list of repositories
            schema:
              $ref: "#/definitions/ReposResponse"
          400:
            description: Invalid input JSON format
        tags:
          - repos
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
        parameters:
          - name: erratum
            description: Errata advisory name
            required: True
            type: string
            in: path
            example: RHSA-2018:0512
        responses:
          200:
            description: Return details about single erratum
            schema:
              $ref: "#/definitions/ErrataResponse"
        tags:
          - errata
        """
        self.process_get(name=erratum)


class ErrataHandlerPost(ErrataHandler):
    """Handler for processing /errata POST requests."""
    def post(self): # pylint: disable=arguments-differ
        """
        ---
        description: Get details about list of errata
        parameters:
          - name: body
            description: Input JSON
            required: True
            in: body
            schema:
              type: object
              properties:
                errata_list:
                  type: array
                  items:
                    type: string
                    example: RHSA-2018:0512
                modified_since:
                  type: string
                  example: "2018-04-05T01:23:45+02:00"
              required:
                - errata_list
        responses:
          200:
            description: Return details about list of errata
            schema:
              $ref: "#/definitions/ErrataResponse"
          400:
            description: Invalid input JSON format
        tags:
          - errata
        """
        self.process_post()


def setup_apispec(handlers):
    """Setup definitions and handlers for apispec."""
    SPEC.definition("UpdatesResponse", properties={
        "update_list": {
            "type": "object",
            "properties": {
                "kernel-2.6.32-696.20.1.el6.x86_64": {
                    "type": "object",
                    "properties": {
                        "available_updates": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "repository": {
                                        "type": "string",
                                        "example": "rhel-6-server-rpms"
                                    },
                                    "releasever": {
                                        "type": "string",
                                        "example": "6Server"
                                    },
                                    "basearch": {
                                        "type": "string",
                                        "example": "x86_64"
                                    },
                                    "erratum": {
                                        "type": "string",
                                        "example": "RHSA-2018:0512"
                                    },
                                    "package": {
                                        "type": "string",
                                        "example": "kernel-2.6.32-696.23.1.el6.x86_64"
                                    }
                                }
                            }
                        },
                        "description": {
                            "type": "string",
                            "example": "package description"
                        },
                        "summary": {
                            "type": "string",
                            "example": "package summary"
                        }
                    }
                }
            }
        },
        "repository_list": {
            "type": "array",
            "items": {
                "type": "string",
                "example": "rhel-6-server-rpms"
            }
        },
        "releasever": {
            "type": "string",
            "example": "6Server"
        },
        "basearch": {
            "type": "string",
            "example": "x86_64"
        },
    })
    SPEC.definition("CvesResponse", properties={
        "cve_list": {
            "type": "object",
            "properties": {
                "CVE-2017-5715": {
                    "type": "object",
                    "properties": {
                        "impact": {
                            "type": "string",
                            "example": "Medium",
                        },
                        "public_date": {
                            "type": "string",
                            "example": "2018-01-04T13:29:00+00:00",
                        },
                        "synopsis": {
                            "type": "string",
                            "example": "CVE-2017-5715",
                        },
                        "description": {
                            "type": "string",
                            "example": "description text",
                        },
                        "modified_date": {
                            "type": "string",
                            "example": "2018-03-31T01:29:00+00:00",
                        },
                        "redhat_url": {
                            "type": "string",
                            "example": "https://access.redhat.com/security/cve/cve-2017-5715",
                        },
                        "cvss3_score": {
                            "type": "string",
                            "example": "5.600",
                        },
                        "secondary_url": {
                            "type": "string",
                            "example": "http://lists.opensuse.org/opensuse-security-announce/2018-01/msg00002.html",
                        },
                        "cwe_list": {
                            "type": "array",
                            "items": {
                                "type": "string",
                                "example": "CWE-200"
                            }
                        }
                    }
                }
            }
        },
        "modified_since": {
            "type": "string",
            "example": "2018-04-05T01:23:45+02:00"
        },
    })
    SPEC.definition("ReposResponse", properties={
        "repository_list": {
            "type": "object",
            "properties": {
                "rhel-6-server-rpms": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "product": {
                                "type": "string",
                                "example": "Red Hat Enterprise Linux Server"
                            },
                            "releasever": {
                                "type": "string",
                                "example": "6Server"
                            },
                            "name": {
                                "type": "string",
                                "example": "Red Hat Enterprise Linux 6 Server (RPMs)"
                            },
                            "url": {
                                "type": "string",
                                "example": "https://cdn.redhat.com/content/dist/rhel/server/6/6Server/x86_64/os/"
                            },
                            "basearch": {
                                "type": "string",
                                "example": "x86_64"
                            },
                            "revision": {
                                "type": "string",
                                "example": "2018-03-27T10:55:16+00:00"
                            },
                            "label": {
                                "type": "string",
                                "example": "rhel-6-server-rpms"
                            }
                        }
                    }
                }
            }
        }
    })
    SPEC.definition("ErrataResponse", properties={
        "errata_list": {
            "type": "object",
            "properties": {
                "RHSA-2018:0512": {
                    "type": "object",
                    "properties": {
                        "updated": {
                            "type": "string",
                            "example": "2018-03-13T17:31:41+00:00"
                        },
                        "severity": {
                            "type": "string",
                            "example": "Important"
                        },
                        "reference_list": {
                            "type": "array",
                            "items": {
                                "type": "string",
                                "example": "classification-RHSA-2018:0512"
                            }
                        },
                        "issued": {
                            "type": "string",
                            "example": "2018-03-13T17:31:28+00:00"
                        },
                        "description": {
                            "type": "string",
                            "example": "description text"
                        },
                        "solution": {
                            "type": "string",
                            "example": "solution text"
                        },
                        "summary": {
                            "type": "string",
                            "example": "summary text"
                        },
                        "url": {
                            "type": "string",
                            "example": "https://access.redhat.com/errata/RHSA-2018:0512"
                        },
                        "synopsis": {
                            "type": "string",
                            "example": "Important: kernel security and bug fix update"
                        },
                        "cve_list": {
                            "type": "array",
                            "items": {
                                "type": "string",
                                "example": "CVE-2017-5715"
                            }
                        },
                        "bugzilla_list": {
                            "type": "array",
                            "items": {
                                "type": "string",
                                "example": "1519778"
                            }
                        },
                        "package_list": {
                            "type": "array",
                            "items": {
                                "type": "string",
                                "example": "kernel-2.6.32-696.23.1.el6.x86_64"
                            }
                        },
                        "type": {
                            "type": "string",
                            "example": "security"
                        }
                    }
                }
            }
        },
        "modified_since": {
            "type": "string",
            "example": "2018-04-05T01:23:45+02:00"
        },
    })
    # Register public API handlers to apispec
    for handler in handlers:
        if handler[0].startswith(r"/api/v1/"):
            SPEC.add_path(urlspec=handler)


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
        setup_apispec(handlers)
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
