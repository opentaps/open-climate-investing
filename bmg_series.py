
import argparse
import get_stocks
import pandas as pd


def add_bmg_series(factor_name, green_ticker, brown_ticker):
    if not factor_name:
        print(' factor name is required !')
        return False
    # do not allow DEFAULT as it is a reserved name
    if factor_name == 'DEFAULT':
        print(' DEFAULT is a reserved factor name!')
        return False
    if not green_ticker:
        print(' green ticker is required !')
        return False
    if not brown_ticker:
        print(' brown ticker is required !')
        return False

    green_data = get_stocks.load_stocks_returns_from_db(green_ticker)
    print('** green_data -> ')
    print(green_data)
    brown_data = get_stocks.load_stocks_returns_from_db(brown_ticker)
    print('** brown_data -> ')
    print(brown_data)

    merged = pd.merge(green_data, brown_data, left_index=True, right_index=True)
    merged['bmg'] = merged['return_x'] - merged['return_y']
    merged['factor_name'] = factor_name
    merged.drop(columns=['return_x', 'return_y'], inplace=True)
    has_value = merged['bmg'].notna()
    merged = merged[has_value]
    print('** merged -> ')
    print(merged)

    get_stocks.import_carbon_risk_factor_into_db(merged)
    return True


def delete_bmg_series(factor_name):
    if not factor_name:
        print(' factor name is required !')
        return False
    # do not allow DEFAULT as it is a reserved name
    if factor_name == 'DEFAULT':
        print(' DEFAULT is a reserved factor name!')
        return False

    get_stocks.delete_carbon_risk_factor_from_db(factor_name)

    return True


def show_bmg_series(factor_name):
    if not factor_name:
        print(' factor name is required !')
        return False
    print(get_stocks.load_carbon_risk_factor_from_db(factor_name))
    return True


def main(args):
    if args.show_factor_name:
        return show_bmg_series(args.show_factor_name)
    elif args.delete_factor_name:
        return delete_bmg_series(args.delete_factor_name)
    else:
        return add_bmg_series(args.factor_name, args.green_ticker, args.brown_ticker)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--show_factor_name",
                        help="specify the factor name to display, for testing")
    parser.add_argument("-d", "--delete_factor_name",
                        help="specify the factor name to remove, cannot be DEFAULT which is a reserved name")
    parser.add_argument("-n", "--factor_name",
                        help="specify the factor name, cannot be DEFAULT which is a reserved name")
    parser.add_argument("-g", "--green_ticker",
                        help="specify the green ticker")
    parser.add_argument("-b", "--brown_ticker",
                        help="specify the brown ticker")
    parser.add_argument("-s", "--start_date",
                        help="Sets the start date for the factor, must be in the YYYY-MM-DD format, defaults to the start date of all the data series for a given stock")
    parser.add_argument("-e", "--end_date",
                        help="Sets the end date for the factor, must be in the YYYY-MM-DD format, defaults to the last date of all the data series for a given stock")
    if not main(parser.parse_args()):
        parser.print_help()

