#!/usr/bin/env python3
"""
Main entrypoint of reposcan tool. It provides and API and allows to sync specified repositories
into specified PostgreSQL database.
"""

import os
import signal
from multiprocessing.pool import Pool
import json
from contextlib import contextmanager
import shutil
import yaml
import git

from prometheus_client import generate_latest
from tornado.ioloop import IOLoop, PeriodicCallback
from tornado.websocket import websocket_connect
import requests
import connexion
from flask import request, send_file, make_response

from common.logging_utils import get_logger, init_logging
from common.constants import VMAAS_VERSION
from database.database_handler import DatabaseHandler, init_db
from database.product_store import ProductStore
from dbchange import DbChangeAPI
from exporter import DUMP, main as export_data
from pkgtree import PKGTREE_FILE, main as export_pkgtree
from mnm import FAILED_AUTH, FAILED_WEBSOCK
from redhatcve.cvemap_controller import CvemapController
from repodata.repository_controller import RepositoryController

LOGGER = get_logger(__name__)
KILL_SIGNALS = (signal.SIGHUP, signal.SIGTERM, signal.SIGINT)

DEFAULT_CHUNK_SIZE = "1048576"
DEFAULT_AUTHORIZED_API_ORG = "RedHatInsights"

REPOLIST_DIR = '/tmp/repolist_git'
REPOLIST_GIT = os.getenv('REPOLIST_GIT', 'https://github.com/RedHatInsights/vmaas-assets.git')
REPOLIST_GIT_TOKEN = os.getenv('REPOLIST_GIT_TOKEN', '')
REPOLIST_PATH = os.getenv('REPOLIST_PATH', 'repolist.json')

WEBSOCKET_RECONNECT_INTERVAL = 60

DEFAULT_CERT_NAME = "DEFAULT"
DEFAULT_CA_CERT = os.getenv("DEFAULT_CA_CERT", "")
DEFAULT_CERT = os.getenv("DEFAULT_CERT", "")
DEFAULT_KEY = os.getenv("DEFAULT_KEY", "")


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


# pylint: disable=unused-argument
def github_auth(github_token, required_scopes=None):
    """Performs authorization using github"""

    host_request = request.host.split(':')[0]

    if host_request in ('localhost', '127.0.0.1'):
        return {'scopes': ['local']}

    if not github_token:
        FAILED_AUTH.inc()
        return None

    user_info_response = requests.get('https://api.github.com/user',
                                      headers={'Authorization': github_token})

    if user_info_response.status_code != 200:
        FAILED_AUTH.inc()
        LOGGER.warning("Cannot execute github API with provided %s", github_token)
        return None
    github_user_login = user_info_response.json()['login']
    orgs_response = requests.get('https://api.github.com/users/' + github_user_login + '/orgs',
                                 headers={'Authorization': github_token})

    if orgs_response.status_code != 200:
        FAILED_AUTH.inc()
        LOGGER.warning("Cannot request github organizations for the user %s", github_user_login)
        return None

    authorized_org = os.getenv('AUTHORIZED_API_ORG', DEFAULT_AUTHORIZED_API_ORG)

    for org_info in orgs_response.json():
        if org_info['login'] == authorized_org:
            request_str = str(request)
            LOGGER.warning("User %s (id %s) got an access to API: %s", github_user_login,
                           user_info_response.json()['id'], request_str)
            return {'scopes': ['local', 'authorized']}

    FAILED_AUTH.inc()
    LOGGER.warning("User %s does not belong to %s organization", authorized_org, github_user_login)
    return None


# pylint: disable=unused-argument

class HealthHandler():
    """Handler class providing health status."""

    @classmethod
    def get(cls, **kwargs):
        """Get API status."""
        return True, 200


class VersionHandler():
    """Handler class providing app version."""

    @classmethod
    def get(cls, **kwargs):
        """Get app version."""
        return VMAAS_VERSION


class TaskStatusHandler():
    """Handler class providing status of currently running background task."""

    @classmethod
    def get(cls, **kwargs):
        """Get status of currently running background task."""
        return TaskStatusResponse(running=SyncTask.is_running(), task_type=SyncTask.get_task_type())


class TaskCancelHandler():
    """Handler class to cancel currently running background task."""

    @classmethod
    def put(cls, **kwargs):
        """Cancel currently running background task."""

        if SyncTask.is_running():
            SyncTask.cancel()
            LOGGER.warning("Background task terminated.")
        return TaskStatusResponse(running=SyncTask.is_running(), task_type=SyncTask.get_task_type())


