"""
Common and utility functions/classes for vulnerability-manager
"""
import csv
from io import StringIO
import json
from math import floor
import os
from distutils.util import strtobool  # pylint: disable=import-error, no-name-in-module
import requests

from flask import Response, request, Request
from prometheus_client import Counter

from common.logging import get_logger
from mnm import FAILED_AUTH, FAILED_WEBSOCK

LOGGER = get_logger(__name__)

DEFAULT_ROUTE = "%s/%s" % (os.environ.get('PATH_PREFIX', "/api"),
                           os.environ.get('APP_NAME', "vmaas"))
IDENTITY_HEADER = "x-rh-identity"
DEFAULT_PAGE_SIZE = 25
READ_ONLY_MODE = strtobool(os.environ.get('READ_ONLY_MODE', 'FALSE'))
DEFAULT_BUSINESS_RISK = 'Not Defined'
DEFAULT_AUTHORIZED_API_ORG = "RedHatInsights"

LOGGER.info("Access URL: %s", DEFAULT_ROUTE)


class InvalidArgumentException(Exception):
    """Illegal arguments for pagination/filtering/sorting"""


class ApplicationException(Exception):
    """General exception in the application"""

    def __init__(self, message, status_code):
        self.message = message
        self.status_code = status_code
        super().__init__()

    def format_exception(self):
        """Formats error message to desired format"""
        if isinstance(self.message, dict):
            return self.message, self.status_code
        return Request.format_exception(self.message, self.status_code)


class MissingEntitlementException(Exception):
    """smart management entitlement is missing"""


class InternalOnlyException(Exception):
    """function is available only for internal users"""


class ReadOnlyModeException(Exception):
    """manager is running in read-only mode"""


def basic_auth(username, password, required_scopes=None):  # pylint: disable=unused-argument
    """
    Basic auth is done on 3scale level.
    """
    raise MissingEntitlementException



def forbidden_missing_entitlement(exception):  # pylint: disable=unused-argument
    """Override default connexion 401 coming from auth() with 403"""
    return Response(response=json.dumps({'errors': [{'detail': 'smart_management entitlement is missing',
                                                     'status': '403'}]}),
                    status=403, mimetype='application/vnd.api+json')


def forbidden_internal_only(exception):  # pylint: disable=unused-argument
    """Override default connexion 401 coming from auth() with 403"""
    return Response(response=json.dumps({'errors': [{'detail': 'api is available for internal users only',
                                                     'status': '403'}]}),
                    status=403, mimetype='application/vnd.api+json')


