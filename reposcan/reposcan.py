#!/usr/bin/python3
"""
Main executable for reposcan tool. It allows to sync specified repositories into specified PostgreSQL database.
"""

from argparse import ArgumentParser

from database.database_handler import DatabaseHandler
from repodata.repository_controller import RepositoryController


def main():
    """Main function."""
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
    parser.add_argument("--repofile", action="store", help="Read repository list from file.")
    args = parser.parse_args()

    # Setup DB connection parameters
    DatabaseHandler.db_name = args.db_name
    DatabaseHandler.db_user = args.db_user
    DatabaseHandler.db_pass = args.db_pass
    DatabaseHandler.db_host = args.db_host
    DatabaseHandler.db_port = args.db_port

    repository_controller = RepositoryController()
    if args.repo:
        for repo_url in args.repo:
            repository_controller.add_repository(repo_url)
    if args.repofile:
        with open(args.repofile, "r") as repo_file:
            for line in repo_file.readlines():
                repository_controller.add_repository(line)
    repository_controller.store()

if __name__ == '__main__':
    main()
