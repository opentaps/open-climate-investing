import pandas as pd
import statsmodels.api as sm
import stock_price_function as spf
import numpy as np
from datetime import datetime
from pandas.tseries.offsets import DateOffset
from pandas.tseries.offsets import MonthEnd

### Gets the CSVs and converts it into the form for the rest to use (mode date to index)


def convert_to_form(df):
    df['date_converted'] = pd.to_datetime(df[df.columns[0]])
    df.index = df['date_converted']
    df = df.drop([df.columns[0], 'date_converted'], axis=1)
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


# Hardcoded stock ticker array
all_stock_data = ['XOM', 'TSLA']
hard_coded = False

### Read in the data
ret_provided = False

print('This application generates a factor model as per Fama-French')
print('It requires certain items')

if hard_coded is False:
    stock_choice = input(
        "Do you have stock return data or would you like to download these? \n (Y if you have/N if you don't) \n")
    stock_choice = stock_choice.upper()
    if stock_choice == 'YES' or stock_choice == 'Y':
        ret_provided = True
    loop_close = False
    while loop_close is False:
        try:
            if ret_provided is True:
                ret_data = input(
                    'What is the file name of the returns (CSV format): ')
                all_stock_data = pd.read_csv(ret_data)
            else:
                ret_data = input(
                    'What is the file name of the tickers (CSV format): ')
                all_stock_data = pd.read_csv(ret_data, header=None)
                all_stock_data = all_stock_data.values
            loop_close = True
        except:
            print('Incorrect CSV')
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

carbon_data = convert_to_form(carbon_data)
ff_data = convert_to_form(ff_data)

### FF to percentages
ff_data = ff_data/100

i = 1
# Create holder dataframe
coef_all = pd.DataFrame()

if ret_provided is False:
    start_range = 0
    end_range = len(all_stock_data)
else:
    start_range = 1
    end_range = len(all_stock_data.columns)

for i in range(start_range, end_range):

    ### Convert stock prices to returns and FF to percentages
    if ret_provided is False:
        if hard_coded is False:
            stock_name = all_stock_data[i].item()
        else:
            stock_name = all_stock_data[i]
        print(stock_name)
        stock_data = spf.stock_df_grab(stock_name)
        stock_data = convert_to_form(stock_data)
        # stock_data['Close'] = np.log(stock_data['Close'])
        stock_data.index = pd.to_datetime(
            stock_data.index, format="%Y%m") + MonthEnd(1)
        stock_data = stock_data.pct_change(periods=1)
        stock_data.dropna(inplace=True)
        # stock_data.index = stock_data.index + DateOffset(months=1)
    else:
        stock_data = all_stock_data[[
            all_stock_data.columns[0], all_stock_data.columns[i]]]
        stock_data = convert_to_form(stock_data)
        stock_name = all_stock_data.columns[i]

    ### Merge the 3 data frames together (inner join on dates)
    all_factor_df = merge_data(
        stock_data, carbon_data)
    all_factor_df = merge_data(all_factor_df, ff_data)

    ### Separate into independent (x) and dependent (y) factors)
    y = all_factor_df[all_factor_df.columns[0]]
    x = all_factor_df.drop(
     all_factor_df.columns[0], axis=1)
    x.insert(0, 'Constant', 1)

    # Estimate regression
    model = sm.OLS(y, x, hasconst=False).fit()

    coef_df = df = pd.read_html(
     model.summary().tables[1].as_html(), header=0, index_col=0)[0]
    coef_df_simple = coef_df[['coef', 'P>|t|']]
    coef_df_simple = pd.DataFrame.transpose(coef_df_simple)
    coef_df_simple['Name'] = [stock_name, stock_name]
    cols = coef_df_simple.columns.tolist()
    cols = cols[-1:] + cols[:-1]
    coef_df_simple = coef_df_simple[cols]
    coef_all = coef_all.append(coef_df_simple)

print(coef_all)
pd.DataFrame.to_csv(coef_all, 'reg_output.csv')
