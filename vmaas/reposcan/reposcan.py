#!/usr/bin/env python3
# pylint: disable=too-many-lines
"""
Main entrypoint of reposcan tool. It provides and API and allows to sync specified repositories
into specified PostgreSQL database.
"""

import atexit
import base64
import json
import os
import shutil
from multiprocessing.pool import Pool
import multiprocessing
from enum import StrEnum
from functools import reduce
from pathlib import Path

from apscheduler.schedulers.background import BackgroundScheduler
import connexion
import git
from prometheus_client import generate_latest
from psycopg2 import DatabaseError
import requests
import starlette.responses
from starlette.middleware.cors import CORSMiddleware

from vmaas.common.config import Config
from vmaas.common.constants import VMAAS_VERSION
from vmaas.common.logging_utils import get_logger, init_logging
from vmaas.common.middlewares import TimingLoggingMiddleware
from vmaas.common.strtobool import strtobool
from vmaas.reposcan.database.database_handler import DatabaseHandler, init_db
from vmaas.reposcan.database.product_store import ProductStore
from vmaas.reposcan.dbchange import DbChangeAPI
from vmaas.reposcan.dbdump import DbDumpAPI
from vmaas.reposcan.exporter import main as export_data, fetch_latest_dump, upload_dump_s3
from vmaas.reposcan.katello import KatelloApi, KATELLO_HOST, KATELLO_API_USER, KATELLO_API_PASS
from vmaas.reposcan.mnm import ADMIN_REQUESTS, FAILED_AUTH, FAILED_IMPORT_CVE, FAILED_IMPORT_CPE, \
    CSAF_FAILED_IMPORT, FAILED_IMPORT_REPO, RELEASE_FAILED_IMPORT, RELEASE_GRAPH_FAILED_IMPORT, REPOS_TO_CLEANUP, \
    REGISTRY
from vmaas.reposcan.pkgtree import main as export_pkgtree, PKGTREE_FILE
from vmaas.reposcan.redhatcpe.cpe_controller import CpeController
from vmaas.reposcan.redhatcsaf.csaf_controller import CsafController
from vmaas.reposcan.redhatcve.cvemap_controller import CvemapController
from vmaas.reposcan.redhatrelease.release_controller import ReleaseController
from vmaas.reposcan.repodata.repository_controller import RepositoryController
from vmaas.reposcan.redhatreleasegraph.modeling import ReleaseGraph
from vmaas.reposcan.database.release_graph_store import ReleaseGraphStore

LOGGER = get_logger(__name__)
CFG = Config()

DEFAULT_CHUNK_SIZE = "1048576"

# FedRAMP deployment using only baked-in content, no git cloning in runtime
IS_FEDRAMP = strtobool(os.getenv("IS_FEDRAMP", "FALSE"))
REPOLIST_STATIC_DIR = Path("/vmaas/repolist_git")

REPOLIST_DIR = Path("/tmp/repolist_git")
REPOLIST_GIT = os.getenv('REPOLIST_GIT', '')
REPOLIST_GIT_REF = os.getenv('REPOLIST_GIT_REF', 'master')
REPOLIST_GIT_TOKEN = os.getenv('REPOLIST_GIT_TOKEN', '')
REPOLIST_PATH = os.getenv('REPOLIST_PATH', 'repolist.json')
RELEASEMAP_PATH = os.getenv('RELEASEMAP_PATH', 'ga_dates.json')
RELEASE_GRAPH_DIR = os.getenv("RELEASE_GRAPH_PATH", "release_graphs")

DEFAULT_CERT_NAME = "DEFAULT"
DEFAULT_ORG_NAME = "DEFAULT"
DEFAULT_CA_CERT = os.getenv("DEFAULT_CA_CERT", "")
DEFAULT_CERT = os.getenv("DEFAULT_CERT", "")
DEFAULT_KEY = os.getenv("DEFAULT_KEY", "")

DEFAULT_PATH_API = "/api"
DEFAULT_PATH = "/api/vmaas"

CACHE_DUMP_RETRY_SECONDS = int(os.getenv("CACHE_DUMP_RETRY_SECONDS", "300"))


class RepoListSource(StrEnum):
    """Supported repolist sources."""
    MANUAL = "manual"
    GIT = "git"
    KATELLO = "katello"


