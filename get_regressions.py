import argparse
from dateutil.relativedelta import relativedelta
import pandas as pd
import db
import get_stocks
import factor_regression
import input_function
import datetime


conn = db.get_db_connection()


def load_stocks_csv(filename):
    print('Loading stock tickers CSV {} ...'.format(filename))
    all_stock_data = pd.read_csv(filename, header=None)
    return all_stock_data.values


def load_carbon_data_from_db(factor_name, frequency='MONTHLY'):
    sql = '''SELECT
            date as "Date",
            bmg as "BMG"
        FROM carbon_risk_factor
        WHERE factor_name = %s and frequency = %s
        ORDER BY date
        '''
    return pd.read_sql_query(sql, con=db.DB_CREDENTIALS,
                             index_col='Date', params=(factor_name,frequency,))


def load_ff_data_from_db(frequency='MONTHLY'):
    sql = '''SELECT
            date as "Date",
            mkt_rf as "Mkt-RF",
            smb as "SMB",
            hml as "HML",
            wml as "WML"
        FROM ff_factor
        WHERE frequency = %s
        ORDER BY date
        '''
    return pd.read_sql_query(sql, con=db.DB_CREDENTIALS,
                             index_col='Date', params=(frequency,))


def load_rf_data_from_db(frequency='MONTHLY'):
    sql = '''SELECT
            date as "Date",
            rf as "Rf"
        FROM risk_free
        WHERE frequency = %s
        ORDER BY date
        '''
    return pd.read_sql_query(sql, con=db.DB_CREDENTIALS,
                             index_col='Date', params=(frequency,))


def bulk_regression_transformer(final_data, ff_names, rf_names, factor_name, interval, frequency='MONTHLY'):
    start_time = datetime.datetime.now()
    ticker_names = final_data['ticker'].unique().tolist()
    start_date = min(final_data.index.values)
    end_date = max(final_data.index.values)
    for temp_ticker in ticker_names:
        temp_data = final_data.loc[final_data.ticker == temp_ticker, :]
        stock_data = temp_data[['ticker', 'return']]
        stock_data = input_function.convert_to_form_db(stock_data)
        if stock_data is None:
            print('!! error processing {}'.format(temp_ticker))
            continue
        stock_data = stock_data.rename(columns={'return': 'Close'})
        stock_data = stock_data.drop(columns=['ticker'])
        ff_data = temp_data[ff_names]
        # ff_data.insert(0, 'date', ff_data.index.values)
        rf_data = temp_data[rf_names]
        # rf_data.insert(0, 'date', rf_data.index.values)
        carbon_data = temp_data['BMG'].to_frame()
        carbon_data.insert(0, 'date', carbon_data.index.values)
        run_regression_internal(stock_data, carbon_data, ff_data, rf_data,
                                temp_ticker, factor_name, start_date, end_date, interval, frequency, verbose=False, silent=True, store=True)
        print(temp_ticker)
    end_time = datetime.datetime.now()
    print(end_time - start_time)


def run_regression(ticker,
                   factor_name,
                   start_date,
                   end_date,
                   interval,
                   frequency='MONTHLY',
                   carbon_data=None,
                   ff_data=None,
                   rf_data=None,
                   verbose=False,
                   silent=False,
                   store=False):
    if carbon_data is None:
        carbon_data = load_carbon_data_from_db(factor_name, frequency=frequency)
        if verbose:
            print('Loaded carbon_data ...')
            print(carbon_data)
    elif verbose:
        print('Got carbon_data ...')
        print(carbon_data)
    if ff_data is None:
        ff_data = load_ff_data_from_db(frequency=frequency)
        if verbose:
            print('Loaded ff_data ...')
            print(ff_data)
    elif verbose:
        print('Got ff_data ...')
        print(ff_data)
    if rf_data is None:
        rf_data = load_rf_data_from_db(frequency=frequency)
        if verbose:
            print('Loaded rf_data ...')
            print(rf_data)
    elif verbose:
        print('Got risk-fre rate')
        print(rf_data)

    stock_data = get_stocks.load_stocks_from_db(ticker, frequency=frequency)
    stock_data = input_function.convert_to_form_db(stock_data)
    if stock_data is None or stock_data.empty:
        stock_data = get_stocks.import_stock(ticker, frequency=frequency)

    if verbose:
        print(stock_data)

    if stock_data is None or stock_data.empty:
        print('No stock data for {} !'.format(ticker))
        return
    # convert to pct change
    stock_data = stock_data.pct_change(periods=1)

    run_regression_internal(stock_data,
                            carbon_data,
                            ff_data,
                            rf_data,
                            ticker,
                            factor_name,
                            start_date,
                            end_date,
                            interval,
                            frequency,
                            verbose,
                            silent,
                            store)


