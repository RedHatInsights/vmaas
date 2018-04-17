#!/usr/bin/python3
"""
Main entrypoint of reposcan tool. It provides and API and allows to sync specified repositories
into specified PostgreSQL database.
"""

import os
from multiprocessing.pool import Pool
import traceback
import json

from apispec import APISpec
import requests
from tornado.ioloop import IOLoop, PeriodicCallback
from tornado.web import RequestHandler, Application

from common.logging import get_logger, init_logging
from database.database_handler import DatabaseHandler
from database.product_store import ProductStore
from download.downloader import VALID_HTTP_CODES
from nistcve.cve_controller import CveRepoController
from repodata.repository_controller import RepositoryController

LOGGER = get_logger(__name__)

SPEC = APISpec(
    title='VMaaS Reposcan',
    version='1',
    plugins=(
        'apispec.ext.tornado',
    ),
    basePath="/api/v1",
    schemes=["http"],
)


def init_db():
    """Setup DB connection parameters"""
    DatabaseHandler.db_name = os.getenv('POSTGRESQL_DATABASE', "vmaas")
    DatabaseHandler.db_user = os.getenv('POSTGRESQL_USER', "vmaas_user")
    DatabaseHandler.db_pass = os.getenv('POSTGRESQL_PASSWORD', "vmaas_passwd")
    DatabaseHandler.db_host = os.getenv('POSTGRESQL_HOST', "database")
    DatabaseHandler.db_port = os.getenv('POSTGRESQL_PORT', 5432)


def repo_sync_task(products=None, repos=None):
    """Function to start syncing all repositories from input list or from database."""
    try:
        init_logging()
        init_db()
        repository_controller = RepositoryController()
        if products:
            product_store = ProductStore()
            product_store.store(products)
            # Reference imported content set to associate with repositories
            repository_controller.repo_store.set_content_set_db_mapping(product_store.cs_to_dbid)

        if repos:
            # Sync repos from input
            for repo in repos:
                repo_url, content_set, basearch, releasever, cert_name, ca_cert, cert, key = repo
                repository_controller.add_repository(repo_url, content_set, basearch, releasever, cert_name=cert_name,
                                                     ca_cert=ca_cert, cert=cert, key=key)
        else:
            # Re-sync repos in DB
            repository_controller.add_synced_repositories()
        repository_controller.store()
    except: # pylint: disable=bare-except
        LOGGER.error(traceback.format_exc())
        DatabaseHandler.rollback()
        return "ERROR"
    return "OK"


def cve_sync_task():
    """Function to start syncing all CVEs."""
    try:
        init_logging()
        init_db()
        controller = CveRepoController()
        controller.add_repos()
        controller.store()
    except: # pylint: disable=bare-except
        LOGGER.error(traceback.format_exc())
        DatabaseHandler.rollback()
        return "ERROR"
    return "OK"


def all_sync_task():
    """Function to start syncing all repositories from database + all CVEs."""
    return "%s, %s" % (repo_sync_task(), cve_sync_task())


class SyncTask:
    """
    Static class providing methods for managing sync worker.
    Limit to single DB worker.
    """
    _running = False
    workers = Pool(1)

    @classmethod
    def start(cls, func, callback, args, kwargs):
        """Start specified function with given parameters in separate worker."""
        cls._running = True

        def _callback(result):
            IOLoop.instance().add_callback(lambda: callback(result))
        cls.workers.apply_async(func, args, kwargs, _callback)

    @classmethod
    def finish(cls):
        """Mark work as done."""
        cls._running = False

    @classmethod
    def is_running(cls):
        """Return True when some sync is running."""
        return cls._running


class ResponseJson(dict): # pylint: disable=too-few-public-methods
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


class SyncHandler(BaseHandler):
    """Base handler class providing common methods for different sync types."""

    task_type = None

    @classmethod
    def start_task(cls, task_func, args, kwargs):
        """Start given task if DB worker isn't currently executing different task."""
        if not SyncTask.is_running():
            msg = "%s sync task started." % cls.task_type
            LOGGER.info(msg)
            SyncTask.start(task_func, cls.finish_task, args, kwargs)
            status_code = 200
            status_msg = ResponseJson(msg)
        else:
            msg = "%s sync request ignored. Another sync task already in progress." % cls.task_type
            LOGGER.info(msg)
            # Too Many Requests
            status_code = 429
            status_msg = ResponseJson(msg, success=False)
        return status_code, status_msg

    @staticmethod
    def _notify_webapp():
        webapp_url = os.getenv('WEBAPP_API_URL', "http://webapp")
        webapp_port = os.getenv('WEBAPP_API_PORT_INTERNAL', 8079)
        refresh_url = "%s:%s/api/internal/refresh" % (webapp_url, webapp_port)
        try:
            response = requests.get(refresh_url)
            if response.status_code not in VALID_HTTP_CODES or not json.loads(response.text)["success"]:
                LOGGER.error("Response from %s: %s", refresh_url, response.text)
        except requests.RequestException:
            LOGGER.error(traceback.format_exc())
            LOGGER.error("Unable to connect to %s.", refresh_url)

    @classmethod
    def finish_task(cls, task_result):
        """Mark current task as finished."""
        LOGGER.info("%s sync task finished: %s.", cls.task_type, task_result)
        SyncTask.finish()
        # Notify webapp to update it's cache
        SyncHandler._notify_webapp()


