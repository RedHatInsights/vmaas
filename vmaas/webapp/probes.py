"""
Prometheus support
We'd like to use something like @REQUEST_TIME.label(endpoint, get).time() in BaseHandler
to get independent Histogram info for all endpoints - but prometheus doesn't let us do that because label()
doesn't return a Histogram, but rather a LabelWrapper.
"""

from prometheus_client import Histogram, Counter

REQUEST_TIME = Histogram('vmaas_webapp_processing_seconds', 'Time spent processing request', ['method', 'path'])

# ...and then we'll build Counter for all-the-things into the BaseHandler
REQUEST_COUNTS = Counter('vmaas_webapp_handler_invocations', 'Number of calls per handler',
                         ['method', 'path', 'status'])