SYNC_REPO_LIST_SOURCE = os.getenv("SYNC_REPO_LIST_SOURCE", str(RepoListSource.MANUAL))
# Allow to optionally disable some parts of sync (e.g. to speed up testing)
SYNC_REPOS = strtobool(os.getenv("SYNC_REPOS", "yes"))
SYNC_CVE_MAP = strtobool(os.getenv("SYNC_CVE_MAP", "yes"))
SYNC_CPE = strtobool(os.getenv("SYNC_CPE", "yes"))
SYNC_CSAF = strtobool(os.getenv("SYNC_CSAF", "yes"))
SYNC_RELEASES = strtobool(os.getenv("SYNC_RELEASES", "yes"))
SYNC_RELEASE_GRAPH = strtobool(os.getenv("SYNC_RELEASE_GRAPH", "yes"))


class TaskStatusResponse(dict):
    """Object used as API response to user."""

    def __init__(self, running=False, task_type=None):
        super().__init__()
        self['running'] = running
        self['task_type'] = task_type


class TaskStartResponse(dict):
    """Object used as API response to user."""

    def __init__(self, msg, success=True):
        super().__init__()
        self['msg'] = msg
        self['success'] = success


def get_identity(x_rh_identity: str) -> dict:
    """Get identity from given b64 string."""
    try:
        decoded_value = base64.b64decode(x_rh_identity).decode("utf-8")
    except Exception:  # pylint: disable=broad-except
        LOGGER.warning("Error decoding b64 string: %s", x_rh_identity)
        decoded_value = ""
    else:
        LOGGER.debug("Identity decoded: %s", decoded_value)
    try:
        identity = json.loads(decoded_value)
    except json.decoder.JSONDecodeError:
        LOGGER.warning("Error parsing JSON identity: %s", decoded_value)
        identity = None
    return identity


def auth_admin(x_rh_identity, required_scopes=None):  # pylint: disable=unused-argument
    """
    Parses user name from the x-rh-identity header
    """
    identity = get_identity(x_rh_identity)
    user = identity.get("identity", {}).get("associate", {}).get("email")
    if user:
        LOGGER.info("User '%s' accessed admin API.", user)
        ADMIN_REQUESTS.inc()
        return {"uid": user}
    FAILED_AUTH.inc()
    return None


# pylint: disable=unused-argument

class HealthHandler():
    """Handler class providing health status."""

    @classmethod
    def get(cls, **kwargs):
        """Get API status."""
        return "Ok", 200


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


class DumpVersionHandler():
    """Handler class for getting latest dump version."""

    @classmethod
    def get(cls, **kwargs):
        """Get the latest version."""
        return fetch_latest_dump()


class GitManager:
    """Handler for setting up the git directory and parsing content"""

    git_dir = None

    @classmethod
    def fetch_git(cls, force: bool = True) -> None:
        """Download data from configured git repo"""
        if not force and cls.git_dir:
            LOGGER.debug("Found previously set git assets")
            return

        if IS_FEDRAMP:
            LOGGER.info("FedRAMP env, using static assets source: %s", REPOLIST_STATIC_DIR)
            git_dir = REPOLIST_STATIC_DIR
        else:
            LOGGER.info("Downloading assets from git %s", REPOLIST_GIT)
            shutil.rmtree(REPOLIST_DIR, True)
            os.makedirs(REPOLIST_DIR, exist_ok=True)

            # Should we just use replacement or add a url handling library, which
            # would be used replace the username in the provided URL ?
            git_url = REPOLIST_GIT
            if REPOLIST_GIT_TOKEN:
                git_url = git_url.replace('https://', f'https://{REPOLIST_GIT_TOKEN}:x-oauth-basic@')
            git_ref = REPOLIST_GIT_REF if REPOLIST_GIT_REF else 'master'

            git.Repo.clone_from(git_url, REPOLIST_DIR, branch=git_ref)
            git_dir = REPOLIST_DIR

        # Success, git dir with files found
        if git_dir.is_dir():
            cls.git_dir = git_dir
        else:
            LOGGER.error("Downloading assets git repo failed: Directory was not created")

    @classmethod
    def get_git_products_repos(cls) -> tuple[dict | None, list | None]:
        """Parse data from set git dir and return products and repos"""
        if not cls.git_dir:
            LOGGER.error("Downloading git repo failed: Directory is missing")
            return None, None

        products, repos = {}, []
        paths = REPOLIST_PATH.split(',')
        for path in paths:
            # Trim the spaces so we can have nicely formatted comma lists
            file_path = cls.git_dir / path.strip()
            if not file_path.is_file():
                LOGGER.error("Downloading git repo failed: File %s was not created", path)
                return None, None

            with open(file_path, 'r', encoding='utf8') as json_file:
                data = json.load(json_file)

            item_products, item_repos = RepolistImportHandler.parse_repolist_json(data)
            if not item_products and not item_repos:
                LOGGER.warning("Input json is not valid")
                return None, None
            products.update(item_products)
            repos += item_repos

        return products, repos

    @classmethod
    def get_git_releases(cls) -> dict | None:
        """Parse data from set git dir and return releases"""
        releasemap_file = cls.git_dir / RELEASEMAP_PATH
        if not cls.git_dir or not releasemap_file.is_file():
            LOGGER.error("Downloading git repo failed: Releasemap is missing")
            return None

        with open(releasemap_file, 'r', encoding='utf8') as json_file:
            return json.load(json_file)

    @classmethod
    def get_git_release_graphs(cls) -> dict | None:
        """Parse data from set git dir and return release graphs"""
        if not cls.git_dir:
            LOGGER.error("Downloading git repo failed: Directory is missing")
            return None

        release_graphs = {}
        release_graph_dir = cls.git_dir / RELEASE_GRAPH_DIR
        if not release_graph_dir.is_dir():
            LOGGER.error("Downloading assets git repo failed: Dir %s was not created", RELEASE_GRAPH_DIR)
            return None

        for graph in release_graph_dir.glob("*.json"):
            with graph.open() as fde:
                content = fde.read()
                release_graphs[graph.name] = ReleaseGraph(graph.name, content)

        return release_graphs


