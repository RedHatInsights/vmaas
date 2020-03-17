"""
Elasticsearch handler class.
"""
import os

from elasticsearch_dsl import connections

INDEXER_HOST = os.getenv("INDEXER_HOST", "localhost")
INDEXER_PORT = int(os.getenv("INDEXER_PORT", "9200"))

class EsHandler:
    es_host = None
    es_port = None

    """ Class for handling connection to elasticsearch. """
    @classmethod
    def get_connection(cls):
        """Create connection object to ES."""
        return connections.create_connection(hosts=[f"{cls.es_host}:{cls.es_port}"])

    @classmethod
    def init_es(cls):
        """ Init es connection parameters. """
        cls.es_host = os.getenv("INDEXER_HOST", "localhost")
        cls.es_port = int(os.getenv("INDEXER_PORT", "9200"))
