import argparse
import yfinance as yf
import pandas as pd
import json
from pandas.tseries.offsets import MonthEnd


def stock_details_grabber(ticker):
    stock = yf.Ticker(ticker)
    info = stock.info
    return info


def stock_grabber(ticker, frequency='MONTHLY', period='max', start=None):
    stock = yf.Ticker(ticker)
    attempt_num = 3
    while attempt_num > 0:
        try:
            interval = '1d'
            if frequency == 'DAILY':
                interval = '1d'
            elif frequency == 'MONTHLY':
                interval = '1mo'
            else:
                raise Exception('Unsupported frequency {}'.format(frequency))
            history = stock.history(period=period, interval=interval, start=start)
            # remove the last entry as it is incomplete?
            history.drop(history.tail(1).index, inplace=True)
            if frequency != 'DAILY':
                history.index = history.index + MonthEnd(1)
            history = history['Close']
            history = history.dropna()
            attempt_num = 0
            return(history)
        except json.decoder.JSONDecodeError:
            attempt_num -= 1
            print("Attempt timed out. Trying again")
    if attempt_num == 0:
        raise ValueError("Timed out")


def stock_df_grab(x, frequency='MONTHLY', start=None):
    try:
        stock_data = stock_grabber(x, frequency=frequency, start=start)
        stock_data = stock_data.to_frame()
        stock_data['Date'] = stock_data.index
        stock_data['Date'] = pd.to_datetime(stock_data['Date']).dt.date
        cols = stock_data.columns.tolist()
        cols = cols[-1:] + cols[:-1]
        stock_data = stock_data[cols]
        stock_data = stock_data.reset_index(drop=True)
        return(stock_data)
    except ValueError as ve:
        raise ValueError("Skipping stock: {}".format(ve))


def main(args):
    if not args.ticker:
        return False
    h = stock_grabber(args.ticker, frequency=args.frequency, period=args.period, start=args.start)
    print(h)
    return True


# run
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Stock price grabber, simply prints the stock prices grabbed for debugging purposes.')
    parser.add_argument("-t", "--ticker",
                        help="specify a single ticker")
    parser.add_argument("--frequency", default='MONTHLY',
                        help="Frequency to use for the various series, eg: MONTHLY, DAILY")
    parser.add_argument("--period", default='max',
                        help="Period to get the stock for, eg: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max")
    parser.add_argument("--start",
                        help="Download start date string (YYYY-MM-DD)")
    if not main(parser.parse_args()):
        parser.print_help()
