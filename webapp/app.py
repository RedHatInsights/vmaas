#!/usr/bin/python3
"""
Main web API module
"""

import os
import sre_constants
import json


from jsonschema.exceptions import ValidationError
from tornado.ioloop import IOLoop, PeriodicCallback
from tornado.websocket import websocket_connect
import tornado.web


from apispec import APISpec
from cache import Cache
from cve import CveAPI
from repos import RepoAPI
from updates import UpdatesAPI
from errata import ErrataAPI
from dbchange import DBChange
from utils import init_logging, get_logger
import gen

VMAAS_VERSION = os.getenv("VMAAS_VERSION", "unknown")
PUBLIC_API_PORT = 8080
MAX_SERVERS = 1

SPEC = APISpec(
    title='VMaaS Webapp',
    version=VMAAS_VERSION,
    plugins=(
        'apispec.ext.tornado',
    ),
    basePath="/api/v1",
    schemes=["http"],
)

WEBSOCKET_RECONNECT_INTERVAL = 60
LOGGER = get_logger(__name__)

class BaseHandler(tornado.web.RequestHandler):
    """Base handler setting CORS headers."""

    db_cache = None
    updates_api = None
    repo_api = None
    cve_api = None
    errata_api = None
    dbchange_api = None

    def data_received(self, chunk):
        pass

    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "Content-Type")

    def options(self): # pylint: disable=arguments-differ
        self.finish()

    def get_post_data(self):
        """extract input JSON from POST request"""
        json_data = ''

        # check if JSON is passed as a file or as a body of POST request
        if self.request.files:
            json_data = self.request.files['file'][0]['body']  # pick up only first file (index 0)
        elif self.request.body:
            json_data = self.request.body

        try:
            data = json.loads(json_data)
        except ValueError:
            data = None
        return data

    @gen.coroutine
    def handle_post(self, api_endpoint):
        """Takes care of validation of input and execution of POST methods."""
        code = 400
        data = self.get_post_data()
        if data:
            try:
                res = api_endpoint.process_list(data)
                code = 200
            except ValidationError as validerr:
                if validerr.absolute_path:
                    res = '%s : %s' % (validerr.absolute_path.pop(), validerr.message)
                else:
                    res = '%s' % validerr.message
                LOGGER.error('ValidationError: %s', res)
            except ValueError as valuerr:
                res = str(valuerr)
                LOGGER.error('ValueError: %s', res)
            except sre_constants.error as sre_err:
                res = 'Regular expression error: ' + str(sre_err)
                LOGGER.error('sre_constants.error: %s', res)
            except Exception as err: # pylint: disable=broad-except
                err_id = err.__hash__()
                res = 'Internal server error <%s>: please include this error id in bug report.' % err_id
                code = 500
                LOGGER.exception(res)
        else:
            res = 'Error: malformed input JSON.'
            LOGGER.error(res)

        self.set_status(code)
        self.write(res)
        yield self.flush()

    @gen.coroutine
    def handle_get(self, api_endpoint, param_name, param):
        """Takes care of validation of input and execution of GET methods."""
        code = 400
        try:
            result = api_endpoint.process_list({param_name : [param]})
            code = 200
        except sre_constants.error as sre_err:
            result = 'Regular expression error: ' + str(sre_err)
            LOGGER.warning('sre_constants.error: %s', result)

        self.set_status(code)
        self.write(result)
        yield self.flush()


class HealthHandler(BaseHandler):
    """Handler class providing health status."""

    @gen.coroutine
    def get(self):  # pylint: disable=arguments-differ
        """Get API status.
           ---
           description: Return API status
           responses:
             200:
               description: Application is alive
           tags:
             - monitoring
        """
        yield self.flush()


class ApiSpecHandler(BaseHandler):
    """Handler class providing API specification."""

    @gen.coroutine
    def get(self): # pylint: disable=arguments-differ
        """Get API specification.
           ---
           description: Get API specification
           responses:
             200:
               description: OpenAPI/Swagger 2.0 specification JSON returned
        """
        result = SPEC.to_dict()
        self.write(result)
        yield self.flush()


class VersionHandler(BaseHandler):
    """Handler class providing app version."""

    @gen.coroutine
    def get(self): # pylint: disable=arguments-differ
        """Get app version.
           ---
           description: Get version of application
           responses:
             200:
               description: Version of application returned
        """
        self.write(VMAAS_VERSION)
        yield self.flush()


