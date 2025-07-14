#!/usr/bin/env python3
"""
Main web API module
"""
import asyncio
import os
import signal
import re

import connexion
from prometheus_client import generate_latest
import requests
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.gzip import GZipMiddleware

from vmaas.webapp.cache import Cache
from vmaas.webapp.cve import CveAPI
from vmaas.webapp.dbchange import DBChange
from vmaas.webapp.errata import ErrataAPI
from vmaas.webapp.packages import PackagesAPI
from vmaas.webapp.pkglist import PkgListAPI
from vmaas.webapp.patches import PatchesAPI
from vmaas.webapp.pkgtree import PkgtreeAPI
from vmaas.webapp.repos import RepoAPI
from vmaas.webapp.rpm_pkg_names import RPMPkgNamesAPI
from vmaas.webapp.srpm_pkg_names import SRPMPkgNamesAPI
from vmaas.webapp.updates import UpdatesAPI
from vmaas.webapp.vulnerabilities import VulnerabilitiesAPI

from vmaas.common.config import Config
from vmaas.common.constants import VMAAS_VERSION
from vmaas.common.logging_utils import get_logger
from vmaas.common.logging_utils import init_logging
from vmaas.common.middlewares import ErrorHandlerMiddleware, TimingLoggingMiddleware
from vmaas.common.strtobool import strtobool

# NOTE: this module is going to be removed soon
# pylint: disable=too-many-positional-arguments

# pylint: disable=too-many-lines
CFG = Config()

REFRESH_CHECK_INTERVAL = 60

GZIP_RESPONSE_ENABLE = strtobool(os.getenv("GZIP_RESPONSE_ENABLE", "off"))
GZIP_COMPRESS_LEVEL = int(os.getenv("GZIP_COMPRESS_LEVEL", "5"))
LATEST_DUMP_ENDPOINT = "api/v1/latestdump"

LOGGER = get_logger(__name__)

DEFAULT_PATH_API = "/api"
DEFAULT_PATH = "/api/vmaas"


class BaseHandler:
    """Base class containing individual repositories"""

    srpm_pkg_names_api = None
    rpm_pkg_names_api = None
    db_cache = None
    updates_api = None
    repo_api = None
    cve_api = None
    errata_api = None
    packages_api = None
    pkglist_api = None
    pkgtree_api = None
    vulnerabilities_api = None
    patches_api = None
    dbchange_api = None
    refreshing = False
    data_ready = False

    @classmethod
    async def handle_request(cls, api_endpoint, api_version, body=None, param_name=None, param=None, **kwargs):  # pylint: disable=unused-argument
        """Takes care of validation of input and execution of request."""
        # If refreshing cache, return 503 so apps can detect this state
        if cls.refreshing:
            return "Data refresh in progress, please try again later.", 503

        if not cls.data_ready:
            return "Data not available, please try again later.", 503

        data = None
        try:
            if body is not None:  # POST
                data = body
            else:  # GET
                data = {param_name: [param]}
            res = api_endpoint.process_list(api_version, data)
            code = 200
        except (ValueError, re.error) as ex:
            res = repr(ex)
            code = 400
        except Exception as err:  # pylint: disable=broad-except
            err_id = hash(err)
            res = 'Internal server error <%s>: please include this error id in bug report.' % err_id
            code = 500
            LOGGER.exception(res)
            LOGGER.error("Input data for <%s>: %s", err_id, data)
        return res, code


class HealthHandler:
    """Handler class providing health status."""

    @classmethod
    async def get(cls, *args, **kwargs):  # pylint: disable=unused-argument
        """Get API status.
           ---
           description: Return API status
           responses:
             200:
               description: Application is alive
        """
        return ""


class ReadyHandler(BaseHandler):
    """Handler class for providing pod status"""

    @classmethod
    async def get(cls, **kwargs):  # pylint: disable=unused-argument
        """Get app status(whether the app is ready to serve requests)"""
        status = 503 if cls.refreshing or not cls.data_ready else 200
        return "", status


class VersionHandler:
    """Handler class providing app version."""

    @classmethod
    async def get(cls, **kwargs):  # pylint: disable=unused-argument
        """Get app version.
           ---
           description: Get version of application
           responses:
             200:
               description: Version of application returned
        """
        return VMAAS_VERSION


class DBChangeHandler(BaseHandler):
    """
    Class to return last-updated information from VMaaS DB
    """

    @classmethod
    async def get(cls, **kwargs):  # pylint: disable=unused-argument
        """Get last-updated-times for VMaaS DB """
        return cls.dbchange_api.process()


