#!/usr/bin/env python3
"""
Main entrypoint of reposcan tool. It provides and API and allows to sync specified repositories
into specified PostgreSQL database.
"""

import os
from multiprocessing.pool import Pool
import json
import requests

from prometheus_client import generate_latest
from tornado.ioloop import IOLoop, PeriodicCallback
from tornado.web import RequestHandler, Application
from tornado.websocket import websocket_connect

from apidoc import SPEC, VMAAS_VERSION, setup_apispec
from common.logging import get_logger, init_logging
from database.database_handler import DatabaseHandler, init_db
from database.product_store import ProductStore
from exporter import DUMP, main as export_data
from pkgtree import PKGTREE_FILE, main as export_pkgtree
from mnm import FAILED_AUTH, FAILED_WEBSOCK
from nistcve.cve_controller import CveRepoController
from redhatcve.cvemap_controller import CvemapController
from repodata.repository_controller import RepositoryController

LOGGER = get_logger(__name__)

DEFAULT_CHUNK_SIZE = "1048576"
WEBSOCKET_RECONNECT_INTERVAL = 60

class TaskStatusResponse(dict):
    """Object used as API response to user."""
    def __init__(self, running=False, task_type=None):
        super(TaskStatusResponse, self).__init__()
        self['running'] = running
        self['task_type'] = task_type


class TaskStartResponse(dict):
    """Object used as API response to user."""
    def __init__(self, msg, success=True):
        super(TaskStartResponse, self).__init__()
        self['msg'] = msg
        self['success'] = success


class BaseHandler(RequestHandler):
    """Base handler setting CORS headers."""
    def data_received(self, chunk):
        pass

    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "Content-Type")
        self.set_header("Access-Control-Allow-Methods", "GET, PUT, POST, DELETE")

    def options(self):
        """Answer OPTIONS request."""
        self.finish()

    def is_authorized(self):
        """Authorization check routine

            only requests from the localhost are allowed w/o authorization token,
            otherwise, GitHub authorization token is required
        """

        host_request = self.request.host.split(':')[0]

        if host_request in ('localhost', '127.0.0.1'):
            return True

        github_token = self.request.headers.get('Authorization', None)
        if not github_token:
            FAILED_AUTH.inc()
            return False

        user_info_response = requests.get('https://api.github.com/user',
                                          headers={'Authorization': github_token})

        if user_info_response.status_code != 200:
            FAILED_AUTH.inc()
            LOGGER.warning("Cannot execute github API with provided %s", github_token)
            return False
        github_user_login = user_info_response.json()['login']
        orgs_response = requests.get('https://api.github.com/users/' + github_user_login + '/orgs',
                                     headers={'Authorization': github_token})

        if orgs_response.status_code != 200:
            FAILED_AUTH.inc()
            LOGGER.warning("Cannot request github organizations for the user %s", github_user_login)
            return False

        for org_info in orgs_response.json():
            if org_info['login'] == 'RedHatInsights':
                request_str = str(self.request)
                LOGGER.warning("User %s (id %s) got an access to API: %s", github_user_login,
                               user_info_response.json()['id'], request_str)
                return True

        FAILED_AUTH.inc()
        LOGGER.warning("User %s does not belong to RedHatInsights organization", github_user_login)
        return False


class MetricsHandler(BaseHandler):
    """Handle requests to the metrics"""

    def get(self): # pylint: disable=arguments-differ
        """Get prometheus metrics"""
        self.write(generate_latest())

class HealthHandler(BaseHandler):
    """Handler class providing health status."""

    def get(self):
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
    def get(self):
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
    def get(self):
        """Get app version.
           ---
           description: Get version of application
           responses:
             200:
               description: Version of application returned
        """
        self.write(VMAAS_VERSION)
        self.flush()


class TaskStatusHandler(BaseHandler):
    """Handler class providing status of currently running background task."""

    def get(self):
        """Get status of currently running background task.
           ---
           description: Get status of currently running background task
           responses:
             200:
               description: Status of currently running background task
               schema:
                 $ref: "#/definitions/TaskStatusResponse"
           tags:
             - task
        """
        self.write(TaskStatusResponse(running=SyncTask.is_running(), task_type=SyncTask.get_task_type()))
        self.flush()


class TaskCancelHandler(BaseHandler):
    """Handler class to cancel currently running background task."""

    def put(self):
        """Cancel currently running background task.
           ---
           description: Cancel currently running background task
           responses:
             200:
               description: Task canceled
               schema:
                 $ref: "#/definitions/TaskStatusResponse"
             403:
               description: GitHub personal access token (PAT) was not provided for authorization.
           tags:
             - task
        """
        if not self.is_authorized():
            FAILED_AUTH.inc()
            self.set_status(403, 'Valid authorization token was not provided')
            return
        if SyncTask.is_running():
            SyncTask.cancel()
            LOGGER.warning("Background task terminated.")
        self.write(TaskStatusResponse(running=SyncTask.is_running(), task_type=SyncTask.get_task_type()))
        self.flush()


