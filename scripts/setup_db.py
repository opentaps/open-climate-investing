import psycopg2.extras
import psycopg2
import configparser
import getpass
import os
import sys
import argparse


def import_bond_factor_into_sql(file_name, cursor):
    print("-- import_bond_factor_into_sql file={}".format(file_name,))
    sql_query = 'COPY bond_factor FROM %s WITH (FORMAT CSV, HEADER);'
    cursor.execute(sql_query, (file_name,))


def import_data_into_sql(table_name, file_name, cursor, bmg=False, wml=False, no_wml=False):
    print("-- import_data_into_sql file={} table={}".format(file_name, table_name))
    if bmg is not False:
        sql_query = "DROP TABLE IF EXISTS _import_carbon_risk_factor CASCADE;"
        cursor.execute(sql_query)
        sql_query = "CREATE TABLE _import_carbon_risk_factor (date date, frequency text, bmg decimal(12, 10), PRIMARY KEY (date));"
        cursor.execute(sql_query)
        sql_query = "COPY _import_carbon_risk_factor FROM %s WITH (FORMAT CSV, HEADER);"
    elif wml:
        sql_query = "DROP TABLE IF EXISTS _import_wml_ff_factor CASCADE;"
        cursor.execute(sql_query)
        sql_query = "CREATE TABLE _import_wml_ff_factor (date date, frequency text, wml decimal(8,5), PRIMARY KEY (date, frequency));"
        cursor.execute(sql_query)
        sql_query = "COPY _import_wml_ff_factor FROM %s WITH (FORMAT CSV, HEADER);"
    elif no_wml:
        sql_query = "DROP TABLE IF EXISTS _import_nowml_ff_factor CASCADE;"
        cursor.execute(sql_query)
        sql_query = "CREATE TABLE _import_nowml_ff_factor (date date, frequency text, mkt_rf decimal(8,5), smb decimal(8,5), hml decimal(8,5), rf decimal(8,5), PRIMARY KEY (date, frequency));"
        cursor.execute(sql_query)
        sql_query = "COPY _import_nowml_ff_factor FROM %s WITH (FORMAT CSV, HEADER);"
    else:
        sql_query = "COPY " + table_name + \
            " FROM %s WITH (FORMAT CSV, HEADER);"
    cursor.execute(sql_query, (file_name, ))
    if bmg is not False:
        sql_query = "INSERT INTO carbon_risk_factor (date, frequency, factor_name, bmg) SELECT date, frequency, '" + \
                                                     bmg + "', bmg FROM _import_carbon_risk_factor;"
        cursor.execute(sql_query)
        sql_query = "DROP TABLE IF EXISTS _import_carbon_risk_factor CASCADE;"
        cursor.execute(sql_query)
    elif wml:
        sql_query = '''INSERT INTO ff_factor (date, frequency, wml)
            SELECT date, frequency, wml FROM _import_wml_ff_factor
            ON CONFLICT (date, frequency) DO
            UPDATE SET wml = EXCLUDED.wml;
            '''
        cursor.execute(sql_query)
        sql_query = "DROP TABLE IF EXISTS _import_wml_ff_factor CASCADE;"
        cursor.execute(sql_query)
    elif no_wml:
        sql_query = '''INSERT INTO ff_factor (date, frequency, mkt_rf, smb, hml)
            SELECT date, frequency, mkt_rf, smb, hml FROM _import_nowml_ff_factor
            ON CONFLICT (date, frequency) DO
            UPDATE SET mkt_rf = EXCLUDED.mkt_rf, smb = EXCLUDED.smb, hml = EXCLUDED.hml;'''
        cursor.execute(sql_query)
        sql_query = "DROP TABLE _import_nowml_ff_factor CASCADE;"
        cursor.execute(sql_query)


def import_spx_constituents_into_sql(file_name, cursor, constituent_ticker):
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


