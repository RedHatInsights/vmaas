"""
Module for /errata API endpoint
"""
from jsonschema import validate, ValidationError
from base import Request
import re
import database.db_handler as DB
from utils import join_packagename, parse_datetime, paginate
from logging_utils import get_logger, init_logging

POOL_SIZE = 10
ERRATA_SCHEMA = {
    "type": "object",
    "required": ["errata_list"],
    "properties": {
        "errata_list": {
            "type": "array",
            "items": {
                "type": "string"
            },
            "minItems": 1
        },
        "modified_since": {
            "type": "string"
        },
        "page": {
            "type": "number"
        },
        "page_size": {
            "type": "number"
        }
    }
}

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

    def _fulltext_search_errata(self, errata_to_process):
        return errata_to_process

    def _check_valid_errata(self, errata_to_process):
        return errata_to_process

    """ def _filter_modified_since(self, errata_to_process, modified_since_dt):
        filtered_errata_to_process = []
        index = 0
        db_connection = self.db_pool.get_connection()
        with db_connection.get_cursor() as cursor:
            for errata in errata_to_process:
                cursor.execute(""" """select name from errata
                                  where name = '%s'""" """% errata)
                errata_detail = cursor.fetchone()
                if not errata_detail:
                    continue
                cursor.execute(""""""select distinct e.updated, es.name as severity,
                                  er.type, er.name, e.issued, e.description,
                                  e.solution, e.summary, e.name as url, e.synopsis,
                                  cve.name as cve,
                                  pn.name, evr.epoch, evr.version, evr.release, a.name as arch,
                                  et.name as type
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
                               """""" % errata)
                query = cursor.fetchall()
                if query[index][ERRATA_UPDATED]:
                    if query[index][ERRATA_UPDATED] >= modified_since_dt:
                        filtered_errata_to_process.append(errata)
                elif query[index][ERRATA_ISSUED] and query[index][ERRATA_UPDATED] >= modified_since_dt:
                    filtered_errata_to_process.append(errata)
        self.db_pool.return_connection(db_connection)  
        return filtered_errata_to_process """

    def _build_references(self, query, bugzilla=False):
        """Builds references/bugzilla list object in POST/GET response."""
        references = []
        bugzillas = []
        LOGGER.info("REFERENCES/BUGZILLA")
        for item in query:
            if item[ERRATA_REF_TYPE] == "bugzilla" and item[ERRATA_REF_NAME] not in bugzillas and bugzilla:
                bugzillas.append(item[ERRATA_REF_NAME])
            elif item[ERRATA_REF_TYPE] == "other" and item[ERRATA_REF_NAME] not in references:
                references.append(item[ERRATA_REF_NAME])
        if bugzilla:
            LOGGER.info("Building bugzila_list")
            return bugzillas
        LOGGER.info("Building reference_list")
        return references

    def _build_cve_list(self, query):
        """Builds cve list object on POST/GET response."""
        cve_list = []
        for item in query:
            if item[ERRATA_CVE]:
                cve_list.append(item[ERRATA_CVE])
        return cve_list

    def _build_package_list(self, query, source=False):
        """Builds {source-}package list object on POST/GET response."""
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
            if not source and package not in package_list:
                package_list.append(package)
            elif source and package not in source_package_list and package[-4:] == ".src":
                source_package_list.append(package)

        if source:
            return source_package_list
        return package_list

    def process_list(self, data):
        """Processes whole errata_list and returns info."""
        validate(data, ERRATA_SCHEMA)
        LOGGER.info("Validating errata schema")

        modified_since = data.get("modified_since", "")
        modified_since_dt = parse_datetime(modified_since)
        errata_to_process = data.get("errata_list", None)
        page = data.get("page", None)
        page_size = data.get("page_size", None)

        response = {"errata_list": {}}
        if modified_since:
            response["modified_since"] = modified_since

        LOGGER.info("ERRATA TO PROCESS: %s", errata_to_process)
        if not errata_to_process:
            return response

        errata_to_process = errata_to_process if \
            self._check_valid_errata(errata_to_process) else \
            self._fulltext_search_errata(errata_to_process)

        LOGGER.info(errata_to_process)
        result = {}
        errata_page_to_process, pagination_response = paginate(errata_to_process, page, page_size)
        LOGGER.info("TO PROCESS: %s", errata_page_to_process)
        db_connection = self.db_pool.get_connection()
        with db_connection.get_cursor() as cursor:
            for index, errata in enumerate(errata_page_to_process):
                result[errata] = {}
                cursor.execute("""select name from errata
                                  where name = '%s'""" % errata)
                errata_detail = cursor.fetchone()
                if not errata_detail:
                    result[errata] = {}
                    response["errata_list"].update(result)
                    continue
                cursor.execute("""select distinct e.updated, es.name as severity,
                                  er.type, er.name, e.issued, e.description,
                                  e.solution, e.summary, e.name as url, e.synopsis,
                                  cve.name as cve,
                                  pn.name, evr.epoch, evr.version, evr.release, a.name as arch,
                                  et.name as type
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
                LOGGER.info("reference_list: %s", self._build_references(query))
                LOGGER.info("cve_list: %s", self._build_cve_list(query))
                LOGGER.info("bugzilla_list: %s", self._build_references(query, bugzilla=True))
                LOGGER.info("package_list: %s", self._build_package_list(query))
                LOGGER.info("source_package_list: %s", self._build_package_list(query, source=True))
                result[errata] = {
                    "updated": query[index][ERRATA_UPDATED],
                    "severity": query[index][ERRATA_SEVERITY],
                    "reference_list": self._build_references(query),
                    "issued": query[index][ERRATA_ISSUED],
                    "description": query[index][ERRATA_DESCRIPTION],
                    "solution": query[index][ERRATA_SOLUTION],
                    "summary": query[index][ERRATA_SUMMARY],
                    "url": "https://access.redhat.com/errata/%s" % str(query[index][ERRATA_URL]),
                    "synopsis": query[index][ERRATA_SYNOPSIS],
                    "cve_list": self._build_cve_list(query),
                    "bugzilla_list": self._build_references(query, bugzilla=True),
                    "package_list": self._build_package_list(query),
                    "source_package_list": self._build_package_list(query, source=True),
                    "type": query[index][ERRATA_TYPE]
                }
                response["errata_list"].update(result)
        response.update(pagination_response)
        self.db_pool.return_connection(db_connection)
        return response

    def process_erratum(self, errata):
        """Processes errata from GET request."""
        response = [str(errata)]
        LOGGER.info(response)
        response_schema = {"errata_list": response}
        return self.process_list(response_schema)
