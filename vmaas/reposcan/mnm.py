"""
Measurement aNd Monitoring - prometheus probes used by reposcan subsystem
"""

import os

from prometheus_client import Counter, Gauge, CollectorRegistry, multiprocess

from vmaas.common.config import Config

CFG = Config()

os.makedirs(CFG.prometheus_multiproc_dir, exist_ok=True)
REGISTRY = CollectorRegistry()
multiprocess.MultiProcessCollector(REGISTRY)

ADMIN_REQUESTS = Counter('vmaas_reposcan_admin_invocations', 'Number of calls on admin API', registry=REGISTRY)
FAILED_AUTH = Counter('vmaas_reposcan_failed_auth_attempts', '# of failed authentication attempts', registry=REGISTRY)
FAILED_WEBSOCK = Counter('vmaas_reposcan_websocket_errors', '# of websocket-cnx errors', registry=REGISTRY)

FAILED_CVEMAP = Counter('vmaas_reposcan_failed_cvemap_reads', '# of failures attempting to read/parse Red Hat CVE data', registry=REGISTRY)
FAILED_CPE_METADATA = Counter('vmaas_reposcan_failed_cpe_reads',
                              '# of failures attempting to read/parse Red Hat CPE metadata', registry=REGISTRY)

FAILED_REPOMD = Counter('vmaas_reposcan_failed_repo_metadata', '# of failed repo-metadata-download attempts', registry=REGISTRY)
FAILED_REPO = Counter('vmaas_reposcan_failed_repository', '# of failed repo-download attempts', registry=REGISTRY)
FAILED_REPO_WITH_HTTP_CODE = Counter('vmaas_reposcan_failed_repository_download_with_code',
                                     '# of failed repo-download attempts with http code', ['http_code'], registry=REGISTRY)

FAILED_METADATA_CHECKSUM = Counter('vmaas_reposcan_failed_metadata_checksum', '# of failed metadata checksum verifications', registry=REGISTRY)

FAILED_IMPORT_REPO = Counter('vmaas_reposcan_failed_repository_import', '# of failed repo-import/update attempts', registry=REGISTRY)
FAILED_IMPORT_CVE = Counter('vmaas_reposcan_failed_cve_import', '# of failed cve-import attempts', registry=REGISTRY)
FAILED_UPDATE_CVE = Counter('vmaas_reposcan_failed_cve_update', '# of failed cve-update attempts', registry=REGISTRY)
FAILED_IMPORT_CPE = Counter('vmaas_reposcan_failed_cpe_import', '# of failed cpe-import attempts', registry=REGISTRY)
FAILED_UPDATE_CPE = Counter('vmaas_reposcan_failed_cpe_update', '# of failed cpe-update attempts', registry=REGISTRY)

CSAF_FAILED_DOWNLOAD = Counter('vmaas_reposcan_failed_csaf_download', '# of failed csaf-download attempts', registry=REGISTRY)
CSAF_FAILED_DELETE = Counter('vmaas_reposcan_failed_csaf_delete', '# of failed csaf-delete attempts', registry=REGISTRY)
CSAF_FAILED_IMPORT = Counter('vmaas_reposcan_failed_csaf_import', '# of failed csaf-import attempts', registry=REGISTRY)
CSAF_FAILED_UPDATE = Counter('vmaas_reposcan_failed_csaf_update', '# of failed csaf-update attempts', registry=REGISTRY)

RELEASE_FAILED_IMPORT = Counter('vmaas_reposcan_failed_release_import', '# of failed release-import attempts', registry=REGISTRY)
RELEASE_GRAPH_FAILED_IMPORT = Counter('vmaas_reposcan_failed_release_graph_import', '# of failed release-import attempts', registry=REGISTRY)

REPOS_TO_CLEANUP = Gauge('vmaas_reposcan_repos_cleanup', '# of repos to cleanup from DB', registry=REGISTRY)

CERT_EXPIRATION_WARNING = Gauge('vmaas_reposcan_certificate_expiration_days', 'Days until CDN certificate expiration', ['cert_name'], registry=REGISTRY)
