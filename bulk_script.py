import pandas as pd
import stock_price_function as spf
from pandas.tseries.offsets import MonthEnd
import regression_function as regfun
import input_function


# Merges the 3 dataframes (returns, FF, carbon) into 1 dataframe


def merge_data(df1, df2):
    df1['date'] = pd.to_datetime(df1.index).date
    # df1['date'] = MonthEnd(df1['date'])
    df2['date'] = pd.to_datetime(df2.index).date
    final_df = pd.merge(df1, df2, how='inner', left_on='date', right_on='date')
    final_df.index = final_df['date']
    final_df.index.rename('Date', inplace=True)
    final_df.drop('date', axis=1, inplace=True)
    return(final_df)


# Read in the data
ret_provided = False

print('This application generates a factor model as per Fama-French')
print('It requires certain items')

input_loop_close = False
while input_loop_close is False:
    stock_choice = input(
        "Do you have stock return data or would you like to download these? \n (Y if you have/N if you don't): ")
    stock_choice = stock_choice.upper()
    if stock_choice == 'YES' or stock_choice == 'Y':
        ret_provided = True
        input_loop_close = True
    elif stock_choice == 'NO' or stock_choice == 'N':
        ret_provided = False
        input_loop_close = True
    else:
        print('Incorrect Option Chosen')
loop_close = False
while loop_close is False:
    try:
        if ret_provided is True:
            ret_data = input(
                'What is the file name of the returns (CSV format): ')
            all_stock_data = pd.read_csv(ret_data)
            all_stock_data = input_function.convert_to_form(all_stock_data)
            if all_stock_data is not False:
                loop_close = True
            else:
                print('CSV is in incorrect format')
        else:
            ret_data = input(
                'What is the file name of the tickers (CSV format): ')
            all_stock_data = pd.read_csv(ret_data, header=None)
            all_stock_data = all_stock_data.values
            loop_close = True
    except FileNotFoundError:
        print("File doesn't exist")
    except pd.errors.ParserError:
        print('File is not a CSV')

use_default = input(
    "Would you like to use the default Carbon Risk and Fama-French Factors? \n (Y if you have/N if you don't): ")
use_default = use_default.upper()

if use_default == 'Y':
    carbon_data = pd.read_csv('data/carbon_risk_factor.csv')
    ff_data = pd.read_csv('data/ff_factors.csv')
    carbon_data = input_function.convert_to_form(carbon_data)
    ff_data = input_function.convert_to_form(ff_data)
else:
    loop_close = False
    while loop_close is False:
        print('What is the carbon data csv saved as: ')
        factor_csv = input('Enter CSV name here: ')
        try:
            carbon_data = pd.read_csv(factor_csv)
        except FileNotFoundError:
            print("File doesn't exist")
        except pd.errors.ParserError:
            print('File is not a CSV')
        else:
            carbon_data = input_function.convert_to_form(carbon_data)
            if ff_data is not False:
                loop_close = True
            else:
                print('CSV is not in correct form')

    loop_close = False
    while loop_close is False:
        print('What is the Fama-French Factors csv saved as: ')
        factor_csv = input('Enter CSV name here: ')
        try:
            ff_data = pd.read_csv(factor_csv)
        except FileNotFoundError:
            print("File doesn't exist")
        except pd.errors.ParserError:
            print('File is not a CSV')
        else:
            ff_data = input_function.convert_to_form(ff_data)
            if ff_data is not False:
                loop_close = True
            else:
                print('CSV is not in correct form')


# FF to percentages
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

    # Convert stock prices to returns and FF to percentages
    if ret_provided is False:
        stock_name = all_stock_data[i].item()
        stock_data = spf.stock_df_grab(stock_name)
        stock_data = input_function.convert_to_form(stock_data)
        stock_data.index = pd.to_datetime(
            stock_data.index, format="%Y%m") + MonthEnd(1)
        stock_data = stock_data.pct_change(periods=1)
        stock_data.dropna(inplace=True)
    else:
        stock_data = all_stock_data[[
            all_stock_data.columns[0], all_stock_data.columns[i]]]
        # stock_data = input_function.convert_to_form(stock_data)
        stock_name = all_stock_data.columns[i]

    # Merge the 3 data frames together (inner join on dates)
    all_factor_df = merge_data(
        stock_data, carbon_data)
    all_factor_df = merge_data(all_factor_df, ff_data)

    # Estimate regression
    model, coef_df_simple = regfun.regression_input_output(
        all_factor_df, stock_name)
    if model is not False:
        print(stock_name)
        coef_all = coef_all.append(coef_df_simple)
    else:
        print(f'Error with stock {stock_name}')

print(coef_all)
pd.DataFrame.to_csv(coef_all, 'reg_output.csv')
