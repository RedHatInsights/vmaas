"""
Module for /health API endpoint
"""

from base import Request


class GetHealth(Request):
    """GET to /v1/health"""
    _endpoint_name = r'/v1/health'

    @classmethod
    def handle_get(cls, **kwargs):
        """Returns JSON with health of API."""
        return {"health": "OK"}, 200

    @classmethod
    def handle_post(cls, **kwargs):
        raise NotImplementedError
