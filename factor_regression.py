import pandas as pd
import numpy as np
import statsmodels.api as sm

### Gets the CSVs and converts it into the form for the rest to use (mode date to index)
def convert_to_form(df):
    df.index = df[df.columns[0]]
    df.drop(df.columns[0], axis = 1, inplace = True)
    return(df)

### Merges the 3 dataframes (returns, FF, carbon) into 1 dataframe
def merge_data(df1, df2):
    df1['date'] = df1.index
    df2['date'] = df2.index
    final_df = pd.merge(df1, df2, how = 'inner', left_on = 'date', right_on = 'date')
    final_df.index = final_df['date']
    final_df.index.rename('Date', inplace = True)
    final_df.drop('date', axis = 1, inplace = True)
    return(final_df)

### Read in the data
stock_data = pd.read_csv('stock_data.csv')
carbon_data = pd.read_csv('carbon_risk_factor.csv')
ff_data = pd.read_csv('ff_factors.csv')

### Convert the CSV into dataframes ready for manipulation
stock_data = convert_to_form(stock_data)
carbon_data = convert_to_form(carbon_data)
ff_data = convert_to_form(ff_data)

### Convert stock prices to returns and FF to percentages
# stock_data['Close'] = np.log(stock_data['Close'])
# stock_data = stock_data.diff(periods = 1)
# stock_data.dropna(inplace=True)
ff_data = ff_data/100

### Merge the 3 data frames together (inner join on dates)
all_factor_df = merge_data(stock_data, carbon_data)
all_factor_df = merge_data(all_factor_df, ff_data)

### Separate into independent (x) and dependent (y) factors)
y = all_factor_df[all_factor_df.columns[0]]
x = all_factor_df.drop(all_factor_df.columns[0], axis = 1)
x = sm.add_constant(x)

### Estimate regression
model = sm.OLS(y, x).fit()
print(model.summary())
