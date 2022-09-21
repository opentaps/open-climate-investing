
import argparse
import get_stocks
import factor_regression
import textwrap
import pandas as pd
import db

conn = db.get_db_connection()

def add_bmg_series(factor_name, green_ticker, brown_ticker, start_date=None, end_date=None, frequency='MONTHLY'):
    if not factor_name:
        print(' factor name is required !')
        return False
    if not green_ticker:
        print(' green ticker is required !')
        return False
    if not brown_ticker:
        print(' brown ticker is required !')
        return False

    print('*** adding factor {} from Brown stocks {} and Green stocks {} ...'.format(factor_name, brown_ticker, green_ticker))
    green_data = get_stocks.load_stocks_returns_from_db(green_ticker, frequency=frequency)
    print('** green_data -> ')
    print(green_data)
    brown_data = get_stocks.load_stocks_returns_from_db(brown_ticker, frequency=frequency)
    print('** brown_data -> ')
    print(brown_data)

    merged = pd.merge(brown_data, green_data, left_index=True, right_index=True)
    merged['bmg'] = merged['return_x'] - merged['return_y']
    merged['factor_name'] = factor_name
    merged.drop(columns=['return_x', 'return_y'], inplace=True)
    # cleanup NaN values
    has_value = merged['bmg'].notna()
    merged = merged[has_value]

    if start_date is not None:
        start_date = factor_regression.parse_date('Start', start_date)
        merged = merged[merged.index >= start_date]

    if end_date is not None:
        end_date = factor_regression.parse_date('End', end_date)
        merged = merged[merged.index <= end_date]

    print('** merged -> ')
    print(merged)

    get_stocks.import_carbon_risk_factor_into_db(merged, frequency=frequency)
    return True


def delete_bmg_series(factor_name):
    if not factor_name:
        print(' factor name is required !')
        return False

    print('*** deleting factor {} ...'.format(factor_name))
    get_stocks.delete_carbon_risk_factor_from_db(factor_name)

    return True


def get_bmg_series():
    # show the current factors
    sql = 'select factor_name, frequency, min(date), max(date) from carbon_risk_factor where group by factor_name order by factor_name;'
    with conn.cursor() as cursor:
        cursor.execute(sql)
        return cursor.fetchall()


def show_bmg_series(factor_name, start_date=None, end_date=None, frequency='MONTHLY'):
    if not factor_name:
        # show the current factors
        series = get_bmg_series()
        if series:
            for (n,from_date,to_date) in series:
                print('{} from {} to {}'.format(n,from_date,to_date))
        else:
            print('No BMG series found.')
        return True
    
    data = get_stocks.load_carbon_risk_factor_from_db(factor_name, frequency=frequency)

    if start_date is not None:
        start_date = factor_regression.parse_date('Start', start_date)
        data = data[data.index >= start_date]

    if end_date is not None:
        end_date = factor_regression.parse_date('End', end_date)
        data = data[data.index <= end_date]

    print(data)

    return True


def main(args):
    if args.show:
        return show_bmg_series(args.factor_name, start_date=args.start_date, end_date=args.end_date, frequency=args.frequency)
    else:
        if not args.factor_name:
            return False
        if args.delete:
            if not delete_bmg_series(args.factor_name):
                return False
        if args.green_ticker or args.brown_ticker:
            if not add_bmg_series(args.factor_name, args.green_ticker, args.brown_ticker, start_date=args.start_date, end_date=args.end_date, frequency=args.frequency):
                return False
        return args.delete or args.green_ticker or args.brown_ticker


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Manage BMG series",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent('''
        Examples:

            Delete the series for MY_FACTOR:
                %(prog)s -n MY_FACTOR -d
            
            Create a series MY_FACTOR from stocks TICK1 and TICK2:
                %(prog)s -n MY_FACTOR -b TICK1 -g TICK2
            
            Display all the series stored in the DB:
                %(prog)s -o

            Display the series values stored in the DB:
                %(prog)s -o MY_FACTOR
            
            Create a series MY_FACTOR from stocks TICK1 and TICK2 for 
            a given time period, deleting the existing values first:
                %(prog)s -n MY_FACTOR -b TICK1 -g TICK2 -d -s 2000-01-01 -e 2020-12-31

        ''')
    )
    parser.add_argument("-n", "--factor_name",
                        help="specify the factor name for the BMG series to operate on, cannot be DEFAULT which is a reserved name")
    parser.add_argument("-o", "--show", action='store_true',
                        help="display the series from the DB, for testing")
    parser.add_argument("-d", "--delete", action='store_true',
                        help="remove the series from the DB")
    parser.add_argument("-g", "--green_ticker",
                        help="specify the green ticker when adding a new series")
    parser.add_argument("-b", "--brown_ticker",
                        help="specify the brown ticker when adding a new series")
    parser.add_argument("-s", "--start_date",
                        help="Sets the start date for the series, must be in the YYYY-MM-DD format, defaults to the earliest date on record")
    parser.add_argument("-e", "--end_date",
                        help="Sets the end date for the series, must be in the YYYY-MM-DD format, defaults to the latest date on record")
    parser.add_argument("--frequency", default='MONTHLY',
                        help="Frequency to use for the various series, eg: MONTHLY, DAILY")
    parser.add_argument("-v", "--verbose", action='store_true',
                        help="more output")
    if not main(parser.parse_args()):
        parser.print_help()

