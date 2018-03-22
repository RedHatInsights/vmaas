#!/usr/bin/python3
"""
Main entrypoint of reposcan tool. It provides and API and allows to sync specified repositories
into specified PostgreSQL database.
"""

import os
from multiprocessing.pool import Pool
import traceback
import json

import requests
from tornado.ioloop import IOLoop, PeriodicCallback
from tornado.web import RequestHandler, Application

from cli.logger import SimpleLogger
from database.database_handler import DatabaseHandler
from database.product_store import ProductStore
from download.downloader import VALID_HTTP_CODES
from nistcve.cve_controller import CveRepoController
from repodata.repository_controller import RepositoryController

LOGGER = SimpleLogger()


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
                repo_label, repo_url, content_set, cert_name, ca_cert, cert, key = repo
                repository_controller.add_repository(repo_label, repo_url, content_set=content_set,
                                                     cert_name=cert_name, ca_cert=ca_cert, cert=cert, key=key)
        else:
            # Re-sync repos in DB
            repository_controller.add_synced_repositories()
        repository_controller.store()
    except: # pylint: disable=bare-except
        LOGGER.log(traceback.format_exc())
        DatabaseHandler.rollback()
        return "ERROR"
    return "OK"


def cve_sync_task():
    """Function to start syncing all CVEs."""
    try:
        init_db()
        controller = CveRepoController()
        controller.add_repos()
        controller.store()
    except: # pylint: disable=bare-except
        LOGGER.log(traceback.format_exc())
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


class ResponseMsg: # pylint: disable=too-few-public-methods
    """Object used as API response to user, represented as JSON string."""
    def __init__(self, msg, success=True):
        self.msg = msg
        self.success = success

    def __repr__(self):
        return json.dumps({"success": self.success, "msg": self.msg})


class SyncHandler(RequestHandler):
    """Base handler class providing common methods for different sync types."""
    def data_received(self, chunk):
        """Handles streamed data."""
        pass

    @staticmethod
    def start_task(task_type, task_func, task_callback, args, kwargs): # pylint: disable=too-many-arguments
        """Start given task if DB worker isn't currently executing different task."""
        if not SyncTask.is_running():
            msg = "%s sync task started." % task_type
            LOGGER.log(msg)
            SyncTask.start(task_func, task_callback, args, kwargs)
            status_code = 200
            status_msg = str(ResponseMsg(msg))
        else:
            msg = "%s sync request ignored. Another sync task already in progress." % task_type
            LOGGER.log(msg)
            # Too Many Requests
            status_code = 429
            status_msg = str(ResponseMsg(msg, success=False))
        return status_code, status_msg

    @staticmethod
    def _notify_webapp():
        webapp_url = os.getenv('WEBAPP_API_URL', "http://webapp")
        webapp_port = os.getenv('WEBAPP_API_PORT_INTERNAL', 8079)
        refresh_url = "%s:%s/api/internal/refresh" % (webapp_url, webapp_port)
        try:
            response = requests.get(refresh_url)
            if response.status_code not in VALID_HTTP_CODES or not json.loads(response.text)["success"]:
                LOGGER.errlog("Response from %s: %s" % (refresh_url, response.text))
        except requests.RequestException:
            LOGGER.errlog(traceback.format_exc())
            LOGGER.errlog("Unable to connect to %s." % refresh_url)

    @staticmethod
    def finish_task(task_type, task_result):
        """Mark current task as finished."""
        LOGGER.log("%s sync task finished: %s." % (task_type, task_result))
        SyncTask.finish()
        # Notify webapp to update it's cache
        SyncHandler._notify_webapp()


class RepoSyncHandler(SyncHandler):
    """Handler for repository sync API."""

    task_type = "Repo"

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
            for product_id, product in repo_group["products"].items():
                product_id = int(product_id)
                products[product_id] = {"name": product["name"], "content_sets": {}}
                for content_set_label, content_set in product["content_sets"].items():
                    products[product_id]["content_sets"][content_set_label] = content_set["name"]
                    for repo_label, repo_url in content_set["repos"].items():
                        repos.append((repo_label, repo_url, content_set_label, cert_name, ca_cert, cert, key))

        return products, repos

    def get(self, *args, **kwargs):
        """Sync repositories stored in DB."""
        status_code, status_msg = SyncHandler.start_task(self.task_type, repo_sync_task, self.on_complete, (), {})
        self.set_status(status_code)
        self.write(status_msg)
        self.flush()

    def post(self, *args, **kwargs):
        """Sync repositories listed in request."""
        try:
            products, repos = self._parse_input_list()
        except: # pylint: disable=bare-except
            products = None
            repos = None
            LOGGER.log(traceback.format_exc())
            self.set_status(400)
            self.write(str(ResponseMsg("Incorrect JSON format.", success=False)))
            self.flush()
        if repos:
            status_code, status_msg = SyncHandler.start_task(self.task_type, repo_sync_task, self.on_complete, (),
                                                             {"products": products, "repos": repos})
            self.set_status(status_code)
            self.write(status_msg)
            self.flush()

    @staticmethod
    def on_complete(res):
        """Callback after worker finishes."""
        SyncHandler.finish_task(RepoSyncHandler.task_type, res)


class CveSyncHandler(SyncHandler):
    """Handler for CVE sync API."""

    task_type = "CVE"

    def get(self, *args, **kwargs):
        """Sync CVEs."""
        status_code, status_msg = SyncHandler.start_task(self.task_type, cve_sync_task, self.on_complete, (), {})
        self.set_status(status_code)
        self.write(status_msg)
        self.flush()

    @staticmethod
    def on_complete(res):
        """Callback after worker finishes."""
        SyncHandler.finish_task(CveSyncHandler.task_type, res)


class AllSyncHandler(SyncHandler):
    """Handler for repo + CVE sync API."""

    task_type = "%s + %s" % (RepoSyncHandler.task_type, CveSyncHandler.task_type)

    def get(self, *args, **kwargs):
        """Sync repos + CVEs."""
        status_code, status_msg = SyncHandler.start_task(self.task_type, all_sync_task, self.on_complete, (), {})
        self.set_status(status_code)
        self.write(status_msg)
        self.flush()

    @staticmethod
    def on_complete(res):
        """Callback after worker finishes."""
        SyncHandler.finish_task(AllSyncHandler.task_type, res)


class ReposcanApplication(Application):
    """Class defining API handlers."""
    def __init__(self):
        handlers = [
            (r"/api/v1/sync/?", AllSyncHandler),
            (r"/api/v1/sync/repo/?", RepoSyncHandler),
            (r"/api/v1/sync/cve/?", CveSyncHandler),
        ]
        Application.__init__(self, handlers)


def periodic_sync():
    """Function running both repo and CVE sync."""
    LOGGER.log("Periodic sync started.")
    SyncHandler.start_task(AllSyncHandler.task_type, all_sync_task, AllSyncHandler.on_complete, (), {})


def main():
    """Main entrypoint."""
    sync_interval = int(os.getenv('REPOSCAN_SYNC_INTERVAL_MINUTES', 720)) * 60000
    if sync_interval > 0:
        PeriodicCallback(periodic_sync, sync_interval).start()
    else:
        LOGGER.log("Periodic syncing disabled.")
    app = ReposcanApplication()
    app.listen(8081)
    IOLoop.instance().start()

if __name__ == '__main__':
    main()
