#!/usr/bin/env python3
"""
database upgrade
"""
import os
import subprocess

import psycopg2

from vmaas.common.config import Config
from vmaas.common.logging_utils import get_logger, init_logging
from vmaas.common.paths import DB_UPGRADES_PATH, DB_CREATE_SQL_PATH
from vmaas.reposcan.database.database_handler import DatabaseHandler, init_db

LOGGER = get_logger(__name__)
SCHEMA_VER_NAME = 'schema_version'


class UpgradeException(Exception):
    """Exception during database """


class DatabaseUpgrade:
    """ This class contains logic for upgrading the database.
    """
    # directory where the upgrade sql scripts are located.
    # must end with '/' character.
    scripts_dir = None

    # map of version to which a script upgrades the db to
    # the name of the script.
    version2file_map = None

    # highest version of a sql upgrade script.  This is the
    # version to which the db will be upgraded.
    version_max = 0

    def __init__(self):
        LOGGER.info('DatabaseUpgrade initializing.')

        DatabaseHandler.close_connection()

        init_db()
        self.init_schema()

        # get upgrade sql scripts directory
        self.scripts_dir = os.getenv('DB_UPGRADE_SCRIPTS_DIR', str(DB_UPGRADES_PATH))
        if not self.scripts_dir.endswith('/'):
            self.scripts_dir += '/'

        # load the version2file_map and version_max
        self.version2file_map, self.version_max = self._load_upgrade_file_list(self.scripts_dir)

    def init_schema(self):
        """Initialize database schema."""
        cfg = Config()
        conn = DatabaseHandler.get_connection()
        if self._is_initialized(conn):
            LOGGER.info("DB schema is already initialized.")
            return

        try:
            self._get_db_lock(conn)
            LOGGER.info("Empty database, initializing...")
            with conn.cursor() as cur:
                if cfg.pg_max_stack_depth:
                    # vmaas.reposcan needs bigger max_stack_depth for ephemeral environment
                    # increase max_stack_depth when the DB is empty (probably only in ephemeral env)
                    cur.connection.autocommit = True  # autocommit to run queries without transaction
                    cur.execute(f"ALTER SYSTEM SET max_stack_depth TO {cfg.pg_max_stack_depth}")
                    cur.execute(f"ALTER DATABASE vmaas SET max_stack_depth TO {cfg.pg_max_stack_depth}")
                    cur.connection.autocommit = False
                with open(DB_CREATE_SQL_PATH, "r", encoding='utf8') as f_db:
                    cur.execute(f_db.read())

            conn.commit()
        finally:
            self._release_db_lock(conn)

    def upgrade(self):
        """perform database upgrade"""
        conn = DatabaseHandler.get_connection()
        try:
            self._get_db_lock(conn)

            db_version = self._get_current_db_version(conn)

            if db_version == self.version_max:
                LOGGER.info('Database is up to date at version: %d', db_version)
                return
            if db_version > self.version_max:
                msg = 'Database version %d is greater than upgrade version %d' % (db_version, self.version_max)
                LOGGER.warning(msg)
                return

            LOGGER.info('Database requires upgrade from version %d to %d', db_version, self.version_max)
            upgrades_to_apply = self._get_upgrades_to_apply(db_version, self.version_max)
            for upgrade in upgrades_to_apply:
                self._apply_upgrade(upgrade['ver'], upgrade['script'], conn)
        finally:
            self._release_db_lock(conn)

    @staticmethod
    def _load_upgrade_file_list(scripts_dir):
        LOGGER.info('Building upgrade script list from directory %s', scripts_dir)
        max_version = 0
        ver2file_map = {}
        files = os.listdir(scripts_dir)
        for name in files:
            if name.endswith('.sql'):
                result = name.split('-', 1)
                if len(result) != 2:
                    LOGGER.info('ignoring file using different name format: %s', name)
                else:
                    try:
                        file_num = int(result[0])
                        if file_num in ver2file_map:
                            raise UpgradeException(
                                "Found two files with same file number",
                                ver2file_map[file_num],
                                name,
                            )
                        LOGGER.debug('adding to list file version %d: %s', file_num, name)
                        ver2file_map[file_num] = {'ver': file_num, 'script': name}
                        if file_num > max_version:
                            LOGGER.debug('max version raised to %d', file_num)
                            max_version = file_num
                    except ValueError:
                        LOGGER.info('ignoring file with non-numeric prefix: %s', name)
            else:
                LOGGER.info('ignoring file without .sql suffix: %s', name)
        return ver2file_map, max_version

    def _get_upgrades_to_apply(self, current_ver, upgrade_ver):
        upgrades_to_apply = []
        missing_upgrades = []
        for file_ver in range(current_ver + 1, upgrade_ver + 1):
            if file_ver in self.version2file_map:
                upgrades_to_apply.append(self.version2file_map[file_ver])
            else:
                missing_upgrades.append(file_ver)
        if missing_upgrades:
            raise UpgradeException('Missing upgrade script versions %s' % missing_upgrades)
        return upgrades_to_apply

    def _apply_upgrade(self, version, script_file, conn):
        LOGGER.info('applying upgrade to version %d', version)
        if version > 1:
            self._insert_log_entry(version, 'starting', script_file, conn)

        psql_env = {'PGPASSWORD': DatabaseHandler.db_pass}
        psql = subprocess.run(['/usr/bin/psql', '--no-password',
                               '-h', DatabaseHandler.db_host,
                               '-p', str(DatabaseHandler.db_port),
                               '-U', DatabaseHandler.db_user,
                               '-d', DatabaseHandler.db_name,
                               '-f', self.scripts_dir + script_file,
                               '--single-transaction',
                               '-v', 'ON_ERROR_STOP=on'],
                              stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE,
                              universal_newlines=True,
                              env=psql_env,
                              check=False)

        if psql.returncode != 0:
            status = 'failed'
            failure = True
            LOGGER.error('upgrade failure')
        else:
            status = 'complete'
            failure = False
            LOGGER.info('upgrade applied successfully')
            self._set_current_db_version(version, conn)
        self._insert_log_entry(version,
                               status,
                               script_file,
                               conn,
                               returncode=psql.returncode,
                               stdout=psql.stdout,
                               stderr=psql.stderr)
        if failure:
            raise UpgradeException(
                "upgrade psql command failed with returncode %d" % psql.returncode,
                "stdout: %s" % psql.stdout,
                "stderr: %s" % psql.stderr,
            )

    @staticmethod
    def _get_db_lock(conn):
        LOGGER.info('getting advisory lock')
        with conn.cursor() as cur:
            cur.execute('SELECT pg_advisory_lock(13)')
        conn.commit()

    @staticmethod
    def _release_db_lock(conn):
        LOGGER.info('releasing advisory lock')
        with conn.cursor() as cur:
            cur.execute('SELECT pg_advisory_unlock(13)')
        conn.commit()

    @staticmethod
    def _get_current_db_version(conn):
        try:
            with conn.cursor() as cur:
                cur.execute('select version from db_version where name = %s',
                            (SCHEMA_VER_NAME,))
                result = cur.fetchone()
            if not result:
                raise UpgradeException("db_version table exists, but no row with name '%s'" % SCHEMA_VER_NAME)
            db_version = result[0]
        except psycopg2.ProgrammingError:
            db_version = 0
        finally:
            conn.commit()
        return db_version

    @staticmethod
    def _set_current_db_version(version, conn):
        with conn.cursor() as cur:
            cur.execute("update db_version set version = %s where name = %s",
                        (version, SCHEMA_VER_NAME))

        conn.commit()

    @staticmethod
    def _insert_log_entry(version, status, script, conn, *, returncode=None, stdout=None, stderr=None):
        with conn.cursor() as cur:
            cur.execute("""insert into db_upgrade_log
                        (version, status, script, returncode, stdout, stderr)
                        values (%s, %s, %s, %s, %s, %s)""",
                        (version, status, script, returncode, stdout, stderr))
        conn.commit()

    @staticmethod
    def _is_initialized(conn):
        initialized = True
        try:
            with conn.cursor() as cur:
                cur.execute("select count(*) from pg_stat_user_tables")
                initialized = bool(int(cur.fetchone()[0]))
        except (psycopg2.ProgrammingError, IndexError):
            initialized = False
        finally:
            conn.commit()
        return initialized


def main():
    """Sets up and run whole application"""
    # Set up endpoint for prometheus monitoring
    init_logging()

    upgrader = DatabaseUpgrade()
    upgrader.upgrade()


if __name__ == "__main__":
    main()
