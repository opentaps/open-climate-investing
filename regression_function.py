import pandas as pd
import statsmodels.api as sm
import statsmodels.stats as stats


def regression_input_output(all_factor_df, stock_name):
    # Separate into independent (x) and dependent (y) factors)
    y = all_factor_df[all_factor_df.columns[0]]
    x = all_factor_df.drop(all_factor_df.columns[0], axis=1)
    x.insert(0, 'Constant', 1)

    # Estimate regression
    model = sm.OLS(y, x).fit()

    coef_df = pd.read_html(
     model.summary().tables[1].as_html(), header=0, index_col=0)[0]
    coef_df_simple = coef_df[['coef', 'std err', 't', 'P>|t|']]
    coef_df_simple = pd.DataFrame.transpose(coef_df_simple)
    coef_df_simple['Name'] = stock_name
    cols = coef_df_simple.columns.tolist()
    cols = cols[-1:] + cols[:-1]
    coef_df_simple = coef_df_simple[cols]

    model_dw_stat = stats.stattools.durbin_watson(model.resid)
    model_jb_stat = stats.stattools.jarque_bera(model.resid)
    model_bp_stat = stats.diagnostic.het_breuschpagan(
        model.resid, model.model.exog)
    coef_df_simple['Jarque-Bera'] = [
        str(round(model_jb_stat[0], 4)), '', '', str(round(model_jb_stat[1], 4))]
    coef_df_simple['Breusch-Pagan'] = [
        str(round(model_bp_stat[0], 4)), '', '', str(round(model_bp_stat[1], 4))]
    coef_df_simple['Durbin-Watson'] = [
        str(round(model_dw_stat, 4)), '', '', '']
    coef_df_simple['R Squared'] = [
        str(round(model.rsquared, 4)), '', '', '']

    return(model, coef_df_simple)
