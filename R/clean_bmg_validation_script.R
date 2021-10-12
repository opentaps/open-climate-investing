# this script has different column names for SPX and MSCI so please comment/uncomment the lines as you need them

# Used to get data from Yahoo
library(quantmod)
# This allows for easy manipulation of the data
library(tidyverse)
# This is for date management
library(lubridate)
# This package does the panel regressions
library(plm)
# All the important functions are here
source("R/key_functions.R")

# Read in the Fama-French and BMG factors
# carbon_data <- read_csv("data/carbon_risk_factor.csv")
carbon_data <- read_csv("data/paris_aligned_bmg.csv") %>%
  select(-Green_Returns, - Brown_Returns)
ff_data <- read_csv("data/ff_factors.csv")
risk_free <- read_csv("data/risk_free.csv")

# Read in the SPX return data from the bulk downloader
#final_stock_returns <- read.csv('data/msci_constituent_returns.csv') # for msci
final_stock_returns <- read.csv('data/spx_constituent_returns.csv') # for spx
final_stock_returns[, 1] <- as.Date(final_stock_returns[, 1])
final_stock_returns <- as_tibble(final_stock_returns)

### Removing outlier stock returns
final_stock_returns <- final_stock_returns %>%
  filter(Returns > -0.7,
         Returns < 1) %>%
  drop_na()


# Read in the sector breakdowns
#final_stock_breakdown <- read_csv("data/msci_constituent_details.csv") # for msci
final_stock_breakdown <- read_csv("data/spx_sector_breakdown.csv") # for spx


# Making the date column have the same name  for the join later
colnames(carbon_data)[1] <- "Date"
colnames(ff_data)[1] <- "Date"

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

# Here is where the regressions are run
# The output is the residuals on certain dates


### Check single OLS
single_stock_name <- "AAPL"
start_date <- "2010-01-01"
end_date <- "2020-12-31"

single_reg <- lm(excess_returns  ~
                   BMG +
                   Mkt_less_RF +
                   SMB +
                   HML +
                   WML,
                 data = all_data %>%
                   filter(Stock == single_stock_name,
                          Date >= start_date,
                          Date <= end_date))

summary(single_reg)

# Get the regression of all stocks
mass_reg_results <- mass_regression(all_data,
                                    "Stock",
                                    c("excess_returns ~ Mkt_less_RF + SMB + HML + WML",
                                      "excess_returns ~ BMG + Mkt_less_RF + SMB + HML + WML"))

get_bmg_regression_results <- lapply(mass_reg_results, function(x) {
  summary(x[["Regression"]][[2]])
})


# Get the coefficient summary table, R-Squared and Adjusted R-Squared
bmg_loading_data <- lapply(get_bmg_regression_results, function(x) 
  {if(get_dataframe_dimensions(x$coefficients)[1] > 2) 
    {data.frame(t(x$coefficients[2, ]),
       x$r.squared,
       x$adj.r.squared)
    }
  }
)

# Removing regressions that didn't run
if (length(which(lapply(bmg_loading_data, function(x) is.null(x)) == TRUE)) > 0) {
  bmg_loading_data <- bmg_loading_data[-which(lapply(bmg_loading_data, function(x) is.null(x)) == TRUE)]
}


# Final output table
bmg_loading_data <- tibble(Stock=names(bmg_loading_data), bind_rows(bmg_loading_data))

# Join sector data to stock


# Panel Regression on Market Residuals

# Get the residual data
no_bmg_regression_data <- get_data_output(mass_reg_results, 1)
no_bmg_regression_data <- data.frame(no_bmg_regression_data$data,
                                      res = no_bmg_regression_data$residuals$num)

# Set up the panel data frame
panel_data <- pdata.frame(no_bmg_regression_data,
                          index = c("Stock", "Date"))


plm_regression <- plm(res ~ BMG, 
                      data=panel_data,
                      model = "within",
                      effect = "individual")

summary(plm_regression)

######################### CHANGE JOIN HERE #####################

### Get list of stocks ###
stock_names <- final_stock_returns %>%
  select(Stock) %>%
  distinct()

### By sector ###
stock_breakdowns <- stock_names %>%
#  inner_join(final_stock_breakdown, by = c("Stock" = "Ticker")) # for msci
  inner_join(final_stock_breakdown, by = c("Stock" = "Symbol")) # for spx


### This is for SPX Only
colnames(stock_breakdowns)[3:4] <- c("GICS_Sector", "GICS_Sub")

### Choose breakdown
# GICS_Sector for SPX by Sector
# GICS_Sub for SPX by Subsector
# Sector for MSCI

breakdown_col_name <- "GICS_Sector"
unique_sectors <- stock_breakdowns %>%
  select(breakdown_col_name) %>%
  distinct()




bmg_loading_final <- c()
no_bmg_regression_data <- tibble(no_bmg_regression_data)
bmg_regression_data_sector_join <- no_bmg_regression_data %>%
  left_join(stock_breakdowns,
            by = c("Stock" = "Stock"))

for (j in 1:nrow(unique_sectors)) {

  sector_regression_data <- bmg_regression_data_sector_join %>%
    filter(.[breakdown_col_name] == as.character(unique_sectors[j, 1]))
  
  sector_panel_data <- pdata.frame(sector_regression_data, 
                                   index = c("Stock", "Date"))
  
  sector_panel_reg <- plm(res~BMG,
                          data=sector_panel_data,
                          model="within",
                          effect="individual")

  sector_bmg_loading <- data.frame(
    Sector = as.character(unique_sectors[j, 1]),
    summary(sector_panel_reg)$coefficients,
    rsq = summary(sector_panel_reg)$r.squared[1])

  bmg_loading_final <- rbind(bmg_loading_final,
                             sector_bmg_loading)
}

bmg_loading_final <- tibble(bmg_loading_final)
colnames(bmg_loading_final) <- c("Sector",
                                 "Coefficients",
                                 "Std Error",
                                 "t-Stat",
                                 "p-Value",
                                 "R-Squared",
                                 "Sector")

bmg_loading_final <- bmg_loading_final %>%
  relocate(Sector, 1)

bmg_loading_final$`p-Value` <- round(bmg_loading_final$`p-Value`, 4)
write_csv(bmg_loading_final, "Loadings Table.csv")
