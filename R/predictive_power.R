# This allows for easy manipulation of the data
library(tidyverse)

### Improvement in predictions

# Read in the Fama-French and BMG factors
carbon_data <- read_csv("data/carbon_risk_factor.csv")
ff_data <- read_csv("data/ff_factors.csv")

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
#             by = c("Stock" = "Symbol"))   # for spx
by = c("Stock" = "Ticker"))   # for msci


### This is for SPX Only
colnames(pred_power)[7:8] <- c("GICS_Sector", "GICS_Sub")


pred_power_table <- pred_power %>%
  mutate(RSq_Diff = FFB_Rsq - FF_Rsq,
         AdjRSq_Diff = FFB_AdjRsq - FF_AdjRsq) %>%
  ### Change the below line by what you want to group things by
  group_by(Sector) %>%
  summarise("Change in R Squared" = mean(RSq_Diff),
            "Change in Adjusted R Squared" = mean(AdjRSq_Diff))

pred_power_table <- pred_power_table %>% tibble::add_row(
  ### Change line below to match line 93-94
  Sector = "All Sectors",
  `Change in R Squared` = all_sector_pred_power[1],
  `Change in Adjusted R Squared` = all_sector_pred_power[2]
)

#Display table
pred_power_table

# Write table
write.csv(pred_power_table, "MSCI Predictive Power Table by Sector.csv")