class DBChangeHandler(BaseHandler):
    """
    Class to return last-updated information from VMaaS DB
    """

    @gen.coroutine
    def get(self): # pylint: disable=arguments-differ
        """
        ---
        description: Get last-updated-times for VMaaS DB
        responses:
          200:
            description: Return last-update timestamps for errata, repos, cves, and the db as a whole
            schema:
              $ref: "#/definitions/DBChangeResponse"
        tags:
          - dbchange
        """
        result = self.dbchange_api.process()
        self.write(result)
        yield self.flush()


class UpdatesHandlerGet(BaseHandler):
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
            x-example: kernel-2.6.32-696.20.1.el6.x86_64
        responses:
          200:
            description: Return list of security updates for single package NEVRA
            schema:
              $ref: "#/definitions/UpdatesResponse"
        tags:
          - updates
        """
        self.handle_get(self.updates_api, 'package_list', nevra)


class UpdatesHandlerPost(BaseHandler):
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
        self.handle_post(self.updates_api)


class CVEHandlerGet(BaseHandler):
    """Handler for processing /cves GET requests."""

    def get(self, cve=None):  # pylint: disable=arguments-differ
        """
        ---
        description: Get details about CVEs. It is possible to use POSIX regular expression as a pattern for CVE names.
        parameters:
          - name: cve
            description: CVE name or POSIX regular expression pattern
            required: True
            type: string
            in: path
            x-example: CVE-2017-5715, CVE-2017-571[1-5], CVE-2017-5.*
        responses:
          200:
            description: Return details about CVEs
            schema:
              $ref: "#/definitions/CvesResponse"
        tags:
          - cves
        """
        self.handle_get(self.cve_api, 'cve_list', cve)


class CVEHandlerPost(BaseHandler):
    """Handler for processing /cves POST requests."""

    def post(self): # pylint: disable=arguments-differ
        """
        ---
        description: Get details about CVEs with additional parameters. As a "cve_list" parameter a complete list of CVE
         names can be provided OR one POSIX regular expression.
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
                    example: CVE-2017-57.*
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
        self.handle_post(self.cve_api)


class ReposHandlerGet(BaseHandler):
    """Handler for processing /repos GET requests."""

    def get(self, repo=None):  # pylint: disable=arguments-differ
        """
        ---
        description: Get details about a repository or repository-expression. It is allowed to use POSIX regular
         expression as a pattern for repository names.
        parameters:
          - name: repo
            description: Repository name or POSIX regular expression pattern
            required: True
            type: string
            in: path
            x-example: rhel-6-server-rpms OR rhel-[4567]-.*-rpms OR rhel-\\d-server-rpms
        responses:
          200:
            description: Return details about repository or repositories that match the expression
            schema:
              $ref: "#/definitions/ReposResponse"
        tags:
          - repos
        """
        self.handle_get(self.repo_api, 'repository_list', repo)


class ReposHandlerPost(BaseHandler):
    """Handler for processing /repos POST requests."""

    def post(self): # pylint: disable=arguments-differ
        """
        ---
        description: Get details about list of repositories. "repository_list" can be either a list of repository
         names, OR a single POSIX regular expression.
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
                    example: rhel-6-server-rpms, rhel-7-server-rpms
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
        self.handle_post(self.repo_api)


class ErrataHandlerGet(BaseHandler):
    """Handler for processing /errata GET requests."""

    def get(self, erratum=None): # pylint: disable=arguments-differ
        """
        ---
        description: Get details about errata. It is possible to use POSIX regular
         expression as a pattern for errata names.
        parameters:
          - name: erratum
            description: Errata advisory name or POSIX regular expression pattern
            required: True
            type: string
            in: path
            x-example: RHSA-2018:0512, RHSA-2018:051[1-5], RH.*
        responses:
          200:
            description: Return details about errata
            schema:
              $ref: "#/definitions/ErrataResponse"
        tags:
          - errata
        """
        self.handle_get(self.errata_api, 'errata_list', erratum)


class ErrataHandlerPost(BaseHandler):
    """ /errata API handler """

    def post(self): # pylint: disable=arguments-differ
        """
        ---
        description: Get details about errata with additional parameters. "errata_list"
         parameter can be either a list of errata names OR a single POSIX regular expression.
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
                    example: RHSA-2018:05.*
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
        self.handle_post(self.errata_api)


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
    SPEC.definition("DBChangeResponse", properties={
        "dbchange": {
            "type": "object",
            "properties": {
                "errata_changes": {
                    "type": "string",
                    "example": "2018-04-16 20:07:58.500192+00"
                    },
                "cve_changes": {
                    "type": "string",
                    "example": "2018-04-16 20:06:47.214266+00"
                    },
                "repository_changes": {
                    "type": "string",
                    "example": "2018-04-16 20:07:55.01395+00"
                    },
                "last_change": {
                    "type": "string",
                    "example": "2018-04-16 20:07:58.500192+00"
                    }
                }
            }
    })
    # Register public API handlers to apispec
    for handler in handlers:
        if handler[0].startswith(r"/api/v1/"):
            SPEC.add_path(urlspec=handler)


