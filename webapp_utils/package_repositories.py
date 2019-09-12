"""
Module for API /packages.
"""
from base import Request
import database.db_handler as DB
from utils import split_packagename

POOL_SIZE = 10

""" Indexes to make the request more readable. """
REPOSITORY_NAME = 0
REPOSITORY_LABEL = 1

class PostPackageRepositories(Request): # pylint: disable=abstract-method
    """ POST to /v1/packages/repositories """
    @classmethod
    def handle_post(cls, **kwargs):
        response = 400
        repositories_api = PackagesRepositoriesAPI()
        try:
            repositories = repositories_api.process_nevras(kwargs.get("body"))
            response = 200
        except Exception as ex: # pylint: disable=broad-except
            repositories = "Unknown exception, %s, include in bug report." % (ex)
        return repositories, response

class PackagesRepositoriesAPI:
    """ Class for handling packages to repositories requests. """
    def __init__(self, dsn=None):
        self.db_pool = DB.DatabasePoolHandler(POOL_SIZE, dsn)

    def process_nevras(self, data):
        """ Method returns the list of repositories where package belongs. """
        # pylint: disable=no-member
        packages = data.get("package_list")
        response = {"data": {}}

        db_connection = self.db_pool.get_connection()
        with db_connection.get_cursor() as cursor:
            for package in packages:
                name, epoch, version, release, arch = split_packagename(package)
                cursor.execute("""select distinct cs.name, cs.label
                                  from package p
                                  left join package_name pn on p.name_id = pn.id
                                  left join evr e on p.evr_id = e.id
                                  left join arch a on p.arch_id = a.id
                                  left join pkg_repo pr on p.id = pr.pkg_id
                                  left join repo r on r.id = pr.repo_id
                                  left join content_set cs on cs.id = r.content_set_id
                                  where pn.name = '%s'
                                  and a.name = '%s'
                                  and e.epoch = '%s'
                                  and e.version = '%s'
                                  and e.release = '%s'
                               """ % (name, arch, epoch, version, release))

                response["data"][package] = []
                for repository_query in cursor: # pylint: disable=not-an-iterable
                    repository_data = {}
                    if repository_query[REPOSITORY_NAME] is not None:
                        repository_data["repo_name"] = repository_query[REPOSITORY_NAME]
                    if repository_query[REPOSITORY_LABEL] is not None:
                        repository_data["label"] = repository_query[REPOSITORY_LABEL]
                    if repository_data:
                        response["data"][package].append(repository_data)

        return response
