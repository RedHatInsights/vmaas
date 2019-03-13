"""
Measurement aNd Monitoring - prometheus probes used by reposcan subsystem
"""

from prometheus_client import Counter

FAILED_AUTH = Counter('vmaas_reposcan_failed_auth_attempts', '# of failed authentication attempts')
FAILED_WEBSOCK = Counter('vmaas_reposcan_websocket_errors', '# of websocket-cnx errors')

FAILED_NIST = Counter('vmaas_reposcan_failed_NIST_reads', '# of failures attempting to read/parse NIST CVE data')

FAILED_CVEMAP = Counter('vmaas_reposcan_failed_cvemap_reads', '# of failures attempting to read/parse Red Hat CVE data')

FAILED_REPOMD = Counter('vmaas_reposcan_failed_repo_metadata', '# of failed repo-metadata-download attempts')
FAILED_REPO = Counter('vmaas_reposcan_failed_repository', '# of failed repo-download attempts')
