"""
Module for API /packages.
"""
from base import Request
import database.db_handler as DB
from common.webapp_utils import join_packagename
from common.logging_utils import init_logging, get_logger
from common.rpm import parse_rpm_name

POOL_SIZE = 10

""" Indexes to make the request more readable. """
PACKAGE_SUMMARY = 0
PACKAGE_DESCRIPTION = 1
SOURCE_PACKAGE_NAME = 2
SOURCE_PACKAGE_EPOCH = 3
SOURCE_PACKAGE_VERSION = 4
SOURCE_PACKAGE_RELEASE = 5
SOURCE_PACKAGE_ARCH = 6
REPOSITORY_LABEL = 7
REPOSITORY_NAME = 8
REPOSITORY_ARCH = 9
REPOSITORY_RELEASEVER = 10
BINARY_PACKAGES = 11

LOGGER = get_logger(__name__)

# pylint: disable=broad-except
class Packages(Request):
    """ POST and GET to /v1/packages """
    @classmethod
    def handle_post(cls, **kwargs):
        response = 400
        packages_api = PackagesAPI()
        try:
            packages = packages_api.process_list(kwargs.get("body"))
            response = 200
        except Exception as _:
            LOGGER.exception("Caught exception: %s", _)
            return cls.format_exception(f"Unknown exception: {_}, include in bug report.", 500)
        return packages, response

    @classmethod
    def handle_get(cls, **kwargs):
        response = 400
        packages_api = PackagesAPI()
        try:
            package = packages_api.process_nevra(kwargs.get("Nevra"))
            response = 200
        except Exception as _:
            LOGGER.exception("Caught exception: %s", _)
            return cls.format_exception(f"Unknown exception: {_}, include in bug report.", 500)
        return package, response

class PackagesAPI:
    """ Class for handling packages API requests. """
    # pylint: disable=no-self-use
    def __init__(self, dsn=None):
        init_logging()
        self.db_pool = DB.DatabasePoolHandler(POOL_SIZE, dsn)

    def _build_repositories(self, query):
        """ Rebuilds the repositories list object in POST/GET response. """
        repositories = []
        for query_repository in query:
            repository = {}
            if query_repository[REPOSITORY_LABEL] is None and \
               query_repository[REPOSITORY_NAME] is None and \
               query_repository[REPOSITORY_ARCH] is None and \
               query_repository[REPOSITORY_RELEASEVER] is None:
                continue

            repository["label"] = query_repository[REPOSITORY_LABEL]
            repository["name"] = query_repository[REPOSITORY_NAME]
            repository["arch"] = query_repository[REPOSITORY_ARCH]
            repository["releasever"] = query_repository[REPOSITORY_RELEASEVER]

            repositories.append(repository)
        return repositories

    def _build_binary_packages(self, query):
        """ Rebuilds list of binary packages object in POST/GET reponse. """
        binary_packages = []
        for query_repository in query:
            if query_repository[BINARY_PACKAGES] is not None:
                binary_packages.append(query_repository[BINARY_PACKAGES])
        return binary_packages

    def process_list(self, data):
        """ Processes whole package_list and returns info. """
        packages = data.get("package_list")
        response = {"package_list": {}}

        db_connection = self.db_pool.get_connection()
        with db_connection.get_cursor() as cursor:
            for package in packages:
                name, epoch, version, release, arch = parse_rpm_name(package, default_epoch='0')
                cursor.execute("""select distinct p.summary, p.description,
                                  pn2.name, evr2.epoch, evr2.version, evr2.release, a2.name,
                                  cs.label, cs.name, a.name, r.releasever,
                                  pn3.name
                                  from package p
                                  left join package_name pn on pn.id = p.name_id 
                                  left join arch ap on p.arch_id = ap.id 
                                  left join evr on p.evr_id = evr.id 
                                  left join package p2 on p2.id = p.source_package_id 
                                  left join package_name pn2 on p2.name_id = pn2.id
                                  left join evr evr2 on p2.evr_id = evr2.id 
                                  left join arch a2 on p2.arch_id = a2.id
                                  left join pkg_repo pr on pr.pkg_id = p.id 
                                  left join repo r on r.id = pr.repo_id 
                                  left join content_set cs on cs.id = r.content_set_id 
                                  left join arch a on a.id = r.basearch_id
                                  left join package p3 on p3.source_package_id = p.id
                                  left join package_name pn3 on p3.name_id = pn3.id
                                  where pn.name = '%s' 
                                  and ap.name = '%s' 
                                  and evr.epoch = '%s' 
                                  and evr.version = '%s' 
                                  and evr.release = '%s'
                               """ % (name, arch, epoch, version, release))
                query = cursor.fetchall()
                pkgs = {}
                pkgs[package] = {}
                for item in query:
                    pkgs[package] = {"summary": item[PACKAGE_SUMMARY],
                                     "description": item[PACKAGE_DESCRIPTION],
                                     "source_package": join_packagename(item[SOURCE_PACKAGE_NAME],
                                                                        item[SOURCE_PACKAGE_EPOCH],
                                                                        item[SOURCE_PACKAGE_VERSION],
                                                                        item[SOURCE_PACKAGE_RELEASE],
                                                                        item[SOURCE_PACKAGE_ARCH]),
                                     "repositories": self._build_repositories(query),
                                     "binary_package_list": self._build_binary_packages(query)
                                    }
                response["package_list"].update(pkgs)
        self.db_pool.return_connection(db_connection)
        return response

    def process_nevra(self, nevra):
        """ Processes only one nevra from GET request. """
        dummy_list = [str(nevra)]
        dummy_schema = {"package_list": dummy_list}
        return self.process_list(dummy_schema)
