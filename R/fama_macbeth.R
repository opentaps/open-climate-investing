library(tidyverse)
library(lubridate)
source("R/key_functions.R")

# Read in the Fama-French and BMG factors
carbon_data <- read_csv("data/carbon_risk_factor.csv")
#carbon_data <- read_csv("data/paris_aligned_bmg.csv") %>%
#  select(-Green_Returns, - Brown_Returns)
ff_data <- read_csv("data/ff_factors.csv")
risk_free <- read_csv("data/risk_free.csv")

# final_stock_returns <- read.csv('data/msci_constituent_returns.csv') # for msci
final_stock_returns <- read.csv('data/spx_constituent_returns.csv') # for spx
final_stock_returns[, 1] <- as.Date(final_stock_returns[, 1])
final_stock_returns <- as_tibble(final_stock_returns)

# Read in the sector breakdowns
final_stock_breakdown <- read_csv("data/msci_constituent_details.csv") # for msci
#final_stock_breakdown <- read_csv("data/spx_sector_breakdown.csv") # for spx

# Making the date column have the same name  for the join later
colnames(carbon_data)[1] <- "Date"
colnames(ff_data)[1] <- "Date"
colnames(risk_free)[1] <- "Date"

# Turning the Fama-French factors from number percentage to decimals
ff_data[, -1] <- ff_data[, -1]/100
risk_free[, -1] <- risk_free[, -1]/100

# Combine the carbon data with the Fama-French factors
all_factor_data <- carbon_data %>%
  inner_join(ff_data, by = c("Date" = "Date"))

all_factor_data <- all_factor_data %>%
  inner_join(risk_free, by = c("Date"="Date"))

all_data <- final_stock_returns %>%
  full_join(all_factor_data, by = c("Date" = "Date")) %>%
  drop_na()

all_data <- all_data %>%
  mutate(excess_returns=Returns-Rf)

# Change market return data column to be more compatible
colnames(all_data)[5] <- "Mkt_less_RF"

# Create a blank dataframe
saved_betas <- c()

# Get stocks
stock_names <- unique(all_data$Stock)

# Need to limit the dataset and do a roll
start_date <- min(all_data$Date)
end_date <- max(all_data$Date)
roll_length <- 60
min_data <- 60

num_rolls <- interval(ymd(start_date), ymd(end_date))%/%months(1) - roll_length + 2
roll_start <- start_date

for (i in 1:num_rolls) {
  roll_end <- ymd(start_date) %m+% months(i) %m+% months(roll_length - 2)
  roll_end <- ceiling_date(roll_end, "month") - days(1)
  roll_start <- ymd(start_date) %m+% months(i - 1)
  roll_start <- ceiling_date(roll_start, "month") - days(1)
  
  roll_data <- all_data %>%
    filter(Date >= roll_start,
           Date <= roll_end)
  
  n_obs <- roll_data %>%
    group_by(Stock) %>%
    summarise(n = n())
  
  valid_stocks <- n_obs %>%
    filter(n >= min_data)
  
  roll_data <- roll_data %>%
    filter(Stock %in% valid_stocks$Stock)
  
  # Get the regression of all stocks
  mass_reg_results <- mass_regression(roll_data,
                                      "Stock",
                                      c("excess_returns ~ BMG + Mkt_less_RF + SMB + HML + WML"))
  
  saved_betas <- rbind(saved_betas,
                       cbind(roll_end, get_data_output(mass_reg_results, 1)$betas))

  roll_start <- ymd(roll_start) %m+% months(1)
  roll_start <- ceiling_date(roll_start, "month") - days(1)
}

saved_betas <- saved_betas %>%
  mutate(roll_end = ymd(roll_end) %m+% months(1)) %>%
  mutate(roll_end = ceiling_date(roll_end, "month") - days(1))

returns_data <- all_data %>%
  dplyr::select(Date, Stock, excess_returns)

beta_data <- saved_betas %>%
  inner_join(returns_data, by = c("roll_end" = "Date", "Stock" = "Stock"))

# Lambda roll

saved_lambdas <- c()

unique_dates <- unique(beta_data$roll_end)

for (i in 1:length(unique_dates)) {
  roll_data <- beta_data %>%
    filter(roll_end == unique_dates[i])
  lambda_regression <- lm(excess_returns ~ BMG + Mkt_less_RF + SMB + HML + WML, data = roll_data)

  saved_lambdas <- rbind(saved_lambdas, data.frame(Date = unique_dates[i], t(lambda_regression$coefficients)))
}

lambda_data <- saved_lambdas %>%
  select(BMG,
         Mkt_less_RF,
         SMB,
         HML,
         WML)

lapply(lambda_data, t.test)
