"""
Importer module for importing data to elastic.
"""
from logging import ERROR

from elasticsearch_dsl import Index
from elasticsearch import logger
from elasticsearch.helpers import bulk as _bulk
from elasticsearch.exceptions import NotFoundError
from database.database_handler import NamedCursor

from common.logging_utils import init_logging, get_logger
import common.webapp_utils as utils
from common.documents.nevra import Nevra, PACKAGES_INDEX

LOGGER = get_logger(__name__)

class Importer:
    """ Importer class which does the importing to the elastic. """

    es_connection = None
    db_instance = None

    def __init__(self, db_instance, es_connection):
        init_logging()
        # Set the ERROR logging for ElasticSearch module
        # to not propagate caught exceptions
        logger.setLevel(ERROR)
        self.es_connection = es_connection
        self.db_instance = db_instance

    def _named_cursor(self, name="default"):
        """ Shorter function to init cursor. """
        return NamedCursor(self.db_instance, name)

    def clear_elastic(self):
        """ Clear elastic index. """
        Index("*", using=self.es_connection).delete()

    def init_elastic(self):
        """ Initialize index. """
        LOGGER.info("Clearing & initializing elastic.")
        self.clear_elastic()
        PACKAGES_INDEX.create(using=self.es_connection)

    def check_elastic(self):
        """ Check if elastic is running. """
        does_exist = True

        try:
            PACKAGES_INDEX.search(using=self.es_connection)
        except NotFoundError:
            does_exist = False

        return does_exist

    def bulk(self, action, stats_only=False):
        """ Bulk insert override. """
        return _bulk(self.es_connection, action, stats_only)

    def _format_src_pkg(self, src_pkg_id):
        """ Format source package of package. """
        if src_pkg_id:
            with self._named_cursor(name="import_src_pkg") as cursor:
                cursor.execute(""" SELECT n.name, evr.epoch, evr.version, evr.release,
                                   a.name
                                   FROM package AS p
                                   LEFT JOIN evr ON p.evr_id = evr.id
                                   LEFT JOIN arch AS a ON p.arch_id = a.id
                                   LEFT JOIN package_name AS n ON p.name_id = n.id
                                   WHERE p.id = %s """ % src_pkg_id)

                src_nevra = cursor.fetchone()
                return utils.join_packagename(*src_nevra)

        return None

    def _format_repo_label(self, pkg_id):
        """ Format repository label by given package. """
        if pkg_id:
            repos = []
            with self._named_cursor(name="import_pkg_repo") as cursor:
                cursor.execute(""" SELECT cs.label
                                   FROM pkg_repo AS pr
                                   LEFT JOIN repo AS r ON pr.repo_id = r.id
                                   LEFT JOIN content_set AS cs ON r.content_set_id = cs.id
                                   WHERE pr.pkg_id = %s
                              """ % (pkg_id))
                for repolabel in cursor:
                    repos.append(repolabel[0])

            return repos
        return None

    def update_nevra(self):
        """ Generator for creating new NEVRA documents and returning them. """
        with self._named_cursor() as cursor:
            cursor.execute(""" SELECT n.name, evr.epoch, evr.version, evr.release,
                                      a.name, p.summary, p.description, p.source_package_id,
                                      p.id
                               FROM package AS p
                               LEFT JOIN evr ON p.evr_id = evr.id
                               LEFT JOIN arch AS a ON p.arch_id = a.id
                               LEFT JOIN package_name AS n ON p.name_id = n.id
                           """)
            for nevra in cursor:
                nevra_doc = Nevra()
                nevra_doc.name = nevra[0]
                nevra_doc.epoch = nevra[1]
                nevra_doc.version = nevra[2]
                nevra_doc.release = nevra[3]
                nevra_doc.arch = nevra[4]
                nevra_doc.summary = nevra[5]
                nevra_doc.description = nevra[6]
                nevra_doc.source_pkg = self._format_src_pkg(nevra[7])
                nevra_doc.meta.id = nevra[8]
                nevra_doc.repo_label = self._format_repo_label(nevra[8])

                yield nevra_doc.to_dict(True)

    def update_es(self):
        """ Initial method which starts updating the elastic. """
        self.init_elastic()
        LOGGER.info("Inserting data to elastic.")
        self.bulk(self.update_nevra())
        LOGGER.info("Inserting data to elastic done.")
