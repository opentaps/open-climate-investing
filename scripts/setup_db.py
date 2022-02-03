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
    print('---> inserted {} bond_factor rows.'.format(cursor.rowcount))


def import_data_into_sql(table_name, file_name, cursor, bmg=False):
    print("-- import_data_into_sql file={} table={}".format(file_name, table_name))
    if bmg is not False:
        sql_query = "DROP TABLE IF EXISTS _import_carbon_risk_factor CASCADE;"
        cursor.execute(sql_query)
        sql_query = "CREATE TABLE _import_carbon_risk_factor (date date, frequency text, bmg decimal(12, 10), PRIMARY KEY (date));"
        cursor.execute(sql_query)
        sql_query = "COPY _import_carbon_risk_factor FROM %s WITH (FORMAT CSV, HEADER);"
    else:
        sql_query = "COPY " + table_name + \
            " FROM %s WITH (FORMAT CSV, HEADER);"
    cursor.execute(sql_query, (file_name, ))
    if not bmg:
        print('---> inserted {} {} rows.'.format(cursor.rowcount, table_name))
    if bmg is not False:
        sql_query = "INSERT INTO carbon_risk_factor (date, frequency, factor_name, bmg) SELECT date, frequency, '" + \
                                                     bmg + "', bmg FROM _import_carbon_risk_factor;"
        cursor.execute(sql_query)
        print('---> inserted {} carbon_risk_factor rows.'.format(cursor.rowcount))
        sql_query = "DROP TABLE IF EXISTS _import_carbon_risk_factor CASCADE;"
        cursor.execute(sql_query)


def import_spx_constituents_into_sql(file_name, cursor, constituent_ticker):
    print("-- import_spx_constituents_into_sql file={} constituent_ticker={}".format(file_name, constituent_ticker))
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
    print('---> inserted {} stock_components rows.'.format(cursor.rowcount))
    cursor.execute("DROP TABLE IF EXISTS _stock_weights CASCADE;")


def import_msci_constituents_into_sql(file_name, cursor, constituent_ticker):
    print("-- import_msci_constituents_into_sql file={} constituent_ticker={}".format(file_name, constituent_ticker))
    cursor.execute("DROP TABLE IF EXISTS _stock_comps CASCADE;")
    cursor.execute(
            "CREATE TABLE _stock_comps (ticker text, name text, weight decimal(8, 5), market_value text, sector text, country text, PRIMARY KEY (ticker));")
    cursor.execute(
        "DELETE FROM stock_components WHERE ticker = '" + constituent_ticker + "';")
    sql_query = "COPY _stock_comps FROM %s WITH (FORMAT CSV, HEADER);"
    cursor.execute(sql_query, (file_name, ))
    cursor.execute(
        "INSERT INTO stocks (ticker, name, sector) SELECT ticker, name, sector FROM _stock_comps ON CONFLICT (ticker) DO NOTHING;")
    print('---> inserted {} stocks rows.'.format(cursor.rowcount))
    cursor.execute("INSERT INTO stock_components (ticker, component_stock, percentage, sector, country) SELECT '"
                   + constituent_ticker + "', ticker, weight, sector, country FROM _stock_comps;")
    print('---> inserted {} stock_components rows.'.format(cursor.rowcount))
    cursor.execute("DROP TABLE IF EXISTS _stock_comps CASCADE;")


def import_msci_etf_sector_into_sql(file_name, cursor, ticker_name):
    print("-- import_msci_etf_sector_into_sql file={} ticker_name={}".format(file_name, ticker_name))
    cursor.execute("DROP TABLE IF EXISTS _msci_etf_sector CASCADE;")
    cursor.execute(
            "CREATE TABLE _msci_etf_sector (ticker text, name text, sector text, PRIMARY KEY (ticker));")
    cursor.execute(
        "DELETE FROM stock_components WHERE ticker = '" + ticker_name + "';")
    sql_query = "COPY _msci_etf_sector FROM %s WITH (FORMAT CSV, HEADER);"
    cursor.execute(sql_query, (file_name, ))
    cursor.execute(
        "INSERT INTO stocks (ticker, name, sector) SELECT ticker, name, sector FROM _msci_etf_sector ON CONFLICT (ticker) DO NOTHING;")
    cursor.execute("INSERT INTO stock_components (ticker, component_stock, sector) SELECT '"
                   + ticker_name + "', ticker, sector FROM _msci_etf_sector;")
    print('---> inserted {} stock_components rows.'.format(cursor.rowcount))
    cursor.execute("DROP TABLE IF EXISTS _msci_etf_sector CASCADE;")


