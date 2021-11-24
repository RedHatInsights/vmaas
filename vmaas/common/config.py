"""
Common VMaaS configuration.
"""
import os
from distutils.util import strtobool

import app_common_python


class Singleton(type):
    """Singleton object."""

    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class BaseConfig:
    """Base configuration, same for clowder and non-clowder."""

    def __init__(self):
        self.postgresql_writer_password = os.getenv(
            "POSTGRESQL_WRITER_PASSWORD", "vmaas_writer_pwd"
        )
        self.postgresql_reader_password = os.getenv(
            "POSTGRESQL_READER_PASSWORD", "vmaas_reader_pwd"
        )
        self.pod_hostname = os.environ.get("HOSTNAME")
        self.is_init_container = strtobool(os.environ.get("INIT_CONTAINER", "false"))
        self.web_port = None
        self.public_port = None
        self.private_port = None
        self.webapp_port = None
        self.metrics_port = None


# pylint: disable=too-many-instance-attributes
class Config(BaseConfig, metaclass=Singleton):
    """VMaaS configuration singleton."""

    def __init__(self):
        super().__init__()
        if app_common_python.isClowderEnabled():
            self.clowder()
        else:
            self.legacy()

    def clowder(self):
        """Configuration from Clowder."""
        cfg = app_common_python.LoadedConfig

        self.db_name = getattr(cfg.database, "name", "")
        self.db_user = getattr(cfg.database, "username", "")
        self.db_pass = getattr(cfg.database, "password", "")
        self.db_host = getattr(cfg.database, "hostname", "")
        self.db_port = getattr(cfg.database, "port", "")
        self.db_ssl_mode = getattr(cfg.database, "sslMode", None)
        self.db_ssl_root_cert_path = cfg.rds_ca() if cfg.database.rdsCa else ""
        self.db_available = bool(self.db_name)

        self.cw_aws_access_key_id = cfg.logging.cloudwatch.accessKeyId
        self.cw_aws_secret_access_key = cfg.logging.cloudwatch.secretAccessKey
        self.cw_aws_region = cfg.logging.cloudwatch.region
        self.cw_aws_log_group = cfg.logging.cloudwatch.logGroup

        self.websocket_url = ""
        self.websocket_host = ""
        self.websocket_port = ""
        self.reposcan_host = ""
        self.reposcan_port = None
        for endpoint in cfg.endpoints:
            if "reposcan" in endpoint.hostname:
                self.reposcan_host = endpoint.hostname
                self.reposcan_port = endpoint.port
        for endpoint in cfg.privateEndpoints:
            if "reposcan" in endpoint.hostname:
                self.remote_dump = f"rsync://{endpoint.hostname}:{endpoint.port}/data/vmaas.db"
            elif "websocket" in endpoint.hostname:
                self.websocket_url = f"ws://{endpoint.hostname}:{endpoint.port}"
                self.websocket_host = endpoint.hostname
                self.websocket_port = endpoint.port

        self.web_port = cfg.webPort
        self.public_port = cfg.publicPort
        self.private_port = cfg.privatePort
        self.metrics_port = cfg.metricsPort

    def legacy(self):
        """Configuration fro environment variables."""
        self.db_available = bool(os.getenv("POSTGRESQL_DATABASE"))
        self.db_name = os.getenv("POSTGRESQL_DATABASE", "vmaas")
        self.db_user = os.getenv("POSTGRESQL_USER", "vmaas_writer")
        self.db_pass = os.getenv("POSTGRESQL_PASSWORD", "vmaas_writer_pwd")
        self.db_host = os.getenv("POSTGRESQL_HOST", "database")
        self.db_port = int(os.getenv("POSTGRESQL_PORT", "5432"))
        self.db_ssl_mode = os.getenv("POSTGRESQL_SSL_MODE", "prefer")
        self.db_ssl_root_cert_path = os.getenv("POSTGRESQL_SSL_ROOT_CERT_PATH", "/opt/rds-ca/rds-cacert")

        self.cw_aws_access_key_id = os.environ.get("CW_AWS_ACCESS_KEY_ID")
        self.cw_aws_secret_access_key = os.environ.get("CW_AWS_SECRET_ACCESS_KEY")
        self.cw_aws_region = os.environ.get("AWS_REGION", "us-east-1")
        self.cw_aws_log_group = os.environ.get("CW_LOG_GROUP", "platform-dev")

        self.websocket_host = os.getenv("WEBSOCKET_HOST", "vmaas_websocket")
        self.websocket_port = "8082"
        self.websocket_url = f"ws://{self.websocket_host}:{self.websocket_port}/"
        self.reposcan_host = os.getenv("REPOSCAN_HOST", "localhost")
        self.reposcan_port = int(os.getenv("REPOSCAN_PORT", "8081"))
        self.webapp_port = "8080"
        self.remote_dump = f"rsync://{self.reposcan_host}:8730/data/vmaas.db"
        self.metrics_port = os.getenv("PROMETHEUS_PORT", "")
