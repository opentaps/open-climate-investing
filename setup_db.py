import psycopg2.extras
import psycopg2
import configparser
import getpass
import os
import argparse


def import_data_into_sql(table_name, file_name, cursor, bmg=False):
    if bmg is not False:
        sql_query = "DROP TABLE IF EXISTS _import_carbon_risk_factor CASCADE;"
        cursor.execute(sql_query)
        sql_query = "CREATE TABLE _import_carbon_risk_factor (date date, bmg decimal(12, 10), PRIMARY KEY (date));"
        cursor.execute(sql_query)
        sql_query = "COPY _import_carbon_risk_factor FROM %s WITH (FORMAT CSV, HEADER);"
    else:
        sql_query = "COPY " + table_name + \
            " FROM %s WITH (FORMAT CSV, HEADER);"
    cursor.execute(sql_query, (file_name, ))
    if bmg is not False:
        sql_query = "INSERT INTO carbon_risk_factor (date, factor_name, bmg) SELECT date, '" + \
                                                     bmg + "', bmg FROM _import_carbon_risk_factor;"
        cursor.execute(sql_query)
        sql_query = "DROP TABLE IF EXISTS _import_carbon_risk_factor CASCADE;"
        cursor.execute(sql_query)


def import_spx_constituents_into_sql(table_name, file_name, cursor, constituent_ticker):
    cursor.execute("DROP TABLE IF EXISTS _stock_weights CASCADE;")
    cursor.execute(
            "CREATE TABLE _stock_weights (ticker text, weight DECIMAL(5,2), PRIMARY KEY (ticker));")
    cursor.execute(
        "DELETE FROM stock_components WHERE ticker = '" + constituent_ticker + "';")
    sql_query = "COPY _stock_weights FROM %s WITH (FORMAT CSV, HEADER);"
    cursor.execute(sql_query, (file_name, ))
    sql_query = "INSERT INTO stock_components(ticker, component_stock, percentage) SELECT '" + \
        constituent_ticker + "', ticker, weight FROM _stock_weights;"
    cursor.execute(sql_query)
    cursor.execute("DROP TABLE IF EXISTS _stock_weights CASCADE;")


def import_msci_constituents_into_sql(table_name, file_name, cursor, constituent_ticker):
    cursor.execute("DROP TABLE IF EXISTS _stock_comps CASCADE;")
    cursor.execute(
            "CREATE TABLE _stock_comps (ticker text, name text, weight decimal(8, 5), market_value text, sector text, country text, PRIMARY KEY (ticker));")
    cursor.execute(
        "DELETE FROM stock_components WHERE ticker = '" + constituent_ticker + "';")
    sql_query = "COPY _stock_comps FROM %s WITH (FORMAT CSV, HEADER);"
    cursor.execute(sql_query, (file_name, ))
    cursor.execute(
        "INSERT INTO stocks (ticker, name, sector) SELECT ticker, name, sector FROM _stock_comps ON CONFLICT (ticker) DO NOTHING;")
    cursor.execute("INSERT INTO stock_components (ticker, component_stock, percentage, sector, country) SELECT 'XWD.TO', ticker, weight, sector, country FROM _stock_comps;")
    cursor.execute("DROP TABLE IF EXISTS _stock_comps CASCADE;")


def main(args):
    root_dir = os.getcwd()

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
        xop_carbon_data = (data_dir + '/bmg_xop_smog_orthogonalized_1.csv')
        risk_free_data = (data_dir + '/risk_free.csv')
        additional_factor_data = (data_dir + '/additional_factor_data.csv')
        sector_breakdown_data = (data_dir + '/spx_sector_breakdown.csv')
        spx_constituent_data = data_dir + '/spx_constituent_weights.csv'
        msci_constituent_data = data_dir + '/msci_constituent_details.csv'

        import_data_into_sql("ff_factor", ff_data, cursor)
        import_data_into_sql("carbon_risk_factor",
                             carbon_data, cursor, bmg="CARIMA")
        import_data_into_sql("carbon_risk_factor",
                             xop_carbon_data, cursor, bmg="DEFAULT")
        import_data_into_sql("risk_free", risk_free_data, cursor)
        import_data_into_sql("additional_factors",
                             additional_factor_data, cursor)
        cursor.execute(
            "INSERT INTO stocks (ticker, name) VALUES ('IVV', 'iShares S&P 500');")
        cursor.execute(
            "INSERT INTO stocks (ticker, name) VALUES ('XWD.TO', 'iShares MSCI World');")

        import_data_into_sql("stocks",
                             sector_breakdown_data, cursor)

        # import components and weights of spx
        import_spx_constituents_into_sql(
            "stock_components", spx_constituent_data, cursor, "IVV")

        # import components and weights of msci
        import_msci_constituents_into_sql(
            0, msci_constituent_data, cursor, "XWD.TO")

        if args.add_stock_data:
            msci_constituent_return_data = data_dir + '/msci_comparison_returns.csv'
            import_data_into_sql("stock_data",
                                 msci_constituent_return_data, cursor)


# run
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--add_data", default=False, action='store_true',
                        help="Import default data")
    parser.add_argument("-s", "--add_stock_data", action='store_true')
    main(parser.parse_args())