def import_monthly_ff_mom_factor_into_sql(file_name, cursor):
    print("-- import_monthly_ff_mom_factor_into_sql file={}".format(file_name,))
    # note: the file may be raw as downloaded which is not a directly importable format
    # so pass it through grep to only get valid rows.
    src = "grep '^[0-9]\\{{6\\}}' {}".format(file_name,)
    cursor.execute("DROP TABLE IF EXISTS _monthly_mom CASCADE;")
    cursor.execute("CREATE TABLE _monthly_mom (date_str text, mom decimal(8,5), PRIMARY KEY (date_str));")
    cursor.execute("COPY _monthly_mom FROM PROGRAM %s WITH (FORMAT CSV);", (src,))
    cursor.execute("""INSERT INTO ff_factor (date, frequency, wml)
                    SELECT (TO_DATE(date_str, 'YYYYMM') + interval '1 month - 1 day')::date, 'MONTHLY', mom
                    FROM _monthly_mom
                    WHERE NOT EXISTS (select 1 from ff_factor f where f.date = (TO_DATE(date_str, 'YYYYMM') + interval '1 month - 1 day')::date and f.frequency = 'MONTHLY')
                    ;""")
    print('---> inserted {} ff_factor rows.'.format(cursor.rowcount))
    cursor.execute("""UPDATE ff_factor SET wml = x.mom
                    FROM _monthly_mom x
                    WHERE
                        ff_factor.date = (TO_DATE(x.date_str, 'YYYYMM') + interval '1 month - 1 day')::date
                        AND ff_factor.frequency = 'MONTHLY'
                        AND (ff_factor.wml is null or ff_factor.wml != x.mom)
                    ;""")
    print('---> updated {} ff_factor rows.'.format(cursor.rowcount))
    cursor.execute("DROP TABLE IF EXISTS _monthly_mom CASCADE;")


def import_daily_ff_mom_factor_into_sql(file_name, cursor):
    print("-- import_daily_ff_mom_factor_into_sql file={}".format(file_name,))
    # note: the file may be raw as downloaded which is not a directly importable format
    # so pass it through grep to only get valid rows.
    src = "grep '^[0-9]\\{{6\\}}' {}".format(file_name,)
    cursor.execute("DROP TABLE IF EXISTS _daily_mom CASCADE;")
    cursor.execute("CREATE TABLE _daily_mom (date_str text, mom decimal(8,5), PRIMARY KEY (date_str));")
    cursor.execute("COPY _daily_mom FROM PROGRAM %s WITH (FORMAT CSV);", (src,))
    cursor.execute("""INSERT INTO ff_factor (date, frequency, wml) 
                    SELECT TO_DATE(date_str, 'YYYYMMDD'), 'DAILY', mom
                    FROM _daily_mom
                    WHERE NOT EXISTS (select 1 from ff_factor f where f.date = TO_DATE(date_str, 'YYYYMMDD') and f.frequency = 'DAILY')
                    ;""")
    print('---> inserted {} ff_factor rows.'.format(cursor.rowcount))
    cursor.execute("""UPDATE ff_factor SET wml = x.mom
                    FROM _daily_mom x
                    WHERE
                        ff_factor.date = TO_DATE(x.date_str, 'YYYYMMDD')
                        AND ff_factor.frequency = 'DAILY'
                        AND (ff_factor.wml is null or ff_factor.wml != x.mom)
                    ;""")
    print('---> updated {} ff_factor rows.'.format(cursor.rowcount))
    cursor.execute("DROP TABLE IF EXISTS _daily_mom CASCADE;")


