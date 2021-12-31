library(tidyverse)

# Make custom carbon factor by carving out the green shares from the primary
# index and then create a brown index from the remainder

# Function to create custom-weighted indices
create_custom_index <- function(stock_tickers,
                                stock_returns,
                                stock_ret_col_names,
                                method = "equal",
                                stock_breakdown = NULL,
                                breakdown_col_names = NULL) {
  
  # Align the columns from the input data to that of the function
  stock_ret_col_names <- list(Date = stock_ret_col_names[1],
                              Returns = stock_ret_col_names[2],
                              Ticker = stock_ret_col_names[3])
  
  # Get the returns of the carve-out tickers
  custom_return_data <- stock_returns %>%
    filter(.[[stock_ret_col_names$Ticker]] %in% stock_tickers) %>%
    rename(ticker = !!sym(stock_ret_col_names$Ticker),
           date = !!sym(stock_ret_col_names$Date),
           returns = !!sym(stock_ret_col_names$Returns))
  # 
  if (method == "equal") {
    # Equal weighting
    # This is simple. Just a grouping by dates and then averaging
    custom_return_data <- custom_return_data %>%
      group_by(date) %>%
      summarise(returns = mean(returns, na.rm = TRUE)) %>%
      ungroup()    
  } else if (method == "market") {
    # Market weighted
    # This is less simple. To do a market weight, the market weighting of
    # the green stocks as a whole in the primary index needs to be calculated.
    # The weights of the individual stocks is then divided by this sum to work
    # out the percentage of the green carveout that each stock has
    breakdown_col_names <- list(Ticker = breakdown_col_names[1],
                                Weight = breakdown_col_names[2])
    stock_weights <- stock_breakdown %>%
      filter(.[[breakdown_col_names$Ticker]] %in% stock_tickers) %>%
      rename(ticker = !!sym(breakdown_col_names$Ticker),
             weight = !!sym(breakdown_col_names$Weight)) %>%
      mutate(reweight = weight/sum(weight))
    custom_return_data <- custom_return_data %>%
      left_join(stock_weights, by = c("ticker" = "ticker")) %>%
      mutate(ret_weight_prod = returns * reweight) %>%
      group_by(date) %>%
      summarise(returns = sum(ret_weight_prod, na.rm = TRUE)) %>%
      ungroup()
  }

  
  return(custom_return_data)
}

# Load all stock returns
final_stock_returns <- read.csv('data/msci_constituent_returns.csv') # for msci
# final_stock_returns <- read.csv('data/spx_constituent_returns.csv') # for spx
final_stock_returns[, 1] <- as.Date(final_stock_returns[, 1])
final_stock_returns <- as_tibble(final_stock_returns)

### Removing outlier stock returns
final_stock_returns <- final_stock_returns %>%
  filter(Returns > -0.7,
         Returns < 1) %>%
  drop_na()

# Read in the sector breakdowns
final_stock_breakdown <- read_csv("data/msci_constituent_details.csv") # for msci
# final_stock_breakdown <- read_csv("data/spx_sector_breakdown.csv") # for spx


# Load in the green stock tickers
# Using SBTI Tickers
green_constituents <- read_csv("data/sbti_in_msci_tickers.csv")

# Only use companies that have set targets
green_constituents <- green_constituents %>%
  filter(Commitment == "Targets Set")

# Choose only the tickers and convert to vector
green_constituents <- green_constituents %>%
  pull(Tickers)

# Choose how you want the carve-out stocks to be weighted

# equally-weighted
green_constituent_returns <- create_custom_index(green_constituents,
                                                 final_stock_returns,
                                                 c("Date", "Returns", "Stock"),
                                                 "equal")

# market-weighted based on latest primary index weights
# green_constituent_returns <- create_custom_index(green_constituents,
#                                                  final_stock_returns,
#                                                  c("Date", "Returns", "Stock"),
#                                                  "market",
#                                                  final_stock_breakdown,
#                                                  c("Ticker", "Weight"))

green_constituent_returns <- green_constituent_returns %>%
  rename(green_returns = returns)

# Now use the remaining stocks as a brown index
brown_constituents <- final_stock_returns %>%
  filter(!(Stock %in% green_constituents)) %>%
  select(Stock) %>%
  unique() %>%
  pull(Stock)

# Choose how you want the carve-out stocks to be weighted

# equally-weighted
brown_constituent_returns <- create_custom_index(brown_constituents,
                                                 final_stock_returns,
                                                 c("Date", "Returns", "Stock"),
                                                 "equal")

# market-weighted based on latest primary index weights
# brown_constituent_returns <- create_custom_index(brown_constituents,
#                                                  final_stock_returns,
#                                                  c("Date", "Returns", "Stock"),
#                                                  "market",
#                                                  final_stock_breakdown,
#                                                  c("Ticker", "Weight"))

brown_constituent_returns <- brown_constituent_returns %>%
  rename(brown_returns = returns)

# Join the series & subtract

bmg_data <- green_constituent_returns %>%
  inner_join(brown_constituent_returns, by = c("date" = "date"))

bmg_data <- bmg_data %>%
  mutate(BMG = brown_returns - green_returns)

# Extract relevant columns & save
carbon_data <- bmg_data %>%
  select(date, BMG)

write.csv(carbon_data, "carve_out_bmg.csv")
