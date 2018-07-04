#!/usr/bin/python3
"""
Main entrypoint of reposcan tool. It provides and API and allows to sync specified repositories
into specified PostgreSQL database.
"""

import os
from multiprocessing.pool import Pool
import json

from apispec import APISpec
from tornado.ioloop import IOLoop, PeriodicCallback
from tornado.web import RequestHandler, Application
from tornado.websocket import WebSocketHandler

from common.logging import get_logger, init_logging
from database.database_handler import DatabaseHandler, init_db
from database.product_store import ProductStore
from exporter import DUMP, main as export_data
from nistcve.cve_controller import CveRepoController
from redhatcve.cvemap_controller import CvemapController
from repodata.repository_controller import RepositoryController

VMAAS_VERSION = os.getenv("VMAAS_VERSION", "unknown")
LOGGER = get_logger(__name__)

SPEC = APISpec(
    title='VMaaS Reposcan',
    version=VMAAS_VERSION,
    plugins=(
        'apispec.ext.tornado',
    ),
    basePath="/api/v1",
)

WEBSOCKET_PING_INTERVAL = 60
WEBSOCKET_TIMEOUT = 300


class NotificationHandler(WebSocketHandler):
    """Websocket handler to send messages to subscribed clients."""
    connections = set()

    def __init__(self, application, request, **kwargs):
        super(NotificationHandler, self).__init__(application, request, **kwargs)
        self.last_pong = None
        self.timeout_callback = None

    def open(self, *args, **kwargs):
        self.connections.add(self)
        # Set last pong timestamp to current timestamp and ping client
        self.last_pong = IOLoop.current().time()
        self.ping(b"")
        # Start periodic callback checking time since last received pong
        self.timeout_callback = PeriodicCallback(self.timeout_check, WEBSOCKET_PING_INTERVAL * 1000)
        self.timeout_callback.start()

    def data_received(self, chunk):
        pass

    def on_message(self, message):
        """We don't need to handle any incoming messages."""
        pass

    def on_close(self):
        self.timeout_callback.stop()
        self.connections.remove(self)

    def timeout_check(self):
        """Check time since we received last pong. Send ping again."""
        now = IOLoop.current().time()
        if now - self.last_pong > WEBSOCKET_TIMEOUT:
            self.close(1000, "Connection timed out.")
            return
        self.ping(b"")

    def on_pong(self, data):
        """Pong received from client."""
        self.last_pong = IOLoop.current().time()


class ResponseJson(dict):
    """Object used as API response to user, represented as JSON"""
    def __init__(self, msg, success=True):
        super(ResponseJson, self).__init__()
        self['msg'] = msg
        self['success'] = success

    def __repr__(self):
        return json.dumps(self)


class BaseHandler(RequestHandler):
    """Base handler setting CORS headers."""
    def data_received(self, chunk):
        pass

    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "Content-Type")

    def options(self): # pylint: disable=arguments-differ
        self.finish()


class HealthHandler(BaseHandler):
    """Handler class providing health status."""

    def get(self):  # pylint: disable=arguments-differ
        """Get API status.
           ---
           description: Return API status
           responses:
             200:
               description: Application is alive
        """
        self.flush()


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


class VersionHandler(BaseHandler):
    """Handler class providing app version."""
    def get(self): # pylint: disable=arguments-differ
        """Get app version.
           ---
           description: Get version of application
           responses:
             200:
               description: Version of application returned
        """
        self.write(VMAAS_VERSION)
        self.flush()


