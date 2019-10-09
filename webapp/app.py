#!/usr/bin/env python3
"""
Main web API module
"""

from json import loads
import os
import signal
import sre_constants
import time
import asyncio
import yaml

from jsonschema.exceptions import ValidationError
from prometheus_client import generate_latest
import connexion
from aiohttp import web, ClientSession, WSMsgType, hdrs

from cache import Cache
from cve import CveAPI
from repos import RepoAPI
from updates import UpdatesAPI
from errata import ErrataAPI
from packages import PackagesAPI
from vulnerabilities import VulnerabilitiesAPI
from dbchange import DBChange
from common.logging_utils import init_logging, get_logger
from probes import REQUEST_COUNTS, REQUEST_TIME

# pylint: disable=too-many-lines

VMAAS_VERSION = os.getenv("VMAAS_VERSION", "unknown")
PUBLIC_API_PORT = 8080

WEBSOCKET_RECONNECT_INTERVAL = 60
LOGGER = get_logger(__name__)


class BaseHandler:
    """Base class containing individual repositories"""

    db_cache = None
    updates_api = None
    repo_api = None
    cve_api = None
    errata_api = None
    packages_api = None
    vulnerabilities_api = None
    dbchange_api = None

    @classmethod
    async def get_post_data(cls, request):
        """extract input JSON from POST request"""
        if request.headers.get(hdrs.CONTENT_TYPE, None) == 'application/json':
            return await request.json()
        raise web.HTTPBadRequest(reason="Invalid body")

    @classmethod
    async def handle_request(cls, api_endpoint, api_version, param_name=None, param=None, **kwargs):
        """Takes care of validation of input and execution of request."""
        request = kwargs.get('request', None)
        if request is None:
            raise ValueError('request not provided')

        data = None
        try:
            if request.method == 'POST':
                data = await cls.get_post_data(request)
            else:
                data = {param_name: [param]}
            res = api_endpoint.process_list(api_version, data)
            code = 200
        except web.HTTPError as exc:
            # We cant return the e as response, this is being deprecated in aiohttp
            return web.Response(body=exc.reason, status=exc.status_code, headers=exc.headers)
        except ValidationError as valid_err:
            if valid_err.absolute_path:
                res = '%s : %s' % (valid_err.absolute_path.pop(), valid_err.message)
            else:
                res = '%s' % valid_err.message
            code = 400
        except (ValueError, sre_constants.error) as ex:
            res = repr(ex)
            code = 400
        except Exception as err:  # pylint: disable=broad-except
            err_id = err.__hash__()
            res = 'Internal server error <%s>: please include this error id in bug report.' % err_id
            code = 500
            LOGGER.exception(res)
            LOGGER.error("Input data for <%s>: %s", err_id, data)
        return web.json_response(res, status=code)


class HealthHandler(BaseHandler):
    """Handler class providing health status."""

    @classmethod
    async def get(cls, **kwargs): # pylint: disable=unused-argument
        """Get API status.
           ---
           description: Return API status
           responses:
             200:
               description: Application is alive
        """

        return web.Response(status=200)


class VersionHandler(BaseHandler):
    """Handler class providing app version."""

    @classmethod
    async def get(cls, **kwargs): #pylint: disable=unused-argument
        """Get app version.
           ---
           description: Get version of application
           responses:
             200:
               description: Version of application returned
        """
        return web.Response(body=str(VMAAS_VERSION), status=200)


class DBChangeHandler(BaseHandler):
    """
    Class to return last-updated information from VMaaS DB
    """

    @classmethod
    async def get(cls, **kwargs): #pylint: disable=unused-argument
        """Get last-updated-times for VMaaS DB """
        return web.json_response(cls.dbchange_api.process())


class UpdatesHandlerGet(BaseHandler):
    """Handler for processing /updates GET requests."""

    @classmethod
    async def get(cls, nevra=None, **kwargs):
        """List security updates for single package NEVRA """
        return await cls.handle_request(cls.updates_api, 1, 'package_list', nevra, **kwargs)


class UpdatesHandlerPost(BaseHandler):
    """Handler for processing /updates POST requests."""

    @classmethod
    async def post(cls, **kwargs):
        """List security updates for list of package NEVRAs"""
        return await cls.handle_request(cls.updates_api, 1, **kwargs)


class UpdatesHandlerV2Get(BaseHandler):
    """Handler for processing /updates GET requests."""

    @classmethod
    async def get(cls, nevra=None, **kwargs):
        """List security updates for single package NEVRA """
        return await cls.handle_request(cls.updates_api, 2, 'package_list', nevra, **kwargs)


class UpdatesHandlerV2Post(BaseHandler):
    """Handler for processing /updates POST requests."""

    @classmethod
    async def post(cls, **kwargs):
        """List security updates for list of package NEVRAs"""
        return await cls.handle_request(cls.updates_api, 2, **kwargs)