class Request:
    """general class for processing requests"""

    _endpoint_name = None

    @staticmethod
    def _check_int_arg(kwargs, key, dflt, zero_allowed=False):
        val = kwargs.get(key, dflt)
        if val < 0 or (val == 0 and not zero_allowed):
            raise ApplicationException("Requested %s out of range: %s" % (key, val), 400)
        return val

    @staticmethod
    def _check_read_only_mode():
        if READ_ONLY_MODE:
            raise ReadOnlyModeException("Service is running in read-only mode. Please try again later.")

    @staticmethod
    def _format_data(output_data_format, data_list):
        if output_data_format == "csv":
            output = StringIO()
            if data_list:
                # create list of columns - type, id and all keys from attributes
                fields = ["type", "id"]
                fields.extend(data_list[0]["attributes"].keys())
                writer = csv.DictWriter(output, fields)
                writer.writeheader()
                for item in data_list:
                    # create flat dictionary (type, id + values from attributes) and write it
                    writer.writerow({field: item.get(field) or item["attributes"].get(field) for field in fields})
            return output.getvalue()
        return data_list

    @classmethod
    def _parse_list_arguments(cls, kwargs):
        # We may get limit/offset, or page/page_size, or both
        # limit/offset 'wins', if it's set
        # page/page_size defaults to 0/DEFAULT_PAGE_SIZE and limit/offset to DEFAULT_PAGE_SIZE if *neither* are set
        # regardless, make sure limit/offset and page/page_size a) both exist, and b) are consistent, before we leave
        offset_set = kwargs.get('offset', '') or kwargs.get('limit', '')
        page_set = kwargs.get('page', '') or kwargs.get('page_size', '')

        if offset_set:
            limit = cls._check_int_arg(kwargs, "limit", DEFAULT_PAGE_SIZE)
            offset = cls._check_int_arg(kwargs, "offset", 0, True)
            page = floor(offset / limit) + 1
            page_size = limit
        elif page_set:
            page = cls._check_int_arg(kwargs, "page", 1)
            page_size = cls._check_int_arg(kwargs, "page_size", DEFAULT_PAGE_SIZE)
            limit = page_size
            offset = (page - 1) * page_size
        else:
            page = 1
            offset = 0
            page_size = DEFAULT_PAGE_SIZE
            limit = DEFAULT_PAGE_SIZE

        data_format = kwargs.get("data_format", "json")
        if data_format not in ["json", "csv"]:
            raise InvalidArgumentException("Invalid data format: %s" % kwargs.get("data_format", None))

        return {
            "filter": kwargs.get("filter", None),
            "sort": kwargs.get("sort", None),
            "page": page,
            "page_size": page_size,
            "limit": limit,
            "offset": offset,
            "data_format": data_format
        }

    @staticmethod
    def validate(github_token):
        """Validate github token, method called by connexion based on x-bearerInfoFunc"""
        if Request.is_authorized():
            return {'scopes': github_token}
        return None

    @staticmethod
    def is_authorized():
        """Authorization check routine

            only requests from the localhost are allowed w/o authorization token,
            otherwise, GitHub authorization token is required
        """

        host_request = request.host.split(':')[0]

        if host_request in ('localhost', '127.0.0.1'):
            return True

        github_token = request.headers.get('Authorization', None)
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

        authorized_org = os.getenv('AUTHORIZED_API_ORG', DEFAULT_AUTHORIZED_API_ORG)

        for org_info in orgs_response.json():
            if org_info['login'] == authorized_org:
                request_str = str(request)
                LOGGER.warning("User %s (id %s) got an access to API: %s", github_user_login,
                               user_info_response.json()['id'], request_str)
                return True

        FAILED_AUTH.inc()
        LOGGER.warning("User %s does not belong to %s organization", authorized_org, github_user_login)
        return False

    @staticmethod
    def format_exception(text, status_code):
        """Formats error message to desired format"""
        return {"errors": [{"status": str(status_code), "detail": text}]}, status_code

    @staticmethod
    def _parse_arguments(kwargs, argv):
        """
        Utility method for getting parameters from request which come as string
        and their conversion to a object we'd like to have.
        Expects array of {'arg_name' : some_str, 'convert_func' : e.g. float, int}
        Returns dict of values if succeeds, throws exception in case of fail
        """
        retval = {}
        errors = []
        for arg in argv:
            retval[arg['arg_name']] = kwargs.get(arg['arg_name'], None)
            if retval[arg['arg_name']]:
                try:
                    if arg['convert_func'] is not None:
                        retval[arg['arg_name']] = arg['convert_func'](retval[arg['arg_name']])
                except ValueError:
                    errors.append({'status': '400',
                                   'detail': 'Error in argument %s: %s' % (arg['arg_name'], retval[arg['arg_name']])})
        if errors:
            raise ApplicationException({'errors': errors}, 400)
        return retval


class GetRequest(Request):
    """general class for processing GET requests"""

    @classmethod
    def get(cls, **kwargs):
        """Answer GET request"""
        #REQUEST_COUNTS.labels('get', cls._endpoint_name).inc()
        try:
            return cls.handle_get(**kwargs)
        except ApplicationException as exc:
            return exc.format_exception()
        except InvalidArgumentException as exc:
            return cls.format_exception(str(exc), 400)
        except Exception:  # pylint: disable=broad-except
            LOGGER.exception('Unhandled exception: ')
            return cls.format_exception('Internal server error', 500)

    @classmethod
    def handle_get(cls, **kwargs):  # pragma: no cover
        """To be implemented in child classes"""
        raise NotImplementedError


