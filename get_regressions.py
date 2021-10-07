import argparse
from dateutil.relativedelta import relativedelta
import pandas as pd
import db
import get_stocks
import factor_regression


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


def load_rf_data_from_db():
    sql = '''SELECT
            date as "Date",
            rf as "Rf"
        FROM risk_free
        ORDER BY date
        '''
    return pd.read_sql_query(sql, con=db.DB_CREDENTIALS,
                             index_col='Date')


def run_regression(ticker, start_date, end_date, interval, carbon_data=None, ff_data=None, rf_data=None, verbose=False, silent=False, store=False, batch=False):
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
    if rf_data is None:
        rf_data = load_rf_data_from_db()
        if verbose:
            print('Loaded rf_data ...')
            print(rf_data)
    elif verbose:
        print('Got risk-fre rate')
        print(rf_data)

    stock_data = get_stocks.import_stock(ticker)
    if len(stock_data) == 0:
        print('No stock data for {} !'.format(ticker))
        return
    # convert to pct change
    stock_data = stock_data.pct_change(periods=1)

    run_regression_internal(stock_data, carbon_data, ff_data, rf_data,
                            ticker, start_date, end_date, interval, verbose, silent, store, batch)


def run_regression_internal(stock_data, carbon_data, ff_data, rf_data, ticker, start_date, end_date, interval, verbose, silent, store, batch):

    try:
        if start_date:
            start_date = factor_regression.parse_date('Start', start_date)
        else:
            # use the common start date of all series:
            start_date = max(min(stock_data.index), min(
                carbon_data.index), min(ff_data.index), min(rf_data.index))

        interval_dt = relativedelta(months=interval)
        if end_date:
            end_date = factor_regression.parse_date('End Date', end_date)
        else:
            end_date = start_date + interval_dt
        start_date, end_date, data_start_date, data_end_date, model_output, coef_df_simple = factor_regression.run_regression(
            stock_data, carbon_data, ff_data, rf_data, ticker, start_date, end_date=end_date, verbose=verbose, silent=silent)
    except factor_regression.DateInRangeError as e:
        print('!! Error running regression on stock {} from {} to {}: {}'.format(
            ticker, start_date, end_date, e))
        if batch and end_date < e.min_date:
            # if in a batch, try to move the window until the end_date is after the min_date
            # while keeping the alignment with start_date
            dt = relativedelta(months=1)
            while end_date < e.min_date:
                start_date += dt
                end_date += dt
            run_regression_internal(stock_data, carbon_data, ff_data, rf_data,
                                    ticker, start_date+dt, interval, verbose, silent, store, batch)

        return
    except ValueError as e:
        print('!! Error running regression on stock {} from {} to {}: {}'.format(
            ticker, start_date, end_date, e))
        return

    if model_output is False:
        print('!! Error running regression on stock {} from {} to {}'.format(
            ticker, start_date, end_date))
        return

    # stop running when the data_end_date is < end_date (we no longer have enough data)
    if data_end_date < end_date:
        print('!! Error running regression on stock {} from {} to {} (not enough available data, ends in {})'.format(
            ticker, start_date, end_date, data_end_date))
        return

    if store:
        print('Ran regression for {} from {} to {} ...'.format(
            ticker, start_date, end_date))
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
            'thru_date': end_date,
            'data_from_date': data_start_date,
            'data_thru_date': data_end_date,
        }
        for index, row in coef_df_simple.iterrows():
            for f in fields:
                sql_field = f.lower().replace(' ', '_').replace('-', '_')
                if index != 'coef':
                    sql_field += index_to_sql_dict[index]
                if row[f] is not None and row[f] != '':
                    sql_params[sql_field] = row[f]
        store_regression_into_db(sql_params)

    if not batch:
        return

    # recurse the new interval
    dt = relativedelta(months=1)
    run_regression_internal(stock_data, carbon_data, ff_data, rf_data,
                            ticker, start_date+dt, interval, verbose, silent, store, batch)


