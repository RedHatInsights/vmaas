"""
Fixtures and utility methods for testing flask application using pytest
"""
import base64
import json
from http import HTTPStatus
from flask import Flask
import pytest
from vmaas.reposcan import reposcan
#  from tornado.wsgi import WSGIContainer

URL_BASE = ""

TURNPIKE_IDENTITY = {
    "identity": {
        "associate": {
            "Role": [
                "vulnerability-admins"
            ],
            "email": "jschmoe@redhat.com",
            "givenName": "Joseph",
            "rhatUUID": "01234567-89ab-cdef-0123-456789abcdef",
            "surname": "Schmoe"
        },
        "auth_type": "saml-auth",
        "type": "Associate"
    }
}

RH_TURNPIKE_IDENTITY_HEADER = {
    "x-rh-identity": base64.b64encode(json.dumps(TURNPIKE_IDENTITY).encode("utf-8"))
}


@pytest.mark.usefixtures('client_class')
class FlaskTestCase:
    """Base class for vulnerability engine manager test cases"""

    @pytest.fixture
    def app(self):
        """Fixture for the application"""
        connexion_app = reposcan.create_app({reposcan.DEFAULT_PATH + "/v1": "reposcan.spec.yaml",
                                             reposcan.DEFAULT_PATH_API + "/v1": "reposcan.spec.yaml",
                                             "": "reposcan.healthz.spec.yaml"})
        return Flask(connexion_app)

    def fetch(self, path, **kwargs):
        """Fetch method for vulnerability API."""
        path = "{}/{}".format(URL_BASE, path.lstrip("/"))
        headers = kwargs.get("headers") or {}
        headers.update(RH_TURNPIKE_IDENTITY_HEADER)
        kwargs["headers"] = headers
        if 'data' in kwargs or 'json' in kwargs:
            headers.update({'Content-type': 'application/json'})
        method = kwargs.get('method', 'get')
        if method.upper() == 'PATCH':
            response = self.client.patch(path, **kwargs)  # pylint: disable=no-member
        elif method.upper() == 'POST':
            response = self.client.post(path, **kwargs)  # pylint: disable=no-member
        elif method.upper() == 'PUT':
            response = self.client.put(path, **kwargs)  # pylint: disable=no-member
        elif method.upper() == 'DELETE':
            response = self.client.delete(path, **kwargs)  # pylint: disable=no-member
        else:
            response = self.client.get(path, **kwargs)  # pylint: disable=no-member
        return FlaskTestResponse(response, method.upper(), path)

    def raw_get(self, path, **kwargs):
        """Raw get to an URI without headers"""
        response = self.client.get(path, **kwargs)  # pylint: disable=no-member
        return FlaskTestResponse(response, "GET", path)

    # pylint: disable=invalid-name
    @staticmethod
    def assertEqual(first, second):
        """Simple assertion. Added to conform to interface from TestCase"""
        assert str(first) == str(second), f"{str(first)} != {str(second)}"

    # pylint: disable=invalid-name
    @staticmethod
    def assertTrue(val):
        """Simple assertion. Added to conform to interface from TestCase"""
        assert val, f"{val} is not True-ish"


class FlaskTestResponse:
    """API response representation."""

    def __init__(self, response, method, path):
        self.raw = response
        # pylint: disable=no-value-for-parameter
        self.status = HTTPStatus(response.status_code)
        self.body = self.load(response)
        self.method = method
        self.path = path

    @staticmethod
    def load(response):
        """Loads the response content."""
        parsed = None
        try:
            parsed = json.loads(response.data)
        # pylint: disable=broad-except
        except Exception:
            pass

        if not parsed and response.data:
            parsed = str(response.data, "utf-8")

        return parsed

    # pylint: disable=invalid-name
    @property
    def ok(self):
        """Checks if response has return code that indicates success."""
        if self.raw and self.raw.status_code >= 200 and self.raw.status_code < 400:
            return True
        return False

    def check_response(self, status_code=None, validate=True):
        """Asserts that the response HTTP status code and content is as expected."""
        if status_code:
            if self.raw.status_code != status_code:
                raise AssertionError(
                    "Expected status code {}, got {}".format(status_code, self.raw.status_code)
                )
        elif not self.ok:
            raise AssertionError("Request failed with {}".format(self.raw.status_code))

        try:
            if self.ok and "errors" in self.body:
                raise AssertionError("Errors returned: {}".format(self.body.errors))
        except TypeError:
            pass

        if validate and self.ok:
            self.validate_schema()

        return self

    def __getattr__(self, name):
        return getattr(self.raw, name)

    def __repr__(self):
        return "<EngineResponse(raw={!r})>".format(self.raw)
