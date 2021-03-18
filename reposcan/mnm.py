"""
Measurement aNd Monitoring - prometheus probes used by reposcan subsystem
"""

from prometheus_client import Counter

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
FAILED_IMPORT_OVAL = Counter('vmaas_reposcan_failed_oval_import', '# of failed oval-import attempts')
