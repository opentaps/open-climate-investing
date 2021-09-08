import pandas as pd
import regression_function as regfun
import input_function
from datetime import datetime
from pandas.tseries.offsets import MonthEnd

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
bulk = False

stock_data, carbon_data, ff_data, ticker = input_function.user_input()

ff_data = ff_data/100

# Merge the 3 data frames together (inner join on dates)
all_factor_df = merge_data(stock_data, carbon_data)
all_factor_df = merge_data(all_factor_df, ff_data)


# Allow start dates
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

model_output, coef_df_simple = regfun.regression_input_output(
    all_factor_df, ticker)

print(model_output.summary())
print(coef_df_simple.to_string())
