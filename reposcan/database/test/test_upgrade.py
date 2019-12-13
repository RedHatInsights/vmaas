"""
Tests for database upgrade, which are made from reposcan.
"""
# pylint: disable=no-self-use, import-outside-toplevel, unused-argument,
import os
import shutil
import psycopg2
import pytest

DB_UPDATES_FIXTURE_PATH = "./dbfixtureupgrades"

NAME = 0
VALUE = 1

VERSION = 0
STATUS = 1
SCRIPT = 2
RETURNCODE = 3

TEST_SCRIPT_1 = "CREATE TABLE TEST{}();"

SCRIPT_COUNT = 10

def _fetch_version(conn):
    """ Fetch current version from db. """
    with conn.cursor() as cursor:
        cursor.execute("SELECT version FROM db_version")
        return (cursor.fetchone())[0]

def _fetch_version_logs(conn):
    """ Fetch all upgrade logs from db. """
    with conn.cursor() as cursor:
        cursor.execute("SELECT version, status, script, returncode FROM db_upgrade_log")
        return cursor.fetchall()

def _fetch_upgrade_ver():
    files = os.listdir(DB_UPDATES_FIXTURE_PATH)
    latest = files[-1]
    return int(latest.split("-")[0])

def _create_script(version, script_content):
    """ Create script with given version number and given script content. """
    script_name = ("%0*d" % (3, version)) + "-test" + str(version) + ".sql"
    script_path = os.path.join(DB_UPDATES_FIXTURE_PATH, script_name)
    script_content = script_content.format(version)

    with open(script_path, "w+") as new_script:
        new_script.write(script_content)
    return script_path

def _remove_script(script_name):
    """ Remove the test script. """
    os.remove(script_name)

def _parse_dsn(dsn_string):
    """ Parsing of DSN string. """
    port = None
    host = None
    user = None
    db_name = None

    params = dsn_string.split(" ")

    for param in params:
        name_value = param.split("=")
        if name_value[NAME] == "port":
            port = name_value[VALUE]
        elif name_value[NAME] == "host":
            host = name_value[VALUE]
        elif name_value[NAME] == "user":
            user = name_value[VALUE]
        elif name_value[NAME] == "dbname":
            db_name = name_value[VALUE]

    return host, user, db_name, port

class TestUpgrade:
    """ Test for the upgrades. """

    @pytest.fixture
    def setup_teardown(self):
        """ Fixture creates fixture folder for fixture upgrades. """
        os.mkdir(DB_UPDATES_FIXTURE_PATH)
        enviroment = dict(os.environ)
        os.environ.clear()
        yield
        shutil.rmtree(DB_UPDATES_FIXTURE_PATH)
        os.environ.update(enviroment)

    def test_upgrade_empty(self, db_conn, setup_teardown):
        """ Test with 0 upgrade tests. """
        conn = db_conn

        try:
            current_version = int(_fetch_version(conn))
        except psycopg2.ProgrammingError:
            pytest.fail("Version cannot be fetched.")

        # Reparse the connection string from the fixture, because
        # upgrade script does upgrading with own connection & cursor
        db_host, db_user, db_name, db_port = _parse_dsn(conn.dsn)

        os.environ["POSTGRESQL_DATABASE"] = db_name
        os.environ["POSTGRESQL_USER"] = db_user
        os.environ["POSTGRESQL_HOST"] = db_host
        os.environ["POSTGRESQL_PORT"] = db_port

        from database import upgrade

        os.environ["DB_UPGRADE_SCRIPTS_DIR"] = DB_UPDATES_FIXTURE_PATH
        upgrade.main()

        new_version = _fetch_version(conn)
        assert new_version == current_version

        logs = _fetch_version_logs(conn)
        assert not logs

    def test_upgrade_single(self, db_conn, setup_teardown):
        """ Test with only single upgrade script. """
        conn = db_conn

        try:
            current_version = int(_fetch_version(conn))
        except psycopg2.ProgrammingError:
            pytest.fail("Version cannot be fetched.")

        test_version = current_version + 1
        script_location = _create_script(test_version, TEST_SCRIPT_1)

        # Reparse the connection string from the fixture, because
        # upgrade script does upgrading with own connection & cursor
        db_host, db_user, db_name, db_port = _parse_dsn(conn.dsn)

        os.environ["POSTGRESQL_DATABASE"] = db_name
        os.environ["POSTGRESQL_USER"] = db_user
        os.environ["POSTGRESQL_HOST"] = db_host
        os.environ["POSTGRESQL_PORT"] = db_port

        from database import upgrade

        os.environ["DB_UPGRADE_SCRIPTS_DIR"] = DB_UPDATES_FIXTURE_PATH

        upgrade.main()

        new_version = _fetch_version(conn)
        assert new_version == test_version

        logs = _fetch_version_logs(conn)
        log = logs.pop()

        assert log[VERSION] == test_version
        assert log[STATUS] == "complete"
        assert log[SCRIPT] == script_location.split("/")[-1]
        assert log[RETURNCODE] == 0

    def test_upgrade_multiple(self, db_conn, setup_teardown):
        """ Test with multiple test upgrade scripts. """
        conn = db_conn

        try:
            current_version = int(_fetch_version(conn))
        except psycopg2.ProgrammingError:
            pytest.fail("Version cannot be fetched.")

        script_locations = []
        max_script = current_version + SCRIPT_COUNT

        for dummy_version in range(current_version, max_script + 1):
            script_locations.append(_create_script(dummy_version, TEST_SCRIPT_1))

        # Reparse the connection string from the fixture, because
        # upgrade script does upgrading with own connection & cursor
        db_host, db_user, db_name, db_port = _parse_dsn(conn.dsn)

        os.environ["POSTGRESQL_DATABASE"] = db_name
        os.environ["POSTGRESQL_USER"] = db_user
        os.environ["POSTGRESQL_HOST"] = db_host
        os.environ["POSTGRESQL_PORT"] = db_port

        from database import upgrade

        os.environ["DB_UPGRADE_SCRIPTS_DIR"] = DB_UPDATES_FIXTURE_PATH

        upgrade.main()

        new_version = int(_fetch_version(conn))
        assert new_version == max_script

        logs = _fetch_version_logs(conn)
        script_num = 0
        while script_num < max_script:
            correct_result = (current_version + script_num,
                              "complete",
                              script_locations[script_num].split("/")[-1],
                              0)
            assert correct_result in logs
            script_num += 1
