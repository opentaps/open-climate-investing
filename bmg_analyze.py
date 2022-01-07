
import argparse
import get_stocks
import factor_regression
import textwrap
import pandas as pd
import db

conn = db.get_db_connection()


def get_count_of_stocks_per_sector(index_stock):
    sql = '''
        select distinct S.sector, count(SC.component_stock)
        from stocks as S
        join stock_components as SC
        on S.ticker = SC.component_stock
        where SC.ticker = %s
        group by S.sector;
    '''
    with conn.cursor() as cursor:
        cursor.execute(sql, (index_stock,))
        return cursor.fetchall()


def get_count_of_stocks_per_sector_map(index_stock):
    rows = get_count_of_stocks_per_sector(index_stock)
    return dict(rows)


def get_stocks_with_significant_final_regression(significance, factor_name=None):
    sql = '''
        select x.ticker, x.bmg_factor_name, ss.bmg_p_gt_abs_t
        from
            (select ticker, bmg_factor_name, max(thru_date) as thru_date
            from stock_stats group by ticker, bmg_factor_name) x
        left join stock_stats ss on ss.ticker = x.ticker and ss.bmg_factor_name = x.bmg_factor_name and ss.thru_date = x.thru_date
        where ss.bmg_p_gt_abs_t < %s
        '''
    if factor_name:
        sql += ' AND x.bmg_factor_name = %s'
    with conn.cursor() as cursor:
        if factor_name:
            cursor.execute(sql, (significance,factor_name,))
        else:
            cursor.execute(sql, (significance,))
        return cursor.fetchall()


def show_stocks_with_significant_final_regression(significance, factor_name=None):
    rows = get_stocks_with_significant_final_regression(significance, factor_name=factor_name)
    print('stock,bmg_factor_name')
    for (ticker,factor,*_) in rows:
        print('{},{}'.format(ticker,factor))
    return True


def get_stocks_with_significant_regressions(significance, factor_name=None):
    sql = '''
        select ss.ticker, ss.bmg_factor_name, s.sector,
        count(1) as total,
        count(CASE WHEN bmg_p_gt_abs_t >= %s THEN 1 END) as not_significant,
        count(CASE WHEN bmg_p_gt_abs_t < %s THEN 1 END) as significant
        from stock_stats ss
        left join stocks s on ss.ticker = s.ticker'''
    if factor_name:
        sql += ' where bmg_factor_name = %s '
    sql += '''
        group by ss.ticker, ss.bmg_factor_name, s.sector
        having count(CASE WHEN bmg_p_gt_abs_t < %s THEN 1 END) > count(CASE WHEN bmg_p_gt_abs_t >= %s THEN 1 END);
        '''
    with conn.cursor() as cursor:
        if factor_name:
            cursor.execute(sql, (significance, significance, factor_name, significance, significance))
        else:
            cursor.execute(sql, (significance, significance, significance, significance))
        return cursor.fetchall()


def show_stocks_with_significant_regressions(significance, factor_name=None):
    rows = get_stocks_with_significant_regressions(significance, factor_name=factor_name)
    print('stock,bmg_factor_name,sector')
    for (ticker,factor,*_) in rows:
        print('{},{}'.format(ticker,factor))
    return True


def get_sectors_with_significant_regressions(significance, factor_name=None):
    sql = '''
        select sector, bmg_factor_name, count(ticker)
        from (select ss.ticker, ss.bmg_factor_name, s.sector,
        count(1) as total,
        count(CASE WHEN bmg_p_gt_abs_t >= %s THEN 1 END) as not_significant,
        count(CASE WHEN bmg_p_gt_abs_t < %s THEN 1 END) as significant
        from stock_stats ss
        left join stocks s on s.ticker = ss.ticker'''
    if factor_name:
        sql += ' where bmg_factor_name = %s '
    sql += '''
        group by ss.ticker, ss.bmg_factor_name, s.sector
        having count(CASE WHEN bmg_p_gt_abs_t < %s THEN 1 END) > count(CASE WHEN bmg_p_gt_abs_t >= %s THEN 1 END)) x
        group by sector, bmg_factor_name
        order by count(ticker) desc, sector;
        '''
    with conn.cursor() as cursor:
        if factor_name:
            cursor.execute(sql, (significance, significance, factor_name, significance, significance))
        else:
            cursor.execute(sql, (significance, significance, significance, significance))
        return cursor.fetchall()