def fetch_regressions_from_db(ticker, start_date=None, end_date=None):
    sql = '''SELECT * FROM stock_stats WHERE ticker = %s'''
    params = [ticker]
    if start_date is not None:
        sql += ' and from_date >= %s'
        params.append(start_date)
    if end_date is not None:
        sql += ' and thru_date <= %s'
        params.append(end_date)
    return pd.read_sql_query(sql, con=db.DB_CREDENTIALS,
                             index_col='ticker', params=params)


def fetch_single_regression_from_db(ticker, from_date, end_date):
    sql = '''SELECT * FROM stock_stats WHERE ticker = %s and from_date = %s and thru_date = %s'''
    params = (ticker, from_date, end_date)
    return pd.read_sql_query(sql, con=db.DB_CREDENTIALS,
                             index_col='ticker', params=params)


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
    if args.show and not args.start_date:
        print('Start date is required, add it with -d YYYY-MM-DD')
        return
    if args.from_db:
        carbon_data = load_carbon_data_from_db()
        ff_data = load_ff_data_from_db()
        rf_data = load_rf_data_from_db()
        stocks = get_stocks.load_stocks_defined_in_db()

        for i in range(0, len(stocks)):
            stock_name = stocks[i]
            print('* running regression for {} ... '.format(stock_name))
            run_regression(stock_name, start_date=args.start_date, end_date=args.end_date, interval=args.interval, carbon_data=carbon_data,
                           ff_data=ff_data, rf_data=rf_data, verbose=args.verbose, silent=(not args.dryrun), store=(args.dryrun), batch=args.batch)
    elif args.ticker:
        run_regression(args.ticker, args.start_date, end_date=args.end_date, interval=args.interval,
                       verbose=args.verbose, store=(args.dryrun), batch=args.batch, silent=(not args.dryrun and args.batch))
    elif args.list:
        df = fetch_regressions_from_db(
            args.list, start_date=args.start_date, end_date=args.end_date)
        print('Loaded from DB: {} entries'.format(len(df)))
        print(' -- sample (truncated) -- ')
        print(df)
    elif args.show:
        df = fetch_single_regression_from_db(
            args.show, args.start_date, args.end_date)
        if len(df):
            # format the dataFrame to be more readable
            print(df.T)
        else:
            print('No data found.')
    else:
        carbon_data = load_carbon_data_from_db()
        ff_data = load_ff_data_from_db()
        rf_data = load_rf_data_from_db()
        stocks = get_stocks.load_stocks_defined_in_db(args.file)
        for i in range(0, len(stocks)):
            stock_name = stocks[i].item()
            run_regression(stock_name, start_date=args.start_date, end_date=args.end_date, interval=args.interval, carbon_data=carbon_data,
                           ff_data=ff_data, rf_data=rf_data, verbose=args.verbose, silent=(not args.dryrun), store=(not args.dryrun), batch=args.batch)


# run
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file",
                        help="specify the CSV file of stock tickers to import")
    parser.add_argument("-D", "--from_db", action='store_true',
                        help="import of tickers in the stocks table of the Database instead of using a CSV file")
    parser.add_argument("-t", "--ticker",
                        help="specify a single ticker to run the regression for, ignores the CSV file")
    parser.add_argument("-n", "--dryrun", action='store_false',
                        help="Only shows the results, do not store the results in the DB")
    parser.add_argument("-l", "--list",
                        help="Show all the regression data for a given ticker from the DB, does not run the regression, optionally use with --start_date and --end_date to filter results")
    parser.add_argument("-s", "--show",
                        help="Show the regression data for a given ticker from the DB, does not run the regression, must use --start_date and --end_date to select which data to display")
    parser.add_argument("-d", "--start_date",
                        help="Sets the start date for the regression, must be in the YYYY-MM-DD format, defaults to the start date of all the data series for a given stock")
    parser.add_argument("-e", "--end_date",
                        help="Sets the end date for the regression, must be in the YYYY-MM-DD format")
    parser.add_argument("-i", "--interval", default=60, type=int,
                        help="Sets number of months for the regresssion interval, defaults to 60")
    parser.add_argument("-b", "--batch", action='store_true',
                        help="Runs the regresssion for multiple time windows of [interval] months length, starting at start_date, shifted by one month per run, until the regression no longer returns data")
    parser.add_argument("-v", "--verbose", action='store_true',
                        help="More verbose output")
    main(parser.parse_args())
