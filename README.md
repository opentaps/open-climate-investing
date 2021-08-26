# open-climate-investing

This is an implementation of the [Carbon Risk Management (CARIMA) model](https://www.uni-augsburg.de/de/fakultaet/wiwi/prof/bwl/wilkens/sustainable-finance/downloads/) developed by Universtat Augsburg with funding from the German
Federal Ministry of Education and Research.  CARIMA is a multi-factor market returns model based on the Fama French 3 Factor Model plus an additional Brown Minus Green (BMG) return history, provided as part of the original 
research project.  It can be used for a variety of climate investing applications, including:
- Calculate the market-implied carbon risk of a stock, investment portfolio, mutual fund, or bond based on historical returns
- Determine the market reaction to the climate policies of a company
- Optimize a portfolio to minimize carbon risk subject to other parameters, such as index tracking or growth-value-sector investment strategies.

### Running the Code

Install the modules listed below.  Then

  python3 factor_regression.py

The inputs are:
- Stock return data: Use the `stock_data.csv` or enter a ticker
- Carbon data: The BMG return history.  By default use `carbon_risk_factor.csv` from the original CARIMA project.
- Fama-French factors: Use either `ff_factors.csv` from the original CARIMA project or `ff_factors_north_american.csv` which is the Fama/French North American 3 Factors series and the North American Momentum Factor (Mom) series from the [Dartmouth Ken French Data Library](http://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html)

The output will be a print output of the statsmodel object, the statsmodel coefficient summary and the coefficient & p-Values (to replicate that of the CARIMA paper)

### modules used
numpy

pandas

yfinance

statsmodels

datetime

### Code
stock_price_script.py allows for the download of stock prices using the Yahoo Finance API

stock_price_function.py adjusts this so it returns an object (which is used later)

factor_regression.py loads in the stock prices, the carbon risk factor and the Fama-French factors. The names of these CSVs are asked for. If stock data would be liked to be downloaded, then it will use stock_price_function.py to do so

### Script Overview
Ensure that you have the relevant modules installed
Have stock_price_script.py in the same folder as factor_regression.py
Have your factor CSVs saved
Run factor_regression.py
Follow the prompts and enter the names of the CSVs as asked


## References
- [Carbon Risk Management (CARIMA) Manual](https://assets.uni-augsburg.de/media/filer_public/ad/69/ad6906c0-cad0-493d-ba3d-1ec7fee5fb72/carima_manual_english.pdf)
- [The Barra US Equity Model (USE4)](http://cslt.riit.tsinghua.edu.cn/mediawiki/images/4/47/MSCI-USE4-201109.pdf)
- [Network for Greening the Financial System, Case Studies of Environmental Risk Analysis Methodologies](https://www.ngfs.net/sites/default/files/medias/documents/case_studies_of_environmental_risk_analysis_methodologies.pdf)