def import_monthly_ff_data_factors_into_sql(file_name, cursor):
    print("-- import_daily_ff_mom_factor_into_sql file={}".format(file_name,))
    # note: the file may be raw as downloaded which is not a directly importable format
    # so pass it through grep to only get valid rows.
    src = "grep '^[0-9]\\{{6\\}}' {}".format(file_name,)
    cursor.execute("DROP TABLE IF EXISTS _monthly_ff CASCADE;")
    cursor.execute("CREATE TABLE _monthly_ff (date_str text, mkt_rf decimal(8,5), smb decimal(8,5), hml decimal(8,5), rf decimal(8,5), PRIMARY KEY (date_str));")
    cursor.execute("COPY _monthly_ff FROM PROGRAM %s WITH (FORMAT CSV);", (src,))
    cursor.execute("""INSERT INTO ff_factor (date, frequency, mkt_rf, smb, hml)
                    SELECT (TO_DATE(date_str, 'YYYYMM') + interval '1 month - 1 day')::date, 'MONTHLY', mkt_rf, smb, hml
                    FROM _monthly_ff
                    WHERE NOT EXISTS (select 1 from ff_factor f where f.date = (TO_DATE(date_str, 'YYYYMM') + interval '1 month - 1 day')::date and f.frequency = 'MONTHLY')
                    ;""")
    print('---> inserted {} ff_factor rows.'.format(cursor.rowcount))
    cursor.execute("""UPDATE ff_factor SET mkt_rf = x.mkt_rf, smb = x.smb, hml = x.hml
                    FROM _monthly_ff x
                    WHERE
                        ff_factor.date = (TO_DATE(x.date_str, 'YYYYMM') + interval '1 month - 1 day')::date
                        AND ff_factor.frequency = 'MONTHLY'
                        AND (
                            (ff_factor.mkt_rf is null or ff_factor.mkt_rf != x.mkt_rf)
                            OR (ff_factor.smb is null or ff_factor.smb != x.smb)
                            OR (ff_factor.hml is null or ff_factor.hml != x.hml)
                        )
                    ;""")
    print('---> updated {} ff_factor rows.'.format(cursor.rowcount))
    cursor.execute("""INSERT INTO risk_free (date, frequency, rf)
                    SELECT (TO_DATE(date_str, 'YYYYMM') + interval '1 month - 1 day')::date, 'MONTHLY', rf
                    FROM _monthly_ff
                    WHERE NOT EXISTS (select 1 from risk_free f where f.date = (TO_DATE(date_str, 'YYYYMM') + interval '1 month - 1 day')::date and f.frequency = 'MONTHLY')
                    ;""")
    print('---> inserted {} risk_free rows.'.format(cursor.rowcount))
    cursor.execute("""UPDATE risk_free SET rf = x.rf
                    FROM _monthly_ff x
                    WHERE
                        risk_free.date = (TO_DATE(x.date_str, 'YYYYMM') + interval '1 month - 1 day')::date
                        AND risk_free.frequency = 'MONTHLY'
                        AND (risk_free.rf is null or risk_free.rf != x.rf)
                    ;""")
    print('---> updated {} risk_free rows.'.format(cursor.rowcount))
    cursor.execute("DROP TABLE IF EXISTS _monthly_ff CASCADE;")


