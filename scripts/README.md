# Scripts

These are mostly python scripts used for data analysis, both in the command line and by the UI component:

 * `setup_db.py` - Initialize the database and load basic data
 * `get_stocks.py` - Get stock historical data
 * `get_regressions.py` - Calculate regressions for stocks versus factors
 * `bmg_series.py` - Create your own BMG series of high versus low climate risk stock returns
 * `correlate.py` - Calculate correlation of your BMG series versus other factors and create orthognalized series
 * `bmg_anlayze.py` - Analyze your BMG series's effectiveness in number of climate risk stocks identified by sector

Each of them has a `--help` option which explains what the parameters are. 

## Examples

Then use `get_stocks.py` to get stock information for `stocks` table and return history for the `stock_data` table:

- `python scripts/get_stocks.py -f some_ticker_file.csv` for using a csv source file
- `python scripts/get_stocks.py -t ALB` to load a single stock with ticker `ALB`
- `python scripts/get_stocks.py -s ALB` shows whether there is data stored for the ticker `ALB`

If your stock ticker is a composite stock, it will calculate the historical returns using the weights in the `stock_components` table.

By default the script will get the Monthly stock values, to get Daily values use `--frequency=DAILY`, eg:
- `python scripts/get_stocks.py -f some_ticker_file.csv --frequency=DAILY` for using a csv source file
- `python scripts/get_stocks.py -t ALB --frequency=DAILY` to load a single stock with ticker `ALB`
- `python scripts/get_stocks.py -s ALB --frequency=DAILY` shows whether there is data stored for the ticker `ALB`

To run the regression, use `get_regressions.py` to save the output in the `stock_stats` table:
- `python scripts/get_regressions.py` for running all the stocks in the database
- `python scripts/get_regressions.py -f some_ticker_file.csv` for using a csv source file
- `python scripts/get_regressions.py -t ALB` to run and store the regression for a given stock

Likewise for using Daily values, eg:
- `python scripts/get_regressions.py -t ALB --frequency=DAILY` to run and store the regression for a given stock

It will use the stock returns in the database by default, or if none are found, get them first.  It has some optional parameters:
- `-s YYYY-MM-DD` to specify an optional start date, by default it will start at the earliest common date from the stocks and risk factors
- `-e YYYY-MM-DD` to specify an optional end date, by default it will end at the latest common date from the stocks and risk factors
- `-i N` for the regression interval in months (defaults to 60 months).
- `-n FACTOR_NAME` to specify the BMG factor to use.  If not specified, `DEFAULT` will be used.
- `-h` to see all parameters available

To calculate a BMG series and store it in the database:
```
python scripts/bmg_series.py -n XOP-SMOG -g SMOG -b XOP
```
where
- `-n <series name>` is the name of your bmg series
- `-b` is the ticker of your Brown stock 
- `-g` is the ticker of your Green stock

Likewise for using Daily values, eg:
```
python scripts/bmg_series.py -n XOP-SMOG -g SMOG -b XOP --frequency=DAILY
```

## Command Line Scripts

These have been deprecated but are still available and can be used to  run regressions in the command line without the database:
```
python scripts/factor_regression.py
```
The inputs are:
- Stock return data: Use the `stock_data.csv` or enter a ticker
- Carbon data: The BMG return history.  By default use `carbon_risk_factor.csv`.
- Fama-French factors: Use either `ff_factors.csv`, which are the `Fama/French Developed 3 Factors` and `Developed Momentum Factor (Mom)`, or `ff_factors_north_american.csv`,  which are the Fama/French `North American 3 Factors` and the `North American Momentum Factor (Mom)` series, from the [Dartmouth Ken French Data Library](http://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html)  The original CARIMA project used the data from `ff_factors.csv`

The output will be a print output of the statsmodel object, the statsmodel coefficient summary, including the coefficient & p-Values (to replicate that of the CARIMA paper)

stock_price_function.py adjusts this so it returns an object (which is used later)

factor_regression.py loads in the stock prices, the carbon risk factor and the Fama-French factors. The names of these CSVs are asked for. If stock data would be liked to be downloaded, then it will use stock_price_function.py to do so

- Ensure that you have the relevant modules installed
- Have stock_price_script.py in the same folder as factor_regression.py
- Have your factor CSVs saved
- Run factor_regression.py and follow the prompts and enter the names of the CSVs as asked

