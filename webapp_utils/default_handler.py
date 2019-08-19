"""
Module for /health API endpoint
"""

from base import Request


class GetHealth(Request): # pylint: disable=abstract-method
    """GET to /v1/health"""
    _endpoint_name = r'/v1/health'

    @classmethod
    def handle_get(cls, **kwargs):  # pylint: disable=unused-argument
        """Returns JSON with health of API."""
        return {"health": "OK"}, 200
