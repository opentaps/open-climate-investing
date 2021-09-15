import argparse
import pandas as pd
import stock_price_function as spf
import input_function
import db
import get_stocks
import factor_regression


csv_file = 'stock_tickers.csv'

conn = db.get_db_connection()


def load_carbon_data_from_db():
    sql = '''SELECT
            date as "Date",
            bmg as "BMG"
        FROM carbon_risk_factor
        ORDER BY date
        '''
    return pd.read_sql_query(sql, con=db.DB_CREDENTIALS,
                             index_col='Date')


def load_ff_data_from_db():
    sql = '''SELECT
            date as "Date",
            mkt_rf as "Mkt-RF",
            smb as "SMB",
            hml as "HML",
            wml as "WML"
        FROM ff_factor
        ORDER BY date
        '''
    return pd.read_sql_query(sql, con=db.DB_CREDENTIALS,
                             index_col='Date')


def run_regression(ticker, start_date, carbon_data=None, ff_data=None, verbose=False, silent=False, store=False):
    if carbon_data is None:
        carbon_data = load_carbon_data_from_db()
        if verbose:
            print('Loaded carbon_data ...')
            print(carbon_data)
    elif verbose:
        print('Got carbon_data ...')
        print(carbon_data)
    if ff_data is None:
        ff_data = load_ff_data_from_db()
        if verbose:
            print('Loaded ff_data ...')
            print(ff_data)
    elif verbose:
        print('Got ff_data ...')
        print(ff_data)

    stock_data = get_stocks.load_stocks_data(ticker)
    if len(stock_data) == 0:
        print('No stock data for {}, loading ...'.format(ticker))
        stock_data = get_stocks.import_stock(ticker)
    if len(stock_data) == 0:
        print('No stock data for ticker {} !'.format(ticker))
        return
    # convert to pct change
    stock_data = stock_data.pct_change(periods=1)
    start_date, max_date, model_output, coef_df_simple = factor_regression.run_regression(
        stock_data, carbon_data, ff_data, ticker, start_date, verbose=verbose, silent=silent)
    if model_output is False:
        print('!! Error running regression on stock {}'.format(ticker))
        return
    if store:
        print('Ran regression for {} from {} to {} ...'.format(
            ticker, start_date, max_date))
        # store results in the DB
        fields = ['Constant', 'BMG', 'Mkt-RF', 'SMB', 'HML', 'WML',
                  'Jarque-Bera', 'Breusch-Pagan', 'Durbin-Watson', 'R Squared']
        index_to_sql_dict = {
            'std err': '_std_error',
            't': '_t_stat',
            'P>|t|': '_p_gt_abs_t',
        }
        sql_params = {
            'ticker': ticker,
            'from_date': start_date,
            'thru_date': max_date
        }
        for index, row in coef_df_simple.iterrows():
            for f in fields:
                sql_field = f.lower().replace(' ', '_').replace('-', '_')
                if index != 'coef':
                    sql_field += index_to_sql_dict[index]
                if row[f]:
                    sql_params[sql_field] = row[f]
        store_regression_into_db(sql_params)


def fetch_regression_from_db(ticker, from_date):
    sql = '''SELECT * FROM stock_stats WHERE ticker = %s and from_date >= %s;'''
    return pd.read_sql_query(sql, con=db.DB_CREDENTIALS,
                             index_col='ticker', params=(ticker, from_date,))


def store_regression_into_db(sql_params):
    del_sql = '''DELETE FROM stock_stats WHERE ticker = %s and from_date = %s and thru_date = %s;'''
    placeholder = ", ".join(["%s"] * len(sql_params))
    stmt = "INSERT INTO stock_stats ({columns}) values ({values});".format(
        columns=",".join(sql_params.keys()), values=placeholder)
    with conn.cursor() as cursor:
        cursor.execute(
            del_sql, (sql_params['ticker'], sql_params['from_date'], sql_params['thru_date']))
        cursor.execute(stmt, list(sql_params.values()))


def main(args):
    if args.ticker:
        run_regression(args.ticker, args.date,
                       verbose=args.verbose, silent=True, store=True)
    elif args.dryrun:
        run_regression(args.dryrun, args.date, verbose=args.verbose)
    elif args.show:
        df = fetch_regression_from_db(args.show, args.date)
        print('Loaded from DB: {} entries'.format(len(df)))
        print(' -- sample (truncated) -- ')
        print(df)
    else:
        carbon_data = load_carbon_data_from_db()
        ff_data = load_ff_data_from_db()
        stocks = get_stocks.load_stocks_csv(args.file)
        for i in range(0, len(stocks)):
            stock_name = stocks[i].item()
            run_regression(stock_name, args.date, carbon_data=carbon_data,
                           ff_data=ff_data, verbose=args.verbose, silent=True, store=True)


# run
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file", default=csv_file,
                        help="specify the CSV file of stock tickers to import")
    parser.add_argument("-t", "--ticker",
                        help="specify a single ticker to run the regression for, ignores the CSV file")
    parser.add_argument("-n", "--dryrun",
                        help="Run and show the regression data for a given ticker, does not store results")
    parser.add_argument("-s", "--show",
                        help="Show the regression data for a given ticker from the DB, does not run the regression, for testing")
    parser.add_argument("-d", "--date", default='2000-01-01',
                        help="Sets the start date for the regression, must be in the YYYY-MM-DD format")
    parser.add_argument("-v", "--verbose", action='store_true',
                        help="More verbose output")
    main(parser.parse_args())
