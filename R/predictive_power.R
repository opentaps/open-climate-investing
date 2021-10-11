# This allows for easy manipulation of the data
library(tidyverse)
# All the important functions are here
source("R/key_functions.R")


### Improvement in predictions

# Read in the Fama-French and BMG factors
carbon_data <- read_csv("data/carbon_risk_factor.csv")
ff_data <- read_csv("data/ff_factors.csv")
risk_free <- read_csv("data/risk_free.csv")

# Read in the SPX return data from the bulk downloader
final_stock_returns <- read.csv('data/msci_constituent_returns.csv') # for msci
#final_stock_returns <- read.csv('data/spx_constituent_returns.csv') # for spx
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
pred_power <- c()

stock_names <- unique(all_data$Stock)

### Run all necessary regression ###
# Get the regression of all stocks
mass_reg_results <- mass_regression(all_data,
                                    "Stock",
                                    c("excess_returns ~ Mkt_less_RF + SMB + HML + WML",
                                      "excess_returns ~ BMG + Mkt_less_RF + SMB + HML + WML"))

get_bmg_regression_results <- lapply(mass_reg_results, function(x) {
  summary(x[["Regression"]][[2]])
})

get_no_bmg_regression_results <- lapply(mass_reg_results, function(x) {
  summary(x[["Regression"]][[1]])
})

# Get the coefficient summary table, R-Squared and Adjusted R-Squared
bmg_pred_data <- lapply(get_bmg_regression_results, function(x) 
  {if(get_dataframe_dimensions(x$coefficients)[1] > 2) 
    {data.frame(x$coefficients[1],
                x$r.squared,
                x$adj.r.squared)
    }
  }
)

no_bmg_pred_data <- lapply(get_no_bmg_regression_results, function(x) 
  {if(get_dataframe_dimensions(x$coefficients)[1] > 2) 
    {data.frame(x$coefficients[1],
                x$r.squared,
                x$adj.r.squared)
    }
  }
)

# Removing regressions that didn't run
if (length(which(lapply(bmg_pred_data, function(x) is.null(x)) == TRUE)) > 0) {
  bmg_pred_data <- bmg_pred_data[-which(lapply(bmg_pred_data, function(x) is.null(x)) == TRUE)]
}

if (length(which(lapply(no_bmg_pred_data, function(x) is.null(x)) == TRUE)) > 0) {
  no_bmg_pred_data <- no_bmg_pred_data[-which(lapply(no_bmg_pred_data, function(x) is.null(x)) == TRUE)]
}

# Final output table
bmg_pred_data <- tibble(Stock=names(bmg_pred_data), bind_rows(bmg_pred_data))
no_bmg_pred_data <- tibble(Stock=names(no_bmg_pred_data), bind_rows(no_bmg_pred_data))

colnames(bmg_pred_data)[2:4] <- c("FFB_Alpha", "FFB_Rsq", "FFB_AdjRsq")
colnames(no_bmg_pred_data)[2:4] <- c("FF_Alpha", "FF_Rsq", "FF_AdjRsq")

pred_power <- bmg_pred_data %>%
  inner_join(no_bmg_pred_data, by = c("Stock"="Stock"))

pred_power <- pred_power %>%
  relocate(FF_Alpha, .after = Stock) %>%
  relocate(FFB_Alpha, .after = FF_Alpha)
  relocate(FF_Rsq, .after = FFB_Alpha) %>%
  relocate(FFB_Rsq, .after = FF_Rsq) %>%
  relocate(FF_AdjRsq, .after = FFB_Rsq) %>%
  relocate(FFB_AdjRsq, .after = FF_AdjRsq)

# Increase in RSq
mean(pred_power$FFB_Rsq - pred_power$FF_Rsq)

# Increase in Adjusted RSq
mean(pred_power$FFB_AdjRsq - pred_power$FF_AdjRsq)


all_sector_pred_power <- c(mean(abs(pred_power$FF_Alpha) - abs(pred_power$FFB_Alpha)),
                           mean(pred_power$FFB_Rsq - pred_power$FF_Rsq),
                           mean(pred_power$FFB_AdjRsq - pred_power$FF_AdjRsq))

### By sector
pred_power <- pred_power %>%
  inner_join(final_stock_breakdown,
#             by = c("Stock" = "Symbol"))   # for spx
by = c("Stock" = "Ticker"))   # for msci

### Remove NAs


### This is for SPX Only
colnames(pred_power)[7:8] <- c("GICS_Sector", "GICS_Sub")


pred_power_table <- pred_power %>%
  mutate(Alpha_Diff = abs(FF_Alpha) - abs(FFB_Alpha),
         RSq_Diff = FFB_Rsq - FF_Rsq,
         AdjRSq_Diff = FFB_AdjRsq - FF_AdjRsq) %>%
  ### Change the below line by what you want to group things by
  group_by(Sector) %>%
  summarise("Reduction in Alpha" = mean(Alpha_Diff),
            "Change in R Squared" = mean(RSq_Diff),
            "Change in Adjusted R Squared" = mean(AdjRSq_Diff))

pred_power_table <- pred_power_table %>% tibble::add_row(
  ### Change line below to match line 93-94
  Sector = "All Sectors",
  `Reduction in Alpha` = all_sector_pred_power[1],
  `Change in R Squared` = all_sector_pred_power[2],
  `Change in Adjusted R Squared` = all_sector_pred_power[3]
)

#Display table
pred_power_table

# Write table
write.csv(pred_power_table, "MSCI Predictive Power Table by Sector.csv")
