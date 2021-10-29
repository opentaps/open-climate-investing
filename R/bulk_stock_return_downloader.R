# Used to get data from Yahoo
library(quantmod)
# This allows for easy manipulation of the data
library(tidyverse)
# This is for date management
library(lubridate)

stock_tickers <- read.csv("data/stock_tickers_msci_world.csv", header = FALSE)
final_stock_returns <- c()
ticker_error_codes <- c()

#Loop to get the stocks
for (i in 1:nrow(stock_tickers)) {
  # Pull the stock ticker from Yahoo Finance with Quantmod
  temp_holder <- tryCatch({
    getSymbols(stock_tickers[i, 1],
               auto.assign = FALSE,
               periodicity = "monthly",
               from = "1999-12-01")
  },
  error=function(cond) {
    ticker_error_codes <<- c(ticker_error_codes, stock_tickers[i, 1])
    message(paste("Stock does not seem to exist:", stock_tickers[i, 1]))
    return(NA)
  })

  if (length(temp_holder) > 1) {
    # Choose a return value in case of error
    # Only use the column for close prices
    temp_holder <- temp_holder[, 4]
    # Calculate the monthly returns of the stock using Quantmod
    temp_holder <- monthlyReturn(temp_holder)
    temp_holder <- temp_holder[-1]

    # Change the object from XTS to a tibble (to make sure month ends are the same)
    temp_holder <- tibble(index(temp_holder), as.vector(temp_holder))
    # Change the column names for compatibility
    colnames(temp_holder) <- c("Date", "Returns")
    # Transform the date column to dates
    temp_holder$Date <- as.Date(temp_holder$Date)
    # Make the date column be month ends
    temp_holder$Date <- ceiling_date(temp_holder$Date, "month") - 1

    # Put the name of the stock next to it
    temp_holder <- temp_holder %>%
      mutate(Stock = stock_tickers[i, 1])

    # Add the stock to the main stock return dataframe
    final_stock_returns <- rbind(final_stock_returns, temp_holder)
    print(stock_tickers[i, 1])
  }
}


# Saves the returns as a CSV
write_csv(final_stock_returns, "msci_constituent_returns.csv")
