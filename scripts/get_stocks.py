import argparse
import pandas as pd
from setup_db import cleanup_abnormal_returns
import stock_price_function as spf
import input_function
import db
from pg import DataError
from decimal import Decimal
import numpy as np


conn = db.get_db_connection()


def load_stocks_csv(filename):
    if not filename:
        return None
    print('Loading stock tickers CSV {} ...'.format(filename))
    all_stock_data = pd.read_csv(filename, header=None)
    return all_stock_data.values


def import_stock(stock_name, always_update_details=False, frequency='MONTHLY', verbose=False):
    try:
        if verbose:
            print("*** importing stock {}".format(stock_name))
        stock_data = load_stocks_data(stock_name, always_update_details=always_update_details, frequency=frequency)
        if verbose and (stock_data is None or stock_data.empty):
            print("*** no stock data could be loaded for {}".format(stock_name))
        try:
            import_stocks_into_db(stock_name, stock_data, frequency=frequency)
        except DataError as e:
            print(
                '!! Cannot import {} due to DataError inserting the data:'.format(stock_name))
            print(e)
            # return an empty data frame in that case
            return pd.DataFrame()
    except ValueError as ve:
        print(ve)
        return pd.DataFrame()
    return stock_data


def update_stocks_info_data(stock_name):
    info = spf.stock_details_grabber(stock_name)
    if info is None:
        print('!! Did not get any stock data for %s'.format(stock_name))
        return
    sql = '''
        INSERT INTO stocks (ticker, name, sector, sub_sector, 
            ebitda, enterprise_value, enterprise_to_ebitda, price_to_book,
            total_cash, total_debt, shares_outstanding)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (ticker) DO
        UPDATE SET
            name = EXCLUDED.name,
            sector = EXCLUDED.sector,
            sub_sector = EXCLUDED.sub_sector,
            ebitda = EXCLUDED.ebitda,
            enterprise_value = EXCLUDED.enterprise_value,
            enterprise_to_ebitda = EXCLUDED.enterprise_to_ebitda,
            price_to_book = EXCLUDED.price_to_book,
            total_cash = EXCLUDED.total_cash,
            total_debt = EXCLUDED.total_debt,
            shares_outstanding = EXCLUDED.shares_outstanding
        ;
    '''
    with conn.cursor() as cursor:
        cursor.execute(sql, (stock_name, info.get('longName'), info.get('sector'), info.get('industry'),
                             info.get('ebitda'), info.get('enterpriseValue'), info.get('enterpriseToEbitda'),
                             info.get('priceToBook'), info.get('totalCash'), info.get('totalDebt'),
                             info.get('sharesOutstanding')))


def check_stocks_info_exist(stock_name):
    # check if the stock is in the DB stocks table
    sql = 'SELECT 1 FROM stocks WHERE ticker = %s;'
    with conn.cursor() as cursor:
        cursor.execute(sql, (stock_name,))
        result = cursor.fetchone()
        if not result:
            return False
        return True



def load_stocks_data(stock_name, always_update_details=False, frequency='MONTHLY'):
    has_info = check_stocks_info_exist(stock_name)
    if always_update_details or not has_info:
        update_stocks_info_data(stock_name)
    stock_data = spf.stock_df_grab(stock_name, frequency=frequency)
    stock_data = input_function.convert_to_form(stock_data)
    return stock_data


def delete_stock_from_db(ticker):
    sql = '''DELETE FROM
        stock_data
        WHERE ticker = %s;'''
    with conn.cursor() as cursor:
        cursor.execute(sql, (ticker,))


def delete_carbon_risk_factor_from_db(factor_name):
    sql = '''DELETE FROM
        carbon_risk_factor
        WHERE factor_name = %s;'''
    with conn.cursor() as cursor:
        cursor.execute(sql, (factor_name,))


def load_carbon_risk_factor_from_db(factor_name, frequency='MONTHLY'):
    sql = '''SELECT date, bmg
        FROM carbon_risk_factor
        WHERE factor_name = %s and frequency = %s
        ORDER BY date
        '''
    return pd.read_sql_query(sql, con=db.DB_CREDENTIALS,
                             index_col='date', params=(factor_name,frequency,))


def get_components_from_db(stock_name):
    sql = '''SELECT component_stock, percentage
             FROM stock_components
             WHERE ticker = %s
             ORDER BY component_stock'''
    with conn.cursor() as cursor:
        cursor.execute(sql, (stock_name,))
        return cursor.fetchall()


