import pgdb
import psycopg2.extras
import psycopg2
import configparser
from psycopg2.pool import ThreadedConnectionPool

config = configparser.ConfigParser()
config.read('db.ini')

DB_HOST = config['DEFAULT']['DatabaseHost']
DB_NAME = config['DEFAULT']['DatabaseName']
DB_USER = config['DEFAULT']['DatabaseUser']
DB_PASS = config['DEFAULT']['DatabasePassword']

DB_CREDENTIALS = "postgresql://{}:{}@{}/{}".format(
    DB_USER, DB_PASS, DB_HOST, DB_NAME)


def get_db_connection():
    try:
        conn = psycopg2.connect(host=DB_HOST, database=DB_NAME,
                                user=DB_USER, password=DB_PASS)
        # do not use transactions since we do not change anything in the DB
        conn.autocommit = True
        return conn
    except Exception as e:
        print('Unable to connect PostgreSQL', e)
        raise SystemExit(1)


def get_db_connection_pool():
    try:
        pool = ThreadedConnectionPool(1, 20, DB_CREDENTIALS)
        return pool
    except Exception as e:
        print('Unable to connect PostgreSQL', e)
        raise SystemExit(1)