class SyncHandler(BaseHandler):
    """Base handler class providing common methods for different sync types."""

    task_type = "Unknown"

    @classmethod
    def start_task(cls, *args, **kwargs):
        """Start given task if DB worker isn't currently executing different task."""
        if not SyncTask.is_running():
            msg = "%s task started." % cls.task_type
            LOGGER.info(msg)
            SyncTask.start(cls.task_type, cls.run_task_and_export, cls.finish_task, *args, **kwargs)
            status_code = 200
            status_msg = TaskStartResponse(msg)
        else:
            msg = "%s task request ignored. Another task already in progress." % cls.task_type
            LOGGER.info(msg)
            # Too Many Requests
            status_code = 429
            status_msg = TaskStartResponse(msg, success=False)
        return status_code, status_msg


    @classmethod
    def run_task_and_export(cls, *args, **kwargs):
        """Run sync task of current class and export."""
        result = cls.run_task(*args, **kwargs)
        if cls not in (ExporterHandler, PkgTreeHandler, RepoListHandler):
            ExporterHandler.run_task()
            PkgTreeHandler.run_task()
        return result

    @staticmethod
    def run_task(*args, **kwargs):
        """Run synchronization task."""
        raise NotImplementedError("abstract method")

    @classmethod
    def finish_task(cls, task_result):
        """Mark current task as finished."""
        if cls not in (PkgTreeHandler, RepoListHandler):
            # Notify webapps to update it's cache
            if ReposcanApplication.websocket:
                ReposcanApplication.websocket.write_message("invalidate-cache")
            else:
                ReposcanApplication.websocket_response_queue.add("invalidate-cache")
        LOGGER.info("%s task finished: %s.", cls.task_type, task_result)
        SyncTask.finish()


