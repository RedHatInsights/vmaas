"""
Common VMaaS configuration.
"""
import os

import app_common_python

from vmaas.common.strtobool import strtobool


class Singleton(type):
    """Singleton object."""

    _instances: dict = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


# pylint: disable=too-many-instance-attributes
class BaseConfig:
    """Base configuration, same for clowder and non-clowder."""

    def __init__(self) -> None:
        self.postgresql_writer_password = os.getenv(
            "POSTGRESQL_WRITER_PASSWORD", "vmaas_writer_pwd"
        )
        self.postgresql_reader_password = os.getenv(
            "POSTGRESQL_READER_PASSWORD", "vmaas_reader_pwd"
        )
        self.pod_hostname = os.environ.get("HOSTNAME")
        self.is_init_container = strtobool(os.environ.get("INIT_CONTAINER", "false"))
        self.is_test = strtobool(os.environ.get("IS_TEST", "false"))
        self.tls_ca_path = None
        self.public_port = None
        self.private_port = None
        self.metrics_port = None

        self.oval_unfixed_eval_enabled = strtobool(os.getenv("OVAL_UNFIXED_EVAL_ENABLED", "TRUE"))
        self.prometheus_multiproc_dir = os.getenv("PROMETHEUS_MULTIPROC_DIR", "/tmp/prometheus_multiproc_dir")

        self.pg_max_stack_depth = os.getenv("PG_MAX_STACK_DEPTH", "")
        self.csaf_product_status_list = os.getenv("CSAF_PRODUCT_STATUS_LIST", "known_affected,fixed").split(",")


# pylint: disable=too-many-instance-attributes
class Config(BaseConfig, metaclass=Singleton):
    """VMaaS configuration singleton."""

    def __init__(self) -> None:
        if not app_common_python.isClowderEnabled():
            raise EnvironmentError("Missing Clowder config.")

        super().__init__()
        self._cfg = app_common_python.LoadedConfig
        self.clowder()

    def clowder(self) -> None:
        """Configuration from Clowder."""
        self.db_name = getattr(self._cfg.database, "name", "")
        self.db_user = getattr(self._cfg.database, "username", "")
        self.db_pass = getattr(self._cfg.database, "password", "")
        self.db_host = getattr(self._cfg.database, "hostname", "")
        self.db_port = getattr(self._cfg.database, "port", "")
        self.db_ssl_mode = getattr(self._cfg.database, "sslMode", None)
        self.db_ssl_root_cert_path = self._cfg.rds_ca() if self._cfg.database.rdsCa else ""
        self.db_available = bool(self.db_name)

        self.cw_aws_access_key_id = self._cfg.logging.cloudwatch.accessKeyId
        self.cw_aws_secret_access_key = self._cfg.logging.cloudwatch.secretAccessKey
        self.cw_aws_region = self._cfg.logging.cloudwatch.region
        self.cw_aws_log_group = self._cfg.logging.cloudwatch.logGroup

        self.tls_ca_path = self._cfg.tlsCAPath
        self.reposcan_url = ""
        self.webapp_go_url = ""
        for endpoint in self._cfg.endpoints:
            if "reposcan" in endpoint.hostname:
                self.reposcan_url = self._build_url(endpoint)
        for endpoint in self._cfg.privateEndpoints:
            if "reposcan" in endpoint.hostname:
                self.remote_dump = f"{self._build_url(endpoint)}/vmaas.db"
            if "webapp" in endpoint.hostname and "go" in endpoint.hostname:
                self.webapp_go_url = self._build_url(endpoint)

        self.public_port = self._cfg.publicPort
        self.private_port = self._cfg.privatePort
        self.metrics_port = self._cfg.metricsPort

    def _build_url(self, endpoint: object, scheme="http") -> str:
        scheme = f"{scheme}s" if self.tls_ca_path else scheme
        port = endpoint.tlsPort if self.tls_ca_path else endpoint.port
        return f"{scheme}://{endpoint.hostname}:{port}"
