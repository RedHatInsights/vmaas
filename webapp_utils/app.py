#!/usr/bin/env python3
"""
Webapp-utils - API utilities for webapp.
"""
import connexion
from connexion import RestyResolver

from common.constants import VMAAS_VERSION

DEFAULT_ROUTE = "/api"


def create_app(specs):
    """ Creates the application for webapp utils. """
    utils_app = connexion.App("webapp-utils", options={'swagger_ui': True,
                                                       'openapi_spec_path': '/openapi.json'})

    for route, spec in specs.items():
        utils_app.add_api(spec,
                          resolver=RestyResolver('app'),
                          validate_responses=True,
                          strict_validation=True,
                          base_path=route,
                          arguments={"vmaas_version": VMAAS_VERSION})

    @utils_app.app.after_request
    def set_default_headers(response): # pylint: disable=unused-variable
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Access-Control-Allow-Headers, \
            Authorization, X-Requested-With, x-rh-identity"
        response.headers["Access-Control-Allow-Methods"] = "GET, OPTIONS, PATCH, POST"

        return response

    return utils_app

application = create_app({DEFAULT_ROUTE: "webapp-utils.yml",  # pylint: disable=invalid-name
                          "": "webapp-utils-healthz.yml"})

if __name__ == "__main__":
    application.run(host='0.0.0.0', port=8083)
