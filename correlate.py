import pandas as pd
import db
import argparse
import statsmodels.api as sm
import statsmodels.stats as stats


def main(args):
    sql = '''SELECT
            date as "date",
            factor_name as "factor_name",
            factor_value as "factor_value"
        FROM additional_factors
        /* WHERE factor_name = %s */
        ORDER BY factor_name, date
        '''

    factor_name = "nada"

    additional_factor_df = pd.read_sql_query(sql, con=db.DB_CREDENTIALS,
                                             index_col='date', params=(factor_name,))

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
    print(model.summary())


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--bmg_factor_name", default='DEFAULT',
                        help="Sets the factor name of the carbon_risk_factor used")
    main(parser.parse_args())