class RepoListHandler(BaseHandler):
    """Handler for repository list/add API."""

    @staticmethod
    def _content_set_to_repos(content_set):
        baseurl = content_set["baseurl"]
        basearches = content_set["basearch"]
        releasevers = content_set["releasever"]

        # (repo_url, basearch, releasever)
        repos = [(baseurl, None, None)]
        # Replace basearch
        if basearches:
            repos = [(repo[0].replace("$basearch", basearch), basearch, repo[2])
                     for basearch in basearches for repo in repos]
        # Replace releasever
        if releasevers:
            repos = [(repo[0].replace("$releasever", releasever), repo[1], releasever)
                     for releasever in releasevers for repo in repos]

        return repos

    def _parse_input_list(self):
        products = {}
        repos = []
        json_data = ""
        # check if JSON is passed as a file or as a body of POST request
        if self.request.files:
            json_data = self.request.files['file'][0]['body']  # pick up only first file (index 0)
        elif self.request.body:
            json_data = self.request.body

        data = json.loads(json_data)
        for repo_group in data:
            # Entitlement cert is optional
            if "entitlement_cert" in repo_group:
                cert_name = repo_group["entitlement_cert"]["name"]
                ca_cert = repo_group["entitlement_cert"]["ca_cert"]
                cert = repo_group["entitlement_cert"]["cert"]
                key = repo_group["entitlement_cert"]["key"]
            else:
                cert_name, ca_cert, cert, key = None, None, None, None

            # Repository list with product and content set information
            for product_name, product in repo_group["products"].items():
                products[product_name] = {"product_id": product.get("redhat_eng_product_id", None), "content_sets": {}}
                for content_set_label, content_set in product["content_sets"].items():
                    products[product_name]["content_sets"][content_set_label] = content_set["name"]
                    for repo_url, basearch, releasever in self._content_set_to_repos(content_set):
                        repos.append((repo_url, content_set_label, basearch, releasever,
                                      cert_name, ca_cert, cert, key))

        return products, repos

    def post(self): # pylint: disable=arguments-differ
        """Add repositories listed in request to the DB.
           ---
           description: Add repositories listed in request to the DB
           parameters:
             - name: body
               description: Input JSON
               required: True
               in: body
               schema:
                 type: array
                 items:
                   type: object
                   properties:
                     entitlement_cert:
                       type: object
                       properties:
                         name:
                           type: string
                           example: RHSM-CDN
                         ca_cert:
                           type: string
                         cert:
                           type: string
                         key:
                           type: string
                       required:
                         - name
                         - ca_cert
                     products:
                       type: object
                       properties:
                         Red Hat Enterprise Linux Server:
                           type: object
                           properties:
                             redhat_eng_product_id:
                               type: integer
                               example: 69
                             content_sets:
                               type: object
                               properties:
                                 rhel-6-server-rpms:
                                   type: object
                                   properties:
                                     name:
                                       type: string
                                       example: Red Hat Enterprise Linux 6 Server (RPMs)
                                     baseurl:
                                       type: string
                                       example: https://cdn/content/dist/rhel/server/6/$releasever/$basearch/os/
                                     basearch:
                                       type: array
                                       items:
                                         type: string
                                         example: x86_64
                                     releasever:
                                       type: array
                                       items:
                                         type: string
                                         example: 6Server
                                   required:
                                     - name
                                     - baseurl
                                     - basearch
                                     - releasever
                           required:
                             - content_sets
                   required:
                     - products
           responses:
             200:
               description: Repos and products added to the DB
               schema:
                 $ref: "#/definitions/StatusResponse"
             400:
               description: Invalid input JSON format
           tags:
             - repos
        """
        try:
            products, repos = self._parse_input_list()
        except Exception as err: # pylint: disable=broad-except
            products = None
            repos = None
            msg = "Internal server error <%s>" % err.__hash__()
            LOGGER.exception(msg)
            self.set_status(400)

            self.write(ResponseJson(msg, success=False))
            self.flush()
        if repos:
            self.import_repositories(products=products, repos=repos)
            msg = "Products and repositories imported."
            self.write(ResponseJson(msg))
            self.flush()

    @staticmethod
    def import_repositories(products=None, repos=None):
        """Function to import all repositories from input list to the DB."""
        try:
            init_logging()
            init_db()

            if products:
                product_store = ProductStore()
                product_store.store(products)

            if repos:
                repository_controller = RepositoryController()
                # Sync repos from input
                for repo_url, content_set, basearch, releasever, cert_name, ca_cert, cert, key in repos:
                    repository_controller.add_repository(repo_url, content_set, basearch, releasever,
                                                         cert_name=cert_name, ca_cert=ca_cert,
                                                         cert=cert, key=key)
                repository_controller.import_repositories()
        except Exception as err: # pylint: disable=broad-except
            msg = "Internal server error <%s>" % err.__hash__()
            LOGGER.exception(msg)
            DatabaseHandler.rollback()


class SyncHandler(BaseHandler):
    """Base handler class providing common methods for different sync types."""

    task_type = None

    @classmethod
    def start_task(cls, *args, **kwargs):
        """Start given task if DB worker isn't currently executing different task."""
        if not SyncTask.is_running():
            msg = "%s task started." % cls.task_type
            LOGGER.info(msg)
            SyncTask.start(cls.run_task_and_export, cls.finish_task, *args, **kwargs)
            status_code = 200
            status_msg = ResponseJson(msg)
        else:
            msg = "%s task request ignored. Another task already in progress." % cls.task_type
            LOGGER.info(msg)
            # Too Many Requests
            status_code = 429
            status_msg = ResponseJson(msg, success=False)
        return status_code, status_msg

    @classmethod
    def run_task_and_export(cls, *args, **kwargs):
        """Run sync task of current class and export."""
        result = cls.run_task(*args, **kwargs)
        if cls != ExporterHandler:
            ExporterHandler.run_task()
        return result

    @staticmethod
    def _notify_webapps():
        for client in NotificationHandler.connections:
            client.write_message("refresh-cache")

    @staticmethod
    def run_task(*args, **kwargs):
        """Run synchronization task."""
        raise NotImplementedError("abstract method")

    @classmethod
    def finish_task(cls, task_result):
        """Mark current task as finished."""
        # Notify webapps to update it's cache
        SyncHandler._notify_webapps()
        LOGGER.info("%s task finished: %s.", cls.task_type, task_result)
        SyncTask.finish()