class RepoSyncHandler(SyncHandler):
    """Handler for repository sync API."""

    task_type = "Repo"

    @staticmethod
    def _content_set_to_repos(content_set):
        baseurl = content_set["baseurl"]
        basearches = content_set["basearch"]
        releasevers = content_set["releasever"]

        # (repo_url, basearch, releasever)
        repos = [(baseurl, None, None)]
        # Replace basearch
        repos = [(repo[0].replace("$basearch", basearch), basearch, repo[2])
                 for basearch in basearches for repo in repos]
        # Replace releasever
        repos = [(repo[0].replace("$releasever", releasever), repo[1], releasever)
                 for releasever in releasevers for repo in repos]

        return repos

    def _parse_input_list(self):
        # pylint: disable=too-many-locals
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

    def get(self): # pylint: disable=arguments-differ
        """Sync repositories stored in DB.
           ---
           description: Sync repositories stored in DB
           responses:
             200:
               description: Sync started
               schema:
                 $ref: "#/definitions/StatusResponse"
             429:
               description: Another sync is already in progress
           tags:
             - sync
        """
        status_code, status_msg = self.start_task(repo_sync_task, (), {})
        self.set_status(status_code)
        self.write(status_msg)
        self.flush()

    def post(self): # pylint: disable=arguments-differ
        """Sync repositories listed in request.
           ---
           description: Sync repositories listed in request
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
               description: Sync started
               schema:
                 $ref: "#/definitions/StatusResponse"
             400:
               description: Invalid input JSON format
             429:
               description: Another sync is already in progress
           tags:
             - sync
        """
        try:
            products, repos = self._parse_input_list()
        except: # pylint: disable=bare-except
            products = None
            repos = None
            LOGGER.warning(traceback.format_exc())
            self.set_status(400)

            self.write(ResponseJson("Incorrect JSON format.", success=False))
            self.flush()
        if repos:
            status_code, status_msg = self.start_task(repo_sync_task, (),
                                                      {"products": products, "repos": repos})
            self.set_status(status_code)
            self.write(status_msg)
            self.flush()


class CveSyncHandler(SyncHandler):
    """Handler for CVE sync API."""

    task_type = "CVE"

    def get(self): # pylint: disable=arguments-differ
        """Sync CVEs.
           ---
           description: Sync CVE lists
           responses:
             200:
               description: Sync started
               schema:
                 $ref: "#/definitions/StatusResponse"
             429:
               description: Another sync is already in progress
           tags:
             - sync
        """
        status_code, status_msg = self.start_task(cve_sync_task, (), {})
        self.set_status(status_code)
        self.write(status_msg)
        self.flush()


class AllSyncHandler(SyncHandler):
    """Handler for repo + CVE sync API."""

    task_type = "%s + %s" % (RepoSyncHandler.task_type, CveSyncHandler.task_type)

    def get(self): # pylint: disable=arguments-differ
        """Sync repos + CVEs.
           ---
           description: Sync repositories stored in DB and CVE lists
           responses:
             200:
               description: Sync started
               schema:
                 $ref: "#/definitions/StatusResponse"
             429:
               description: Another sync is already in progress
           tags:
             - sync
        """
        status_code, status_msg = self.start_task(all_sync_task, (), {})
        self.set_status(status_code)
        self.write(status_msg)
        self.flush()


def setup_apispec(handlers):
    """Setup definitions and handlers for apispec."""
    SPEC.definition("StatusResponse", properties={"success": {"type": "boolean"},
                                                  "msg": {"type": "string", "example": "Repo sync task started."}})
    # Register public API handlers to apispec
    for handler in handlers:
        if handler[0].startswith(r"/api/v1/"):
            SPEC.add_path(urlspec=handler)


class ReposcanApplication(Application):
    """Class defining API handlers."""
    def __init__(self):
        handlers = [
            (r"/api/v1/apispec/?", ApiSpecHandler),
            (r"/api/v1/sync/?", AllSyncHandler),
            (r"/api/v1/sync/repo/?", RepoSyncHandler),
            (r"/api/v1/sync/cve/?", CveSyncHandler),
        ]
        setup_apispec(handlers)
        Application.__init__(self, handlers)


def periodic_sync():
    """Function running both repo and CVE sync."""
    LOGGER.info("Periodic sync started.")
    AllSyncHandler.start_task(all_sync_task, (), {})


def main():
    """Main entrypoint."""
    init_logging()
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
