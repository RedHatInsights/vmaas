"""
Module for /errata API endpoint
"""
from jsonschema import validate, ValidationError
from base import Request
import database.db_handler as DB
import time
from utils import join_packagename, parse_datetime, paginate
from logging_utils import get_logger, init_logging

POOL_SIZE = 10

ERRATA_UPDATED = 0
ERRATA_SEVERITY = 1
ERRATA_REF_TYPE = 2
ERRATA_REF_NAME = 3
ERRATA_ISSUED = 4
ERRATA_DESCRIPTION = 5
ERRATA_SOLUTION = 6
ERRATA_SUMMARY = 7
ERRATA_URL = 8
ERRATA_SYNOPSIS = 9
ERRATA_CVE = 10
ERRATA_PKGID_NAME = 11
ERRATA_PKGID_EPOCH = 12
ERRATA_PKGID_VERSION = 13
ERRATA_PKGID_RELEASE = 14
ERRATA_PKGID_ARCH = 15
ERRATA_TYPE = 16

MIN_ERRATA_SEARCH_SIZE = 4

LOGGER = get_logger(__name__)


class PostErrata(Request):  # pylint: disable=abstract-method
    """POST to /v1/errata"""
    @classmethod
    def handle_post(cls, **kwargs):
        response = 400
        errata_api = ErrataAPI()
        try:
            errata = errata_api.process_list(kwargs.get("body"))
            response = 200
        except ValidationError:
            errata = "Error: malformed request JSON"
        return errata, response


class GetErrata(Request):  # pylint: disable=abstract-method
    """GET to /v1/errata"""
    @classmethod
    def handle_get(cls, **kwargs):
        response = 400
        errata_api = ErrataAPI()
        try:
            errata = errata_api.process_erratum(kwargs.get("erratum"))
            response = 200
        except ValidationError:
            errata = "Error: malformed request JSON"
        return errata, response


