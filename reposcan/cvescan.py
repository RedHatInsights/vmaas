#!/usr/bin/python3
"""
Main executable for cvescan tool. It allows to sync CVEs from NIST NVD web API.
"""


from argparse import ArgumentParser

from database.database_handler import DatabaseHandler
from nistcve.cve_controller import CveRepoController

def main():
    """Main function."""
    parser = ArgumentParser()
    parser.add_argument("-d", "--db-name", action="store",
                        help="Database name (default 'vmaas').",
                        default="vmaas")
    parser.add_argument("-U", "--db-user", action="store",
                        help="Database user (default 'vmaas_user').",
                        default="vmaas_user")
    parser.add_argument("-P", "--db-pass", action="store",
                        help="Database password (default 'vmaas_passwd').",
                        default="vmaas_passwd")
    parser.add_argument("-H", "--db-host", action="store",
                        help="Database host (default 'localhost').",
                        default="localhost")
    parser.add_argument("-p", "--db-port", action="store",
                        help="Database port (default '5432').",
                        default="5432")
    args = parser.parse_args()

    # Setup DB connection parameters
    DatabaseHandler.db_name = args.db_name
    DatabaseHandler.db_user = args.db_user
    DatabaseHandler.db_pass = args.db_pass
    DatabaseHandler.db_host = args.db_host
    DatabaseHandler.db_port = args.db_port

    controller = CveRepoController()
    controller.add_repos()
    controller.store()

if __name__ == '__main__':
    main()