class SyncHandler:
    """Base handler class providing common methods for different sync types."""

    task_type = "Unknown"

    @classmethod
    def start_task(cls, *args, export=True, **kwargs):
        """Start given task if DB worker isn't currently executing different task."""
        if not SyncTask.is_running():
            msg = "%s task started." % cls.task_type
            LOGGER.info(msg)
            task = cls.run_task
            if export:
                task = cls.run_task_and_export
            SyncTask.start(cls.task_type, task, cls.finish_task, *args, **kwargs)
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
        result = []
        result.append(cls.run_task(*args, **kwargs))
        if cls not in (ExporterHandler, PkgTreeHandler, RepoListHandler, GitRepoListHandler, KatelloRepoListHandler, CleanTmpHandler):
            result.append(ExporterHandler.run_task())
            result.append(PkgTreeHandler.run_task())
            result.append(S3ExporterHandler.run_task())
        return result

    @staticmethod
    def run_task(*args, **kwargs):
        """Run synchronization task."""
        raise NotImplementedError("abstract method")

    @classmethod
    def finish_task(cls, task_result):
        """Mark current task as finished."""
        is_err = reduce(lambda was, msg: was if was else "ERROR" in msg, task_result, False)
        LOGGER.info("%s task finished: %s.", cls.task_type, task_result)
        SyncTask.finish()
        return is_err


