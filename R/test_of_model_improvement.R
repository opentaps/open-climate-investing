# This allows for easy manipulation of the data
library(tidyverse)
library(plm)
library(car)
library(lmtest)

### Improvement in predictions

# Read in the Fama-French and BMG factors
carbon_data <- read_csv("data/bmg_carima.csv")
ff_data <- read_csv("data/ff_factors.csv")

# Read in the SPX return data from the bulk downloader
#final_stock_returns <- read.csv('data/msci_constituent_returns.csv') # for msci
final_stock_returns <- read.csv('data/spx_constituent_returns.csv') # for spx
final_stock_returns[, 1] <- as.Date(final_stock_returns[, 1])
final_stock_returns <- as_tibble(final_stock_returns)

# Read in the sector breakdowns
#final_stock_breakdown <- read_csv("data/msci_constituent_details.csv") # for msci
final_stock_breakdown <- read_csv("data/spx_sector_breakdown.csv") # for spx

# Making the date column have the same name  for the join later
colnames(carbon_data)[1] <- "Date"
colnames(ff_data)[1] <- "Date"

# Turning the Fama-French factors from number percentage to decimals
ff_data[, -1] <- ff_data[, -1]/100

# Combine the carbon data with the Fama-French factors
all_factor_data <- carbon_data %>%
  inner_join(ff_data, by = c("Date" = "Date"))

all_data <- final_stock_returns %>%
  full_join(all_factor_data, by = c("Date" = "Date")) %>%
  drop_na()

# Change market return data column to be more compatible
colnames(all_data)[5] <- "Mkt_less_RF"

# Single regression
plm_ff <- plm(Returns ~ Mkt_less_RF + SMB + HML + WML,
                data = all_data,
                model = "within",
                effect = "individual",
                index = c("Stock", "Date"))

plm_ff_bmg <- plm(Returns ~ Mkt_less_RF + SMB + HML + WML + BMG,
                  data = all_data,
                  model = "within",
                  effect = "individual",
                  index = c("Stock", "Date"))
