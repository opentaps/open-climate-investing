import argparse
import pandas as pd
import stock_price_function as spf
import input_function
import db


conn = db.get_db_connection()


def load_stocks_csv(filename):
    print('Loading stock tickers CSV {} ...'.format(filename))
    all_stock_data = pd.read_csv(filename, header=None)
    return all_stock_data.values


def import_stock(stock_name):
    stock_data = load_stocks_data(stock_name)
    import_stocks_into_db(stock_name, stock_data)
    return stock_data


def load_stocks_data(stock_name):
    stock_data = spf.stock_df_grab(stock_name)
    stock_data = input_function.convert_to_form(stock_data)
    return stock_data


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
        for index, row in stock_data.iterrows():
            #print('-- {} = {} : {}%'.format(index, row['Close'], row['r']))
            cursor.execute(sql, (stock_name, index, row['Close'], row['r']))


def load_stocks_from_db(stock_name):
    sql = '''SELECT date, close
        FROM stock_data
        WHERE ticker = %s
        ORDER BY date
        '''
    return pd.read_sql_query(sql, con=db.DB_CREDENTIALS,
                             index_col='date', params=(stock_name,))


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
            import_stock(stock_name)

    elif args.ticker:
        import_stock(args.ticker)
    elif args.show:
        df = load_stocks_from_db(args.show)
        print('Loaded from DB: {} entries'.format(len(df)))
        print(' -- sample (truncated) -- ')
        print(df)
    else:
        stocks = load_stocks_csv(args.file)

        for i in range(0, len(stocks)):
            stock_name = stocks[i].item()
            import_stock(stock_name)


# run
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file",
                        help="specify the CSV file of stock tickers to import")
    parser.add_argument("-D", "--from_db", action='store_true',
                        help="import of tickers in the stocks table of the Database instead of using a CSV file")
    parser.add_argument("-t", "--ticker",
                        help="specify a single ticker to import, ignores the CSV file")
    parser.add_argument("-s", "--show",
                        help="Show the data for a given ticker, for testing")
    main(parser.parse_args())
