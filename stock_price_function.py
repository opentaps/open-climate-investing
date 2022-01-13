import yfinance as yf
import pandas as pd
import json
from pandas.tseries.offsets import MonthEnd


def stock_details_grabber(ticker):
    stock = yf.Ticker(ticker)
    info = stock.info
    return info


def stock_grabber(ticker, frequency='MONTHLY'):
    stock = yf.Ticker(ticker)
    attempt_num = 3
    while attempt_num > 0:
        try:
            if frequency == 'DAILY':
                history = stock.history(period='max', interval='1d')
            elif frequency == 'MONTHLY':
                history = stock.history(period='max', interval='1mo')
            else:
                raise Exception('Unsupported frequency {}'.format(frequency))
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


def stock_df_grab(x, frequency='MONTHLY'):
    try:
        stock_data = stock_grabber(x, frequency=frequency)
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
