import yfinance as yf
import pandas as pd
from pandas.tseries.offsets import MonthEnd


def stock_grabber(ticker):
    stock = yf.Ticker(ticker)
    hist = stock.history(period='max', interval='1mo')
    hist.drop(hist.tail(1).index, inplace=True)
    hist.index = hist.index + MonthEnd(1)
    print(hist)
    hist = hist['Close']
    hist = hist.dropna()
    return(hist)


def stock_df_grab(x):
    stock_data = stock_grabber(x)
    stock_data = stock_data.to_frame()
    stock_data['Date'] = stock_data.index
    stock_data['Date'] = pd.to_datetime(stock_data['Date']).dt.date
    cols = stock_data.columns.tolist()
    cols = cols[-1:] + cols[:-1]
    stock_data = stock_data[cols]
    stock_data = stock_data.reset_index(drop=True)
    return(stock_data)