class RepolistImportHandler(SyncHandler):
    """Base class for importing repolists"""
    task_type = "Import repositories"

    @classmethod
    def _content_set_to_repos(cls, content_set):
        all_repos = []

        # Unpack list of content sets if provided
        if isinstance(content_set, list):
            for cset in content_set:
                all_repos += cls._content_set_to_repos(cset)
            return all_repos
        baseurls = content_set["baseurl"]
        basearches = content_set["basearch"]
        releasevers = content_set["releasever"]

        # Accept a list or single baseurl
        if isinstance(baseurls, str):
            baseurls = [baseurls]
        if not isinstance(baseurls, list):
            raise ValueError("baseurl has to be either a list or a string")

        for baseurl in baseurls:
            repos = [(baseurl, None, None)]
            # Replace basearch
            if basearches:
                repos = [(repo[0].replace("$basearch", basearch), basearch, repo[2])
                         for basearch in basearches for repo in repos]
            # Replace releasever
            if releasevers:
                repos = [(repo[0].replace("$releasever", releasever), repo[1], releasever)
                         for releasever in releasevers for repo in repos]

            all_repos.extend(repos)

        return all_repos

    @classmethod
    def parse_repolist_json(cls, data):
        """Parse JSON in standard repolist format, see yaml spec"""
        products = {}
        repos = []
        seen = set()
        for repo_group in data:
            organization = repo_group.get("organization", DEFAULT_ORG_NAME)
            # Entitlement cert is optional, use default if not specified in input JSON
            if "entitlement_cert" in repo_group and isinstance(repo_group['entitlement_cert'], dict):
                cert_name = repo_group["entitlement_cert"]["name"]
                ca_cert = repo_group["entitlement_cert"]["ca_cert"]
                cert = repo_group["entitlement_cert"]["cert"]
                key = repo_group["entitlement_cert"]["key"]
                # Disable any kind of certificate
            elif "entitlement_cert" in repo_group and isinstance(repo_group['entitlement_cert'], bool) \
                    and repo_group["entitlement_cert"] is False:
                cert_name, ca_cert, cert, key = None, None, None, None

            elif DEFAULT_CA_CERT or DEFAULT_CERT:
                cert_name = DEFAULT_CERT_NAME
                ca_cert = DEFAULT_CA_CERT
                cert = DEFAULT_CERT
                key = DEFAULT_KEY
            else:
                cert_name, ca_cert, cert, key = None, None, None, None

            # Repository list with product and content set information
            for product_name, product in repo_group["products"].items():
                product_id = product.get('redhat_eng_product_id', None)
                products[product_name] = {"product_id": product_id, "content_sets": {}}
                if product_id is not None and product_id in seen or seen.add(product_id):
                    return None, None
                for content_set_label, content_set in product["content_sets"].items():
                    products[product_name]["content_sets"][content_set_label] = content_set
                    for repo_url, basearch, releasever in cls._content_set_to_repos(content_set):
                        repos.append((repo_url, content_set_label, basearch, releasever,
                                      cert_name, ca_cert, cert, key, organization))

        return products, repos

    @staticmethod
    def run_task(*args, **kwargs):
        """Function to import all repositories from input list to the DB."""
        try:
            products = kwargs.get("products", None)
            repos = kwargs.get("repos", None)
            verbose = kwargs.get("verbose", False)
            delete = kwargs.get("delete", False)
            init_logging()
            init_db()

            if products:
                product_store = ProductStore()
                product_store.store(products)

            if repos:
                repository_controller = RepositoryController()
                repos_in_db = repository_controller.repo_store.list_repositories()
                # Sync repos from input
                for repo_url, content_set, basearch, releasever, cert_name, ca_cert, cert, key, organization in repos:
                    repository_controller.add_repository(repo_url, content_set, basearch, releasever, organization,
                                                         cert_name=cert_name, ca_cert=ca_cert,
                                                         cert=cert, key=key)
                    repos_in_db.pop((content_set, basearch, releasever, organization), None)
                if verbose:
                    for content_set, basearch, releasever, organization in repos_in_db:
                        LOGGER.warning("Repository in DB but not in repolist: %s", ", ".join(
                            filter(None, (content_set, basearch, releasever, organization))))
                    REPOS_TO_CLEANUP.set(len(repos_in_db))
                repository_controller.import_repositories()
                # For certain repository sources (katello) delete unused repos from DB automatically
                if delete:
                    repository_controller.delete_repos(repos_in_db)
        except Exception as err:  # pylint: disable=broad-except
            msg = "Internal server error <%s>" % hash(err)
            LOGGER.exception(msg)
            DatabaseHandler.rollback()
            if isinstance(err, DatabaseError):
                return "DB_ERROR"
            return "ERROR"
        finally:
            DatabaseHandler.close_connection()
        return "OK"


class GitRepoListHandler(RepolistImportHandler):
    """Handler for importing repolists from git"""
    task_type = "Import repositories from git"

    @staticmethod
    def run_task(*args, **kwargs):
        """Start importing from git"""
        init_logging()

        if not any([REPOLIST_GIT, IS_FEDRAMP]):
            LOGGER.warning("Git repository URL not set and can't use the static repository.")
            return "SKIPPED"

        GitManager.fetch_git(force=kwargs.get("force_git_fetch", True))
        products, repos = GitManager.get_git_products_repos()
        if products is None or repos is None:
            return "ERROR"
        return RepolistImportHandler.run_task(products=products, repos=repos, verbose=True)

    @classmethod
    def put(cls, **kwargs):
        """Add repositories listed in request to the DB"""
        try:
            status_code, status_msg = cls.start_task()
            return status_msg, status_code
        except Exception as err:  # pylint: disable=broad-except
            msg = "Internal server error <%s>" % hash(err)
            LOGGER.exception(msg)
            FAILED_IMPORT_REPO.inc()
            return TaskStartResponse(msg, success=False), 400


class GitRepoListCleanupHandler(SyncHandler):
    """Handler for deleting repos from DB if repos are not in repolist"""
    task_type = "Cleanup repositories from DB"

    @staticmethod
    def run_task(*args, **kwargs):
        """Start importing from git"""
        try:
            init_logging()
            init_db()

            if not any([REPOLIST_GIT, IS_FEDRAMP]):
                LOGGER.warning("Git repository URL not set and can't use the static repository.")
                return "SKIPPED"

            GitManager.fetch_git(force=kwargs.get("force_git_fetch", True))
            _, repos = GitManager.get_git_products_repos()
            if not repos:
                return "ERROR"

            repository_controller = RepositoryController()
            repos_in_db = repository_controller.repo_store.list_repositories()
            for _, content_set, basearch, releasever, _, _, _, _, organization in repos:
                repos_in_db.pop((content_set, basearch, releasever, organization), None)
            repository_controller.delete_repos(repos_in_db)
        except Exception as err:  # pylint: disable=broad-except
            msg = "Internal server error <%s>" % hash(err)
            LOGGER.exception(msg)
            DatabaseHandler.rollback()
            if isinstance(err, DatabaseError):
                return "DB_ERROR"
            return "ERROR"
        finally:
            DatabaseHandler.close_connection()
        return "OK"

    @classmethod
    def delete(cls, **kwargs):
        """Cleanup repositories from DB"""
        try:
            status_code, status_msg = cls.start_task()
            return status_msg, status_code
        except Exception as err:  # pylint: disable=broad-except
            msg = "Internal server error <%s>" % hash(err)
            LOGGER.exception(msg)
            FAILED_IMPORT_REPO.inc()
            return TaskStartResponse(msg, success=False), 400