class RepoDeleteHandler(SyncHandler):
    """Handler for repository item API."""

    task_type = "Delete"

    def delete(self, repo=None): # pylint: disable=arguments-differ
        """Delete repository.
           ---
           description: Delete repository
           responses:
             200:
               description: Repository deletion started
               schema:
                 $ref: "#/definitions/StatusResponse"
             429:
               description: Another task is already in progress
           tags:
             - repos
        """
        status_code, status_msg = self.start_task(repo=repo)
        self.set_status(status_code)
        self.write(status_msg)

    @staticmethod
    def run_task(*args, **kwargs):
        """Function to start deleting repos."""
        try:
            repo = kwargs.get("repo", None)
            init_logging()
            init_db()
            repository_controller = RepositoryController()
            repository_controller.delete_content_set(repo)
        except Exception as err:  # pylint: disable=broad-except
            msg = "Internal server error <%s>" % err.__hash__()
            LOGGER.exception(msg)
            DatabaseHandler.rollback()
            return "ERROR"
        return "OK"


class ExporterHandler(SyncHandler):
    """Handler for Export API."""

    task_type = "Export"

    def put(self): # pylint: disable=arguments-differ
        """Export disk dump.
           ---
           description: Export disk dump
           responses:
             200:
               description: Sync started
               schema:
                 $ref: "#/definitions/StatusResponse"
             429:
               description: Another task is already in progress
           tags:
             - export
        """
        status_code, status_msg = self.start_task()
        self.set_status(status_code)
        self.write(status_msg)
        self.flush()

    @staticmethod
    def run_task(*args, **kwargs):
        """Function to start exporting disk dump."""
        try:
            export_data(DUMP)
        except Exception as err: # pylint: disable=broad-except
            msg = "Internal server error <%s>" % err.__hash__()
            LOGGER.exception(msg)
            DatabaseHandler.rollback()
            return "ERROR"
        return "OK"


class RepoSyncHandler(SyncHandler):
    """Handler for repository sync API."""

    task_type = "Repo"

    def put(self): # pylint: disable=arguments-differ
        """Sync repositories stored in DB.
           ---
           description: Sync repositories stored in DB
           responses:
             200:
               description: Sync started
               schema:
                 $ref: "#/definitions/StatusResponse"
             429:
               description: Another task is already in progress
           tags:
             - sync
        """
        status_code, status_msg = self.start_task()
        self.set_status(status_code)
        self.write(status_msg)
        self.flush()

    @staticmethod
    def run_task(*args, **kwargs):
        """Function to start syncing all repositories available from database."""
        try:
            init_logging()
            init_db()
            repository_controller = RepositoryController()
            repository_controller.add_db_repositories()
            repository_controller.store()
        except Exception as err: # pylint: disable=broad-except
            msg = "Internal server error <%s>" % err.__hash__()
            LOGGER.exception(msg)
            DatabaseHandler.rollback()
            return "ERROR"
        return "OK"


class CveSyncHandler(SyncHandler):
    """Handler for CVE sync API."""

    task_type = "CVE"

    def put(self): # pylint: disable=arguments-differ
        """Sync CVEs.
           ---
           description: Sync CVE lists
           responses:
             200:
               description: Sync started
               schema:
                 $ref: "#/definitions/StatusResponse"
             429:
               description: Another task is already in progress
           tags:
             - sync
        """
        status_code, status_msg = self.start_task()
        self.set_status(status_code)
        self.write(status_msg)
        self.flush()

    @staticmethod
    def run_task(*args, **kwargs):
        """Function to start syncing all CVEs."""
        try:
            init_logging()
            init_db()
            controller = CveRepoController()
            controller.add_repos()
            controller.store()
        except Exception as err: # pylint: disable=broad-except
            msg = "Internal server error <%s>" % err.__hash__()
            LOGGER.exception(msg)
            DatabaseHandler.rollback()
            return "ERROR"
        return "OK"


