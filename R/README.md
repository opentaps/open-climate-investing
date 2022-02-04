# R scripts

These scripts were mostly used for the development of the model.  You don't need them to use the software, but they are here in case you want to explore a bit more.

To use the R scripts and apps, please download the latest version of [R](https://cran.r-project.org/) and [RStudio](https://www.rstudio.com/products/rstudio/download/).
Open the script `/R/requirements_r.R` and run it.
This will install all the packages

Start R Studio and set your working directory to `open-climate-investing` either with Session > Set working Directory or the following command in the R Studio console:
```
setwd("~/path-to-my/open-climate-investing")
```

- bulk_stock_return_downloader.R is a method to download multiple stocks. Using line 8, replace "stock_tickers.csv" with the list of tickers you wish to use, saved as a CSV in the data/ folder