class KatelloRepoListHandler(RepolistImportHandler):
    """Handler for importing repolists from Katello"""
    task_type = "Import repositories from Katello"

    @staticmethod
    def run_task(*args, **kwargs):
        """Start importing from Katello"""
        init_logging()
        init_db()
        if not KATELLO_HOST or not KATELLO_API_USER or not KATELLO_API_PASS:
            LOGGER.warning("KATELLO_HOST, KATELLO_API_USER or KATELLO_API_PASS not set, skipping download of repositories from Katello.")
            return "SKIPPED"
        katello_api = KatelloApi(KATELLO_HOST, KATELLO_API_USER, KATELLO_API_PASS)
        products, repos, success = katello_api.get_products_repos()
        if not success:
            return "ERROR"
        return RepolistImportHandler.run_task(products=products, repos=repos, verbose=True, delete=True)

    @classmethod
    def put(cls, **kwargs):
        """Add repositories listed in request to the DB"""
        try:
            status_code, status_msg = cls.start_task()
            return status_msg, status_code
        except Exception as err:  # pylint: disable=broad-except
            msg = "Internal server error <%s>" % hash(err)
            LOGGER.exception(msg)
            FAILED_IMPORT_REPO.inc()
            return TaskStartResponse(msg, success=False), 400


class RepoListHandler(RepolistImportHandler):
    """Handler for repository list/add API."""

    task_type = "Import repositories"

    @classmethod
    def post(cls, body, **kwargs):
        """Add repositories listed in request to the DB"""
        try:
            products, repos = cls.parse_repolist_json(body)
            if not products and not repos:
                msg = "Input json is not valid"
                LOGGER.warning(msg)
                return TaskStartResponse(msg, success=False), 400
            status_code, status_msg = cls.start_task(products=products, repos=repos)
            return status_msg, status_code
        except Exception as err:  # pylint: disable=broad-except
            msg = "Internal server error <%s>" % hash(err)
            LOGGER.exception(msg)
            FAILED_IMPORT_REPO.inc()
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
            msg = "Internal server error <%s>" % hash(err)
            LOGGER.exception(msg)
            DatabaseHandler.rollback()
            return "ERROR"
        finally:
            DatabaseHandler.close_connection()
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
            export_data()
        except Exception as err:  # pylint: disable=broad-except
            msg = "Internal server error <%s>" % hash(err)
            LOGGER.exception(msg)
            DatabaseHandler.rollback()
            if isinstance(err, DatabaseError):
                return "DB_ERROR"
            return "ERROR"
        finally:
            DatabaseHandler.close_connection()
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
            msg = "Internal server error <%s>" % hash(err)
            LOGGER.exception(msg)
            DatabaseHandler.rollback()
            if isinstance(err, DatabaseError):
                return "DB_ERROR"
            return "ERROR"
        finally:
            DatabaseHandler.close_connection()
        return "OK"


class S3ExporterHandler(SyncHandler):
    """Handler for S3 Export API."""

    task_type = "S3 Export dump"

    @classmethod
    def put(cls, **kwargs):
        """Export disk dump to S3."""

        status_code, status_msg = cls.start_task()
        return status_msg, status_code

    @staticmethod
    def run_task(*args, **kwargs):
        """Function to export db dump to S3 bucket."""
        try:
            if not CFG.s3_available:
                LOGGER.warning("S3 not available, skipping upload to S3")
                return "SKIPPED"
            upload_dump_s3()
        except Exception as err:  # pylint: disable=broad-except
            msg = "Internal server error <%s>" % hash(err)
            LOGGER.exception(msg)
            return "ERROR"
        finally:
            DatabaseHandler.close_connection()
        return "OK"


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
            msg = "Internal server error <%s>" % hash(err)
            LOGGER.exception(msg)
            DatabaseHandler.rollback()
            if isinstance(err, DatabaseError):
                return "DB_ERROR"
            return "ERROR"
        finally:
            DatabaseHandler.close_connection()
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
            msg = "Internal server error <%s>" % hash(err)
            LOGGER.exception(msg)
            FAILED_IMPORT_CVE.inc()
            DatabaseHandler.rollback()
            if isinstance(err, DatabaseError):
                return "DB_ERROR"
            return "ERROR"
        finally:
            DatabaseHandler.close_connection()
        return "OK"


