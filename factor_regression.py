import pdb
import pandas as pd
import regression_function as regfun
import input_function
from datetime import datetime

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


def run_regression(stock_data, carbon_data, ff_data, ticker, start_date, verbose=True, silent=False):
    ff_data = ff_data/100

    # Merge the 3 data frames together (inner join on dates)
    all_factor_df = merge_data(stock_data, carbon_data)
    all_factor_df = merge_data(all_factor_df, ff_data)

    if len(all_factor_df) == 0:
        raise ValueError('No data could be loaded!')

    if verbose:
        print('Data is ...')
        print(all_factor_df)

    # Allow start dates
    max_date = max(all_factor_df.index)
    min_date = min(all_factor_df.index)
    if verbose:
        print('Data available from {} to {}'.format(min_date, max_date))

    try:
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
    except ValueError:
        raise ValueError(
            'Date {} not in correct format, must be YYYY-MM-DD'.format(start_date))

    start_date = start_date.date()
    if verbose:
        print('start_date is {}'.format(start_date))
    if start_date >= max_date:
        raise ValueError(
            'Start date {} must be before {}'.format(start_date, max_date))
    if start_date >= min_date:
        all_factor_df = all_factor_df[(all_factor_df.index >= start_date)]
        # could be empty now if the ticker has no data after the start date
        if len(all_factor_df) == 0:
            raise ValueError('No data for stock {} overlapping the ff_factor and carbon_data after date {}'.format(
                ticker, start_date))
    else:
        if verbose or not silent:
            print('Date too early, using {} instead.'.format(min_date))
        start_date = min_date

    if verbose or not silent:
        print('Running regression from {} to {}'.format(start_date, max_date))

    model_output, coef_df_simple = regfun.regression_input_output(
        all_factor_df, ticker)

    if (verbose or not silent) and model_output is not False:
        print(model_output.summary())
        print(coef_df_simple.to_string())
    return (start_date, max_date, model_output, coef_df_simple)


# run
if __name__ == "__main__":
    # Read in the data
    stock_data, carbon_data, ff_data, ticker = input_function.user_input()
    start_date = input(
        'What would you like the start date to be (format YYYY-MM-DD): ')

    run_regression(stock_data, carbon_data, ff_data, ticker, start_date)
