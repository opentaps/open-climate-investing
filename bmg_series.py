
import argparse
import get_stocks
import factor_regression
import textwrap
import pandas as pd
import db

conn = db.get_db_connection()

def add_bmg_series(factor_name, green_ticker, brown_ticker, start_date=None, end_date=None):
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

    print('*** adding factor {} from stocks {} and {} ...'.format(factor_name, green_ticker, brown_ticker))
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

    print('*** deleting factor {} ...'.format(factor_name))
    get_stocks.delete_carbon_risk_factor_from_db(factor_name)

    return True


def get_bmg_series():
    # show the current factors
    sql = 'select factor_name, min(date), max(date) from carbon_risk_factor group by factor_name order by factor_name;'
    with conn.cursor() as cursor:
        cursor.execute(sql)
        return cursor.fetchall()


def show_bmg_series(factor_name, start_date=None, end_date=None):
    if not factor_name:
        # show the current factors
        series = get_bmg_series()
        if series:
            for (n,from_date,to_date) in series:
                print('{} from {} to {}'.format(n,from_date,to_date))
        else:
            print('No BMG series found.')
        return True
    
    data = get_stocks.load_carbon_risk_factor_from_db(factor_name)

    if start_date is not None:
        start_date = factor_regression.parse_date('Start', start_date)
        data = data[data.index >= start_date]

    if end_date is not None:
        end_date = factor_regression.parse_date('End', end_date)
        data = data[data.index <= end_date]

    print(data)

    return True


def get_stocks_with_significant_final_regression(significance):
    sql = '''
        select x.ticker, x.bmg_factor_name, ss.bmg_p_gt_abs_t
        from
            (select ticker, bmg_factor_name, max(thru_date) as thru_date
            from stock_stats group by ticker, bmg_factor_name) x
        left join stock_stats ss on ss.ticker = x.ticker and ss.bmg_factor_name = x.bmg_factor_name and ss.thru_date = x.thru_date
        where ss.bmg_p_gt_abs_t < %s;
        '''
    with conn.cursor() as cursor:
        cursor.execute(sql, (significance,))
        return cursor.fetchall()


def show_stocks_with_significant_final_regression(significance):
    rows = get_stocks_with_significant_final_regression(significance)
    print('stock,bmg_factor_name')
    for (ticker,factor,*_) in rows:
        print('{},{}'.format(ticker,factor))
    return True


def get_stocks_with_significant_regressions(significance):
    sql = '''
        select ss.ticker, ss.bmg_factor_name, s.sector,
        count(1) as total,
        count(CASE WHEN bmg_p_gt_abs_t >= %s THEN 1 END) as not_significant,
        count(CASE WHEN bmg_p_gt_abs_t < %s THEN 1 END) as significant
        from stock_stats ss
        left join stocks s on ss.ticker = s.ticker
        group by ss.ticker, ss.bmg_factor_name, s.sector
        having count(CASE WHEN bmg_p_gt_abs_t < %s THEN 1 END) > count(CASE WHEN bmg_p_gt_abs_t >= %s THEN 1 END);
        '''
    with conn.cursor() as cursor:
        cursor.execute(sql, (significance, significance, significance, significance))
        return cursor.fetchall()


def show_stocks_with_significant_regressions(significance):
    rows = get_stocks_with_significant_regressions(significance)
    print('stock,bmg_factor_name,sector')
    for (ticker,factor,*_) in rows:
        print('{},{}'.format(ticker,factor))
    return True


def get_sectors_with_significant_regressions(significance):
    sql = '''
        select sector, bmg_factor_name, count(ticker)
        from (select ss.ticker, ss.bmg_factor_name, s.sector,
        count(1) as total,
        count(CASE WHEN bmg_p_gt_abs_t >= %s THEN 1 END) as not_significant,
        count(CASE WHEN bmg_p_gt_abs_t < %s THEN 1 END) as significant
        from stock_stats ss
        left join stocks s on s.ticker = ss.ticker
        group by ss.ticker, ss.bmg_factor_name, s.sector
        having count(CASE WHEN bmg_p_gt_abs_t < %s THEN 1 END) > count(CASE WHEN bmg_p_gt_abs_t >= %s THEN 1 END)) x
        group by sector, bmg_factor_name
        order by count(ticker) desc, sector;
        '''
    with conn.cursor() as cursor:
        cursor.execute(sql, (significance, significance, significance, significance))
        return cursor.fetchall()


def show_sectors_with_significant_regressions(significance):
    rows = get_sectors_with_significant_regressions(significance)
    print('sector,bmg_factor_name,count')
    for (sector,factor,count) in rows:
        print('{},{},{}'.format(sector,factor,count))
    return True


def main(args):
    if args.list_stocks_with_significant_final_regression:
        return show_stocks_with_significant_final_regression(args.significance)
    if args.list_stocks_with_significant_regressions:
        return show_stocks_with_significant_regressions(args.significance)
    if args.list_sectors_with_significant_regressions:
        return show_sectors_with_significant_regressions(args.significance)
    if args.show:
        return show_bmg_series(args.factor_name, start_date=args.start_date, end_date=args.end_date)
    else:
        if not args.factor_name:
            return False
        if args.delete:
            if not delete_bmg_series(args.factor_name):
                return False
        if args.green_ticker or args.brown_ticker:
            if not add_bmg_series(args.factor_name, args.green_ticker, args.brown_ticker, start_date=args.start_date, end_date=args.end_date):
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
                %(prog)s -n MY_FACTOR -g TICK1 -g TICK2
            
            Display all the series stored in the DB:
                %(prog)s -o

            Display the series values stored in the DB:
                %(prog)s -o MY_FACTOR
            
            Create a series MY_FACTOR from stocks TICK1 and TICK2 for 
            a given time period, deleting the existing values first:
                %(prog)s -n MY_FACTOR -g TICK1 -g TICK2 -d -s 2000-01-01 -e 2020-12-31

        ''')
    )
    parser.add_argument("-n", "--factor_name",
                        help="specify the factor name for the BMG series to operate on, cannot be DEFAULT which is a reserved name")
    parser.add_argument("-o", "--show", action='store_true',
                        help="display the series from the DB, for testing")
    parser.add_argument("--list_sectors_with_significant_regressions", action='store_true',
                        help="display the count of stocks by sectors that have at least half of their regressions being significant (bmg_p_gt_abs_t > SIGNIFICANCE) from the DB")
    parser.add_argument("--list_stocks_with_significant_regressions", action='store_true',
                        help="display the stocks that have at least half of their regressions being significant (bmg_p_gt_abs_t > SIGNIFICANCE) from the DB")
    parser.add_argument("--list_stocks_with_significant_final_regression", action='store_true',
                        help="display the stocks that have their final regression being significant (bmg_p_gt_abs_t > SIGNIFICANCE) from the DB")
    parser.add_argument("--significance", default=0.01,
                        help="Sets the p-value that is considered significant for list_stocks_with_significant_regressions")
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
    parser.add_argument("-v", "--verbose", action='store_true',
                        help="more output")
    if not main(parser.parse_args()):
        parser.print_help()

