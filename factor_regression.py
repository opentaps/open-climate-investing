import pandas as pd
import statsmodels.api as sm
import stock_price_function as spf
from datetime import datetime
from pandas.tseries.offsets import DateOffset
from pandas.tseries.offsets import MonthEnd

### Gets the CSVs and converts it into the form for the rest to use (mode date to index)


def convert_to_form(df):
    df[df.columns[0]] = pd.to_datetime(df[df.columns[0]])
    df.index = df[df.columns[0]]
    df.drop(df.columns[0], axis=1, inplace=True)
    return(df)

### Merges the 3 dataframes (returns, FF, carbon) into 1 dataframe


def merge_data(df1, df2):
    df1['date'] = pd.to_datetime(df1.index).date
    # df1['date'] = MonthEnd(df1['date'])
    df2['date'] = pd.to_datetime(df2.index).date
    final_df = pd.merge(df1, df2, how='inner', left_on='date', right_on='date')
    final_df.index = final_df['date']
    final_df.index.rename('Date', inplace=True)
    final_df.drop('date', axis=1, inplace=True)
    return(final_df)


### Read in the data
ret_provided = False

print('This application generates a factor model as per Fama-French')
print('It requires certain items')
stock_choice = input(
    "Do you have stock return data or would you like to download these? \n (Y if you have/N if you don't) \n")
stock_choice = stock_choice.upper()
if stock_choice == 'YES' or stock_choice == 'Y':
    loop_close = False
    ret_provided = True
    while loop_close is False:
        ret_data = input(
            'What is the file name of the returns (CSV format): ')
        try:
            stock_data = pd.read_csv(ret_data)
            loop_close = True
        except:
            print('Incorrect CSV')
            loop_close = False
else:
    loop_close = False
    while loop_close is False:
        ticker = input('Enter Ticker Name: ')
        try:
            stock_data = spf.stock_df_grab(ticker)
            loop_close = True
        except:
            print('Ticker error or error with API')
            loop_close = False

loop_close = False
while loop_close is False:
    print('What is the carbon data csv saved as: ')
    factor_csv = input('Enter CSV name here: ')
    try:
        carbon_data = pd.read_csv(factor_csv)
        loop_close = True
    except:
        print('Incorrect file name')
        loop_close = False

loop_close = False
while loop_close is False:
    print('What is the Fama-French Factors csv saved as: ')
    factor_csv = input('Enter CSV name here: ')
    try:
        ff_data = pd.read_csv(factor_csv)
        loop_close = True
    except:
        print('Incorrect file name')
        loop_close = False


### Convert the CSV into dataframes ready for manipulation
stock_data = convert_to_form(stock_data)
carbon_data = convert_to_form(carbon_data)
ff_data = convert_to_form(ff_data)

### Convert stock prices to returns and FF to percentages
if ret_provided is False:
    # stock_data['Close'] = np.log(stock_data['Close'])
    stock_data.index = pd.to_datetime(
        stock_data.index, format="%Y%m") + MonthEnd(1)
    stock_data = stock_data.pct_change(periods=1)
    stock_data.dropna(inplace=True)
    # stock_data.index = stock_data.index + DateOffset(months=1)
ff_data = ff_data/100

### Merge the 3 data frames together (inner join on dates)
all_factor_df = merge_data(stock_data, carbon_data)
all_factor_df = merge_data(all_factor_df, ff_data)


### Allow start dates
min_date = min(all_factor_df.index)
print('The earliest date is: ' + min_date.strftime('%Y-%m-%d'))

loop_close = False
while loop_close == False:
    start_date = input(
        'What would you like the start date to be (format YYYY-MM-DD): ')
    try:
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        try:
            start_date = start_date.date()
            all_factor_df = all_factor_df[(all_factor_df.index >= start_date)]
            loop_close = True
        except:
            print('Date too early')
    except:
        print('Date incorrect')

print('Starting date is now ' + min(all_factor_df.index).strftime('%Y-%m-%d'))

### Separate into independent (x) and dependent (y) factors)
y = all_factor_df[all_factor_df.columns[0]]
x = all_factor_df.drop(all_factor_df.columns[0], axis=1)
x = sm.add_constant(x)

### Estimate regression
model = sm.OLS(y, x).fit()
print(model.summary())

coef_df = df = pd.read_html(
    model.summary().tables[1].as_html(), header=0, index_col=0)[0]
coef_df_simple = coef_df[['coef', 'P>|t|']]
print(coef_df)
print(coef_df_simple)