class CVEHandlerGet(BaseHandler):
    """Handler for processing /cves GET requests."""

    @classmethod
    async def get(cls, cve=None, **kwargs):
        """
        Get details about CVEs. It is possible to use POSIX regular expression as a pattern for CVE names.
        """
        return await cls.handle_request(cls.cve_api, 1, 'cve_list', cve, **kwargs)


class CVEHandlerPost(BaseHandler):
    """Handler for processing /cves POST requests."""

    @classmethod
    async def post(cls, **kwargs):
        """
        Get details about CVEs with additional parameters. As a "cve_list" parameter a complete list of CVE
        names can be provided OR one POSIX regular expression.
        """
        return await cls.handle_request(cls.cve_api, 1, **kwargs)


class ReposHandlerGet(BaseHandler):
    """Handler for processing /repos GET requests."""

    @classmethod
    async def get(cls, repo=None, **kwargs):
        """
        Get details about a repository or repository-expression. It is allowed to use POSIX regular
        expression as a pattern for repository names.
        """
        return await cls.handle_request(cls.repo_api, 1, 'repository_list', repo, **kwargs)


class ReposHandlerPost(BaseHandler):
    """Handler for processing /repos POST requests."""

    @classmethod
    async def post(cls, **kwargs):
        """
        Get details about list of repositories. "repository_list" can be either a list of repository
        names, OR a single POSIX regular expression.
        """
        return await cls.handle_request(cls.repo_api, 1, **kwargs)


class ErrataHandlerGet(BaseHandler):
    """Handler for processing /errata GET requests."""

    @classmethod
    async def get(cls, erratum=None, **kwargs):
        """
        Get details about errata. It is possible to use POSIX regular
        expression as a pattern for errata names.
        """
        return await cls.handle_request(cls.errata_api, 1, 'errata_list', erratum, **kwargs)


class ErrataHandlerPost(BaseHandler):
    """ /errata API handler """

    @classmethod
    async def post(cls, **kwargs):
        """
        Get details about errata with additional parameters. "errata_list"
        parameter can be either a list of errata names OR a single POSIX regular expression.
        """
        return await cls.handle_request(cls.errata_api, 1, **kwargs)


class PackagesHandlerGet(BaseHandler):
    """Handler for processing /packages GET requests."""

    @classmethod
    async def get(cls, nevra=None, **kwargs):
        """Get details about packages."""
        return await cls.handle_request(cls.packages_api, 1, 'package_list', nevra, **kwargs)


class PackagesHandlerPost(BaseHandler):
    """ /packages API handler """

    @classmethod
    async def post(cls, **kwargs):
        """Get details about packages. "package_list" must be a list of"""
        return await cls.handle_request(cls.packages_api, 1, **kwargs)


class VulnerabilitiesHandlerGet(BaseHandler):
    """Handler for processing /vulnerabilities GET requests."""

    @classmethod
    async def get(cls, nevra=None, **kwargs):
        """ List of applicable CVEs for a single package NEVRA
        """
        return await cls.handle_request(cls.vulnerabilities_api, 1, 'package_list', nevra, **kwargs)


class VulnerabilitiesHandlerPost(BaseHandler):
    """Handler for processing /vulnerabilities POST requests."""

    @classmethod
    async def post(cls, **kwargs):
        """List of applicable CVEs to a package list. """
        return await cls.handle_request(cls.vulnerabilities_api, 1, **kwargs)


class Websocket:
    """ main websocket handling class"""
    def __init__(self):
        self.websocket_url = "ws://%s:8082/" % os.getenv("WEBSOCKET_HOST", "vmaas_websocket")
        self.websocket = None
        self.task = None
        self.websocket_response_queue = set()

    def stop(self):
        """Stop vmaas application"""
        if self.websocket is not None:
            self.websocket.close()
            self.websocket = None

        self.task.cancel()
        self.task = None

    @staticmethod
    def _refresh_cache():
        BaseHandler.db_cache.reload()
        use_hot_cache = os.getenv("HOTCACHE_ENABLED", "YES")
        if use_hot_cache.upper() == "YES":
            BaseHandler.updates_api.clear_hot_cache()
        LOGGER.info("Cached data refreshed.")

    async def websocket_loop(self):
        """Main loop for handling websocket connection"""
        async with ClientSession() as session:
            while True:
                async with session.ws_connect(url=self.websocket_url) as socket:
                    LOGGER.info("Connected to: %s", self.websocket_url)
                    self.websocket = socket
                    # subscribe for notifications
                    await self.websocket.send_str("subscribe-webapp")
                    # Re-send queued messages
                    for item in self.websocket_response_queue:
                        await self.websocket.send_str(item)
                    self.websocket_response_queue.clear()

                    # handle websocket messages
                    await self.websocket_msg_handler()
                    self.websocket = None
                    # Reconnection sleep, then, the outer loop will begin again, reconnecting this client
                    await asyncio.sleep(WEBSOCKET_RECONNECT_INTERVAL * 1000)

    async def websocket_msg_handler(self):
        """Handle active websocket connection, returning upon close"""
        async for msg in self.websocket:
            LOGGER.debug("Websocket message: %s, %s", msg.type, msg.data)
            if msg.type in (WSMsgType.CLOSED, WSMsgType.ERROR):
                return None

            if msg.data == 'refresh-cache':
                self._refresh_cache()
                msg = f"refreshed {BaseHandler.db_cache.dbchange['exported']}"
                if self.websocket:
                    self.websocket.send_str(msg)
                else:
                    self.websocket_response_queue.add(msg)
            else:
                LOGGER.warning("Unhandled websocket message %s", msg.data)