class UpdatesHandlerGet(BaseHandler):
    """Handler for processing /updates GET requests."""

    @classmethod
    async def get(cls, nevra=None, **kwargs):
        """List security updates for single package NEVRA """
        return await cls.handle_request(cls.updates_api, 1, None, 'package_list', nevra, **kwargs)


class UpdatesHandlerPost(BaseHandler):
    """Handler for processing /updates POST requests."""

    @classmethod
    async def post(cls, body, **kwargs):
        """List security updates for list of package NEVRAs"""
        return await cls.handle_request(cls.updates_api, 1, body, **kwargs)


class UpdatesHandlerV2Get(BaseHandler):
    """Handler for processing /updates GET requests."""

    @classmethod
    async def get(cls, nevra=None, **kwargs):
        """List security updates for single package NEVRA """
        return await cls.handle_request(cls.updates_api, 2, None, 'package_list', nevra, **kwargs)


class UpdatesHandlerV2Post(BaseHandler):
    """Handler for processing /updates POST requests."""

    @classmethod
    async def post(cls, body, **kwargs):
        """List security updates for list of package NEVRAs"""
        return await cls.handle_request(cls.updates_api, 2, body, **kwargs)


class UpdatesHandlerV3Get(BaseHandler):
    """Handler for processing /updates GET requests."""

    @classmethod
    async def get(cls, nevra=None, **kwargs):
        """List security updates for single package NEVRA """
        return await cls.handle_request(cls.updates_api, 3, None, 'package_list', nevra, **kwargs)


class UpdatesHandlerV3Post(BaseHandler):
    """Handler for processing /updates POST requests."""

    @classmethod
    async def post(cls, body, **kwargs):
        """List security updates for list of package NEVRAs"""
        return await cls.handle_request(cls.updates_api, 3, body, **kwargs)


class CVEHandlerGet(BaseHandler):
    """Handler for processing /cves GET requests."""

    @classmethod
    async def get(cls, cve=None, **kwargs):
        """
        Get details about CVEs. It is possible to use POSIX regular expression as a pattern for CVE names.
        """
        return await cls.handle_request(cls.cve_api, 1, None, 'cve_list', cve, **kwargs)


class CVEHandlerPost(BaseHandler):
    """Handler for processing /cves POST requests."""

    @classmethod
    async def post(cls, body, **kwargs):
        """
        Get details about CVEs with additional parameters. As a "cve_list" parameter a complete list of CVE
        names can be provided OR one POSIX regular expression.
        """
        return await cls.handle_request(cls.cve_api, 1, body, **kwargs)


class ReposHandlerGet(BaseHandler):
    """Handler for processing /repos GET requests."""

    @classmethod
    async def get(cls, repo=None, **kwargs):
        """
        Get details about a repository or repository-expression. It is allowed to use POSIX regular
        expression as a pattern for repository names.
        """
        return await cls.handle_request(cls.repo_api, 1, None, 'repository_list', repo, **kwargs)


class ReposHandlerPost(BaseHandler):
    """Handler for processing /repos POST requests."""

    @classmethod
    async def post(cls, body, **kwargs):
        """
        Get details about list of repositories. "repository_list" can be either a list of repository
        names, OR a single POSIX regular expression.
        """
        return await cls.handle_request(cls.repo_api, 1, body, **kwargs)


class ErrataHandlerGet(BaseHandler):
    """Handler for processing /errata GET requests."""

    @classmethod
    async def get(cls, erratum=None, **kwargs):
        """
        Get details about errata. It is possible to use POSIX regular
        expression as a pattern for errata names.
        """
        return await cls.handle_request(cls.errata_api, 1, None, 'errata_list', erratum, **kwargs)


class ErrataHandlerPost(BaseHandler):
    """ /errata API handler """

    @classmethod
    async def post(cls, body, **kwargs):
        """
        Get details about errata with additional parameters. "errata_list"
        parameter can be either a list of errata names OR a single POSIX regular expression.
        """
        return await cls.handle_request(cls.errata_api, 1, body, **kwargs)


class PackagesHandlerGet(BaseHandler):
    """Handler for processing /packages GET requests."""

    @classmethod
    async def get(cls, nevra=None, **kwargs):
        """Get details about packages."""
        return await cls.handle_request(cls.packages_api, 1, None, 'package_list', nevra, **kwargs)


class PackagesHandlerPost(BaseHandler):
    """ /packages API handler """

    @classmethod
    async def post(cls, body, **kwargs):
        """Get details about packages. "package_list" must be a list of"""
        return await cls.handle_request(cls.packages_api, 1, body, **kwargs)


class PkgListHandlerPost(BaseHandler):
    """ /pkglist API handler """

    @classmethod
    async def post(cls, body, **kwargs):
        """Get details about all packages."""
        return await cls.handle_request(cls.pkglist_api, 1, body, **kwargs)


