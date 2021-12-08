import argparse
import pandas as pd
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


def import_stock(stock_name):
    try:
        stock_data = load_stocks_data(stock_name)
        try:
            import_stocks_into_db(stock_name, stock_data)
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


def load_stocks_data(stock_name):
    stock_data = spf.stock_df_grab(stock_name)
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


def load_carbon_risk_factor_from_db(factor_name):
    sql = '''SELECT date, bmg
        FROM carbon_risk_factor
        WHERE factor_name = %s
        ORDER BY date
        '''
    return pd.read_sql_query(sql, con=db.DB_CREDENTIALS,
                             index_col='date', params=(factor_name,))


def import_carbon_risk_factor_into_db(data):
    sql = '''INSERT INTO
        carbon_risk_factor (date, factor_name, bmg)
        VALUES (%s, %s, %s)
        ON CONFLICT (date, factor_name) DO
        UPDATE SET bmg = EXCLUDED.bmg;'''
    with conn.cursor() as cursor:
        for index, row in data.iterrows():
            cursor.execute(sql, (index, row['factor_name'], row['bmg']))


def import_stocks_into_db(stock_name, stock_data):
    sql = '''INSERT INTO
        stock_data (ticker, date, close, return)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (ticker, date) DO
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
            cursor.execute(sql, (stock_name, index, row['Close'], row['r']))


def import_stocks_returns_into_db(stock_name, stock_data):
    sql = '''INSERT INTO
        stock_data (ticker, date, return)
        VALUES (%s, %s, %s)
        ON CONFLICT (ticker, date) DO
        UPDATE SET return = EXCLUDED.return;'''
    with conn.cursor() as cursor:
        for index, row in stock_data.iterrows():
            cursor.execute(sql, (stock_name, index, row['return']))


def load_stocks_returns_from_db(stock_name):
    df = load_stocks_data_with_returns_from_db(
        stock_name, with_components=True, import_when_missing=True)
    is_composite = 'composite_return' in df.columns
    # remove columns we do not need here
    if is_composite:
        df = df[['composite_return']].rename(
            columns={'composite_return': 'return'})
    else:
        df = df[['return']]
    # if it was a composite, save the resulting return values in the DB as well
    import_stocks_returns_into_db(stock_name, df)
    return df


def load_stocks_data_with_returns_from_db(stock_name, with_components=False, import_when_missing=False):
    sql = '''SELECT date, close, return
        FROM stock_data
        WHERE ticker = %s
        ORDER BY date
        '''
    df = pd.read_sql_query(sql, con=db.DB_CREDENTIALS,
                           index_col='date', params=(stock_name,))
    if (df is None or df.empty) and import_when_missing:
        import_stock(stock_name)
        # try again
        df = pd.read_sql_query(sql, con=db.DB_CREDENTIALS,
                               index_col='date', params=(stock_name,))

    if with_components:
        sql = '''SELECT component_stock, percentage
             FROM stock_components
             WHERE ticker = %s
             ORDER BY component_stock'''
        with conn.cursor() as cursor:
            cursor.execute(sql, (stock_name,))
            components = cursor.fetchall()
            if not components:
                # not a composite ?
                print(
                    '*** stock {} is not a composite (no components found) !'.format(stock_name))
                return df
            else:
                for (ticker, percentage) in components:
                    df2 = load_stocks_data_with_returns_from_db(
                        ticker, import_when_missing=import_when_missing)
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


def load_stocks_from_db(stock_name):
    sql = '''SELECT date, close
        FROM stock_data
        WHERE ticker = %s
        ORDER BY date
        '''
    return pd.read_sql_query(sql, con=db.DB_CREDENTIALS,
                             index_col='date', params=(stock_name,))


def load_all_stocks_from_db():
    sql = '''SELECT *
        FROM stock_data
        ORDER BY ticker, date
        '''
    return pd.read_sql_query(sql, con=db.DB_CREDENTIALS,
                             index_col='date')


def load_stocks_defined_in_db():
    sql = '''SELECT ticker FROM stocks ORDER BY ticker'''
    df = pd.read_sql_query(sql, con=db.DB_CREDENTIALS,
                           index_col='ticker')
    return df.index


def main(args):
    if args.from_db:
        stocks = load_stocks_defined_in_db()

        for i in range(0, len(stocks)):
            stock_name = stocks[i]
            print('* loading stocks for {} ... '.format(stock_name))
            import_stock(stock_name)

    elif args.delete:
        delete_stock_from_db(args.delete)
    elif args.ticker:
        import_stock(args.ticker)
    elif args.show:
        if args.with_returns:
            df = load_stocks_data_with_returns_from_db(
                args.show, with_components=args.with_components)
        else:
            df = load_stocks_from_db(args.show)
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
            stock_name = stocks[i].item()
            print("Trying to get: " + stock_name)
            import_stock(stock_name)
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
    parser.add_argument("--with_returns", action='store_true',
                        help="When showing, also show the return values")
    parser.add_argument("--with_components", action='store_true',
                        help="When showing, JOIN the values of the component stocks")
    parser.add_argument("-o", "--output",
                        help="When showing, save all the data into this CSV file")
    if not main(parser.parse_args()):
        parser.print_help()
