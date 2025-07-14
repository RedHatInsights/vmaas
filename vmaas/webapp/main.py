"""Entry point for the application"""
from prometheus_client import start_http_server
from vmaas.webapp.app import create_app, DEFAULT_PATH, DEFAULT_PATH_API

from vmaas.common.config import Config

cfg = Config()
start_http_server(int(cfg.metrics_port))
# pylint: disable=invalid-name
app = create_app({DEFAULT_PATH + "/v1": "webapp.v1.spec.yaml",
                  DEFAULT_PATH + "/v2": "webapp.v2.spec.yaml",
                  DEFAULT_PATH + "/v3": "webapp.v3.spec.yaml",
                  DEFAULT_PATH_API + "/v1": "webapp.v1.spec.yaml",
                  DEFAULT_PATH_API + "/v2": "webapp.v2.spec.yaml",
                  DEFAULT_PATH_API + "/v3": "webapp.v3.spec.yaml",
                  "": "webapp.healthz.spec.yaml"})