def import_daily_ff_data_factors_into_sql(file_name, cursor):
    print("-- import_daily_ff_data_factors file={}".format(file_name,))
    # note: the file may be raw as downloaded which is not a directly importable format
    # so pass it through grep to only get valid rows.
    src = "grep '^[0-9]\\{{6\\}}' {}".format(file_name,)
    cursor.execute("DROP TABLE IF EXISTS _daily_ff CASCADE;")
    cursor.execute("CREATE TABLE _daily_ff (date_str text, mkt_rf decimal(8,5), smb decimal(8,5), hml decimal(8,5), rf decimal(8,5), PRIMARY KEY (date_str));")
    cursor.execute("COPY _daily_ff FROM PROGRAM %s WITH (FORMAT CSV);", (src,))
    cursor.execute("""INSERT INTO ff_factor (date, frequency, mkt_rf, smb, hml)
                    SELECT TO_DATE(date_str, 'YYYYMMDD'), 'DAILY', mkt_rf, smb, hml
                    FROM _daily_ff
                    WHERE NOT EXISTS (select 1 from ff_factor f where f.date = TO_DATE(date_str, 'YYYYMMDD') and f.frequency = 'DAILY')
                    ;""")
    print('---> inserted {} ff_factor rows.'.format(cursor.rowcount))
    cursor.execute("""UPDATE ff_factor SET mkt_rf = x.mkt_rf, smb = x.smb, hml = x.hml
                    FROM _daily_ff x
                    WHERE
                        ff_factor.date = TO_DATE(date_str, 'YYYYMMDD')
                        AND ff_factor.frequency = 'DAILY'
                        AND (
                            (ff_factor.mkt_rf is null or ff_factor.mkt_rf != x.mkt_rf)
                            OR (ff_factor.smb is null or ff_factor.smb != x.smb)
                            OR (ff_factor.hml is null or ff_factor.hml != x.hml)
                        )
                    ;""")
    print('---> updated {} ff_factor rows.'.format(cursor.rowcount))
    cursor.execute("""INSERT INTO risk_free (date, frequency, rf)
                    SELECT TO_DATE(date_str, 'YYYYMMDD'), 'DAILY', rf
                    FROM _daily_ff
                    WHERE NOT EXISTS (select 1 from risk_free f where f.date = TO_DATE(date_str, 'YYYYMMDD') and f.frequency = 'DAILY')
                    ;""")
    print('---> inserted {} risk_free rows.'.format(cursor.rowcount))
    cursor.execute("""UPDATE risk_free SET rf = x.rf
                    FROM _daily_ff x
                    WHERE
                        risk_free.date = TO_DATE(x.date_str, 'YYYYMMDD')
                        AND risk_free.frequency = 'DAILY'
                        AND (risk_free.rf is null or risk_free.rf != x.rf)
                    ;""")
    print('---> updated {} risk_free rows.'.format(cursor.rowcount))
    cursor.execute("DROP TABLE IF EXISTS _daily_ff CASCADE;")


def cleanup_incomplete_factors(cursor):
    print("-- cleanup_incomplete_factors")
    # because those fields come from different files with different date coverage
    cursor.execute("DELETE FROM ff_factor WHERE mkt_rf is null or smb is null or hml is null or wml is null;")
    print('---> removed {} incomplete ff_factor rows.'.format(cursor.rowcount))


def cleanup_abnormal_returns(cursor, ticker=None):
    if ticker:
        print("-- cleanup_abnormal_returns ticker={}".format(ticker,))
        cursor.execute("delete from stock_data where ticker = ? and (return > 1 or return = 'NaN');", (ticker,))
    else:
        print("-- cleanup_abnormal_returns")
        cursor.execute("delete from stock_data where return > 1 or return = 'NaN';")
    print('---> removed {} abnormal stock_data rows.'.format(cursor.rowcount))


CONFIG_FILE = 'db.ini'