class CpeSyncHandler(SyncHandler):
    """Handler for Cpe sync API."""

    task_type = "Sync CPE metadata"

    @classmethod
    def put(cls, **kwargs):
        """Sync CPE metadata."""

        status_code, status_msg = cls.start_task()
        return status_msg, status_code

    @staticmethod
    def run_task(*args, **kwargs):
        """Function to start syncing all CVEs."""
        try:
            init_logging()
            init_db()
            controller = CpeController()
            controller.store()
        except Exception as err:  # pylint: disable=broad-except
            msg = "Internal server error <%s>" % hash(err)
            LOGGER.exception(msg)
            FAILED_IMPORT_CPE.inc()
            DatabaseHandler.rollback()
            if isinstance(err, DatabaseError):
                return "DB_ERROR"
            return "ERROR"
        finally:
            DatabaseHandler.close_connection()
        return "OK"


def metrics():
    """Generate Prometheus metrics."""
    return generate_latest(REGISTRY), 200, {'Content-Type': 'text/plain; charset=utf-8'}


class CsafSyncHandler(SyncHandler):
    """Handler for CSAF sync API."""

    task_type = "Sync CSAF metadata"

    @classmethod
    def put(cls, **kwargs):
        """Sync CSAF metadata."""

        status_code, status_msg = cls.start_task()
        return status_msg, status_code

    @staticmethod
    def run_task(*args, **kwargs):
        """Function to start syncing CSAFs."""
        try:
            init_logging()
            init_db()
            controller = CsafController()
            controller.store()
        except Exception as err:  # pylint: disable=broad-except
            msg = "Internal server error <%s>" % hash(err)
            LOGGER.exception(msg)
            CSAF_FAILED_IMPORT.inc()
            DatabaseHandler.rollback()
            if isinstance(err, DatabaseError):
                return "DB_ERROR"
            return "ERROR"
        finally:
            DatabaseHandler.close_connection()
        return "OK"


class ReleaseSyncHandler(SyncHandler):
    """Handler for RHEL OS release version sync API."""

    task_type = "Sync RHEL releases"

    @classmethod
    def put(cls, **kwargs):
        """Sync RHEL releases."""
        status_code, status_msg = cls.start_task()
        return status_msg, status_code

    @staticmethod
    def run_task(*args, **kwargs):
        """Function to start syncing RHEL releases."""
        try:
            init_logging()
            init_db()

            if not any([REPOLIST_GIT, IS_FEDRAMP]):
                LOGGER.warning("Git repository URL not set and can't use the static repository.")
                return "SKIPPED"

            GitManager.fetch_git(force=kwargs.get("force_git_fetch", True))
            releases = GitManager.get_git_releases()

            if releases is None:
                return "ERROR"

            controller = ReleaseController()
            controller.store(releases)
        except Exception as err:  # pylint: disable=broad-except
            msg = "Internal server error <%s>" % hash(err)
            LOGGER.exception(msg)
            RELEASE_FAILED_IMPORT.inc()
            DatabaseHandler.rollback()
            if isinstance(err, DatabaseError):
                return "DB_ERROR"
            return "ERROR"
        finally:
            DatabaseHandler.close_connection()
        return "OK"


class ReleaseGraphSyncHandler(SyncHandler):
    """Handler for RHEL release graph sync API."""

    task_type = "Sync RHEL release graphs"

    @classmethod
    def put(cls, **kwargs):
        """Sync RHEL release graphs."""
        status_code, status_msg = cls.start_task()
        return status_msg, status_code

    @staticmethod
    def run_task(*args, **kwargs):
        """Function to start syncing RHEL release graphs."""
        try:
            init_logging()
            init_db()

            if not any([REPOLIST_GIT, IS_FEDRAMP]):
                LOGGER.warning("Git repository URL not set and can't use the static repository.")
                return "SKIPPED"

            GitManager.fetch_git(force=kwargs.get("force_git_fetch", True))
            release_graphs = GitManager.get_git_release_graphs()

            if release_graphs is None:
                return "ERROR"

            store = ReleaseGraphStore(release_graphs)
            store.store()
        except Exception as err:  # pylint: disable=broad-except
            msg = "Internal server error <%s>" % hash(err)
            LOGGER.exception(msg)
            RELEASE_GRAPH_FAILED_IMPORT.inc()
            DatabaseHandler.rollback()
            if isinstance(err, DatabaseError):
                return "DB_ERROR"
            return "ERROR"
        finally:
            DatabaseHandler.close_connection()
        return "OK"