def import_carbon_risk_factor_into_db(data, frequency='MONTHLY'):
    sql = '''INSERT INTO
        carbon_risk_factor (date, frequency, factor_name, bmg)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (date, frequency, factor_name) DO
        UPDATE SET bmg = EXCLUDED.bmg;'''
    with conn.cursor() as cursor:
        for index, row in data.iterrows():
            cursor.execute(sql, (index, frequency, row['factor_name'], row['bmg']))


def import_stocks_into_db(stock_name, stock_data, frequency='MONTHLY'):
    sql = '''INSERT INTO
        stock_data (ticker, frequency, date, close, return)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (ticker, frequency, date) DO
        UPDATE SET close = EXCLUDED.close, return = EXCLUDED.return;'''
    with conn.cursor() as cursor:
        # we store both the values of Close and the Returns from pct_change
        pc = stock_data.pct_change()
        pc.rename(columns={'Close': 'r'}, inplace=True)
        stock_data = pd.merge(stock_data, pc, on='date_converted')
        # Remove abnormal return values
        stock_data = stock_data[stock_data['r'] <= 1]
        for index, row in stock_data.iterrows():
            #print('-- {} = {} : {}%'.format(index, row['Close'], row['r']))
            cursor.execute(sql, (stock_name, frequency, index, row['Close'], row['r']))


def import_stocks_returns_into_db(stock_name, stock_data, frequency='MONTHLY'):
    sql = '''INSERT INTO
        stock_data (ticker, frequency, date, return)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (ticker, frequency, date) DO
        UPDATE SET return = EXCLUDED.return;'''
    with conn.cursor() as cursor:
        for index, row in stock_data.iterrows():
            cursor.execute(sql, (stock_name, frequency, index, row['return']))


def load_stocks_returns_from_db(stock_name, frequency='MONTHLY', verbose=False):
    df = load_stocks_data_with_returns_from_db(
        stock_name, with_components=True, import_when_missing=True, frequency=frequency, verbose=verbose)
    is_composite = 'composite_return' in df.columns
    # remove columns we do not need here
    if is_composite:
        df = df[['composite_return']].rename(
            columns={'composite_return': 'return'})
    else:
        df = df[['return']]
    # if it was a composite, save the resulting return values in the DB as well
    import_stocks_returns_into_db(stock_name, df, frequency=frequency)
    return df


def load_stocks_data_with_returns_from_db(stock_name, with_components=False, import_when_missing=False, always_update_details=False, frequency='MONTHLY', verbose=False):
    sql = '''SELECT date, close, return
        FROM stock_data
        WHERE ticker = %s and frequency = %s
        ORDER BY date
        '''
    df = pd.read_sql_query(sql, con=db.DB_CREDENTIALS,
                           index_col='date', params=(stock_name,frequency,))
    if (df is None or df.empty) and import_when_missing:
        if verbose:
            print("*** no data in DB for {}, will import it".format(stock_name))
        import_stock(stock_name, always_update_details=always_update_details, frequency=frequency)
        # try again
        df = pd.read_sql_query(sql, con=db.DB_CREDENTIALS,
                               index_col='date', params=(stock_name,frequency,))

    if with_components:
        components = get_components_from_db(stock_name)
        if not components:
            # not a composite ?
            if verbose:
                print('*** stock {} is not a composite (no components found) !'.format(stock_name))
            return df
        else:
            if verbose:
                print("*** loading components for {} ...".format(stock_name))
            for (ticker, percentage) in components:
                if verbose:
                    print("*** loading component {} as {} of {} ...".format(ticker, percentage, stock_name))
                if not percentage:
                    print("!!! Missing percentage of {} as component of {}".format(ticker, stock_name))
                    continue
                df2 = load_stocks_data_with_returns_from_db(
                    ticker, import_when_missing=import_when_missing, frequency=frequency, verbose=verbose)
                df = df.join(df2, how="outer",
                             rsuffix='_{}'.format(ticker))
                df['percentage_{}'.format(ticker)] = percentage
                df['p_return_{}'.format(ticker)] = df['return_{}'.format(
                    ticker)].astype(str).apply(Decimal) * percentage
            # sum the specific columns
            df['sum_p_returns'] = df.filter(
                regex="p_return").astype(float).sum(axis=1)
            df['sum_percentages'] = df.filter(
                regex="percentage").sum(axis=1)
            df['composite_return'] = df['sum_p_returns'] / \
                df['sum_percentages']
    return df


def load_stocks_from_db(stock_name, frequency='MONTHLY'):
    sql = '''SELECT date, close
        FROM stock_data
        WHERE ticker = %s and frequency = %s
        ORDER BY date
        '''
    return pd.read_sql_query(sql, con=db.DB_CREDENTIALS,
                             index_col='date', params=(stock_name,frequency,))


