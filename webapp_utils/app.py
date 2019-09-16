#!/usr/bin/env python3
"""
Webapp-utils - API utilities for webapp.
"""
import yaml
import connexion
from connexion import RestyResolver

with open("webapp-utils.yml", "rb") as specfile:
    SPEC = yaml.safe_load(specfile)


def create_app():
    """ Creates the application for webapp utils. """
    utils_app = connexion.App("webapp-utils", options={'swagger_ui': False,
                                                       'openapi_spec_path': 'openapi.json'})
    utils_app.add_api(SPEC,
                      resolver=RestyResolver('api'),
                      validate_responses=True,
                      strict_validation=True)

    @utils_app.app.after_request
    def set_default_headers(response): # pylint: disable=unused-variable
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Access-Control-Allow-Headers, \
            Authorization, X-Requested-With, x-rh-identity"
        response.headers["Access-Control-Allow-Methods"] = "GET, OPTIONS, PATCH, POST"

        return response

    return utils_app

application = create_app() # pylint: disable=invalid-name

if __name__ == "__main__":
    application.run(host='0.0.0.0', port=8083)