class SyncHandler:
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
        if cls not in (ExporterHandler, PkgTreeHandler, RepoListHandler, GitRepoListHandler):
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
        if cls not in (PkgTreeHandler, RepoListHandler, GitRepoListHandler):
            # Notify webapps to update it's cache
            if ReposcanWebsocket.websocket:
                ReposcanWebsocket.websocket.write_message("invalidate-cache")
            else:
                ReposcanWebsocket.websocket_response_queue.add("invalidate-cache")
        LOGGER.info("%s task finished: %s.", cls.task_type, task_result)
        SyncTask.finish()


class RepolistImportHandler(SyncHandler):
    """Base class for importing repolists"""
    task_type = "Import repositories"

    @classmethod
    def _content_set_to_repos(cls, content_set):
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

    @classmethod
    def parse_repolist_json(cls, data):
        """Parse JSON in standard repolist format, see yaml spec"""
        products = {}
        repos = []
        for repo_group in data:
            # Entitlement cert is optional, use default if not specified in input JSON
            if "entitlement_cert" in repo_group:
                cert_name = repo_group["entitlement_cert"]["name"]
                ca_cert = repo_group["entitlement_cert"]["ca_cert"]
                cert = repo_group["entitlement_cert"]["cert"]
                key = repo_group["entitlement_cert"]["key"]
            elif DEFAULT_CA_CERT or DEFAULT_CERT:
                cert_name = DEFAULT_CERT_NAME
                ca_cert = DEFAULT_CA_CERT
                cert = DEFAULT_CERT
                key = DEFAULT_KEY
            else:
                cert_name, ca_cert, cert, key = None, None, None, None

            # Repository list with product and content set information
            for product_name, product in repo_group["products"].items():
                products[product_name] = {"product_id": product.get("redhat_eng_product_id", None), "content_sets": {}}
                for content_set_label, content_set in product["content_sets"].items():
                    products[product_name]["content_sets"][content_set_label] = content_set["name"]
                    for repo_url, basearch, releasever in cls._content_set_to_repos(content_set):
                        repos.append((repo_url, content_set_label, basearch, releasever,
                                      cert_name, ca_cert, cert, key))

        return products, repos

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
        except Exception as err:  # pylint: disable=broad-except
            msg = "Internal server error <%s>" % err.__hash__()
            LOGGER.exception(msg)
            DatabaseHandler.rollback()
            return "ERROR"
        return "OK"


class GitRepoListHandler(RepolistImportHandler):
    """Handler for importing repolists from git"""
    task_type = "Import repositories from git"

    @staticmethod
    def run_task(*args, **kwargs):
        """Start importing from git"""

        if not REPOLIST_GIT_TOKEN:
            LOGGER.warning("REPOLIST_GIT_TOKEN not set, skipping download of repositories from git.")
            return "SKIPPED"

        LOGGER.info("Downloading repolist.json from git %s", REPOLIST_GIT)
        shutil.rmtree(REPOLIST_DIR, True)
        os.makedirs(REPOLIST_DIR, exist_ok=True)

        # Should we just use replacement or add a url handling library, which
        # would be used replace the username in the provided URL ?
        git_url = REPOLIST_GIT.replace('https://', f'https://{REPOLIST_GIT_TOKEN}:x-oauth-basic@')

        repo = git.Git('/').clone(git_url, REPOLIST_DIR)
        assert repo

        if not os.path.isdir(REPOLIST_DIR) or not os.path.isfile(REPOLIST_DIR + '/' + REPOLIST_PATH):
            LOGGER.error("Downloading repolist failed: Directory was not created")

        json_file = open(REPOLIST_DIR + '/' + REPOLIST_PATH, 'r')
        data = json.load(json_file)
        assert data

        products, repos = RepolistImportHandler.parse_repolist_json(data)
        return RepolistImportHandler.run_task(products=products, repos=repos)

    @classmethod
    def put(cls, **kwargs):
        """Add repositories listed in request to the DB"""
        try:
            status_code, status_msg = cls.start_task()
            return status_msg, status_code
        except Exception as err:  # pylint: disable=broad-except
            msg = "Internal server error <%s>" % err.__hash__()
            LOGGER.exception(msg)
            return TaskStartResponse(msg, success=False), 400


