#!/usr/bin/python3
"""
Main entrypoint of reposcan tool. It provides and API and allows to sync specified repositories
into specified PostgreSQL database.
"""

import os
from multiprocessing.pool import Pool
import traceback

from tornado.ioloop import IOLoop
from tornado.web import RequestHandler, Application
import ujson

from cli.logger import SimpleLogger
from database.database_handler import DatabaseHandler
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


def repo_sync_task(repos=None):
    """Function to start syncing all repositories from input list or from database."""
    try:
        init_db()
        repository_controller = RepositoryController()
        if repos:
            # Sync repos from input
            for repo in repos:
                repo_name, repo_url, cert_name, ca_cert, cert, key = repo
                repository_controller.add_repository(repo_name, repo_url, cert_name=cert_name,
                                                     ca_cert=ca_cert, cert=cert, key=key)
        else:
            # Re-sync repos in DB
            repository_controller.add_synced_repositories()
        repository_controller.store()
    except: # pylint: disable=bare-except
        LOGGER.log(traceback.format_exc())
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
        return "ERROR"
    return "OK"


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
        return ujson.dumps({"success": self.success, "msg": self.msg})


class SyncHandler(RequestHandler):
    """Base handler class providing common methods for different sync types."""
    def data_received(self, chunk):
        """Handles streamed data."""
        pass

    def start_task(self, task_type, task_func, task_callback, args, kwargs): # pylint: disable=too-many-arguments
        """Start given task if DB worker isn't currently executing different task."""
        if not SyncTask.is_running():
            msg = "%s sync task started." % task_type
            LOGGER.log(msg)
            SyncTask.start(task_func, task_callback, args, kwargs)
            self.write(str(ResponseMsg(msg)))
        else:
            msg = "%s sync request ignored. Another sync task already in progress." % task_type
            LOGGER.log(msg)
            # Too Many Requests
            self.set_status(429)
            self.write(str(ResponseMsg(msg, success=False)))

    @staticmethod
    def finish_task(task_type, task_result):
        """Mark current task as finished."""
        LOGGER.log("%s sync task finished: %s." % (task_type, task_result))
        SyncTask.finish()


class RepoSyncHandler(SyncHandler):
    """Handler for repository sync API."""

    task_type = "Repo"

    def _parse_repo_list(self):
        repos = []
        json_data = ""
        # check if JSON is passed as a file or as a body of POST request
        if self.request.files:
            json_data = self.request.files['file'][0]['body']  # pick up only first file (index 0)
        elif self.request.body:
            json_data = self.request.body

        data = ujson.loads(json_data)
        for repo_group in data:
            # Entitlement cert is optional
            if "entitlement_cert" in repo_group:
                cert_name = repo_group["entitlement_cert"]["name"]
                ca_cert = repo_group["entitlement_cert"]["ca_cert"]
                cert = repo_group["entitlement_cert"]["cert"]
                key = repo_group["entitlement_cert"]["key"]
            else:
                cert_name, ca_cert, cert, key = None, None, None, None

            for repo_name, repo_url in repo_group["repos"].items():
                repos.append((repo_name, repo_url, cert_name, ca_cert, cert, key))

        return repos

    def get(self, *args, **kwargs):
        """Sync repositories stored in DB."""
        self.start_task(self.task_type, repo_sync_task, self.on_complete, (), {})

    def post(self, *args, **kwargs):
        """Sync repositories listed in request."""
        try:
            repos = self._parse_repo_list()
        except: # pylint: disable=bare-except
            repos = None
            LOGGER.log(traceback.format_exc())
            self.set_status(400)
            self.write(str(ResponseMsg("Incorrect JSON format.", success=False)))
        if repos:
            self.start_task(self.task_type, repo_sync_task, self.on_complete, (), {"repos": repos})

    def on_complete(self, res):
        """Callback after worker finishes."""
        self.finish_task(self.task_type, res)


class CveSyncHandler(SyncHandler):
    """Handler for CVE sync API."""

    task_type = "CVE"

    def get(self, *args, **kwargs):
        """Sync CVEs."""
        self.start_task(self.task_type, cve_sync_task, self.on_complete, (), {})

    def on_complete(self, res):
        """Callback after worker finishes."""
        self.finish_task(self.task_type, res)


class ReposcanApplication(Application):
    """Class defining API handlers."""
    def __init__(self):
        handlers = [
            (r"/api/v1/sync/repo/?", RepoSyncHandler),
            (r"/api/v1/sync/cve/?", CveSyncHandler),
        ]
        Application.__init__(self, handlers)


def main():
    """Main entrypoint."""
    app = ReposcanApplication()
    app.listen(8081)
    IOLoop.instance().start()

if __name__ == '__main__':
    main()
