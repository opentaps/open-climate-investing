# open-climate-investing

If you've ever heard that ESG investing is hard, that there's not enough climate disclosures, that we don't know enough...

__STOP__

This project is here to make climate investing actionable.  We are building both open source software and openly available data sets so that you can identify relative value trades, optimize portfolios, and structure benchmarks for climate aligned investing.

Our first project is an implementation of the [Carbon Risk Management (CARIMA) model](https://www.uni-augsburg.de/de/fakultaet/wiwi/prof/bwl/wilkens/sustainable-finance/downloads/) developed by Universtat Augsburg with funding from the German
Federal Ministry of Education and Research.  CARIMA is a multi-factor market returns model based on the Fama French 3 Factor Model plus an additional Brown Minus Green (BMG) return history, provided as part of the original
research project.  It can be used for a variety of climate investing applications, including:
- Calculate the market-implied carbon risk of a stock, investment portfolio, mutual fund, or bond based on historical returns
- Determine the market reaction to the climate policies of a company
- Optimize a portfolio to minimize carbon risk subject to other parameters, such as index tracking or growth-value-sector investment strategies.

## Running the Code
Install the required python modules (use `pip3` instead of `pip` according to your python installation):
```
pip install -r requirements.txt
```

### Using a Database

Init the Database using:
```
./init_db.sh
```

Note: if you need a different database or credentials, edit both `init_db.sh` and `db.py`.

The stock interface uses `get_stocks.py` will save the output in the `stock_data` table and can used the following ways:

- `python get_stocks.py -f some_ticker_file.csv` for using a csv source file
- `python get_stocks.py -t ALB` to load a single stock with ticker `ALB`
- `python get_stocks.py -s ALB` shows whether there is data stored for the ticker `ALB`

Running the regression, the `get_regressions.py` script will save the output in the `stock_stats` table.

All instances support optional parameters:
- `-s YYY-MM-DD` to specify an optional start date, by default it will start at the earliest common date from the stocks and risk factors
- `-e YYY-MM-DD` to specify an optional end date, by default it will end at the latest common date from the stocks and risk factors
- `-i N` for the regression interval in months (defaults to 60 months).

- `python get_regressions.py` for running all the stocks in the database
- `python get_regressions.py -f some_ticker_file.csv` for using a csv source file
- `python get_regressions.py -t ALB` to run and store the regression for a given stock


### Viewing the Results

There is a react UI in the `ui/` directory.  It will need data including stocks and their regression results (see above) in the database.  Once you've
run `get_regressions.py`, then you can use this UI to view the results.

To run it, start both the node server and the react app (simultaneously in two terminal sessions) :
```
cd ui/node-server
npm run start
```
and
```
cd ui/react
npm run start
```

### Running Command Line Scripts

These have been deprecated but are still available and can be used to  run regressions in the command line without the database:
```
python factor_regression.py
```
The inputs are:
- Stock return data: Use the `stock_data.csv` or enter a ticker
- Carbon data: The BMG return history.  By default use `carbon_risk_factor.csv` from the original CARIMA project.
- Fama-French factors: Use either `ff_factors.csv` from the original CARIMA project or `ff_factors_north_american.csv` which is the Fama/French North American 3 Factors series and the North American Momentum Factor (Mom) series from the [Dartmouth Ken French Data Library](http://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html)

The output will be a print output of the statsmodel object, the statsmodel coefficient summary, including the coefficient & p-Values (to replicate that of the CARIMA paper)

stock_price_function.py adjusts this so it returns an object (which is used later)

factor_regression.py loads in the stock prices, the carbon risk factor and the Fama-French factors. The names of these CSVs are asked for. If stock data would be liked to be downloaded, then it will use stock_price_function.py to do so

- Ensure that you have the relevant modules installed
- Have stock_price_script.py in the same folder as factor_regression.py
- Have your factor CSVs saved
- Run factor_regression.py and follow the prompts and enter the names of the CSVs as asked

## Understanding the Output

The model uses the coefficients on each factor to calculate the stocks loadings on to it. If it is positive, it indicates that the stock returns are positively linked to that factor (i.e. if that factor increases, the returns increase), and the inverse if it is negative.

To determine if it is statistically significant, the t-statistic is calculated and the p-value provided. The null hypothesis is that the coefficient is not statistically significant. Thus, if the probability is below a cutoff, the null hypothesis is rejected and the loading can be considered statistically significant. A cutoff commonly used is the 5% level. In this case, if the p-value is below 0.05, then the loading is considered to be statistically significant.

Ordinary least square regression is based on certain assumptions. There are a variety of statistics that are used to test these assumptions, some of which are presented in the output.

The Jarque-Bera statistic tests the assumption that the data is Gaussian distributed (also known as normally distributed). The null hypothesis in this case is that the distribution is not different to what is expected if it follows a Gaussian distributed. If the p-value is above the cutoff, then one can assume that it is Gaussian distributed and the assumption of Gaussian distribution is not violated.

The Breusch-Pagan tests for heteroskedasticity. Hetereskedasticity is the phenomenon where the the variability of the random disturbance is different across elements of the factors used, ie the variability of the stock returns changes as the values of the factors change.  The null hypothesis is that there is no heteroskedasticity, so if the p-value is below the cutoff, then there is not evidence to suggest that the assumption of homogeneity is violated.

The Durbin-Watson test calculated whether there is autocorrelation. Autocorrelation occurs when the errors are correlated with time (i.e. the unsystematic/stock-specific risk of the stock changes through time). A value between 1.5 and 2.5 is traditionally used to conclude that there is no autocorrelation.

The R Squared is what percentage of the stock returns (dependent variable) are explained by the factors (independent variables). The higher the percentage, the more of a stock returns can be considered to be based on the factor model.

An overview of ordinary least-squares regression can be found [here on Wikipedia](https://en.wikipedia.org/wiki/Ordinary_least_squares)

## R Scripts

To use the R scripts and apps, please download the latest version of [R](https://cran.r-project.org/) and [RStudio](https://www.rstudio.com/products/rstudio/download/).
Open the script `/R/requirements_r.R` and run it.
This will install all the packages

- bulk_stock_return_downloader.R is a method to download multiple stocks. Using line 8, replace "stock_tickers.csv" with the list of tickers you wish to use, saved as a CSV in the data/ folder

## The Book

A [free book](book/README.md) which explains climate investing and how to use this project.  You can also [read it online at gitbook](https://app.gitbook.com/@opentaps/s/open-climate-investing/v/main/book).

## Data Sources

Data included in this project come from the following sources:

* The Fama French factors, risk free rate, and momentum come from the Developed 3 Factors and Developed MOM Factors from [Dartmouth Ken French Data Library](http://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html) via the CARIMA project.  There are small differences between their factors and the ones directly from the Dartmouth.
* Index returns and constituents are based on traded ETF's:
    * MSCI World is from the [iShares MSCI World Index ETF (ticker XWD)](https://www.blackrock.com/ca/investors/en/products/239697/ishares-msci-world-index-etf)
    * MSCI All Country World Index (ACWI) is from [iShares MSCI ACWI ETF (ticker ACWI)](https://www.ishares.com/us/products/239600/ishares-msci-acwi-etf#/)
    * MSCI ACWI Low Carbon Index is from [iShares MSCI ACWI Low Carbon Target ETF (ticker CRBN)](https://www.ishares.com/us/products/271054/ishares-msci-acwi-low-carbon-target-etf)
    * S&P 500 is from the [iShares Core S&P 500 ETF (ticker IVV)](https://www.ishares.com/us/products/239726/ishares-core-sp-500-etf)
    * S&P 500 Paris Aligned is from the [iShares S&P 500 Paris-Aligned Climate UCITS ETF (ticker UPAB)](https://www.ishares.com/uk/individual/en/products/318387/ishares-s-p-500-paris-aligned-climate-ucits-etf)
    * S&P® Oil & Gas Exploration & Production Select Industry® Index is from the [SPDR® S&P® Oil & Gas Exploration & Production ETF (ticker XOP)](https://www.ssga.com/us/en/intermediary/etfs/funds/spdr-sp-oil-gas-exploration-production-etf-xop)
    * MVIS Global Low Carbon Energy Index is from the [VanEck Low Carbon Energy ETF (ticker SMOG)](https://www.vaneck.com/us/en/investments/low-carbon-energy-etf-smog/)
    * List of [ETFs corresponding to S&P 500 sectors](https://www.sectorspdr.com/sectorspdr/)
    * List of [ETFs corresponding to MSCI sectors](https://www.msci.com/documents/1296102/1360895/MSCI-Exchange-Traded-Products-ETFs-Based-on-MSCI-Indexes-Q4-2018.pdf/4a82c677-0fe4-12f0-1be2-26076423f862) 
* Fixed income market data come are from these sources:
    * Interest rate data is from [Federal Reserve H15](https://www.federalreserve.gov/datadownload/Choose.aspx?rel=H15) using Monthly Averages. 
    * BBB OAS is from [St Louis Fed BAMLC0A4CBBB](https://fred.stlouisfed.org/series/BAMLC0A4CBBB/downloaddata) using Frequenty=Monthly, Aggregation=End of Period 
    * High Yield OAS is from [St Louis Fed BAMLH0A0HYM2](https://fred.stlouisfed.org/series/BAMLH0A0HYM2/downloaddata) using Frequenty=Monthly, Aggregation=End of Period																		

## References
- [Carbon Risk Management (CARIMA) Manual](https://assets.uni-augsburg.de/media/filer_public/ad/69/ad6906c0-cad0-493d-ba3d-1ec7fee5fb72/carima_manual_english.pdf)
- [A Practitioner's Guide to Factor Models] (https://www.cfainstitute.org/en/research/foundation/1994/a-practitioners-guide-to-factor-models)
- [The Barra US Equity Model (USE4)](http://cslt.riit.tsinghua.edu.cn/mediawiki/images/4/47/MSCI-USE4-201109.pdf)
- [Network for Greening the Financial System, Case Studies of Environmental Risk Analysis Methodologies](https://www.ngfs.net/sites/default/files/medias/documents/case_studies_of_environmental_risk_analysis_methodologies.pdf)