class RepoListHandler(RepolistImportHandler):
    """Handler for repository list/add API."""

    task_type = "Import repositories"

    @classmethod
    def _parse_input_list(cls):
        # check if JSON is passed as a file or as a body of POST request
        data = None
        if request.files:
            json_data = request.files['file'][0]['body']  # pick up only first file (index 0)
            data = json.loads(json_data)
        elif request.data:
            data = request.json

        return cls.parse_repolist_json(data)

    @classmethod
    def post(cls, **kwargs):
        """Add repositories listed in request to the DB"""
        try:
            products, repos = cls._parse_input_list()
            status_code, status_msg = cls.start_task(products=products, repos=repos)
            return status_msg, status_code
        except Exception as err:  # pylint: disable=broad-except
            msg = "Internal server error <%s>" % err.__hash__()
            LOGGER.exception(msg)
            return TaskStartResponse(msg, success=False), 400


class RepoDeleteHandler(SyncHandler):
    """Handler for repository item API."""

    task_type = "Delete repositories"

    @classmethod
    def delete(cls, repo, **kwargs):  # pylint: disable=arguments-differ
        """Delete repository."""
        status_code, status_msg = cls.start_task(repo=repo)
        return status_msg, status_code

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

    @classmethod
    def put(cls, **kwargs):
        """Export disk dump."""

        status_code, status_msg = cls.start_task()
        return status_msg, status_code

    @staticmethod
    def run_task(*args, **kwargs):
        """Function to start exporting disk dump."""
        try:
            export_data(DUMP)
        except Exception as err:  # pylint: disable=broad-except
            msg = "Internal server error <%s>" % err.__hash__()
            LOGGER.exception(msg)
            DatabaseHandler.rollback()
            return "ERROR"
        return "OK"


class PkgTreeHandler(SyncHandler):
    """Handler for Package Tree API."""

    task_type = "Export package tree"

    @classmethod
    def put(cls, **kwargs):
        """Export package tree."""

        status_code, status_msg = cls.start_task()
        return status_msg, status_code

    @staticmethod
    def run_task(*args, **kwargs):
        """Function to start exporting disk dump."""
        try:
            export_pkgtree(PKGTREE_FILE)
        except Exception as err:  # pylint: disable=broad-except
            msg = "Internal server error <%s>" % err.__hash__()
            LOGGER.exception(msg)
            DatabaseHandler.rollback()
            return "ERROR"
        return "OK"


class PkgTreeDownloadHandler():
    """Handler class to download package tree to the caller."""

    @classmethod
    def get(cls, **kwargs):
        """Download the package tree."""

        try:
            response = make_response(send_file(PKGTREE_FILE))
            response.headers["Content-Type"] = "application/json"
            response.headers["Content-Encoding"] = "gzip"
            response.direct_passthrough = True
            return response

        except FileNotFoundError:
            return 'Package Tree file not found.  Has it been generated?', 404


class DbChangeHandler():
    """Handler for dbchange metadata information API. """

    @classmethod
    def get(cls, **kwargs):
        """Get the metadata information about database."""
        dbchange_api = DbChangeAPI()
        result = dbchange_api.process()
        return result


class RepoSyncHandler(SyncHandler):
    """Handler for repository sync API."""

    task_type = "Sync repositories"

    @classmethod
    def put(cls, **kwargs):
        """Sync repositories stored in DB."""

        status_code, status_msg = cls.start_task()
        return status_msg, status_code

    @staticmethod
    def run_task(*args, **kwargs):
        """Function to start syncing all repositories available from database."""
        try:
            init_logging()
            init_db()
            repository_controller = RepositoryController()
            repository_controller.add_db_repositories()
            repository_controller.store()
        except Exception as err:  # pylint: disable=broad-except
            msg = "Internal server error <%s>" % err.__hash__()
            LOGGER.exception(msg)
            DatabaseHandler.rollback()
            return "ERROR"
        return "OK"


class CvemapSyncHandler(SyncHandler):
    """Handler for CVE sync API."""

    task_type = "Sync CVE map"

    @classmethod
    def put(cls, **kwargs):
        """Sync CVEmap."""

        status_code, status_msg = cls.start_task()
        return status_msg, status_code

    @staticmethod
    def run_task(*args, **kwargs):
        """Function to start syncing all CVEs."""
        try:
            init_logging()
            init_db()
            controller = CvemapController()
            controller.store()
        except Exception as err:  # pylint: disable=broad-except
            msg = "Internal server error <%s>" % err.__hash__()
            LOGGER.exception(msg)
            DatabaseHandler.rollback()
            return "ERROR"
        return "OK"