def run_regression_internal(stock_data,
                            carbon_data,
                            ff_data,
                            rf_data,
                            ticker,
                            factor_name,
                            start_date,
                            end_date,
                            interval,
                            frequency,
                            verbose,
                            silent,
                            store):
    if frequency == 'DAILY':
        freq = 'D'
        if interval == 0:
            interval = 730
        interval_dt = relativedelta(days=interval)
    elif frequency == 'MONTHLY':
        freq = 'M'
        if interval == 0:
            interval = 60
        interval_dt = relativedelta(months=interval)
    else:
        raise Exception("Unsupported frequency: {}".format(frequency))

    try:
        if start_date:
            start_date = pd.Period(start_date, freq=freq).end_time.date()
            start_date = factor_regression.parse_date('Start', start_date)
        else:
            # use the common start date of all series:
            start_date = max(min(stock_data.index), min(
                carbon_data.index), min(ff_data.index), min(rf_data.index))

        if end_date:
            end_date = pd.Period(end_date, freq=freq).end_time.date()
            end_date = factor_regression.parse_date('End Date', end_date)
        else:
            # use the common end date of all series:
            end_date = min(max(stock_data.index), max(
                carbon_data.index), max(ff_data.index), max(rf_data.index))
        r_end_date = start_date+interval_dt
        r_end_date = pd.Period(r_end_date, freq=freq).end_time.date()
        if r_end_date > end_date:
            print('!! Done running regression on stock {} from {} to {} (next regression would end in {})'.format(
                ticker, start_date, end_date, r_end_date))
            return
        start_date += datetime.timedelta(days=1)
        start_date, r_end_date, data_start_date, data_end_date, model_output, coef_df_simple = factor_regression.run_regression(
            stock_data, carbon_data, ff_data, rf_data, ticker, start_date, end_date=r_end_date, verbose=verbose, silent=silent)
        if verbose:
            print("-- {} ran regression start={} end={} data_start={} data_end={} wanted_end={}".format(
                ticker, start_date, r_end_date, data_start_date, data_end_date, end_date))
    except factor_regression.DateInRangeError as e:
        print('!! Error running regression on stock {} from {} to {}: {}'.format(
            ticker, start_date, end_date, e))
        return
    except ValueError as e:
        print('!! Error running regression on stock {} from {} to {}: {}'.format(
            ticker, start_date, end_date, e))
        return

    if model_output is False:
        print('!! Error running regression on stock {} from {} to {}'.format(
            ticker, start_date, end_date))
        return

    # stop running when the data_end_date is > end_date (we no longer have enough data)
    if data_end_date > end_date:
        print('!! Finished running regression on stock {} from {} to {} (data ends in {})'.format(
            ticker, start_date, end_date, data_end_date))
        return

    if store:
        print('Ran regression for {} from {} to {} ...'.format(
            ticker, start_date, r_end_date))
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
            'frequency': frequency,
            'bmg_factor_name': factor_name,
            'from_date': start_date,
            'thru_date': r_end_date,
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

    # recurse the new interval
    start_date += interval_dt
    if frequency == 'MONTHLY':
        start_date -= datetime.timedelta(days=1)
    run_regression_internal(stock_data, carbon_data, ff_data, rf_data,
                            ticker, factor_name, start_date, end_date, interval, frequency, verbose, silent, store)


def store_regression_into_db(sql_params):
    del_sql = '''DELETE FROM stock_stats WHERE ticker = %s and frequency = %s and bmg_factor_name = %s and from_date = %s and thru_date = %s;'''
    placeholder = ", ".join(["%s"] * len(sql_params))
    stmt = "INSERT INTO stock_stats ({columns}) values ({values});".format(
        columns=",".join(sql_params.keys()), values=placeholder)
    with conn.cursor() as cursor:
        cursor.execute(
            del_sql, (sql_params['ticker'], sql_params['frequency'], sql_params['bmg_factor_name'], sql_params['from_date'], sql_params['thru_date']))
        cursor.execute(stmt, list(sql_params.values()))