def import_msci_constituents_into_sql(file_name, cursor, constituent_ticker):
    cursor.execute("DROP TABLE IF EXISTS _stock_comps CASCADE;")
    cursor.execute(
            "CREATE TABLE _stock_comps (ticker text, name text, weight decimal(8, 5), market_value text, sector text, country text, PRIMARY KEY (ticker));")
    cursor.execute(
        "DELETE FROM stock_components WHERE ticker = '" + constituent_ticker + "';")
    sql_query = "COPY _stock_comps FROM %s WITH (FORMAT CSV, HEADER);"
    cursor.execute(sql_query, (file_name, ))
    cursor.execute(
        "INSERT INTO stocks (ticker, name, sector) SELECT ticker, name, sector FROM _stock_comps ON CONFLICT (ticker) DO NOTHING;")
    cursor.execute("INSERT INTO stock_components (ticker, component_stock, percentage, sector, country) SELECT '"
                   + constituent_ticker + "', ticker, weight, sector, country FROM _stock_comps;")
    cursor.execute("DROP TABLE IF EXISTS _stock_comps CASCADE;")


def import_carbon_constituents_into_sql(file_name, cursor, constituent_ticker):
    cursor.execute("DROP TABLE IF EXISTS _stock_comps CASCADE;")
    cursor.execute(
            "CREATE TABLE _stock_comps (ticker text, name text, market_value text, weight decimal(8, 5), sector text, PRIMARY KEY (ticker));")
    cursor.execute(
        "DELETE FROM stock_components WHERE ticker = '" + constituent_ticker + "';")
    sql_query = "COPY _stock_comps FROM %s WITH (FORMAT CSV, HEADER);"
    cursor.execute(sql_query, (file_name, ))
    cursor.execute(
        "INSERT INTO stocks (ticker, name, sector) SELECT ticker, name, sector FROM _stock_comps ON CONFLICT (ticker) DO NOTHING;")
    cursor.execute(
        "INSERT INTO stock_components (ticker, component_stock, percentage, sector) SELECT '" + constituent_ticker + "', ticker, weight, sector FROM _stock_comps;")
    cursor.execute("DROP TABLE IF EXISTS _stock_comps CASCADE;")


def cleanup_abnormal_returns(cursor, ticker=None):
    if ticker:
        cursor.execute("delete from stock_data where ticker = ? and (return > 1 or return = 'NaN');", (ticker,))
    else:
        cursor.execute("delete from stock_data where return > 1 or return = 'NaN';")


CONFIG_FILE = 'db.ini'


