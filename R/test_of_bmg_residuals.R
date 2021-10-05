# This allows for easy manipulation of the data
library(tidyverse)
library(plm)
library(car)
library(ggplot)

### Improvement in predictions

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

# Create a blank dataframe
factor_residuals <- c()

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
    # temp_reg_ff <- summary(temp_reg_ff)
    temp_reg_ff_bmg <- lm(Returns ~ Mkt_less_RF + SMB + HML + WML + BMG, data = temp_data)
    # temp_reg_ff_bmg <- summary(temp_reg_ff_bmg)
    
    temp_factor_residuals <- data.frame(Stock = temp_stock_name,
                                  FF_residuals = temp_reg_ff$residuals,
                                  FFB_residuals = temp_reg_ff_bmg$residuals)
    factor_residuals <- rbind(factor_residuals,
                              temp_factor_residuals)
  }
  print(c(i, temp_stock_name))
}

factor_residuals <- tibble(factor_residuals)
factor_residuals <- factor_residuals %>%
  filter(Stock != "BRK")

var.test(factor_residuals$FF_residuals,
         factor_residuals$FFB_residuals)

ks.test(factor_residuals$FF_residuals, "pnorm", mean=mean(factor_residuals$FF_residuals), sd=sd(factor_residuals$FF_residuals))

leveneTest(y <- c(factor_residuals$FF_residuals, factor_residuals$FFB_residuals),
           group <- as.factor(c(rep(1, length(factor_residuals$FF_residuals)), 
                                rep(2, length(factor_residuals$FFB_residuals)))))


#create histogram of residuals
ggplot(data = factor_residuals, aes(x = FF_residuals)) +
  geom_histogram(bins = 30, fill = 'steelblue', color = 'black') +
  labs(title = 'Histogram of Residuals', x = 'Residuals', y = 'Frequency')

# ff_reg <- lm(Returns ~ Stock + 
#                Mkt_less_RF:Stock +
#                SMB:Stock +
#                HML:Stock +
#                WML:Stock,
#              data = all_data)

# all_data <- pdata.frame(all_data, index = c("Stock", "Date"))

# Single regression
# pvcm_ff <- pvcm(Returns ~ Mkt_less_RF + SMB + HML + WML, 
#                 data = all_data,
#                 model = "within",
#                 effect = "individual")

reg_residuals <- tibble(reg_residuals)