class RepoListHandler(SyncHandler):
    """Handler for repository list/add API."""

    task_type = "Import repositories"

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

    def post(self):
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
               description: Repos and products import started
               schema:
                 $ref: "#/definitions/TaskStartResponse"
             429:
               description: Another task is already in progress
             400:
               description: Invalid input JSON format
             403:
               description: GitHub personal access token (PAT) was not provided for authorization.
           tags:
             - repos
        """
        if not self.is_authorized():
            self.set_status(403, 'Valid authorization token was not provided')
            return
        try:
            products, repos = self._parse_input_list()
        except Exception as err: # pylint: disable=broad-except
            products = None
            repos = None
            msg = "Internal server error <%s>" % err.__hash__()
            LOGGER.exception(msg)
            self.set_status(400)
            self.write(TaskStartResponse(msg, success=False))
            self.flush()
        if repos:
            status_code, status_msg = self.start_task(products=products, repos=repos)
            self.set_status(status_code)
            self.write(status_msg)
            self.flush()

    @staticmethod
    def run_task(*args, **kwargs):
        """Function to import all repositories from input list to the DB."""
        try:
            products = kwargs.get("products", None)
            repos = kwargs.get("repos", None)
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
            return "ERROR"
        return "OK"


class RepoDeleteHandler(SyncHandler):
    """Handler for repository item API."""

    task_type = "Delete repositories"

    def options(self, repo=None): # pylint: disable=arguments-differ,unused-argument
        self.finish()

    def delete(self, repo=None):
        """Delete repository.
           ---
           description: Delete repository
           parameters:
             - name: repo
               description: Repository name or POSIX regular expression pattern
               required: True
               type: string
               in: path
               x-example: rhel-6-server-rpms OR rhel-[4567]-.*-rpms OR rhel-\\d-server-rpms
           responses:
             200:
               description: Repository deletion started
               schema:
                 $ref: "#/definitions/TaskStartResponse"
             429:
               description: Another task is already in progress
             403:
               description: GitHub personal access token (PAT) was not provided for authorization.
           tags:
             - repos
        """
        if not self.is_authorized():
            FAILED_AUTH.inc()
            self.set_status(403, 'Valid authorization token was not provided')
            return
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

    task_type = "Export dump"

    def put(self):
        """Export disk dump.
           ---
           description: Export disk dump
           responses:
             200:
               description: Sync started
               schema:
                 $ref: "#/definitions/TaskStartResponse"
             429:
               description: Another task is already in progress
             403:
               description: GitHub personal access token (PAT) was not provided for authorization.
           tags:
             - export
        """
        if not self.is_authorized():
            FAILED_AUTH.inc()
            self.set_status(403, 'Valid authorization token was not provided')
            return
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


class PkgTreeHandler(SyncHandler):
    """Handler for Package Tree API."""

    task_type = "Export package tree"

    def put(self):
        """Export package tree.
           ---
           description: Export package tree
           responses:
             200:
               description: Sync started
               schema:
                 $ref: "#/definitions/TaskStartResponse"
             429:
               description: Another task is already in progress
             403:
               description: GitHub personal access token (PAT) was not provided for authorization.
           tags:
             - sync
        """
        if not self.is_authorized():
            FAILED_AUTH.inc()
            self.set_status(403, 'Valid authorization token was not provided')
            return
        status_code, status_msg = self.start_task()
        self.set_status(status_code)
        self.write(status_msg)
        self.flush()

    @staticmethod
    def run_task(*args, **kwargs):
        """Function to start exporting disk dump."""
        try:
            export_pkgtree(PKGTREE_FILE)
        except Exception as err: # pylint: disable=broad-except
            msg = "Internal server error <%s>" % err.__hash__()
            LOGGER.exception(msg)
            DatabaseHandler.rollback()
            return "ERROR"
        return "OK"


class PkgTreeDownloadHandler(BaseHandler):
    """Handler class to download package tree to the caller."""
    def __init__(self, application, request, **kwargs):
        super(PkgTreeDownloadHandler, self).__init__(application, request, **kwargs)
        self.chunk_size = int(os.getenv('CHUNK_SIZE', DEFAULT_CHUNK_SIZE))

    def get(self):
        """Download the package tree.
           ---
           description: Download the package tree.
           responses:
             200:
               description: The package tree
               schema:
                 $ref: "#/definitions/PkgTreeDownloadResponse"
             403:
               description: GitHub personal access token (PAT) was not provided for authorization.
             404:
               description: Package Tree file not found.  Has it been generated yet?  Try /sync/pkgtree first.
           tags:
             - pkgtree
        """
        if not self.is_authorized():
            FAILED_AUTH.inc()
            self.set_status(403, 'Valid authorization token was not provided')
            return

        try:
            with open(PKGTREE_FILE, 'rb') as pkgtree_file_reader:
                self.set_header("Content-Type", "application/json")
                self.set_header("Content-Encoding", "gzip")
                while True:
                    chunk = pkgtree_file_reader.read(self.chunk_size)
                    if not chunk:
                        break
                    self.write(chunk)
                self.flush()
        except FileNotFoundError:
            self.set_status(404, 'Package Tree file not found.  Has it been generated?')
            return

class RepoSyncHandler(SyncHandler):
    """Handler for repository sync API."""

    task_type = "Sync repositories"

    def put(self):
        """Sync repositories stored in DB.
           ---
           description: Sync repositories stored in DB
           responses:
             200:
               description: Sync started
               schema:
                 $ref: "#/definitions/TaskStartResponse"
             429:
               description: Another task is already in progress
             403:
               description: GitHub personal access token (PAT) was not provided for authorization.
           tags:
             - sync
        """
        if not self.is_authorized():
            FAILED_AUTH.inc()
            self.set_status(403, 'Valid authorization token was not provided')
            return
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

    task_type = "Sync CVEs"

    def put(self):
        """Sync CVEs.
           ---
           description: Sync CVE lists
           responses:
             200:
               description: Sync started
               schema:
                 $ref: "#/definitions/TaskStartResponse"
             429:
               description: Another task is already in progress
             403:
               description: GitHub personal access token (PAT) was not provided for authorization.
           tags:
             - sync
        """
        if not self.is_authorized():
            self.set_status(403, 'Valid authorization token was not provided')
            return
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

    task_type = "Sync CVE map"

    def put(self):
        """Sync CVEmap.
           ---
           description: Sync CVE map
           responses:
             200:
               description: Sync started
               schema:
                 $ref: "#/definitions/TaskStartResponse"
             429:
               description: Another task is already in progress
             403:
               description: GitHub personal access token (PAT) was not provided for authorization.
           tags:
             - sync
        """
        if not self.is_authorized():
            FAILED_AUTH.inc()
            self.set_status(403, 'Valid authorization token was not provided')
            return
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

    def put(self):
        """Sync repos + CVEs + CVEmap.
           ---
           description: Sync repositories stored in DB and CVE lists
           responses:
             200:
               description: Sync started
               schema:
                 $ref: "#/definitions/TaskStartResponse"
             429:
               description: Another task is already in progress
             403:
               description: GitHub personal access token (PAT) was not provided for authorization.
           tags:
             - sync
        """
        if not self.is_authorized():
            FAILED_AUTH.inc()
            self.set_status(403, 'Valid authorization token was not provided')
            return
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


class SyncTask:
    """
    Static class providing methods for managing sync worker.
    Limit to single DB worker.
    """
    _running = False
    _running_task_type = None
    workers = Pool(1)

    @classmethod
    def start(cls, task_type, func, callback, *args, **kwargs):
        """Start specified function with given parameters in separate worker."""
        cls._running = True
        cls._running_task_type = task_type
        ioloop = IOLoop.instance()

        def _callback(result):
            ioloop.add_callback(lambda: callback(result))
        cls.workers.apply_async(func, args, kwargs, _callback)

    @classmethod
    def finish(cls):
        """Mark work as done."""
        cls._running = False
        cls._running_task_type = None

    @classmethod
    def is_running(cls):
        """Return True when some sync is running."""
        return cls._running

    @classmethod
    def get_task_type(cls):
        """Get currently running task type."""
        return cls._running_task_type

    @classmethod
    def cancel(cls):
        """Terminate the process pool."""
        cls.workers.terminate()
        cls.workers.join()
        cls.workers = Pool(1)
        cls.finish()


class ReposcanApplication(Application):
    """Class defining API handlers."""

    websocket = None
    websocket_url = "ws://%s:8082/" % os.getenv("WEBSOCKET_HOST", "vmaas_websocket")
    websocket_response_queue = set()
    reconnect_callback = None

    def __init__(self):
        handlers = [
            (r"/api/v1/monitoring/health/?", HealthHandler),
            (r"/api/v1/apispec/?", ApiSpecHandler),
            (r"/api/v1/version/?", VersionHandler),
            (r"/api/v1/repos/?", RepoListHandler),
            (r"/api/v1/repos/(?P<repo>[\\a-zA-Z0-9%*-.+?\[\]]+)", RepoDeleteHandler),
            (r"/api/v1/sync/?", AllSyncHandler),
            (r"/api/v1/sync/repo/?", RepoSyncHandler),
            (r"/api/v1/sync/cve/?", CveSyncHandler),
            (r"/api/v1/sync/cvemap/?", CvemapSyncHandler),
            (r"/api/v1/sync/pkgtree/?", PkgTreeHandler),
            (r"/api/v1/export/?", ExporterHandler),
            (r"/api/v1/pkgtree/?", PkgTreeDownloadHandler),
            (r"/api/v1/task/status/?", TaskStatusHandler),
            (r"/api/v1/task/cancel/?", TaskCancelHandler),
            (r"/metrics", MetricsHandler)
        ]

        Application.__init__(self, handlers)

        setup_apispec(handlers)

    @classmethod
    def websocket_reconnect(cls):
        """Try to connect to given WS URL, set message handler and callback to evaluate this connection attempt."""
        if cls.websocket is None:
            websocket_connect(cls.websocket_url, on_message_callback=cls._read_websocket_message,
                              callback=cls._websocket_connect_status)

    @classmethod
    def _websocket_connect_status(cls, future):
        """Check if connection attempt succeeded."""
        try:
            result = future.result()
        except: # pylint: disable=bare-except
            result = None

        if result is None:
            # TODO: print the traceback as debug message when we use logging module instead of prints here
            FAILED_WEBSOCK.inc()
            LOGGER.warning("Unable to connect to: %s", cls.websocket_url)
        else:
            LOGGER.info("Connected to: %s", cls.websocket_url)
            result.write_message("subscribe-reposcan")
            for item in cls.websocket_response_queue:
                result.write_message(item)
            cls.websocket_response_queue.clear()

        cls.websocket = result

    @classmethod
    def _read_websocket_message(cls, message):
        """Read incoming websocket messages."""
        if message is None:
            FAILED_WEBSOCK.inc()
            LOGGER.warning("Connection to %s closed: %s (%s)", cls.websocket_url,
                           cls.websocket.close_reason, cls.websocket.close_code)
            cls.websocket = None


def periodic_sync():
    """Function running both repo and CVE sync."""
    LOGGER.info("Periodic sync started.")
    AllSyncHandler.start_task()


def create_app():
    """Create reposcan app."""
    init_logging()
    LOGGER.info("Starting (version %s).", VMAAS_VERSION)
    sync_interval = int(os.getenv('REPOSCAN_SYNC_INTERVAL_MINUTES', "720")) * 60000
    if sync_interval > 0:
        PeriodicCallback(periodic_sync, sync_interval).start()
    else:
        LOGGER.info("Periodic syncing disabled.")
    app = ReposcanApplication()
    app.listen(8081)

    app.websocket_reconnect()
    app.reconnect_callback = PeriodicCallback(app.websocket_reconnect, WEBSOCKET_RECONNECT_INTERVAL * 1000)
    app.reconnect_callback.start()


def main():
    """Main entrypoint."""
    create_app()
    IOLoop.instance().start()


if __name__ == '__main__':
    main()