class Application(tornado.web.Application):
    """ main webserver application class """
    def __init__(self):
        handlers = [
            (r"/api/v1/monitoring/health/?", HealthHandler),
            (r"/api/v1/apispec/?", ApiSpecHandler),
            (r"/api/v1/version/?", VersionHandler),
            (r"/api/v1/updates/?", UpdatesHandlerPost),
            (r"/api/v1/updates/(?P<nevra>[a-zA-Z0-9%-._:]+)", UpdatesHandlerGet),
            (r"/api/v1/cves/?", CVEHandlerPost),
            (r"/api/v1/cves/(?P<cve>[\\a-zA-Z0-9%*-.+^$?\[\]]+)", CVEHandlerGet),
            (r"/api/v1/repos/?", ReposHandlerPost),
            (r"/api/v1/repos/(?P<repo>[\\a-zA-Z0-9%*-.+?\[\]]+)", ReposHandlerGet),
            (r"/api/v1/errata/?", ErrataHandlerPost),
            (r"/api/v1/errata/(?P<erratum>[\\a-zA-Z0-9%*-:.+?\[\]]+)", ErrataHandlerGet),
            (r"/api/v1/dbchange/?", DBChangeHandler)  # GET request
        ]

        tornado.web.Application.__init__(self, handlers, autoreload=False, debug=False, serve_traceback=False)

        setup_apispec(handlers)
        self.reposcan_websocket_url = os.getenv("REPOSCAN_WEBSOCKET_URL", "ws://reposcan:8081/notifications")
        self.reposcan_websocket = None
        self.reconnect_callback = None

    @staticmethod
    def _refresh_cache():
        BaseHandler.db_cache.reload()
        BaseHandler.updates_api.clear_hot_cache()
        LOGGER.info("Cached data refreshed.")

    def websocket_reconnect(self):
        """Try to connect to given WS URL, set message handler and callback to evaluate this connection attempt."""
        if self.reposcan_websocket is None:
            websocket_connect(self.reposcan_websocket_url, on_message_callback=self._read_websocket_message,
                              callback=self._websocket_connect_status)

    def _websocket_connect_status(self, future):
        """Check if connection attempt succeeded."""
        try:
            result = future.result()
        except: # pylint: disable=bare-except
            result = None

        if result is None:
            # TODO: print the traceback as debug message when we use logging module instead of prints here
            LOGGER.warning("Unable to connect to: %s", self.reposcan_websocket_url)
        else:
            LOGGER.info("Connected to: %s", self.reposcan_websocket_url)

        self.reposcan_websocket = result

    def _read_websocket_message(self, message):
        """Read incoming websocket messages."""
        if message is not None:
            if message == "refresh-cache":
                self._refresh_cache()
        else:
            LOGGER.warning("Connection to %s closed: %s (%s)", self.reposcan_websocket_url,
                           self.reposcan_websocket.close_reason, self.reposcan_websocket.close_code)
            self.reposcan_websocket = None


def main():
    """ The main function. It creates VmaaS application, servers, run everything."""

    vmaas_app = Application()

    server = tornado.httpserver.HTTPServer(vmaas_app)
    server.bind(PUBLIC_API_PORT)
    num_servers = int(os.getenv("MAX_VMAAS_SERVERS", MAX_SERVERS))
    server.start(num_servers)  # start forking here
    init_logging(num_servers)
    LOGGER.info("Starting (version %s).", VMAAS_VERSION)

    # The rest stuff must be done only after forking
    BaseHandler.db_cache = Cache()
    BaseHandler.updates_api = UpdatesAPI(BaseHandler.db_cache)
    BaseHandler.repo_api = RepoAPI(BaseHandler.db_cache)
    BaseHandler.cve_api = CveAPI(BaseHandler.db_cache)
    BaseHandler.errata_api = ErrataAPI(BaseHandler.db_cache)
    BaseHandler.dbchange_api = DBChange(BaseHandler.db_cache)

    vmaas_app.websocket_reconnect()
    vmaas_app.reconnect_callback = PeriodicCallback(vmaas_app.websocket_reconnect, WEBSOCKET_RECONNECT_INTERVAL * 1000)
    vmaas_app.reconnect_callback.start()

    IOLoop.instance().start()



if __name__ == '__main__':
    main()
