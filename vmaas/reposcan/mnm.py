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

ADMIN_REQUESTS = Counter('vmaas_reposcan_admin_invocations', 'Number of calls on admin API')
FAILED_AUTH = Counter('vmaas_reposcan_failed_auth_attempts', '# of failed authentication attempts')
FAILED_WEBSOCK = Counter('vmaas_reposcan_websocket_errors', '# of websocket-cnx errors')

FAILED_CVEMAP = Counter('vmaas_reposcan_failed_cvemap_reads', '# of failures attempting to read/parse Red Hat CVE data')
FAILED_CPE_METADATA = Counter('vmaas_reposcan_failed_cpe_reads',
                              '# of failures attempting to read/parse Red Hat CPE metadata')

FAILED_REPOMD = Counter('vmaas_reposcan_failed_repo_metadata', '# of failed repo-metadata-download attempts')
FAILED_REPO = Counter('vmaas_reposcan_failed_repository', '# of failed repo-download attempts')
FAILED_REPO_WITH_HTTP_CODE = Counter('vmaas_reposcan_failed_repository_download_with_code',
                                     '# of failed repo-download attempts with http code', ['http_code'])

FAILED_IMPORT_REPO = Counter('vmaas_reposcan_failed_repository_import', '# of failed repo-import/update attempts')
FAILED_IMPORT_CVE = Counter('vmaas_reposcan_failed_cve_import', '# of failed cve-import attempts')
FAILED_UPDATE_CVE = Counter('vmaas_reposcan_failed_cve_update', '# of failed cve-update attempts')
FAILED_IMPORT_CPE = Counter('vmaas_reposcan_failed_cpe_import', '# of failed cpe-import attempts')
FAILED_UPDATE_CPE = Counter('vmaas_reposcan_failed_cpe_update', '# of failed cpe-update attempts')

OVAL_FAILED_DOWNLOAD = Counter('vmaas_reposcan_failed_oval_download', '# of failed oval-download attempts')
OVAL_DELETED_STREAMS = Counter('vmaas_reposcan_oval_deleted_streams', '# of deleted oval streams')

OVAL_FAILED_IMPORT = Counter('vmaas_reposcan_failed_oval_import', '# of failed oval-import attempts')
OVAL_FAILED_UPDATE = Counter('vmaas_reposcan_failed_oval_update', '# of failed oval-update attempts')
OVAL_FAILED_DELETE = Counter('vmaas_reposcan_failed_oval_delete', '# of failed oval-delete attempts')

REPOS_TO_CLEANUP = Gauge('vmaas_reposcan_repos_cleanup', '# of repos to cleanup from DB')
