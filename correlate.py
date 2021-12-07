import pandas as pd
import db
import argparse
import statsmodels.api as sm
import psycopg2.extras as extras
import psycopg2


def execute_batch(conn, df, table):
    """
    Using psycopg2.extras.execute_batch() to insert the dataframe
    """
    # Create a list of tupples from the dataframe values
    tuples = [tuple(x) for x in df.to_numpy()]
    # Comma-separated dataframe columns
    cols = ','.join(list(df.columns))
    # SQL quert to execute
    query = "INSERT INTO %s(%s) VALUES(%%s,%%s,%%s)" % (table, cols)
    cursor = conn.cursor()
    try:
        extras.execute_batch(cursor, query, tuples)
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print("Error: %s" % error)
        conn.rollback()
        cursor.close()
        return 1
    print("execute_batch() done")
    cursor.close()


def main(args):

    conn = db.get_db_connection()
    sql = '''SELECT
            date as "date",
            factor_name as "factor_name",
            factor_value as "factor_value"
        FROM additional_factors
        /* WHERE factor_name = %s */
        ORDER BY factor_name, date
        '''

    additional_factor_df = pd.read_sql_query(sql, con=db.DB_CREDENTIALS,
                                             index_col='date', params=(args.bmg_factor_name,))

    additional_factor_names = additional_factor_df['factor_name'].unique()

    sql = '''SELECT
            date,
            mkt_rf,
            smb,
            hml,
            wml
        FROM ff_factor
        ORDER BY date
        '''

    ff_factors_df = pd.read_sql_query(sql, con=db.DB_CREDENTIALS,
                                      index_col='date')

    sql = '''SELECT
            date,
            bmg
        FROM carbon_risk_factor
        WHERE factor_name = %s
        ORDER BY date
        '''

    bmg_factors_df = pd.read_sql_query(sql, con=db.DB_CREDENTIALS,
                                       index_col='date', params=(args.bmg_factor_name,))

    final_df = bmg_factors_df
    final_df = pd.merge(bmg_factors_df,
                        ff_factors_df,
                        on='date',
                        how='left')

    for factor_name in additional_factor_names:
        individual_factor_df = additional_factor_df.loc[additional_factor_df['factor_name'] == factor_name]
        final_df = pd.merge(final_df,
                            individual_factor_df,
                            on='date',
                            how='left')
        final_df = final_df.rename(columns={'factor_value': factor_name})
        final_df = final_df.drop('factor_name', axis=1)
        final_df = final_df.dropna()

    print(final_df.corr())

    y = final_df[final_df.columns[0]]
    x = final_df.drop(final_df.columns[0], axis=1)
    x.insert(0, 'Constant', 1)

    # Estimate regression
    model = sm.OLS(y, x).fit()

    if args.verbose:
        print(model.summary())

    # Get coefficient results
    coef_df = pd.read_html(
        model.summary().tables[1].as_html(), header=0, index_col=0)[0]
    coef_df_simple = coef_df[['coef', 'std err', 't', 'P>|t|']]
    coef_df_simple = pd.DataFrame.transpose(coef_df_simple)
    cols = coef_df_simple.columns.tolist()
    cols = cols[-1:] + cols[:-1]
    coef_df_simple = coef_df_simple[cols]

    # Get the p-values of the coefficients and select below significance
    chosen_vars = coef_df_simple.iloc[3, :]
    chosen_vars = chosen_vars[chosen_vars < args.significance]
    chosen_vars = chosen_vars.index
    chosen_vars = chosen_vars[chosen_vars != "Constant"]

    # Simplify input matrix to only include significant variables
    x = x.loc[:, chosen_vars]
    x.insert(0, 'Constant', 1)

    # Run final orthogonalisation regresssion
    model = sm.OLS(y, x).fit()
    if args.verbose:
        print(model.summary())

    orthog_name = args.bmg_factor_name + "-ORTHOGONALISED"

    resid_table = pd.DataFrame()
    resid_table["date"] = model.resid.index
    resid_table["factor_name"] = orthog_name
    resid_table["bmg"] = model.resid.values
    if args.verbose:
        print(resid_table)

    # Delete if previously orthogonalised
    del_sql = '''DELETE
              FROM carbon_risk_factor
              WHERE factor_name = %s
              '''
    with conn.cursor() as cursor:
        cursor.execute(
            del_sql, (orthog_name, ))

    # Insert into carbon risk factor table
    execute_batch(conn, resid_table, 'carbon_risk_factor')


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--bmg_factor_name", default='DEFAULT',
                        help="Sets the factor name of the carbon_risk_factor used")
    parser.add_argument("-s", "--significance", default=0.1,
                        help="Sets the p-value that is considered significant for orthogonalisation")
    parser.add_argument("-v", "--verbose", action='store_true',
                        help="Provides much more output data")
    main(parser.parse_args())