class PkgtreeHandlerGet(BaseHandler):
    """Handler for processing /pkgtree GET requests."""

    @classmethod
    async def get(cls, package_name=None, **kwargs):
        """Get package NEVRAs tree for a single package name."""
        return await cls.handle_request(cls.pkgtree_api, 1, None, 'package_name_list', package_name, **kwargs)


class PkgtreeHandlerV3Get(BaseHandler):
    """Handler for processing /pkgtree GET requests."""

    @classmethod
    async def get(cls, package_name=None, **kwargs):
        """Get package NEVRAs tree for a single package name."""
        return await cls.handle_request(cls.pkgtree_api, 3, None, 'package_name_list', package_name, **kwargs)


class PkgtreeHandlerPost(BaseHandler):
    """ /pkgtree API handler """

    @classmethod
    async def post(cls, body, **kwargs):
        """Get package NEVRAs trees for package names. "package_name_list" must be a list of package names."""
        return await cls.handle_request(cls.pkgtree_api, 1, body, **kwargs)


class PkgtreeHandlerV3Post(BaseHandler):
    """ /pkgtree API handler """

    @classmethod
    async def post(cls, body, **kwargs):
        """Get package NEVRAs trees for package names. "package_name_list" must be a list of package names."""
        return await cls.handle_request(cls.pkgtree_api, 3, body, **kwargs)


class VulnerabilitiesHandlerGet(BaseHandler):
    """Handler for processing /vulnerabilities GET requests."""

    @classmethod
    async def get(cls, nevra=None, **kwargs):
        """ List of applicable CVEs for a single package NEVRA
        """
        return await cls.handle_request(cls.vulnerabilities_api, 1, None, 'package_list', nevra, **kwargs)


class VulnerabilitiesHandlerPost(BaseHandler):
    """Handler for processing /vulnerabilities POST requests."""

    @classmethod
    async def post(cls, body, **kwargs):
        """List of applicable CVEs to a package list. """
        return await cls.handle_request(cls.vulnerabilities_api, 1, body, **kwargs)


class PatchesHandlerGet(BaseHandler):
    """Handler for processing /patches GET requests."""

    @classmethod
    async def get(cls, nevra=None, **kwargs):
        """ List of applicable errata for a single package NEVRA
        """
        return await cls.handle_request(cls.patches_api, 1, None, 'package_list', nevra, **kwargs)


class PatchesHandlerPost(BaseHandler):
    """Handler for processing /patches POST requests."""

    @classmethod
    async def post(cls, body, **kwargs):
        """List of applicable errata to a package list. """
        return await cls.handle_request(cls.patches_api, 1, body, **kwargs)


class SRPMPkgNamesHandlerPost(BaseHandler):
    """Handler for processing /package_names/srpms POST requests."""

    @classmethod
    async def post(cls, body, **kwargs):
        """RPM list or Content Set list by SRPM list or RPM list"""
        return await cls.handle_request(cls.srpm_pkg_names_api, 1, body, **kwargs)


class SRPMPkgNamesHandlerGet(BaseHandler):
    """Handler for processing /package_names/srpms GET requests."""

    @classmethod
    async def get(cls, srpm=None, **kwargs):
        """RPM list or Content Set list by SRPM list or RPM list"""
        return await cls.handle_request(cls.srpm_pkg_names_api, 1, None, 'srpm_name_list', srpm, **kwargs)


class RPMPkgNamesHandlerPost(BaseHandler):
    """Handler for processing /package_names/rpms POST requests."""

    @classmethod
    async def post(cls, body, **kwargs):
        """RPM list or Content Set list by SRPM list or RPM list"""
        return await cls.handle_request(cls.rpm_pkg_names_api, 1, body, **kwargs)


class RPMPkgNamesHandlerGet(BaseHandler):
    """Handler for processing /package_names/rpms GET requests."""

    @classmethod
    async def get(cls, rpm=None, **kwargs):
        """RPM list or Content Set list by SRPM list or RPM list"""
        return await cls.handle_request(cls.rpm_pkg_names_api, 1, None, 'rpm_name_list', rpm, **kwargs)


def metrics():
    """Provide current prometheus metrics"""
    return generate_latest(), 200, {'Content-Type': 'text/plain; charset=utf-8'}


def dummy_200():
    """Dummy endpoint returning 200"""
    return "", 200


def dummy_report_200():
    """Dummy /os/vulnerability/report endpoint returning 200"""
    return "", 200