class AllSyncHandler(SyncHandler):
    """Handler for repo + CVE sync API."""

    task_type = "%s + %s + %s" % (GitRepoListHandler.task_type,
                                  RepoSyncHandler.task_type,
                                  CvemapSyncHandler.task_type)

    @classmethod
    def put(cls, **kwargs):
        """Sync repos + CVEs + CVEmap."""

        status_code, status_msg = cls.start_task()
        return status_msg, status_code

    @staticmethod
    def run_task(*args, **kwargs):
        """Function to start syncing all repositories from database + all CVEs."""
        return "%s, %s, %s" % (GitRepoListHandler.run_task(),
                               RepoSyncHandler.run_task(),
                               CvemapSyncHandler.run_task())


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

        def _err_callback(err):
            LOGGER.error("SyncTask error: %s", err)
            SyncTask.finish()

        cls.workers.apply_async(func, args, kwargs, _callback, _err_callback)

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
        with disabled_signals():
            cls.workers.terminate()
            cls.workers.join()
            cls.workers = Pool(1)
            cls.finish()


class ReposcanWebsocket():
    """Class defining API handlers."""

    websocket = None
    websocket_url = "ws://%s:8082/" % os.getenv("WEBSOCKET_HOST", "vmaas_websocket")
    websocket_response_queue = set()
    reconnect_callback = None

    @staticmethod
    def stop():
        """Stop the application"""
        if SyncTask.is_running():
            SyncTask.cancel()
        IOLoop.instance().stop()

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
        except:  # pylint: disable=bare-except
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


@contextmanager
def disabled_signals():
    """ Temporarily disables signal handlers, using contextlib to automatically re-enable them"""
    handlers = {}
    for sig in KILL_SIGNALS:
        handlers[sig] = signal.signal(sig, signal.SIG_DFL)
    try:
        yield True
    finally:
        for sig in KILL_SIGNALS:
            signal.signal(sig, handlers[sig])


def create_app():
    """Create reposcan app."""

    init_logging()
    LOGGER.info("Starting (version %s).", VMAAS_VERSION)
    sync_interval = int(os.getenv('REPOSCAN_SYNC_INTERVAL_MINUTES', "360")) * 60000
    if sync_interval > 0:
        PeriodicCallback(periodic_sync, sync_interval).start()
    else:
        LOGGER.info("Periodic syncing disabled.")

    ws_handler = ReposcanWebsocket()

    def terminate(*_):
        """Trigger shutdown."""
        LOGGER.info("Signal received, stopping application.")
        # Kill asyncio ioloop
        IOLoop.instance().add_callback_from_signal(ws_handler.stop)
        # Kill background pool
        SyncTask.cancel()

    for sig in KILL_SIGNALS:
        signal.signal(sig, terminate)

    ws_handler.websocket_reconnect()
    ws_handler.reconnect_callback = PeriodicCallback(ws_handler.websocket_reconnect,
                                                     WEBSOCKET_RECONNECT_INTERVAL * 1000)
    ws_handler.reconnect_callback.start()

    with open('reposcan.spec.yaml', 'rb') as specfile:
        SPEC = yaml.safe_load(specfile)  # pylint: disable=invalid-name
    SPEC['info']['version'] = VMAAS_VERSION

    app = connexion.App(__name__, options={
        'swagger_ui': True,
        'openapi_spec_path': '/openapi.json'
    })

    # Response validation is disabled due to returing streamed response in GET /pkgtree
    # https://github.com/zalando/connexion/pull/467 should fix it
    app.add_api(SPEC, resolver=connexion.RestyResolver('reposcan'),
                validate_responses=False,
                strict_validation=True,
                base_path='/api'
                )

    @app.app.route('/metrics', methods=['GET'])
    def metrics():  # pylint: disable=unused-variable
        # /metrics API shouldn't be visible in the API documentation,
        # hence it's added here in the create_app step
        return generate_latest(), 200, {'Content-Type': 'text/plain; charset=utf-8'}

    @app.app.after_request
    def set_headers(response):  # pylint: disable=unused-variable
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type"
        return response

    return app
