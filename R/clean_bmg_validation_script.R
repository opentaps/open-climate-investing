# this script has different column names for SPX and MSCI so please comment/uncomment the lines as you need them

# Used to get data from Yahoo
library(quantmod)
# This allows for easy manipulation of the data
library(tidyverse)
# This is for date management
library(lubridate)
# This package does the panel regressions
library(plm)

# Read in the Fama-French and BMG factors
carbon_data <- read_csv("data/carbon_risk_factor.csv")
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

# Here is where the regressions are run
# The output is the residuals on certain dates

get_loadings <- function(stock_names, all_data, carbon_data) {

  # Create a blank dataframe
  no_carbon_residuals <- c()

  # Start look to go through all the stocks in stock_names
  for (i in 1:nrow(stock_names)) {
    # Get the stocks name
    temp_stock_name <- as.character(stock_names[i, 1])
    # Filter all the data to only include that stock
    temp_data <- all_data %>%
      dplyr::filter(Stock == temp_stock_name)
    # If there is more than 12 months of data, run the FF (no BMG) regression
    if (nrow(temp_data) >= 12) {
      temp_reg <- lm(Returns ~ Mkt_less_RF + SMB + HML + WML, data = temp_data)

      # Create a dataframe
      temp_no_carbon_residuals <- data.frame(Stock = temp_stock_name,
                                             Res = temp_reg$residuals,
                                             Date = temp_data$Date,
                                             Returns = temp_data$Returns)

      # Append to a dataframe
      no_carbon_residuals <- rbind(no_carbon_residuals, temp_no_carbon_residuals)
    }
    print(c(i, temp_stock_name))
  }


  # Ensure that there are no duplicated residuals
  no_carbon_residuals <- no_carbon_residuals %>%
    unique()

  # Join the BMG factor to the residuals
  no_carbon_residuals <- no_carbon_residuals %>%
    left_join(carbon_data, by = c("Date" = "Date"))

  # Create a panel dataframe on the above dataframe (required for PLM)
  no_carbon_data <- pdata.frame(no_carbon_residuals, index = c("Stock", "Date"))
  # Remove duplicates that have somehow creeped in
  if (length(which(duplicated(index(no_carbon_data))) == TRUE) > 0) {
    no_carbon_data <- no_carbon_data[-which(duplicated(index(no_carbon_data))), ]
  }

  # Run the panel regression of the BMG factor on the residuals
  no_carbon_regression <- plm(Res ~ BMG,
                              data = no_carbon_data,
                              effect = "individual",
                              model = "within")

  return(no_carbon_regression)

}

# Get unique stock names
stock_names <- all_data %>%
  select(Stock) %>%
  unique()

market_output <- get_loadings(stock_names, all_data, carbon_data)

######################### CHANGE JOIN HERE #####################

### By sector ###
stock_breakdowns <- stock_names %>%
#  inner_join(final_stock_breakdown, by = c("Stock" = "Ticker")) # for msci
  inner_join(final_stock_breakdown, by = c("Stock" = "Symbol")) # for spx


### This is for SPX Only
colnames(stock_breakdowns)[3:4] <- c("GICS_Sector", "GICS_Sub")


### Starting again
#unique_sectors <- unique(stock_breakdowns$"Sector")   # for msci
#unique_sectors <- unique(stock_breakdowns$"GICS_Sector")   # for spx by sector
unique_sectors <- unique(stock_breakdowns$"GICS_Sub")   # for spx by sub-industry


bmg_loading_final <- c()


for (j in 1:length(unique_sectors)) {

  stock_names <- stock_breakdowns %>%
  #  filter(Sector == unique_sectors[j]) %>%    # for msci
#    filter(GICS_Sector == unique_sectors[j]) %>%    # for spx by sector
    filter(GICS_Sub == unique_sectors[j]) %>%    # for spx by sub-industry
    select(Stock)

  sector_no_carbon_regression <- get_loadings(stock_names, all_data, carbon_data)
  sector_bmg_loading <- data.frame(
    summary(sector_no_carbon_regression)$coefficients,
    rsq = summary(sector_no_carbon_regression)$r.squared[1])
  sector_bmg_loading <- sector_bmg_loading %>%
    mutate(sector = unique_sectors[j])

  bmg_loading_final <- rbind(bmg_loading_final,
                             sector_bmg_loading)
}

bmg_loading_final <- tibble(bmg_loading_final)
colnames(bmg_loading_final) <- c("Coefficients",
                                 "Std Error",
                                 "t-Stat",
                                 "p-Value",
                                 "R-Squared",
                                 "Sector")

bmg_loading_final <- bmg_loading_final %>%
  relocate(Sector, 1)

bmg_loading_final$`p-Value` <- round(bmg_loading_final$`p-Value`, 4)
write_csv(bmg_loading_final, "Loadings Table.csv")


### Improvement in predictions

# Create a blank dataframe
pred_power <- c()

stock_names <- unique(all_data$Stock)

# Start look to go through all the stocks in stock_names
for (i in 1:length(stock_names)) {
  # Get the stocks name
  temp_stock_name <- as.character(stock_names[i])
  # Filter all the data to only include that stock
  temp_data <- all_data %>%
    dplyr::filter(Stock == temp_stock_name)
  # If there is more than 12 months of data, run the FF (no BMG) regression
  if (nrow(temp_data) >= 12) {
    temp_reg_ff <- lm(Returns ~ Mkt_less_RF + SMB + HML + WML, data = temp_data)
    temp_reg_ff <- summary(temp_reg_ff)
    temp_reg_ff_bmg <- lm(Returns ~ Mkt_less_RF + SMB + HML + WML + BMG, data = temp_data)
    temp_reg_ff_bmg <- summary(temp_reg_ff_bmg)
    
    temp_pred_power <- data.frame(Stock = temp_stock_name,
                                  FF_Rsq = temp_reg_ff$r.squared,
                                  FFB_Rsq = temp_reg_ff_bmg$r.squared,
                                  FF_AdjRsq = temp_reg_ff$adj.r.squared,
                                  FFB_AdjRsq = temp_reg_ff_bmg$adj.r.squared)
    pred_power <- rbind(pred_power,
                        temp_pred_power)
  }
  print(c(i, temp_stock_name))
}

pred_power <- tibble(pred_power)

# Increase in RSq
mean(pred_power$FFB_Rsq - pred_power$FF_Rsq)

# Increase in Adjusted RSq
mean(pred_power$FFB_AdjRsq - pred_power$FF_AdjRsq)


all_sector_pred_power <- c(mean(pred_power$FFB_Rsq - pred_power$FF_Rsq),
                           mean(pred_power$FFB_AdjRsq - pred_power$FF_AdjRsq))

### By sector
pred_power <- pred_power %>%
  inner_join(final_stock_breakdown,
             by = c("Stock" = "Symbol"))


### This is for SPX Only
colnames(pred_power)[7:8] <- c("GICS_Sector", "GICS_Sub")


pred_power_table <- pred_power %>%
  mutate(RSq_Diff = FFB_Rsq - FF_Rsq,
         AdjRSq_Diff = FFB_AdjRsq - FF_AdjRsq) %>%
  group_by(GICS_Sector) %>%
  summarise("Change in R Squared" = mean(RSq_Diff), 
            "Change in Adjusted R Squared" = mean(AdjRSq_Diff))

pred_power_table <- pred_power_table %>% tibble::add_row(
  GICS_Sector = "All Sectors",
  `Change in R Squared` = all_sector_pred_power[1],
  `Change in Adjusted R Squared` = all_sector_pred_power[2]
)

pred_power_table