def load_cache_to_apis():
    """Reload cache in APIs."""
    BaseHandler.updates_api = UpdatesAPI(BaseHandler.db_cache)
    BaseHandler.repo_api = RepoAPI(BaseHandler.db_cache)
    BaseHandler.cve_api = CveAPI(BaseHandler.db_cache)
    BaseHandler.errata_api = ErrataAPI(BaseHandler.db_cache)
    BaseHandler.packages_api = PackagesAPI(BaseHandler.db_cache)
    BaseHandler.vulnerabilities_api = VulnerabilitiesAPI(BaseHandler.db_cache, BaseHandler.updates_api)
    BaseHandler.dbchange_api = DBChange(BaseHandler.db_cache)


def create_app():
    """Create VmaaS application and servers"""

    init_logging()

    LOGGER.info("Starting (version %s).", VMAAS_VERSION)
    LOGGER.info('Hotcache enabled: %s', os.getenv("HOTCACHE_ENABLED", "YES"))

    with open('webapp.spec.yaml', 'rb') as specfile:
        SPEC = yaml.safe_load(specfile)  # pylint: disable=invalid-name

    @web.middleware
    async def timing_middleware(request, handler, **kwargs):
        """ Middleware that handles timing of requests"""
        start_time = time.time()
        if asyncio.iscoroutinefunction(handler):
            res = await handler(request, **kwargs)
        else:
            res = handler(request, **kwargs)

        duration = (time.time() - start_time)
        # (0)  /(1) /(2) /(3)
        #     /api /v1  /updates
        const_path = '/'.join(request.path.split('/')[:4])
        REQUEST_TIME.labels(request.method, const_path).observe(duration)
        REQUEST_COUNTS.labels(request.method, const_path, res.status).inc()

        return res

    @web.middleware
    async def error_formater(request, handler, **kwargs):
        #pylint: disable=broad-except
        def build_error(detail, status):
            errors = {"detail": detail, "status": status}
            return {"errors": [errors]}

        res = await handler(request, **kwargs)

        try:
            if res.status >= 400:
                original_error = loads(res.body)
                better_error = build_error(original_error["detail"], original_error["status"])
                return web.json_response(better_error, status=res.status)
            return res
        except TypeError: # The error response is not made by connexion
            better_error = build_error(original_error, res.status)
            return web.json_response(better_error, status=res.status)
        except Exception as _:
            LOGGER.exception(_)
            return web.json_response(build_error("Internal server error", 500), status=500)


    app = connexion.AioHttpApp(__name__, options={
        'swagger_ui': True,
        'openapi_spec_path': '/v1/apispec',
        'middlewares': [error_formater,
                        timing_middleware]
    })

    def metrics(request, **kwargs): #pylint: disable=unused-argument
        """Provide current prometheus metrics"""
        # /metrics API shouldn't be visible in the API documentation,
        # hence it's added here in the create_app step
        return web.Response(text=generate_latest().decode('utf-8'))

    async def on_prepare(request, response): #pylint: disable=unused-argument
        """Hook for preparing new responses"""
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type"

    app.app.on_response_prepare.append(on_prepare)
    app.app.router.add_get("/metrics", metrics)

    app.add_api(SPEC, resolver=connexion.RestyResolver('app'),
                validate_responses=False,
                strict_validation=False,
                base_path='/api',
                pass_context_arg_name='request'
                )

    BaseHandler.db_cache = Cache()
    load_cache_to_apis()

    return app


def init_websocket():
    """Init websocket conenction on main event loop"""
    socket = Websocket()

    def terminate(*_):
        """Trigger shutdown."""
        LOGGER.info("Signal received, stopping application.")
        asyncio.get_event_loop().call_soon(socket.stop)

    signals = (signal.SIGHUP, signal.SIGTERM, signal.SIGINT)
    for sig in signals:
        signal.signal(sig, terminate)

    # start websocket handling coroutine
    socket.task = asyncio.get_event_loop().create_task(socket.websocket_loop())
