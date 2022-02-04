# User Interface

To start the user interface, start both the node server and the react app (simultaneously in two terminal sessions) :
```
cd ui/node-server
npm run start
```
and
```
cd ui/react
npm run start
```

There are two tabs: Stocks and BMG Analysis.  The Stocks tab allows you to search for individual stocks or sector ETF funds, and then look at their statistics.  The BMG Analysis helps you analyze the validity of your BMG data series for identifying climate risks.  It shows how many stocks in different sectors have market-implied climate risk based on your BMG series and what the market-implied climate risk factor loadings look like for those stocks.

### Understanding the Output

The model uses the coefficients on each factor to calculate the stocks loadings on to it. If it is positive, it indicates that the stock returns are positively linked to that factor (i.e. if that factor increases, the returns increase), and the inverse if it is negative.

To determine if it is statistically significant, the t-statistic is calculated and the p-value provided. The null hypothesis is that the coefficient is not statistically significant. Thus, if the probability is below a cutoff, the null hypothesis is rejected and the loading can be considered statistically significant. A cutoff commonly used is the 5% level. In this case, if the p-value is below 0.05, then the loading is considered to be statistically significant.

Ordinary least square regression is based on certain assumptions. There are a variety of statistics that are used to test these assumptions, some of which are presented in the output.

The Jarque-Bera statistic tests the assumption that the data is Gaussian distributed (also known as normally distributed). The null hypothesis in this case is that the distribution is not different to what is expected if it follows a Gaussian distributed. If the p-value is above the cutoff, then one can assume that it is Gaussian distributed and the assumption of Gaussian distribution is not violated.

The Breusch-Pagan tests for heteroskedasticity. Hetereskedasticity is the phenomenon where the the variability of the random disturbance is different across elements of the factors used, ie the variability of the stock returns changes as the values of the factors change.  The null hypothesis is that there is no heteroskedasticity, so if the p-value is below the cutoff, then there is not evidence to suggest that the assumption of homogeneity is violated.

The Durbin-Watson test calculated whether there is autocorrelation. Autocorrelation occurs when the errors are correlated with time (i.e. the unsystematic/stock-specific risk of the stock changes through time). A value between 1.5 and 2.5 is traditionally used to conclude that there is no autocorrelation.

The R Squared is what percentage of the stock returns (dependent variable) are explained by the factors (independent variables). The higher the percentage, the more of a stock returns can be considered to be based on the factor model.

An overview of ordinary least-squares regression can be found [here on Wikipedia](https://en.wikipedia.org/wiki/Ordinary_least_squares)

## Configuration

The UI uses the same db.ini configuration file, so you do not have to configure the database for it separately.