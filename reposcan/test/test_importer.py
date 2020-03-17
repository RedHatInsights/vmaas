"""
Tests for elasticsearch importer in reposcan.
"""

import pytest
from elasticsearch_dsl import Index
from pytest_elasticsearch.factories import elasticsearch_proc, elasticsearch
from common.documents.nevra import Nevra

from importer import Importer
import common.webapp_utils as utils

# pylint: disable=invalid-name
# pylint: disable=redefined-outer-name

es_proc = elasticsearch_proc()
es_conn = elasticsearch("es_proc")

class TestImporter:
    """ Tests for the Importer. """

    importer = None

    @pytest.fixture(autouse=True)
    def _init_importer(self, exporter_db_conn, es_conn):
        """ Initialize importer by fixtures. """
        self.importer = Importer(exporter_db_conn, es_conn)

    def test_index_init(self, es_conn):
        """ Test ES schema init. """
        self.importer.init_elastic()
        Index(name="packages").search(using=es_conn)

    def test_data_import(self, exporter_db_conn, es_conn):
        """ Test clean import of data from DB, check only NEVRAs. """
        self.importer.update_es()

        db_nevras = []
        with exporter_db_conn.cursor() as cursor:
            cursor.execute(""" SELECT n.name, evr.epoch, evr.version, evr.release,
                                      a.name, p.summary, p.description, p.source_package_id,
                                      p.id
                               FROM package AS p
                               LEFT JOIN evr ON p.evr_id = evr.id
                               LEFT JOIN arch AS a ON p.arch_id = a.id
                               LEFT JOIN package_name AS n ON p.name_id = n.id
                           """)

            for db_nevra in cursor:
                db_nevra = utils.join_packagename(db_nevra[0], db_nevra[1], db_nevra[2],
                                                  db_nevra[3], db_nevra[4])
                db_nevras.append(db_nevra)

        for doc_nevra in Nevra.search(using=es_conn).scan():
            doc_nevra = utils.join_packagename(doc_nevra.name, doc_nevra.epoch, doc_nevra.version,
                                               doc_nevra.release, doc_nevra.arch)
            assert doc_nevra in db_nevras

    def test_data_import_repolabels(self, exporter_db_conn, es_conn):
        """ Test clean import of data from DB, check only repolabels. """
        self.importer.update_es()

        db_repos = []
        with exporter_db_conn.cursor() as cursor:
            cursor.execute(""" SELECT cs.label
                               FROM pkg_repo AS pr
                               LEFT JOIN repo AS r ON pr.repo_id = r.id
                               LEFT JOIN content_set AS cs ON r.content_set_id = cs.id
                           """)

            for db_repo in cursor:
                db_repos.append(db_repo[0])

        for doc_repo in Nevra.search(using=es_conn).scan():
            for repo in doc_repo.repo_label:
                assert repo in db_repos

    def test_update_on_update(self, exporter_db_conn, es_conn):
        """ Test clean import and then update on import. """
        self.importer.update_es()
        self.importer.update_es()

        db_nevras = []
        with exporter_db_conn.cursor() as cursor:
            cursor.execute(""" SELECT n.name, evr.epoch, evr.version, evr.release,
                                      a.name, p.summary, p.description, p.source_package_id,
                                      p.id
                               FROM package AS p
                               LEFT JOIN evr ON p.evr_id = evr.id
                               LEFT JOIN arch AS a ON p.arch_id = a.id
                               LEFT JOIN package_name AS n ON p.name_id = n.id
                           """)

            for db_nevra in cursor:
                db_nevra = utils.join_packagename(db_nevra[0], db_nevra[1], db_nevra[2],
                                                  db_nevra[3], db_nevra[4])
                db_nevras.append(db_nevra)

        for doc_nevra in Nevra.search(using=es_conn).scan():
            doc_nevra = utils.join_packagename(doc_nevra.name, doc_nevra.epoch, doc_nevra.version,
                                               doc_nevra.release, doc_nevra.arch)
            assert doc_nevra in db_nevras


    def test_elastic_clear(self, es_conn):
        """ Test if ES gets cleaned. """
        self.importer.clear_elastic()
        assert not Index(name="packages").exists(using=es_conn)