def main(args):
    if args.reuse:
        # read the existing config 
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
        print('** write config:')
        print(config.write(sys.stdout))
        with open(CONFIG_FILE, 'w') as configfile:
            config.write(configfile)

    # Connect to maintenance database
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

    print('** connect to created DB: {} at {} with user {}'.format(DB_NAME, DB_HOST, DB_USER))
    conn = psycopg2.connect(host=DB_HOST, database=DB_NAME,
                            user=DB_USER, password=DB_PASS)

    conn.autocommit = True
    cursor = conn.cursor()

    # Run the initial schema file to create tables, etc.
    script_dir = os.getcwd() + '/scripts'
    print('** init schema')
    cursor.execute(open(script_dir + "/init_schema.sql", "r").read())

    # Run the initial data load to create tables, etc.
    data_dir = os.getcwd() + '/data'

    if args.add_data:
        ff_data_factors = (data_dir + '/Developed_3_Factors.csv')
        ff_data_factors_daily = (data_dir + '/Developed_3_Factors_Daily.csv')
        ff_mom_factor = (data_dir + '/Developed_MOM_Factor.csv')
        ff_mom_factor_daily = (data_dir + '/Developed_MOM_Factor_Daily.csv')

        carbon_data = (data_dir + '/bmg_carima.csv')
        xop_carbon_data = (data_dir + '/bmg_xop_smog.csv')
        additional_factor_data = (data_dir + '/additional_factor_data.csv')
        sector_breakdown_data = (data_dir + '/spx_sector_breakdown.csv')
        spx_constituent_data = data_dir + '/spx_constituent_weights.csv'
        msci_constituent_data = data_dir + '/msci_constituent_details.csv'
        msci_etf_sector_data = data_dir + '/msci_etf_sector_mapping.csv'
        bond_factor_data = data_dir + '/interest_rates.csv'

        print('** importing Developed_3_Factors')
        import_monthly_ff_data_factors_into_sql(ff_data_factors, cursor)
        print('** importing Developed_MOM_Factor')
        import_monthly_ff_mom_factor_into_sql(ff_mom_factor, cursor)

        print('** importing Developed_3_Factors_Daily')
        import_daily_ff_data_factors_into_sql(ff_data_factors_daily, cursor)
        print('** importing Developed_MOM_Factor_Daily')
        import_daily_ff_mom_factor_into_sql(ff_mom_factor_daily, cursor)

        print('** cleanup imported factors')
        cleanup_incomplete_factors(cursor)

        print('** importing carbon_risk_factor CARIMA')
        import_data_into_sql("carbon_risk_factor",
                             carbon_data, cursor, bmg="CARIMA")
        print('** importing carbon_risk_factor DEFAULT')
        import_data_into_sql("carbon_risk_factor",
                             xop_carbon_data, cursor, bmg="DEFAULT")
        print('** importing additional_factors')
        import_data_into_sql("additional_factors",
                             additional_factor_data, cursor)

        # import the bond_factor
        print('** importing bond factor')
        import_bond_factor_into_sql(bond_factor_data, cursor)

        print('** adding stocks IVV and XWD.TO')
        cursor.execute(
            "INSERT INTO stocks (ticker, name) VALUES ('IVV', 'iShares S&P 500');")
        cursor.execute(
            "INSERT INTO stocks (ticker, name) VALUES ('XWD.TO', 'iShares MSCI World');")

        print('** adding stocks MSCI_SECTOR_ETFS')
        cursor.execute(
            "INSERT INTO stocks (ticker, name) VALUES ('MSCI_SECTOR_ETFS', 'MSCI Sector ETF''s');")

        print('** importing stocks')
        import_data_into_sql("stocks", sector_breakdown_data, cursor)

        # import components and weights of spx
        print('** importing stock_components IVV')
        import_spx_constituents_into_sql(spx_constituent_data, cursor, "IVV")

        # import components and weights of msci
        print('** importing stock_components XWD.TO')
        import_msci_constituents_into_sql(msci_constituent_data, cursor, "XWD.TO")

        # import components of msci etf
        import_msci_etf_sector_into_sql(msci_etf_sector_data, cursor, "MSCI_SECTOR_ETFS")

        # set the component sector info
        cursor.execute("""UPDATE stock_components
            SET sector = x.sector, sub_sector = x.sub_sector 
            FROM stocks x
            WHERE x.ticker = stock_components.component_stock
            ;""")

    print('All DONE')


# run
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--add_data", default=False, action='store_true',
                        help="Import default Fama French factors, monthly carbno risk factors, and index composition data")
    parser.add_argument("-R", "--reuse", action='store_true', help='Reuse the current db.ini config instead of asking for the settings')
    main(parser.parse_args())
