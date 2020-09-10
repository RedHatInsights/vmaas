"""
Module for /errata API endpoint
"""
import psycopg2

from base import Request
import database.db_handler as DB
from common.logging_utils import get_logger, init_logging
from common.rpm import join_rpm_name
from pagination import paginate

POOL_SIZE = 10

ERRATA_UPDATED = 0
ERRATA_SEVERITY = 1
ERRATA_ISSUED = 2
ERRATA_DESCRIPTION = 3
ERRATA_SOLUTION = 4
ERRATA_SUMMARY = 5
ERRATA_URL = 6
ERRATA_SYNOPSIS = 7
ERRATA_TYPE = 8

ERRATA_PKG_NAME = 0
ERRATA_PKG_EPOCH = 1
ERRATA_PKG_VERSION = 2
ERRATA_PKG_RELEASE = 3
ERRATA_PKG_ARCH = 4

MIN_ERRATA_SEARCH_SIZE = 1

LOGGER = get_logger(__name__)

# pylint: disable=broad-except


class Errata(Request):
    """POST and GET to /v1/errata"""
    @classmethod
    def handle_post(cls, **kwargs):
        response = 400
        errata_api = ErrataAPI()
        try:
            errata = errata_api.process_list(kwargs.get("body"))
            response = 200
        except Exception as _:
            LOGGER.exception("Caught exception: %s", _)
            return cls.format_exception(f"Unknown exception: {_}, include in bug report.", 500)
        return errata, response

    @classmethod
    def handle_get(cls, **kwargs):
        response = 400
        errata_api = ErrataAPI()
        try:
            errata = errata_api.process_erratum(kwargs.get("erratum"))
            response = 200
        except Exception as _:
            LOGGER.exception("Caught exception: %s", _)
            return cls.format_exception(f"Unknown exception: {_}, include in bug report.", 500)
        return errata, response


class ErrataAPI:
    """Class handling errata API requests."""

    def __init__(self):
        init_logging()
        self.db_pool = DB.DatabasePoolHandler(POOL_SIZE)

    def _build_references(self, errata, bugzilla=False):
        """Builds references/bugzilla list object in POST/GET response."""
        references = []
        bugzillas = []
        db_connection = self.db_pool.get_connection()
        with db_connection.get_cursor() as cursor:
            cursor.execute("""select er.type, er.name
                              from errata e
                              left join errata_refs er on e.id = er.errata_id
                              where e.name in %s
                           """, [tuple(errata,)])
            query = cursor.fetchall()
        self.db_pool.return_connection(db_connection)
        for item in query:
            if bugzilla and item[0] == "bugzilla" and item[1] not in bugzillas:
                bugzillas.append(item[1])
            elif item[0] == "other" and item[1] not in references:
                references.append(item[1])
        if bugzilla:
            return bugzillas
        return references

    def _build_cve_list(self, errata):
        """Builds cve list object on POST/GET response."""
        cve_list = []
        db_connection = self.db_pool.get_connection()
        with db_connection.get_cursor() as cursor:
            cursor.execute("""select cve.name
                              from errata e
                              left join errata_cve ec on e.id = ec.errata_id
                              left join cve on ec.cve_id = cve.id
                              where e.name in %s
                           """, [tuple(errata,)])
            query = cursor.fetchall()
        self.db_pool.return_connection(db_connection)
        for item in query:
            if item[0] and not item[0] in cve_list:
                cve_list.append(item[0])
        return cve_list

    def _build_package_list(self, errata, source=False):
        package_list = []
        source_package_list = []
        db_connection = self.db_pool.get_connection()
        with db_connection.get_cursor() as cursor:
            cursor.execute("""select pn.name, evr.epoch, evr.version,
                              evr.release, a.name as arch
                              from errata e
                              left join pkg_errata pkge on e.id = pkge.errata_id
                              left join package p on pkge.pkg_id = p.id
                              left join package_name pn on p.name_id = pn.id
                              left join evr on p.evr_id = evr.id
                              left join arch a on p.arch_id = a.id
                              where e.name in %s
                           """, [tuple(errata,)])
            query = cursor.fetchall()
        self.db_pool.return_connection(db_connection)
        for item in query:
            package = join_rpm_name(
                item[ERRATA_PKG_NAME],
                item[ERRATA_PKG_EPOCH],
                item[ERRATA_PKG_VERSION],
                item[ERRATA_PKG_RELEASE],
                item[ERRATA_PKG_ARCH]
            )
            if package and not source and not package in package_list and not package[-4:] == ".src":
                package_list.append(package)
            elif package and source and not package in source_package_list and package[-4:] == ".src":
                source_package_list.append(package)
        if source:
            return source_package_list
        return package_list

    def _fill_errata(self, errata):
        """Returns existing errata acording to search string."""
        errata_list = []
        if not len(errata) >= MIN_ERRATA_SEARCH_SIZE:
            return errata_list
        db_connection = self.db_pool.get_connection()
        with db_connection.get_cursor() as cursor:
            errata = '%' + errata + '%'
            cursor.execute("""select name from errata
                              where name like %s
                           """, (errata,))
            query = cursor.fetchall()
            for item in query:
                errata_list.append(item[0])
        return errata_list

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
        if not errata_to_process and errata_to_search:
            errata_to_process = self._fill_errata(errata_to_search)
        elif not errata_to_process and not errata_to_search:
            return response
        result = {}
        errata_page_to_process, pagination_response = paginate(errata_to_process, page, page_size)
        db_connection = self.db_pool.get_connection()
        with db_connection.get_cursor() as cursor:
            cursor.execute("""select distinct e.updated, es.name as severity,
                                  e.issued, e.description,
                                  e.solution, e.summary, e.name as url, e.synopsis,
                                  et.name as type
                                  from errata e
                                  left join errata_severity es on e.severity_id = es.id
                                  left join errata_type et on e.errata_type_id = et.id
                                  where e.name in %s
                               """, [tuple(errata_page_to_process,)])
            for i, errata in enumerate(cursor):
                result[errata_page_to_process[i]] = {}
                result[errata_page_to_process[i]] = {
                    "updated": errata[ERRATA_UPDATED],
                    "severity": errata[ERRATA_SEVERITY],
                    "reference_list": self._build_references(errata_page_to_process),
                    "issued": errata[ERRATA_ISSUED],
                    "description": errata[ERRATA_DESCRIPTION],
                    "solution": errata[ERRATA_SOLUTION],
                    "summary": errata[ERRATA_SUMMARY],
                    "url": "https://access.redhat.com/errata/%s" % str(errata[ERRATA_URL]),
                    "synopsis": errata[ERRATA_SYNOPSIS],
                    "cve_list": self._build_cve_list(errata_page_to_process),
                    "bugzilla_list": self._build_references(errata_page_to_process, bugzilla=True),
                    "package_list": self._build_package_list(errata_page_to_process),
                    "source_package_list": self._build_package_list(errata_page_to_process, source=True),
                    "type": errata[ERRATA_TYPE]
                }
            response["errata_list"].update(result)
        response.update(pagination_response)
        self.db_pool.return_connection(db_connection)
        return response

    def process_erratum(self, errata):
        """Processes errata from GET request."""
        response = [str(errata)]
        response_schema = {"errata_list": response}
        return self.process_list(response_schema)
