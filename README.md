### open-climate-investing
init code by Si Chen and Matthew Bowler

### modules used
numpy
pandas
yfinance
statsmodels
datetime

### Execution
stock_price_script.py allows for the download of stock prices using the Yahoo Finance API

stock_price_function.py adjusts this so it returns an object (which is used later)

factor_regression.py loads in the stock prices, the carbon risk factor and the Fama-French factors. The names of these CSVs are asked for. If stock data would be liked to be downloaded, then it will use stock_price_function.py to do so

### To Use
Ensure that you have the relevant modules installed
Have stock_price_script.py in the same folder as factor_regression.py
Have your factor CSVs saved
Run factor_regression.py
Follow the prompts and enter the names of the CSVs as asked

### Outputs
Currently just a print output of the statsmodel object, the statsmodel coefficient summary and the coefficient & p-Values (to replicate that of the CARIMA paper)