class PatchRequest(Request):
    """general class for processing PATCH requests"""

    @classmethod
    def patch(cls, **kwargs):
        """Answer PATCH request"""
        #REQUEST_COUNTS.labels('patch', cls._endpoint_name).inc()
        try:
            cls._check_read_only_mode()
            return cls.handle_patch(**kwargs)
        except ApplicationException as exc:
            return exc.format_exception()
        except InvalidArgumentException as exc:
            return cls.format_exception(str(exc), 400)
        except ReadOnlyModeException as exc:
            return cls.format_exception(str(exc), 503)
        except Exception:  # pylint: disable=broad-except
            LOGGER.exception('Unhandled exception: ')
            return cls.format_exception('Internal server error', 500)

    @classmethod
    def handle_patch(cls, **kwargs):  # pragma: no cover
        """To be implemented in child classes"""
        raise NotImplementedError


class PostRequest(Request):
    """general class for processing POST requests"""

    @classmethod
    def post(cls, **kwargs):
        """Answer POST request"""
        #REQUEST_COUNTS.labels('post', cls._endpoint_name).inc()
        try:
            cls._check_read_only_mode()
            return cls.handle_post(**kwargs)
        except ApplicationException as exc:
            return exc.format_exception()
        except InvalidArgumentException as exc:
            return cls.format_exception(str(exc), 400)
        except ReadOnlyModeException as exc:
            return cls.format_exception(str(exc), 503)
        except Exception:  # pylint: disable=broad-except
            LOGGER.exception('Unhandled exception: ')
            return cls.format_exception('Internal server error', 500), 500

    @classmethod
    def handle_post(cls, **kwargs):  # pragma: no cover
        """To be implemented in child classes"""
        raise NotImplementedError


class PutRequest(Request):
    """general class for processing PUT requests"""

    @classmethod
    def put(cls, **kwargs):
        """Answer PUT request"""
        #REQUEST_COUNTS.labels('put', cls._endpoint_name).inc()
        try:
            cls._check_read_only_mode()
            return cls.handle_put(**kwargs)
        except ApplicationException as exc:
            return exc.format_exception()
        except InvalidArgumentException as exc:
            return cls.format_exception(str(exc), 400)
        except ReadOnlyModeException as exc:
            return cls.format_exception(str(exc), 503)
        except Exception:  # pylint: disable=broad-except
            LOGGER.exception('Unhandled exception: ')
            return cls.format_exception('Internal server error', 500)

    @classmethod
    def handle_put(cls, **kwargs):  # pragma: no cover
        """To be implemented in child classes"""
        raise NotImplementedError


class DeleteRequest(Request):
    """general class for processing DELETE requests"""

    @classmethod
    def delete(cls, **kwargs):
        """Answer DELETE request"""
        #REQUEST_COUNTS.labels('delete', cls._endpoint_name).inc()
        try:
            cls._check_read_only_mode()
            return cls.handle_delete(**kwargs)
        except ApplicationException as exc:
            return exc.format_exception()
        except InvalidArgumentException as exc:
            return cls.format_exception(str(exc), 400)
        except ReadOnlyModeException as exc:
            return cls.format_exception(str(exc), 503)
        except Exception:  # pylint: disable=broad-except
            LOGGER.exception('Unhandled exception: ')
            return cls.format_exception('Internal server error', 500)

    @classmethod
    def handle_delete(cls, **kwargs):  # pragma: no cover
        """To be implemented in child classes"""
        raise NotImplementedError


def parse_int_list(input_str):
    """Function to parse string with ints to list, e.g. '1,2,3' -> [1,2,3]"""
    return [int(part) for part in input_str.split(",")]