def main(args):
    start_time = datetime.datetime.now()
    if args.ticker:
        run_regression(ticker=args.ticker,
                       factor_name=args.factor_name,
                       start_date=args.start_date,
                       end_date=args.end_date,
                       interval=args.interval,
                       frequency=args.frequency,
                       verbose=args.verbose,
                       store=(not args.dryrun),
                       silent=(not args.dryrun))
    elif args.file:
        carbon_data = load_carbon_data_from_db(args.factor_name, frequency=args.frequency)
        ff_data = load_ff_data_from_db(frequency=args.frequency)
        rf_data = load_rf_data_from_db(frequency=args.frequency)
        stocks = load_stocks_csv(args.file)
        for i in range(0, len(stocks)):
            stock_name = stocks[i].item()
            print('* running regression for {} ... '.format(stock_name))
            run_regression(stock_name,
                           factor_name=args.factor_name,
                           start_date=args.start_date,
                           end_date=args.end_date,
                           interval=args.interval,
                           frequency=args.frequency,
                           carbon_data=carbon_data,
                           ff_data=ff_data,
                           rf_data=rf_data,
                           verbose=args.verbose,
                           silent=(not args.dryrun),
                           store=(not args.dryrun))
    elif args.bulk_regression:
        carbon_data = load_carbon_data_from_db(args.factor_name, frequency=args.frequency)
        # print(carbon_data)
        ff_data = load_ff_data_from_db(frequency=args.frequency)
        rf_data = load_rf_data_from_db(frequency=args.frequency)
        stock_data = get_stocks.load_all_stocks_from_db()
        # stock_data = input_function.convert_to_form_db(stock_data)
        # stock_data['date'] = stock_data.index
        # print(stock_data)
        final_data = stock_data.join(carbon_data).join(ff_data).join(rf_data)
        final_data = final_data.dropna()
        bulk_regression_transformer(
            final_data, ff_data.columns, rf_data.columns, args.factor_name, args.interval, frequency=args.frequency)
    else:
        carbon_data = load_carbon_data_from_db(args.factor_name, frequency=args.frequency)
        ff_data = load_ff_data_from_db(frequency=args.frequency)
        rf_data = load_rf_data_from_db(frequency=args.frequency)
        stocks = get_stocks.load_stocks_defined_in_db()
        for i in range(0, len(stocks)):
            stock_name = stocks[i]
            print('* running regression for {} ... '.format(stock_name))
            run_regression(stock_name,
                           factor_name=args.factor_name,
                           start_date=args.start_date,
                           end_date=args.end_date,
                           interval=args.interval,
                           frequency=args.frequency,
                           carbon_data=carbon_data,
                           ff_data=ff_data,
                           rf_data=rf_data,
                           verbose=args.verbose,
                           silent=(not args.dryrun),
                           store=(not args.dryrun))
    end_time = datetime.datetime.now()
    print("Total run time: ", end_time - start_time)


# run
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--from_db", action='store_true',
                        help="import of tickers in the stocks table of the Database instead of using a CSV file, this is the default unless -t or -f is used")
    parser.add_argument("-f", "--file",
                        help="specify the CSV file of stock tickers to import")
    parser.add_argument("-t", "--ticker",
                        help="specify a single ticker to run the regression for, ignores the CSV file")
    parser.add_argument("-o", "--dryrun", action='store_true',
                        help="Only shows the results, do not store the results in the DB")
    parser.add_argument("-s", "--start_date",
                        help="Sets the start date for the regression, must be in the YYYY-MM-DD format, defaults to the start date of all the data series for a given stock")
    parser.add_argument("-e", "--end_date",
                        help="Sets the end date for the regression, must be in the YYYY-MM-DD format, defaults to the last date of all the data series for a given stock")
    parser.add_argument("-i", "--interval", default=0, type=int,
                        help="Sets number of months for the regression interval, defaults to 60 months for MONTHLY frequency or 730 days for DAILY frequency")
    parser.add_argument("-n", "--factor_name", default='DEFAULT',
                        help="Sets the factor name of the carbon_risk_factor used")
    parser.add_argument("--frequency", default='MONTHLY',
                        help="Frequency to use for the various series, eg: MONTHLY, DAILY")
    parser.add_argument("-v", "--verbose", action='store_true',
                        help="More verbose output")
    parser.add_argument("-b", "--bulk_regression", action='store_true',
                        help="Run bulk regression that should run faster")
    main(parser.parse_args())
