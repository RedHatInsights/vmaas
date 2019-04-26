"""
Prometheus support
We'd like to use something like @REQUEST_TIME.label(endpoint, get).time() in BaseHandler
to get independent Histogram info for all endpoints - but prometheus doesn't let us do that because label()
doesn't return a Histogram, but rather a LabelWrapper.
"""

from prometheus_client import Histogram, Counter

UPDATES_V1_TIME = Histogram('vmaas_webapp_updates_v1_processing_seconds', 'Time spent processing /v1/updates requests')
UPDATES_V2_TIME = Histogram('vmaas_webapp_updates_v2_processing_seconds', 'Time spent processing /v2/updates requests')
CVES_TIME = Histogram('vmaas_webapp_cve_processing_seconds', 'Time spent processing /cves requests')
REPOS_TIME = Histogram('vmaas_webapp_repos_processing_seconds', 'Time spent processing /repos requests')
ERRATA_TIME = Histogram('vmaas_webapp_errata_processing_seconds', 'Time spent processing /errata requests')
VULNERABILITIES_TIME = Histogram('vmaas_webapp_vulnerabilities_processing_seconds',
                                 'Time spent processing /vulnerabilities requests')
# ...and then we'll build Counter for all-the-things into the BaseHandler
REQUEST_COUNTS = Counter('vmaas_webapp_handler_invocations', 'Number of calls per handler', ['method', 'endpoint'])
UPDATES_CACHE_HITS = Counter('vmaas_updates_cache_hits', 'Number of /updates hot cache hits')
UPDATES_CACHE_MISSES = Counter('vmaas_updates_cache_misses', 'Number of /updates hot cache misses')

HOT_CACHE_INSERTS = Counter('vmaas_hotcache_inserts', 'Number of inserts into cache')
HOT_CACHE_REMOVAL = Counter('vmaas_hotcache_removal', 'Number of times something was removed from hot cache')
