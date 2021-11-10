import pandas as pd
import stock_price_function as spf
from pandas.tseries.offsets import MonthEnd
import dateutil


def convert_to_form(df):
    try:
        df['date_converted'] = pd.to_datetime(df[df.columns[0]])
        df.index = df['date_converted']
        df = df.drop([df.columns[0], 'date_converted'], axis=1)
    except dateutil.parser._parser.ParserError:
        df = False
    return(df)


def convert_to_form_db(df):
    try:
        df['date_converted'] = pd.to_datetime(df.index)
        df.index = df['date_converted']
        df = df.drop(['date_converted'], axis=1)
        df.rename(columns={"close": "Close"}, inplace=True)
    except dateutil.parser._parser.ParserError:
        df = False
    return(df)


def get_convert_file(file_name):
    try:
        data = pd.read_csv(file_name)
    except FileNotFoundError:
        print("File doesn't exist")
        return(False)
    except pd.errors.ParserError:
        print('File is not a CSV')
        return(False)
    else:
        try:
            data = convert_to_form(data)
            if data is not False:
                data.index = pd.to_datetime(
                        data.index, format="%Y%m") + MonthEnd(1)
                return(data)
            else:
                print('Dates are not in correct format')
                return(False)
        except pd.errors.ParserError:
            print('CSV is not in correct form')
            return(False)
    # Gets the CSVs and converts it into the
    # form for the rest to use (mode date to index)


def user_input():
    print('This application generates a factor model as per Fama-French')
    print('It requires certain items')
    stock_choice = input(
        "Do you have stock return data or would you like to download these? \n (Y if you have/N if you don't): ")
    stock_choice = stock_choice.upper()
    if stock_choice == 'YES' or stock_choice == 'Y':
        loop_close = False
        ticker = False
        while loop_close is False:
            stock_file_name = input(
                    'What is the file name of the returns (CSV format): ')
            stock_data = get_convert_file(stock_file_name)
            if stock_data is not False:
                ticker = stock_data.columns[0]
                loop_close = True
    else:
        loop_close = False
        while loop_close is False:
            ticker = input('Enter Ticker Name: ')
            # try:
            stock_data = spf.stock_df_grab(ticker)
            if stock_data.empty is False:
                stock_data = convert_to_form(stock_data)
                stock_data = stock_data.pct_change(periods=1)
                stock_data.dropna(inplace=True)
                loop_close = True
            else:
                print('Ticker error or error with API')

    input_loop_close = False
    while input_loop_close is False:
        use_default = input(
            "Would you like to use the default Carbon Risk and Fama-French Factors? \n (Y if you have/N if you don't): ")
        use_default = use_default.upper()

        if use_default == 'Y':
            carbon_data = pd.read_csv('data/carbon_risk_factor.csv')
            ff_data = pd.read_csv('data/ff_factors.csv')
            rf_data = pd.read_csv('data/risk_free.csv')
            carbon_data = convert_to_form(carbon_data)
            ff_data = convert_to_form(ff_data)
            rf_data = convert_to_form(rf_data)
            input_loop_close = True
        elif use_default == 'N':
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
                    carbon_data = convert_to_form(carbon_data)
                    if carbon_data is not False:
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
                    ff_data = convert_to_form(ff_data)
                    if ff_data is not False:
                        loop_close = True
                    else:
                        print('CSV is not in correct form')
            loop_close = False
            while loop_close is False:
                print('What is the risk-free rate csv saved as: ')
                rf_csv = input('Enter CSV name here: ')
                try:
                    rf_data = pd.read_csv(rf_csv)
                except FileNotFoundError:
                    print("File doesn't exist")
                except pd.errors.ParserError:
                    print('File is not a CSV')
                else:
                    rf_data = convert_to_form(rf_data)
                    if rf_data is not False:
                        loop_close = True
                    else:
                        print('CSV is not in correct form')
            input_loop_close = True
        else:
            print('Incorrect Input')

    return(stock_data, carbon_data, ff_data, rf_data, ticker)
