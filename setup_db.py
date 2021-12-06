import psycopg2.extras
import psycopg2
import configparser
import getpass
import os
import argparse


def import_data_into_sql(table_name, file_name, cursor):
    sql_query = "COPY " + table_name + " FROM %s WITH (FORMAT CSV, HEADER);"
    data = (file_name, )
    cursor.execute(sql_query, data)


def main(args):
    root_dir = os.getcwd()
    print(root_dir)

    # User input for database management
    DB_HOST = input(
        "What is the address of your server (default is localhost): ")

    DB_MAINTENANCE_DB = input(
        "What is your maintenance database name (normally postgres): ")

    DB_USER = input(
        "What is your username (default is postgres): ")

    DB_PASS = getpass.getpass(
        "What is your password (this will be hidden when you type): ")

    DB_NAME = input(
        "What would you like to name your database: ")

    # Save to config file
    config = configparser.ConfigParser()
    config['DEFAULT'] = {
        'DatabaseHost': DB_HOST,
        'DatabaseName': DB_NAME,
        'DatabaseUser': DB_USER,
        'DatabasePassword': DB_PASS
    }

    # Connect to maintenance database
    with open('db.ini', 'w') as configfile:
        config.write(configfile)

    conn = psycopg2.connect(host=DB_HOST, database=DB_MAINTENANCE_DB,
                            user=DB_USER, password=DB_PASS)
    conn.autocommit = True
    cursor = conn.cursor()

    # Create new database
    sql_drop_db = 'DROP DATABASE IF EXISTS ' + DB_NAME + ';'
    cursor.execute(sql_drop_db)

    sql_create_db = 'CREATE DATABASE ' + DB_NAME + ';'
    cursor.execute(sql_create_db)

    # Disconnect and connect to created database
    conn.close()

    conn = psycopg2.connect(host=DB_HOST, database=DB_NAME,
                            user=DB_USER, password=DB_PASS)

    conn.autocommit = True
    cursor = conn.cursor()

    # Run the initial schema file to create tables, etc.
    cursor.execute(open("init_schema.sql", "r").read())

    # Run the initial data load to create tables, etc.
    data_dir = os.getcwd() + '/data'

    if args.add_data:
        ff_data = (data_dir + '/ff_factors.csv')
        carbon_data = (data_dir + '/bmg_carima.csv')
        risk_free_data = (data_dir + '/risk_free.csv')
        additional_factor_data = (data_dir + '/additional_factor_data.csv')
        import_data_into_sql("ff_factor", ff_data, cursor)
        import_data_into_sql("carbon_risk_factor", carbon_data, cursor)
        import_data_into_sql("risk_free", risk_free_data, cursor)
        import_data_into_sql("additional_factors",
                             additional_factor_data, cursor)


# run
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--add_data", default=False, action='store_true',
                        help="Import default data")
    main(parser.parse_args())