def main(args):
    if args.reuse:
        # read the existing config 
        if args.verbose:
            print('** reusing current DB config')
        config = configparser.ConfigParser()
        config.read(CONFIG_FILE)

        DB_HOST = config['DEFAULT']['DatabaseHost']
        DB_MAINTENANCE_DB = config['DEFAULT']['MaintenanceDatabaseName']
        DB_NAME = config['DEFAULT']['DatabaseName']
        DB_USER = config['DEFAULT']['DatabaseUser']
        DB_PASS = config['DEFAULT']['DatabasePassword']

    else:
        # User input for database management
        DB_HOST = input(
            "What is the address of your server (default is localhost): ")
        if not DB_HOST:
            DB_HOST = 'localhost'

        DB_MAINTENANCE_DB = input(
            "What is your maintenance database name (default is postgres): ")
        if not DB_MAINTENANCE_DB:
            DB_MAINTENANCE_DB = 'postgres'

        DB_USER = input(
            "What is your username (leave empty to use the current username): ")

        DB_PASS = getpass.getpass(
            "What is your password (this will be hidden when you type): ")

        DB_NAME = input(
            "What would you like to name your database: (default is open_climate_investing) ")
        if not DB_NAME:
            DB_NAME = 'open_climate_investing'

        # Save to config file
        config = configparser.ConfigParser()
        config['DEFAULT'] = {
            'DatabaseHost': DB_HOST,
            'DatabaseName': DB_NAME,
            'MaintenanceDatabaseName': DB_MAINTENANCE_DB,
            'DatabaseUser': DB_USER,
            'DatabasePassword': DB_PASS
        }

        # Write the config
        if args.verbose:
            print('** write config:')
            print(config.write(sys.stdout))
        with open(CONFIG_FILE, 'w') as configfile:
            config.write(configfile)

    # Connect to maintenance database
    if args.verbose:
        print('** connect to maintenance DB: {} at {} with user {}'.format(DB_MAINTENANCE_DB, DB_HOST, DB_USER))
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

    if args.verbose:
        print('** connect to created DB: {} at {} with user {}'.format(DB_NAME, DB_HOST, DB_USER))
    conn = psycopg2.connect(host=DB_HOST, database=DB_NAME,
                            user=DB_USER, password=DB_PASS)

    conn.autocommit = True
    cursor = conn.cursor()

    # Run the initial schema file to create tables, etc.
    script_dir = os.getcwd() + '/scripts'
    if args.verbose:
        print('** init schema')
    cursor.execute(open(script_dir + "/init_schema.sql", "r").read())

    # Run the initial data load to create tables, etc.
    data_dir = os.getcwd() + '/data'

    if args.add_data:
        ff_data = (data_dir + '/ff_factors.csv')
        ff_data_daily = (data_dir + '/ff_factors_daily.csv')
        ff_data_daily_wml = (data_dir + '/ff_factors_daily_wml.csv')
        carbon_data = (data_dir + '/bmg_carima.csv')
        xop_carbon_data = (data_dir + '/bmg_xop_smog_orthogonalized_1.csv')
        risk_free_data= (data_dir + '/risk_free.csv')
        risk_free_data_daily = (data_dir + '/risk_free_daily.csv')
        additional_factor_data = (data_dir + '/additional_factor_data.csv')
        sector_breakdown_data = (data_dir + '/spx_sector_breakdown.csv')
        spx_constituent_data = data_dir + '/spx_constituent_weights.csv'
        msci_constituent_data = data_dir + '/msci_constituent_details.csv'
        carbon_constituent_data = data_dir + '/crbn_materials_constituent_details.csv'
        bond_factor_data = data_dir + '/interest_rates.csv'

        if args.verbose:
            print('** importing ff_factor')
        import_data_into_sql("ff_factor", ff_data, cursor)
        if args.verbose:
            print('** importing ff_factor_daily')
        import_data_into_sql("ff_factor", ff_data_daily, cursor, no_wml=True)
        if args.verbose:
            print('** importing ff_factor_daily_wml (WML)')
        import_data_into_sql("ff_factor", ff_data_daily_wml, cursor, wml=True)
        if args.verbose:
            print('** importing carbon_risk_factor CARIMA')
        import_data_into_sql("carbon_risk_factor",
                             carbon_data, cursor, bmg="CARIMA")
        if args.verbose:
            print('** importing carbon_risk_factor DEFAULT')
        import_data_into_sql("carbon_risk_factor",
                             xop_carbon_data, cursor, bmg="DEFAULT")
        if args.verbose:
            print('** importing risk_free')
        import_data_into_sql("risk_free", risk_free_data, cursor)
        if args.verbose:
            print('** importing risk_free_daily')
        import_data_into_sql("risk_free", risk_free_data_daily, cursor)
        if args.verbose:
            print('** importing additional_factors')
        import_data_into_sql("additional_factors",
                             additional_factor_data, cursor)
        
        # import the bond_factor
        if args.verbose:
            print('** importing bond factor')
        import_bond_factor_into_sql(bond_factor_data, cursor)

        if args.verbose:
            print('** adding stocks IVV and XWD.TO')
        cursor.execute(
            "INSERT INTO stocks (ticker, name) VALUES ('IVV', 'iShares S&P 500');")
        cursor.execute(
            "INSERT INTO stocks (ticker, name) VALUES ('XWD.TO', 'iShares MSCI World');")

        if args.verbose:
            print('** importing stocks')
        import_data_into_sql("stocks",
                             sector_breakdown_data, cursor)

        # import components and weights of spx
        if args.verbose:
            print('** importing stock_components IVV')
        import_spx_constituents_into_sql(spx_constituent_data, cursor, "IVV")

        # import components and weights of msci
        if args.verbose:
            print('** importing carbon_constituent_data XWD.TO')
        import_msci_constituents_into_sql(msci_constituent_data, cursor, "XWD.TO")

        if args.verbose:
            print('** importing carbon_constituent_data CRBN-MAT')
        import_carbon_constituents_into_sql(carbon_constituent_data, cursor, "CRBN-MAT")

        if args.add_stock_data:
            msci_constituent_return_data = data_dir + '/msci_comparison_returns.csv'
            if args.verbose:
                print('** importing stock_data: msci_comparison_returns')
            import_data_into_sql("stock_data",
                                 msci_constituent_return_data, cursor)
    if args.verbose:
        print('All DONE')


# run
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--add_data", default=False, action='store_true',
                        help="Import default data")
    parser.add_argument("-s", "--add_stock_data", action='store_true')
    parser.add_argument("-R", "--reuse", action='store_true', help='Reuse the current db.ini config instead of asking for the settings')
    parser.add_argument("-v", "--verbose", action='store_true')
    main(parser.parse_args())
