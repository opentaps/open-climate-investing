import pandas as pd
import stock_price_function as spf
from datetime import datetime
from pandas.tseries.offsets import MonthEnd


# Gets the CSVs and converts it into the
# form for the rest to use (mode date to index)
def convert_to_form(df):
    df['date_converted'] = pd.to_datetime(df[df.columns[0]])
    df.index = df['date_converted']
    df = df.drop([df.columns[0], 'date_converted'], axis=1)
    return(df)


def user_input():
    print('This application generates a factor model as per Fama-French')
    print('It requires certain items')
    stock_choice = input(
        "Do you have stock return data or would you like to download these? \n (Y if you have/N if you don't): ")
    stock_choice = stock_choice.upper()
    if stock_choice == 'YES' or stock_choice == 'Y':
        loop_close = False
        ret_provided = True
        ticker = False
        while loop_close is False:
            ret_data = input(
                'What is the file name of the returns (CSV format): ')
            try:
                stock_data = pd.read_csv(ret_data)
                ticker = stock_data.columns[0]
                stock_data = convert_to_form(stock_data)
                stock_data.index = pd.to_datetime(
                    stock_data.index, format="%Y%m") + MonthEnd(1)
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
                stock_data = convert_to_form(stock_data)
                loop_close = True
            except:
                print('Ticker error or error with API')
                loop_close = False

    use_default = input(
        "Would you like to use the default Carbon Risk and Fama-French Factors? \n (Y if you have/N if you don't): ")
    use_default = use_default.upper()

    if use_default == 'Y':
        carbon_data = pd.read_csv('carbon_risk_factor.csv')
        ff_data = pd.read_csv('ff_factors.csv')
    else:
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

    carbon_data = convert_to_form(carbon_data)
    ff_data = convert_to_form(ff_data)

    return(stock_data, carbon_data, ff_data, ticker)