def all_sync_handlers() -> list:
    """Return all sync-handlers selected using env vars."""
    handlers = []
    handlers.extend([GitRepoListHandler] if SYNC_REPO_LIST_SOURCE == RepoListSource.GIT else [])  # type: ignore[list-item]
    handlers.extend([KatelloRepoListHandler] if SYNC_REPO_LIST_SOURCE == RepoListSource.KATELLO else [])  # type: ignore[list-item]
    handlers.extend([RepoSyncHandler] if SYNC_REPOS else [])  # type: ignore[list-item]
    handlers.extend([CvemapSyncHandler] if SYNC_CVE_MAP else [])  # type: ignore[list-item]
    handlers.extend([CpeSyncHandler] if SYNC_CPE else [])  # type: ignore[list-item]
    handlers.extend([CsafSyncHandler] if SYNC_CSAF else [])  # type: ignore[list-item]
    handlers.extend([ReleaseSyncHandler] if SYNC_RELEASES else [])  # type: ignore[list-item]
    handlers.extend([ReleaseGraphSyncHandler] if SYNC_RELEASE_GRAPH else [])  # type: ignore[list-item]
    return handlers


class AllSyncHandler(SyncHandler):
    """Handler for repo + CVE sync API."""

    task_type = " + ".join([h.task_type for h in all_sync_handlers()])

    @classmethod
    def put(cls, **kwargs):
        """Sync repos + CVEs + CVEmap."""

        status_code, status_msg = cls.start_task()
        return status_msg, status_code

    @staticmethod
    def run_task(*args, **kwargs):
        """Function to start syncing all repositories from database + all CVEs."""
        GitManager.git_dir = None
        tasks = ", ".join([h.run_task(force_git_fetch=False) for h in all_sync_handlers()])
        return tasks


class CleanTmpHandler(SyncHandler):
    """Handler for /tmp cleaning API."""

    task_type = "Clean temporary data"

    @classmethod
    def put(cls, **kwargs):
        """Clean temporary data."""

        status_code, status_msg = cls.start_task()
        return status_msg, status_code

    @staticmethod
    def run_task(*args, **kwargs):
        """Function to start cleaning temporary data."""
        try:
            init_logging()
            tmpdir = Path("/tmp")
            for item in tmpdir.iterdir():
                try:
                    if item.is_dir():
                        shutil.rmtree(item)
                    else:
                        os.unlink(item)
                    LOGGER.info("Deleted file or directory: %s", item)
                except Exception as err:  # pylint: disable=broad-except
                    LOGGER.warning("Unable to delete file or directory: %s (%s)", item, err)
        except Exception as err:  # pylint: disable=broad-except
            msg = "Internal server error <%s>" % hash(err)
            LOGGER.exception(msg)
            return "ERROR"
        return "OK"


class DbDumpHandler(SyncHandler):
    """Handler for export . """

    task_type = "Export pg_dbump"

    @classmethod
    def put(cls, **kwargs):
        """Export pg_dump."""
        status_code, status_msg = cls.start_task(export=False)
        return status_msg, status_code

    @classmethod
    def get(cls, **kwargs):
        """Get the pg_dump."""
        return DbDumpAPI.download()

    @staticmethod
    def run_task(*args, **kwargs):
        """Function to start exporting disk dump."""
        try:
            DbDumpAPI.create()
        except Exception as err:  # pylint: disable=broad-except
            msg = "Internal server error <%s>" % hash(err)
            LOGGER.exception(msg)
            return "ERROR"
        return "OK"


class WebappPprof:
    """Handler for webapp-go profile info."""

    @classmethod
    def get(cls, param, **kwargs):
        """Get webapp-go profile info."""
        if not strtobool(os.getenv("ENABLE_PROFILER", "false")):
            return "Set ENABLE_PROFILER=true to enable profiler"
        if param == "profile":
            param = "profile?seconds=20"
        res = requests.get(url=f"{CFG.webapp_go_url}/debug/pprof/{param}", timeout=60)
        headers = {"Content-Disposition": f"attachment; filename={param}"}
        return starlette.responses.Response(
            content=res.content,
            status_code=200,
            media_type="application/octet-stream",
            headers=headers,
        )


