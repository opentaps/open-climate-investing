import yfinance as yf
import pandas as pd

def stock_grabber(ticker):
    stock = yf.Ticker(ticker)
    hist = stock.history(period='max', interval = '1mo')
    hist.drop(hist.tail(1).index,inplace=True)
    hist.index = hist.index - pd.to_timedelta(1, unit = 'd')
    hist = hist['Close']
    hist = hist.dropna()
    return(hist)

x = input('Choose your stock: ')
stock_data = stock_grabber(x)
print(stock_data)

save_data = input('Save Data (y/n)?: ')
if save_data == 'y' or save_data == 'Y' or save_data == 'yes' or save_data == 'Yes':
    stock_data.to_csv("stock_data.csv")
    print(x + ' saved')