def load_all_stocks_from_db(frequency='MONTHLY'):
    sql = '''SELECT *
        FROM stock_data
        WHERE frequency = %s
        ORDER BY ticker, date
        '''
    return pd.read_sql_query(sql, con=db.DB_CREDENTIALS,
                             index_col='date', params=(frequency,))


def load_stocks_defined_in_db():
    sql = '''SELECT ticker FROM stocks ORDER BY ticker'''
    df = pd.read_sql_query(sql, con=db.DB_CREDENTIALS,
                           index_col='ticker')
    return df.index


def get_stock_details(ticker):
    sql = '''SELECT * FROM stocks WHERE ticker = %s'''
    df = pd.read_sql_query(sql, con=db.DB_CREDENTIALS,
                           index_col='ticker', params=(ticker,))
    return df


def import_stock_or_returns(stock_name, always_update_details=False, frequency='MONTHLY', verbose=False):
    df = import_stock(stock_name, always_update_details=always_update_details, frequency=frequency, verbose=verbose)
    if (df is None or df.empty) and get_components_from_db(stock_name):
        # for a composite, we can compute and import the returns only
        print("** Stock {} is a composite, will only compute and save the returns ...".format(stock_name))
        df = load_stocks_returns_from_db(stock_name, verbose=verbose)

    if verbose:
        print("results -> ")
        print(df)
    else:
        print("-> imported {} rows".format(len(df)))


def main(args):
    if args.clean_bad_returns:
        with conn.cursor() as cursor:
            cleanup_abnormal_returns(cursor)
            print("-- {} entries affected.".format(cursor.rowcount))
        return True
    if args.from_db:
        stocks = load_stocks_defined_in_db()

        for i in range(0, len(stocks)):
            stock_name = stocks[i]
            print('* loading stocks for {} ... '.format(stock_name))
            import_stock_or_returns(stock_name, always_update_details=args.update_stocks_details, frequency=args.frequency, verbose=args.verbose)

    elif args.delete:
        delete_stock_from_db(args.delete)
    elif args.ticker:
        import_stock_or_returns(args.ticker, always_update_details=args.update_stocks_details, frequency=args.frequency, verbose=args.verbose)
    elif args.show:
        sd = get_stock_details(args.show)
        print('-- Stock details for {}'.format(args.show))
        print(sd.T)
        if args.with_returns:
            df = load_stocks_data_with_returns_from_db(
                args.show, with_components=args.with_components, frequency=args.frequency, verbose=args.verbose)
        else:
            df = load_stocks_from_db(args.show, frequency=args.frequency)
        print('Loaded from DB: {} entries'.format(len(df)))
        print(' -- sample (truncated) -- ')
        print(df)
        if args.output:
            df.to_csv(args.output)
    elif args.file:
        stocks = load_stocks_csv(args.file)
        if stocks is None:
            print('Error reading CSV file {}'.format(args.file))
            return False

        for i in range(0, len(stocks)):
            stock_name = stocks[i].item(0)
            print("Trying to get: " + stock_name)
            import_stock(stock_name, always_update_details=args.update_stocks_details, frequency=args.frequency)
    else:
        return False
    return True


# run
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file",
                        help="specify the CSV file of stock tickers to import")
    parser.add_argument("-d", "--from_db", action='store_true',
                        help="import of tickers in the stocks table of the Database instead of using a CSV file")
    parser.add_argument("-t", "--ticker",
                        help="specify a single ticker to import, ignores the CSV file")
    parser.add_argument("-x", "--delete",
                        help="specify a single ticker to delete")
    parser.add_argument("-s", "--show",
                        help="Show the data for a given ticker, for testing")
    parser.add_argument("--frequency", default='MONTHLY',
                        help="Frequency to use for the various series, eg: MONTHLY, DAILY")
    parser.add_argument("--update_stocks_details", action='store_true',
                        help="When getting stocks data, always update the stock details from YF in the stocks entry even if a value already exist")
    parser.add_argument("--with_returns", action='store_true',
                        help="When showing, also show the return values")
    parser.add_argument("--clean_bad_returns", action='store_true',
                        help="Cleanup the bad returns (NaN and > 1) for a given stock with -t else for all stocks")
    parser.add_argument("--with_components", action='store_true',
                        help="When showing, JOIN the values of the component stocks")
    parser.add_argument("-o", "--output",
                        help="When showing, save all the data into this CSV file")
    parser.add_argument("-v", "--verbose", action='store_true',
                        help="More verbose output.")
    if not main(parser.parse_args()):
        parser.print_help()