class SyncTask:
    """
    Static class providing methods for managing sync worker.
    Limit to single DB worker.
    """
    _process = None
    _running_task_type = None
    workers = None

    @classmethod
    def init(cls):
        """Initialize process pool for sync worker(s)."""
        if not cls.workers:
            # Don't inherit signal handlers in worker (set method to "spawn" instead of "fork").
            # Terminating worker would result in terminating uvicorn otherwise.
            multiprocessing.set_start_method("spawn")
            cls.workers = Pool(1)

    @classmethod
    def start(cls, task_type, func, callback, *args, **kwargs):
        """Start specified function with given parameters in separate worker."""
        if cls.workers is None:
            raise RuntimeError("SyncTask not initialized")
        cls._process = cls.workers._pool[0]  # pylint: disable=protected-access
        cls._running_task_type = task_type

        def _err_callback(err):
            LOGGER.error("SyncTask error: %s", err)
            SyncTask.finish()

        cls.workers.apply_async(func, args, kwargs, callback, _err_callback)

    @classmethod
    def finish(cls):
        """Mark work as done."""
        cls._process = None
        cls._running_task_type = None

    @classmethod
    def is_running(cls):
        """Return True when some sync is running."""
        # If process is killed during sync, no exception is thrown but Pool respawns process
        return cls._process is not None and cls._process.pid == cls.workers._pool[0].pid  # pylint: disable=protected-access

    @classmethod
    def get_task_type(cls):
        """Get currently running task type."""
        return cls._running_task_type

    @classmethod
    def cancel(cls):
        """Terminate the current running sync task."""
        if cls._process is not None:
            try:
                cls._process.terminate()
                cls._process.join()
            except Exception as err:  # pylint: disable=broad-except
                LOGGER.warning("Error terminating sync process: %s", err)
        cls.finish()

    @classmethod
    def shutdown(cls):
        """Shutdown the entire worker pool during application shutdown."""
        # First cancel any running task
        cls.cancel()
        
        # Then terminate the worker pool
        if cls.workers is not None:
            try:
                cls.workers.terminate()
                cls.workers.join()
            except Exception as err:  # pylint: disable=broad-except
                LOGGER.warning("Error terminating worker pool: %s", err)


def periodic_sync():
    """Function running both repo and CVE sync."""

    LOGGER.info("Periodic sync started.")
    AllSyncHandler.start_task()


def create_app(specs):
    """Create reposcan app."""
    init_logging()
    SyncTask.init()
    LOGGER.info("Starting (version %s).", VMAAS_VERSION)
    
    # Register cleanup handler for graceful shutdown
    def cleanup_sync_tasks():
        """Clean up running sync tasks on application shutdown."""
        LOGGER.info("Application shutting down, performing cleanup.")
        
        # Shutdown periodic scheduler if running
        if scheduler is not None:
            try:
                LOGGER.info("Shutting down periodic scheduler.")
                scheduler.shutdown(wait=False)
            except Exception as err:  # pylint: disable=broad-except
                LOGGER.warning("Error shutting down scheduler: %s", err)
        
        # Shutdown sync tasks and worker pool
        LOGGER.info("Shutting down sync tasks.")
        SyncTask.shutdown()
    
    atexit.register(cleanup_sync_tasks)
    # Store scheduler reference for cleanup
    scheduler = None
    sync_interval = int(os.getenv('REPOSCAN_SYNC_INTERVAL_MINUTES', "360"))
    if sync_interval > 0:
        scheduler = BackgroundScheduler()
        scheduler.add_job(periodic_sync, trigger="interval", minutes=sync_interval)
        scheduler.start()
        LOGGER.info("Periodic syncing running every %s minute(s).", sync_interval)
    else:
        LOGGER.info("Periodic syncing disabled.")

    if SYNC_REPO_LIST_SOURCE in RepoListSource:
        LOGGER.info("Repository list source: %s", SYNC_REPO_LIST_SOURCE)
    else:
        LOGGER.warning("Unsupported repository list source: %s", SYNC_REPO_LIST_SOURCE)

    # Let uvicorn handle signals for graceful shutdown
    # Custom shutdown cleanup is handled in the SyncTask class methods

    app = connexion.AsyncApp(__name__, swagger_ui_options=connexion.options.SwaggerUIOptions(swagger_ui=True))

    # Response validation is disabled due to returing streamed response in GET /pkgtree
    # https://github.com/zalando/connexion/pull/467 should fix it
    for route, spec in specs.items():
        app.add_api(spec, resolver=connexion.RestyResolver('reposcan'),
                    validate_responses=False,
                    strict_validation=True,
                    base_path=route,
                    arguments={"vmaas_version": VMAAS_VERSION}
                    )

    app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_headers=["Content-Type"])
    app.add_middleware(TimingLoggingMiddleware, position=connexion.middleware.MiddlewarePosition.BEFORE_EXCEPTION,
                       vmaas_component="reposcan")
    return app
