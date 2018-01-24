#!/usr/bin/python3

from argparse import ArgumentParser

from database.database_handler import DatabaseHandler
from repodata.repository_controller import RepositoryController

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument("-d", "--db-name", action="store", help="Database name (default 'vmaas').",
                        default="vmaas")
    parser.add_argument("-U", "--db-user", action="store", help="Database user (default 'vmaas_user').",
                        default="vmaas_user")
    parser.add_argument("-P", "--db-pass", action="store", help="Database password (default 'vmaas_passwd').",
                        default="vmaas_passwd")
    parser.add_argument("-H", "--db-host", action="store", help="Database host (default 'localhost').",
                        default="localhost")
    parser.add_argument("-p", "--db-port", action="store", help="Database port (default '5432').",
                        default="5432")
    parser.add_argument("-r", "--repo", action="append",
                        help="Sync given repository (can be specifed multiple times).")
    args = parser.parse_args()

    # Setup DB connection parameters
    DatabaseHandler.db_name = args.db_name
    DatabaseHandler.db_user = args.db_user
    DatabaseHandler.db_pass = args.db_pass
    DatabaseHandler.db_host = args.db_host
    DatabaseHandler.db_port = args.db_port

    if args.repo:
        repository_controller = RepositoryController()
        for repo_url in args.repo:
            repository_controller.add_repository(repo_url)
        repository_controller.store()
