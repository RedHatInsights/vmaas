"""Entry point for the reposcan component"""
from prometheus_client import start_http_server

from vmaas.common.config import Config
from vmaas.reposcan.reposcan import create_app, DEFAULT_PATH, DEFAULT_PATH_API

cfg = Config()
start_http_server(int(cfg.metrics_port))
# pylint: disable=invalid-name
app = create_app({DEFAULT_PATH + "/v1": "reposcan.spec.yaml",
                  DEFAULT_PATH_API + "/v1": "reposcan.spec.yaml",
                  "": "reposcan.healthz.spec.yaml"})
