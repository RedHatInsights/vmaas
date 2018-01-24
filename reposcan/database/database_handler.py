import psycopg2


class DatabaseHandler:
    db_name = None
    db_user = None
    db_pass = None
    db_host = None
    db_port = None
    connection = None

    @classmethod
    def get_connection(cls):
        if cls.connection is None:
            cls.connection = psycopg2.connect(
                database=cls.db_name, user=cls.db_user, password=cls.db_pass, host=cls.db_host, port=cls.db_port)
        return cls.connection

    @classmethod
    def close_connection(cls):
        if cls.connection is not None:
            cls.connection.close()
            cls.connection = None