def show_sectors_with_significant_regressions(significance, factor_name=None, index_stock=None):
    rows = get_sectors_with_significant_regressions(significance, factor_name=factor_name)
    index_map = dict()
    if index_stock:
        print('sector,bmg_factor_name,count,ratio')
        index_map = get_count_of_stocks_per_sector_map(index_stock)
    else:
        print('sector,bmg_factor_name,count')
    for (sector,factor,count) in rows:
        if index_stock:
            index_count = index_map.get(sector)
            if index_count:
                ratio = count / index_count
            else:
                ratio = None
            print('{},{},{}.{}'.format(sector,factor,count,ratio))
        else:
            print('{},{},{}'.format(sector,factor,count))
    return True


def get_sectors_with_significant_final_regression(significance, factor_name=None):
    sql = '''
        select sector, bmg_factor_name, count(ticker)
        from (
            select s.sector, x.ticker, x.bmg_factor_name, ss.bmg_p_gt_abs_t
            from
                (select ticker, bmg_factor_name, max(thru_date) as thru_date
                from stock_stats group by ticker, bmg_factor_name) x
            left join stock_stats ss on ss.ticker = x.ticker and ss.bmg_factor_name = x.bmg_factor_name and ss.thru_date = x.thru_date
            left join stocks s on s.ticker = ss.ticker
            where ss.bmg_p_gt_abs_t < %s'''
    if factor_name:
        sql += ' AND ss.bmg_factor_name = %s'
    sql += '''
        ) y
        group by sector, bmg_factor_name
        order by count(ticker) desc, sector;
        '''
    with conn.cursor() as cursor:
        if factor_name:
            cursor.execute(sql, (significance,factor_name,))
        else:
            cursor.execute(sql, (significance,))
        return cursor.fetchall()


def show_sectors_with_significant_final_regression(significance, factor_name=None, index_stock=None):
    rows = get_sectors_with_significant_final_regression(significance, factor_name=factor_name)
    index_map = dict()
    if index_stock:
        print('sector,bmg_factor_name,count,ratio')
        index_map = get_count_of_stocks_per_sector_map(index_stock)
    else:
        print('sector,bmg_factor_name,count')
    for (sector,factor,count) in rows:
        if index_stock:
            index_count = index_map.get(sector)
            if index_count:
                ratio = count / index_count
            else:
                ratio = None
            print('{},{},{}.{}'.format(sector,factor,count,ratio))
        else:
            print('{},{},{}'.format(sector,factor,count))
    return True


def main(args):
    if args.list_stocks_with_significant_final_regression:
        return show_stocks_with_significant_final_regression(args.significance, factor_name=args.factor_name)
    if args.list_stocks_with_significant_regressions:
        return show_stocks_with_significant_regressions(args.significance, factor_name=args.factor_name)
    if args.list_sectors_with_significant_regressions:
        return show_sectors_with_significant_regressions(args.significance, factor_name=args.factor_name, index_stock=args.index_stock)
    if args.list_sectors_with_significant_final_regression:
        return show_sectors_with_significant_final_regression(args.significance, factor_name=args.factor_name, index_stock=args.index_stock)
    return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Output analysys of BMG series",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("-n", "--factor_name",
                        help="specify the factor name for the BMG series to operate on, cannot be DEFAULT which is a reserved name")
    parser.add_argument("--list_stocks_with_significant_regressions", action='store_true',
                        help="display the stocks that have at least half of their regressions being significant (bmg_p_gt_abs_t > SIGNIFICANCE) from the DB")
    parser.add_argument("--list_stocks_with_significant_final_regression", action='store_true',
                        help="display the stocks that have their final regression being significant (bmg_p_gt_abs_t > SIGNIFICANCE) from the DB")
    parser.add_argument("--list_sectors_with_significant_regressions", action='store_true',
                        help="display the count of stocks by sectors that have at least half of their regressions being significant (bmg_p_gt_abs_t > SIGNIFICANCE) from the DB, if index_stock is given also give the ratio of that number by the number of stocks in the index for the same sector")
    parser.add_argument("--list_sectors_with_significant_final_regression", action='store_true',
                        help="display the sectors that have their final regression being significant (bmg_p_gt_abs_t > SIGNIFICANCE) from the DB, if index_stock is given also give the ratio of that number by the number of stocks in the index for the same sector")
    parser.add_argument("--significance", default=0.05,
                        help="Sets the p-value that is considered significant for list_stocks_with_significant_regressions")
    parser.add_argument("-i", "--index_stock",
                        help="Sets the index stock to compare to, eg: XWD.TO")
    parser.add_argument("-s", "--start_date",
                        help="Sets the start date for the series, must be in the YYYY-MM-DD format, defaults to the earliest date on record")
    parser.add_argument("-e", "--end_date",
                        help="Sets the end date for the series, must be in the YYYY-MM-DD format, defaults to the latest date on record")
    parser.add_argument("-v", "--verbose", action='store_true',
                        help="more output")
    if not main(parser.parse_args()):
        parser.print_help()


