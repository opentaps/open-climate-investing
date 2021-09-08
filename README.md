# open-climate-investing

This is an implementation of the [Carbon Risk Management (CARIMA) model](https://www.uni-augsburg.de/de/fakultaet/wiwi/prof/bwl/wilkens/sustainable-finance/downloads/) developed by Universtat Augsburg with funding from the German
Federal Ministry of Education and Research.  CARIMA is a multi-factor market returns model based on the Fama French 3 Factor Model plus an additional Brown Minus Green (BMG) return history, provided as part of the original
research project.  It can be used for a variety of climate investing applications, including:
- Calculate the market-implied carbon risk of a stock, investment portfolio, mutual fund, or bond based on historical returns
- Determine the market reaction to the climate policies of a company
- Optimize a portfolio to minimize carbon risk subject to other parameters, such as index tracking or growth-value-sector investment strategies.

### Running the Code
Install the required python modules (use `pip3` instead of `pip` according to your python installation):
```
pip install -r requirements.txt
```

Then:
```
python3 factor_regression.py
```
The inputs are:
- Stock return data: Use the `stock_data.csv` or enter a ticker
- Carbon data: The BMG return history.  By default use `carbon_risk_factor.csv` from the original CARIMA project.
- Fama-French factors: Use either `ff_factors.csv` from the original CARIMA project or `ff_factors_north_american.csv` which is the Fama/French North American 3 Factors series and the North American Momentum Factor (Mom) series from the [Dartmouth Ken French Data Library](http://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html)

The output will be a print output of the statsmodel object, the statsmodel coefficient summary, including the coefficient & p-Values (to replicate that of the CARIMA paper)


### Code
stock_price_function.py adjusts this so it returns an object (which is used later)

factor_regression.py loads in the stock prices, the carbon risk factor and the Fama-French factors. The names of these CSVs are asked for. If stock data would be liked to be downloaded, then it will use stock_price_function.py to do so


### Script Overview
- Ensure that you have the relevant modules installed
- Have stock_price_script.py in the same folder as factor_regression.py
- Have your factor CSVs saved
- Run factor_regression.py and follow the prompts and enter the names of the CSVs as asked

### Output Interpretation
There are various statistics that are produced. The model replicated uses the coefficients on each factor to calculate the stocks loadings on to it. If it is positive, it indicates that the stock returns are positively linked to that factor (i.e. if that factor increases, the returns increase), and the inverse if it is negative. 
To determine if it is statistically significant, the t-statistic is calculated and the p-value provided. The null hypothesis is that the coefficient is not statistically significant. Thus, if the probability is below a cutoff, the null hypothesis is rejected and the loading can be considered statistically significant. A cutoff commonly used is the 5% level. In this case, if the p-value is below 0.05, then the loading is considered to be statistically significant.
Ordinary least square regression is based on certain assumptions. There are a variety of statistics that are used to test these assumptions, some of which are presented in the output.
The Jarque-Bera statistic tests the assumption that the data is Gaussian distributed (also known as normally distributed). The null hypothesis in this case is that the distribution is not different to what is expected if it follows a Gaussian distributed. If the p-value is above the cutoff, then one can assume that it is Gaussian distributed and the assumption of Gaussian distribution is not violated.
The Breusch-Pagan tests for heteroskedasticity. Hetereskedasticity is the phenomenon where the the variability of the random disturbance is different across elements of the factors used. The null hypothesis is that there is no heteroskedasticity, so if the p-value is below the cutoff, then there is not evidence to suggest that the assumption of homogeneity is violated.
The Durbin-Watson test calculated whether there is autocorrelation. Autocorrelation occurs when the errors are correlated with time (i.e. the unsystematic/stock-specific risk of the stock changes through time). A value between 1.5 and 2.5 is traditionally used to conclude that there is no autocorrelation.
The R Squared is what percentage of the stock returns (dependent variable) are explained by the factors (independent variables). The higher the percentage, the more of a stock returns can be considered to be based on the factor model.
An overview of ordinary least-squares can be found (here on Wikipedia)[https://en.wikipedia.org/wiki/Ordinary_least_squares]

## References
- [Carbon Risk Management (CARIMA) Manual](https://assets.uni-augsburg.de/media/filer_public/ad/69/ad6906c0-cad0-493d-ba3d-1ec7fee5fb72/carima_manual_english.pdf)
- [The Barra US Equity Model (USE4)](http://cslt.riit.tsinghua.edu.cn/mediawiki/images/4/47/MSCI-USE4-201109.pdf)
- [Network for Greening the Financial System, Case Studies of Environmental Risk Analysis Methodologies](https://www.ngfs.net/sites/default/files/medias/documents/case_studies_of_environmental_risk_analysis_methodologies.pdf)