class ErrataAPI:
    """Class handling errata API requests."""

    def __init__(self):
        init_logging()
        self.db_pool = DB.DatabasePoolHandler(POOL_SIZE)

    def _build_references(self, query, bugzilla=False):
        """Builds references/bugzilla list object in POST/GET response."""
        references = []
        bugzillas = []
        for item in query:
            if bugzilla and item[ERRATA_REF_TYPE] == "bugzilla" and item[ERRATA_REF_NAME] not in bugzillas:
                bugzillas.append(item[ERRATA_REF_NAME])
            elif item[ERRATA_REF_TYPE] == "other" and item[ERRATA_REF_NAME] not in references:
                references.append(item[ERRATA_REF_NAME])
        if bugzilla:
            return bugzillas
        return references

    def _build_cve_list(self, query):
        """Builds cve list object on POST/GET response."""
        cve_list = []
        for item in query:
            if item[ERRATA_CVE] and not item[ERRATA_CVE] in cve_list:
                cve_list.append(item[ERRATA_CVE])
        return cve_list

    def _build_package_list(self, query, source=False):
        package_list = []
        source_package_list = []
        for item in query:
            package = join_packagename(
                item[ERRATA_PKGID_NAME],
                item[ERRATA_PKGID_EPOCH],
                item[ERRATA_PKGID_VERSION],
                item[ERRATA_PKGID_RELEASE],
                item[ERRATA_PKGID_ARCH]
            )
            if package and not source and not package in package_list and not package[-4:] == ".src":
                package_list.append(package)
            elif package and source and not package in source_package_list and package[-4:] == ".src":
                source_package_list.append(package)
        if source:
            return source_package_list
        return package_list

    def _fill_errata(self, search):
        """Returns existing errata acording to search string."""
        errata_list = []
        if not len(search) >= MIN_ERRATA_SEARCH_SIZE:
            return errata_list
        db_connection = self.db_pool.get_connection()
        with db_connection.get_cursor() as cursor:
            for errata in search:
                errata = '%' + errata + '%'
                cursor.execute("""select name from errata
                                  where name like '%s'
                               """ % errata)
                query = cursor.fetchall()
                for item in query:
                    errata_list.append(item[0])
        return errata_list

    def _errata_exists(self, errata):
        """Checks if given errata is in db."""
        db_connection = self.db_pool.get_connection()
        with db_connection.get_cursor() as cursor:
            cursor.execute("""select name from errata
                              where name = '%s'""" % errata)
            errata_detail = cursor.fetchone()
        self.db_pool.return_connection(db_connection)
        return errata_detail

    def process_list(self, data):
        """Processes whole errata_list/errata_schema and returns info."""
        modified_since = data.get("modified_since", "")
        errata_to_process = data.get("errata_list", None)
        errata_to_search = data.get("errata_search", None)
        page = data.get("page", None)
        page_size = data.get("page_size", None)
        response = {"errata_list": {}}
        if modified_since:
            response["modified_since"] = modified_since
        start_time = time.time()
        if not errata_to_process and not errata_to_search:
            return response
        elif not errata_to_process and errata_to_search:
            errata_to_process = self._fill_errata(errata_to_search)
        errata_fill_time = time.time() - start_time
        LOGGER.info("ERRATA_FILL_TIME: %s", errata_fill_time)
        result = {}
        errata_page_to_process, pagination_response = paginate(errata_to_process, page, page_size)
        pagination_time = time.time() - start_time - errata_fill_time
        errata_start_time = time.time()
        LOGGER.info("ERRATA_PAGINATION_TIME: %s", pagination_time)
        db_connection = self.db_pool.get_connection()
        with db_connection.get_cursor() as cursor:
            for errata in errata_page_to_process:
                result[errata] = {}
                if not self._errata_exists(errata):
                    continue
                cursor.execute("""select distinct e.updated, es.name as severity,
                                  er.type, er.name, e.issued, e.description,
                                  e.solution, e.summary, e.name as url, e.synopsis,
                                  cve.name as cve, pn.name, evr.epoch, evr.version,
                                  evr.release, a.name as arch, et.name as type
                                  from errata e
                                  left join errata_severity es on e.severity_id = es.id
                                  left join errata_refs er on e.id = er.errata_id
                                  left join errata_cve ec on e.id = ec.errata_id
                                  left join cve on ec.cve_id = cve.id
                                  left join pkg_errata pkge on e.id = pkge.errata_id
                                  left join package p on pkge.pkg_id = p.id
                                  left join package_name pn on p.name_id = pn.id
                                  left join evr on p.evr_id = evr.id
                                  left join arch a on p.arch_id = a.id
                                  left join errata_type et on e.errata_type_id = et.id
                                  where e.name = '%s'
                               """ % errata)
                query = cursor.fetchall()
                query_time = time.time() - errata_start_time
                LOGGER.info("SINGLE ERRATA queru cumulative time: %s", query_time)
                result[errata] = {
                    "updated": query[0][ERRATA_UPDATED],
                    "severity": query[0][ERRATA_SEVERITY],
                    "reference_list": self._build_references(query),
                    "issued": query[0][ERRATA_ISSUED],
                    "description": query[0][ERRATA_DESCRIPTION],
                    "solution": query[0][ERRATA_SOLUTION],
                    "summary": query[0][ERRATA_SUMMARY],
                    "url": "https://access.redhat.com/errata/%s" % str(query[0][ERRATA_URL]),
                    "synopsis": query[0][ERRATA_SYNOPSIS],
                    "cve_list": self._build_cve_list(query),
                    "bugzilla_list": self._build_references(query, bugzilla=True),
                    "package_list": self._build_package_list(query),
                    "source_package_list": self._build_package_list(query, source=True),
                    "type": query[0][ERRATA_TYPE]
                }
            response["errata_list"].update(result)
        response.update(pagination_response)
        self.db_pool.return_connection(db_connection)
        return response

    def process_erratum(self, errata):
        """Processes errata from GET request."""
        # TODO: errata_list vs errata_search input
        response = [str(errata)]
        response_schema = {"errata_list": response}
        return self.process_list(response_schema)