class RefreshTimer:
    """ main refresh timer handling class"""

    def __init__(self):
        self.task = None

    def stop(self):
        """Stop timer task"""
        self.task.cancel()
        self.task = None

    async def _refresh_cache(self):
        if not BaseHandler.refreshing:
            LOGGER.info("Starting cached data refresh.")
            BaseHandler.refreshing = True
            BaseHandler.data_ready = False
            await BaseHandler.db_cache.reload_async()
            if BaseHandler.db_cache.dbchange.get('exported'):  # check if timestamp is set in cache
                BaseHandler.data_ready = True
            BaseHandler.refreshing = False
            LOGGER.info("Cached data refreshed.")
        else:
            LOGGER.warning("Cached data refresh already in progress.")

    async def run_timer(self):
        """Infinite loop handling refresh timer"""
        LOGGER.info("Refresh timer started.")
        while True:
            try:
                latest_dump = await self.fetch_latest_dump()
                if latest_dump and latest_dump != BaseHandler.db_cache.dbchange.get('exported'):
                    LOGGER.info("New dump found: %s.", latest_dump)
                    await self._refresh_cache()
            except requests.exceptions.RequestException:
                LOGGER.exception("Unable to connect to reposcan API: ")
            except:  # noqa pylint: disable=bare-except
                LOGGER.exception("Refresh timer error occured: ")
            await asyncio.sleep(REFRESH_CHECK_INTERVAL)

    @staticmethod
    async def fetch_latest_dump():
        """Method fetches latest dump from reposcan"""
        resp = requests.get(f"{CFG.reposcan_url}/{LATEST_DUMP_ENDPOINT}", verify=CFG.tls_ca_path, timeout=10)
        return resp.text


def load_cache_to_apis():
    """Reload cache in APIs."""
    BaseHandler.updates_api = UpdatesAPI(BaseHandler.db_cache)
    BaseHandler.repo_api = RepoAPI(BaseHandler.db_cache)
    BaseHandler.cve_api = CveAPI(BaseHandler.db_cache)
    BaseHandler.errata_api = ErrataAPI(BaseHandler.db_cache)
    BaseHandler.packages_api = PackagesAPI(BaseHandler.db_cache)
    BaseHandler.pkglist_api = PkgListAPI(BaseHandler.db_cache)
    BaseHandler.pkgtree_api = PkgtreeAPI(BaseHandler.db_cache)
    BaseHandler.vulnerabilities_api = VulnerabilitiesAPI(BaseHandler.db_cache, BaseHandler.updates_api)
    BaseHandler.patches_api = PatchesAPI(BaseHandler.db_cache, BaseHandler.updates_api)
    BaseHandler.dbchange_api = DBChange(BaseHandler.db_cache)
    BaseHandler.srpm_pkg_names_api = SRPMPkgNamesAPI(BaseHandler.db_cache)
    BaseHandler.rpm_pkg_names_api = RPMPkgNamesAPI(BaseHandler.db_cache)


def create_app(specs):
    """Create VmaaS application and servers"""
    # pylint: disable=too-many-statements
    init_logging()
    LOGGER.info("Starting (version %s).", VMAAS_VERSION)

    app = connexion.AsyncApp(__name__,
                             swagger_ui_options=connexion.options.SwaggerUIOptions(swagger_ui=True))

    for route, spec in specs.items():
        app.add_api(spec, resolver=connexion.RestyResolver('app'),
                    validate_responses=False,
                    strict_validation=False,
                    base_path=route,
                    pass_context_arg_name='request',
                    arguments={'vmaas_version': VMAAS_VERSION})

    app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_headers=["Content-Type"], allow_methods=["GET", "OPTIONS", "POST"])
    if GZIP_RESPONSE_ENABLE:
        app.add_middleware(GZipMiddleware, minimum_size=1, compresslevel=GZIP_COMPRESS_LEVEL)
    app.add_middleware(ErrorHandlerMiddleware)
    app.add_middleware(TimingLoggingMiddleware, position=connexion.middleware.MiddlewarePosition.BEFORE_EXCEPTION,
                       vmaas_component="webapp")

    BaseHandler.db_cache = Cache()
    load_cache_to_apis()

    init_refresh_timer()

    return app


def init_refresh_timer():
    """Init refresh timer on main event loop"""
    refresh_timer = RefreshTimer()

    def terminate(*_):
        """Trigger shutdown."""
        LOGGER.info("Signal received, stopping application.")
        asyncio.get_event_loop().call_soon(refresh_timer.stop)

    signals = (signal.SIGHUP, signal.SIGTERM, signal.SIGINT)
    for sig in signals:
        signal.signal(sig, terminate)

    # start refresh timer handling coroutine
    refresh_timer.task = asyncio.get_event_loop().create_task(refresh_timer.run_timer())
