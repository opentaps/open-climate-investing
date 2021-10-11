import pgdb
import psycopg2.extras
import psycopg2

DB_HOST = '127.0.01'
DB_NAME = 'open_climate_investing'
DB_USER = ''
DB_PASS = ''

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