class CvemapSyncHandler(SyncHandler):
    """Handler for CVE sync API."""

    task_type = "CVEmap"

    def put(self): # pylint: disable=arguments-differ
        """Sync CVEmap.
           ---
           description: Sync CVE map
           responses:
             200:
               description: Sync started
               schema:
                 $ref: "#/definitions/StatusResponse"
             429:
               description: Another task is already in progress
           tags:
             - sync
        """
        status_code, status_msg = self.start_task()
        self.set_status(status_code)
        self.write(status_msg)
        self.flush()

    @staticmethod
    def run_task(*args, **kwargs):
        """Function to start syncing all CVEs."""
        try:
            init_logging()
            init_db()
            controller = CvemapController()
            controller.store()
        except Exception as err: # pylint: disable=broad-except
            msg = "Internal server error <%s>" % err.__hash__()
            LOGGER.exception(msg)
            DatabaseHandler.rollback()
            return "ERROR"
        return "OK"


class AllSyncHandler(SyncHandler):
    """Handler for repo + CVE sync API."""

    task_type = "%s + %s + %s" % (RepoSyncHandler.task_type,
                                  CvemapSyncHandler.task_type,
                                  CveSyncHandler.task_type)

    def put(self): # pylint: disable=arguments-differ
        """Sync repos + CVEs + CVEmap.
           ---
           description: Sync repositories stored in DB and CVE lists
           responses:
             200:
               description: Sync started
               schema:
                 $ref: "#/definitions/StatusResponse"
             429:
               description: Another task is already in progress
           tags:
             - sync
        """
        status_code, status_msg = self.start_task()
        self.set_status(status_code)
        self.write(status_msg)
        self.flush()

    @staticmethod
    def run_task(*args, **kwargs):
        """Function to start syncing all repositories from database + all CVEs."""
        return "%s, %s, %s" % (RepoSyncHandler.run_task(),
                               CvemapSyncHandler.run_task(),
                               CveSyncHandler.run_task())

def setup_apispec(handlers):
    """Setup definitions and handlers for apispec."""
    SPEC.definition("StatusResponse", properties={"success": {"type": "boolean"},
                                                  "msg": {"type": "string", "example": "Repo sync task started."}})
    # Register public API handlers to apispec
    for handler in handlers:
        if handler[0].startswith(r"/api/v1/"):
            SPEC.add_path(urlspec=handler)


class SyncTask:
    """
    Static class providing methods for managing sync worker.
    Limit to single DB worker.
    """
    _running = False
    workers = Pool(1)

    @classmethod
    def start(cls, func, callback, *args, **kwargs):
        """Start specified function with given parameters in separate worker."""
        cls._running = True
        ioloop = IOLoop.instance()

        def _callback(result):
            ioloop.add_callback(lambda: callback(result))
        cls.workers.apply_async(func, args, kwargs, _callback)

    @classmethod
    def finish(cls):
        """Mark work as done."""
        cls._running = False

    @classmethod
    def is_running(cls):
        """Return True when some sync is running."""
        return cls._running


class ReposcanApplication(Application):
    """Class defining API handlers."""
    def __init__(self):
        handlers = [
            (r"/notifications/?", NotificationHandler),
            (r"/api/v1/monitoring/health/?", HealthHandler),
            (r"/api/v1/apispec/?", ApiSpecHandler),
            (r"/api/v1/version/?", VersionHandler),
            (r"/api/v1/repos/?", RepoListHandler),
            (r"/api/v1/repos/(?P<repo>[\\a-zA-Z0-9%*-.+?\[\]]+)", RepoDeleteHandler),
            (r"/api/v1/sync/?", AllSyncHandler),
            (r"/api/v1/sync/repo/?", RepoSyncHandler),
            (r"/api/v1/sync/cve/?", CveSyncHandler),
            (r"/api/v1/sync/cvemap/?", CvemapSyncHandler),
            (r"/api/v1/export/?", ExporterHandler),
        ]

        Application.__init__(self, handlers)

        setup_apispec(handlers)


def periodic_sync():
    """Function running both repo and CVE sync."""
    LOGGER.info("Periodic sync started.")
    AllSyncHandler.start_task()


def main():
    """Main entrypoint."""
    init_logging()
    LOGGER.info("Starting (version %s).", VMAAS_VERSION)
    sync_interval = int(os.getenv('REPOSCAN_SYNC_INTERVAL_MINUTES', 720)) * 60000
    if sync_interval > 0:
        PeriodicCallback(periodic_sync, sync_interval).start()
    else:
        LOGGER.info("Periodic syncing disabled.")
    app = ReposcanApplication()
    app.listen(8081)
    IOLoop.instance().start()

if __name__ == '__main__':
    main()
