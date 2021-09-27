import pdb
import pandas as pd
import regression_function as regfun
import input_function
from datetime import datetime


class DateInRangeError(Exception):
    """Exception raised for errors in the input dates.

    Attributes:
        date -- input date which caused the error
        min_date -- min value of the valid date range
        max_date -- max value of the valid date range
        message -- explanation of the error
    """

    def __init__(self, date, min_date, max_date, name="Date"):
        self.date = date
        self.min_date = min_date
        self.max_date = max_date
        self.message = name + \
            ' not in a valid range (given {} not in {} - {})'.format(date,
                                                                     min_date, max_date)
        super().__init__(self.message)


# Merges the 3 dataframes (returns, FF, carbon) into 1 dataframe
def merge_data(df1, df2):
    df1['date'] = pd.to_datetime(df1.index).date
    df2['date'] = pd.to_datetime(df2.index).date
    final_df = pd.merge(df1, df2, how='inner', left_on='date', right_on='date')
    final_df.index = final_df['date']
    final_df.index.rename('Date', inplace=True)
    final_df.drop('date', axis=1, inplace=True)
    return(final_df)


def parse_date(name, date_str):
    if type(date_str) != str:
        return date_str
    try:
        return datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        raise ValueError(
            '{} Date {} not in correct format, must be YYYY-MM-DD'.format(name, date_str))


def run_regression(stock_data, carbon_data, ff_data, ticker, start_date=None, end_date=None, verbose=True, silent=False):
    ff_data = ff_data/100

    # Merge the 3 data frames together (inner join on dates)
    all_factor_df = merge_data(stock_data, carbon_data)
    all_factor_df = merge_data(all_factor_df, ff_data)

    if len(all_factor_df) == 0:
        raise ValueError('No data could be loaded!')

    if verbose:
        print('Data is ...')
        print(all_factor_df)

    # Check start and end dates
    max_date = max(all_factor_df.index)
    min_date = min(all_factor_df.index)
    if verbose:
        print('Data available from {} to {}'.format(min_date, max_date))

    if start_date is not None:
        start_date = parse_date('Start', start_date)
    else:
        start_date = min_date

    if end_date is not None:
        end_date = parse_date('End', end_date)
    else:
        end_date = max_date

    if verbose:
        print('start_date is {}, end_date is {}'.format(start_date, end_date))
    if start_date >= max_date:
        raise DateInRangeError(start_date, min_date, max_date, 'Start date')
    if end_date <= min_date:
        raise DateInRangeError(end_date, min_date, max_date, 'End date')

    data_start_date = start_date
    data_end_date = end_date
    if start_date >= min_date:
        all_factor_df = all_factor_df[(all_factor_df.index >= start_date)]
    else:
        if verbose or not silent:
            print('Start Date too early, using {} instead.'.format(min_date))
        data_start_date = min_date
    if end_date <= max_date:
        all_factor_df = all_factor_df[(all_factor_df.index <= end_date)]
    else:
        if verbose or not silent:
            print('End Date too late, using {} instead.'.format(max_date))
        data_end_date = max_date

    # could be empty now if the ticker has no data after the start date
    if len(all_factor_df) == 0:
        raise ValueError('No data for stock {} overlapping the ff_factor and carbon_data after date {}'.format(
            ticker, start_date))
    # the statistical functions are not valid with less than 20 data points
    if len(all_factor_df) < 20:
        raise ValueError('Not enough data for stock {} overlapping the ff_factor and carbon_data after date {}'.format(
            ticker, start_date))

    if verbose or not silent:
        print('Running {} - {} regression using data from {} to {} -- data has {} entries'.format(start_date,
                                                                                                  end_date, data_start_date, data_end_date, len(all_factor_df)))

    model_output, coef_df_simple = regfun.regression_input_output(
        all_factor_df, ticker)

    if (verbose or not silent) and model_output is not False:
        print(model_output.summary())
        print(coef_df_simple.to_string())
    return (start_date, end_date, data_start_date, data_end_date, model_output, coef_df_simple)


# run
if __name__ == "__main__":
    # Read in the data
    stock_data, carbon_data, ff_data, ticker = input_function.user_input()
    start_date = input(
        'What would you like the start date to be (format YYYY-MM-DD): ')

    run_regression(stock_data, carbon_data, ff_data, ticker, start_date)
