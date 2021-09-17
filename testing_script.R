library(quantmod)
library(tidyverse)
library(lubridate)
library(plm)

# Read in the list of stock tickers, carbon risk factor and F&F factors
test_stocks <- read.csv("stock_tickers.csv", header = FALSE)
carbon_data <- read_csv("carbon_risk_factor.csv")
ff_data <- read_csv("ff_factors.csv")

final_stock_returns <- c()

final_stock_returns <- read_csv('spx_constituent_returns.csv')
final_stock_returns <- final_stock_returns[, -1]

final_stock_breakdown <- read_csv("spx_sector_breakdown.csv")

# Making the date column have the same name for the join later
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

all_data <- all_data %>% 
  filter(Stock != "CNRG")

stock_names <- all_data %>%
  select(Stock) %>%
  unique()

no_carbon_residuals <- c()

for (i in 1:nrow(stock_names)) {
  temp_no_carbon_residuals <- c()
  temp_stock_name <- as.character(stock_names[i, 1])
  temp_data <- all_data %>%
    dplyr::filter(Stock == temp_stock_name)
  if (nrow(temp_data) >= 12) {
    temp_reg <- lm(Returns ~ Mkt_less_RF + SMB + HML + WML, data = temp_data)
  }
  temp_no_carbon_residuals <- data.frame(Stock = temp_stock_name,
                                         Res = temp_reg$residuals,
                                         Date = temp_data$Date,
                                         Returns = temp_data$Returns)
  no_carbon_residuals <- rbind(no_carbon_residuals, temp_no_carbon_residuals)
}

no_carbon_residuals <- no_carbon_residuals %>%
  unique()

no_carbon_residuals <- no_carbon_residuals %>%
  left_join(carbon_data, by = c("Date" = "Date"))

no_carbon_data <- pdata.frame(no_carbon_residuals, index = c("Stock", "Date"))
no_carbon_data <- no_carbon_data[-which(duplicated(index(no_carbon_data))), ]
no_carbon_regression <- plm(Res ~ BMG, 
                            data = no_carbon_data,
                            effect = "individual",
                            model = "within")


### By sector
stock_breakdowns <- stock_names %>% 
  inner_join(final_stock_breakdown, by = c("Stock" = "Symbol"))


# unique_sectors <- unique(stock_breakdowns$`GICS Sector`)
unique_sectors <- unique(stock_breakdowns$`GICS Sub-Industry`)

bmg_loading_final <- c()

for (j in 1:length(unique_sectors)) {
  no_carbon_residuals <- c()
  stock_names <- stock_breakdowns %>%
    filter(`GICS Sector` == unique_sectors[j]) %>%
    select(Stock)
  
  for (i in 1:nrow(stock_names)) {
    temp_no_carbon_residuals <- c()
    temp_stock_name <- as.character(stock_names[i, 1])
    temp_data <- all_data %>%
      dplyr::filter(Stock == temp_stock_name)
    if (nrow(temp_data) >= 12) {
      temp_reg <- lm(Returns ~ Mkt_less_RF + SMB + HML + WML, data = temp_data)
    }
    temp_no_carbon_residuals <- data.frame(Stock = temp_stock_name,
                                           Res = temp_reg$residuals,
                                           Date = temp_data$Date,
                                           Returns = temp_data$Returns)
    no_carbon_residuals <- rbind(no_carbon_residuals, temp_no_carbon_residuals)
  }
  
  no_carbon_residuals <- no_carbon_residuals %>%
    unique()
  
  no_carbon_residuals <- no_carbon_residuals %>%
    left_join(carbon_data, by = c("Date" = "Date"))
  
  no_carbon_data <- pdata.frame(no_carbon_residuals, index = c("Stock", "Date"))
  if (length(which(duplicated(index(no_carbon_data)))) > 0) {
    no_carbon_data <- no_carbon_data[-which(duplicated(index(no_carbon_data))), ]
  }
  
  sector_no_carbon_regression <- plm(Res ~ BMG, 
                                     data = no_carbon_data,
                                     effect = "individual",
                                     model = "within")
  
  
  sector_bmg_loading <- data.frame(
    summary(sector_no_carbon_regression)$coefficients, 
      rsq = summary(sector_no_carbon_regression)$r.squared[1])
  sector_bmg_loading <- sector_bmg_loading %>%
    mutate(sector = unique_sectors[j])
  
  bmg_loading_final <- rbind(bmg_loading_final,
                             sector_bmg_loading)
}

bmg_loading_final <- tibble(bmg_loading_final)

# market_data <- ff_data %>% select(Date, `Mkt-RF`)
# market_data <- market_data %>%
#   mutate(Stock = 'Market') %>%
#   full_join(carbon_data, by = c("Date" = "month")) %>%
#   full_join(ff_data, by = c("Date" = "Date")) %>%
#   drop_na()

# Change market return data column to be more compatible
colnames(all_data)[5] <- "Mkt_less_RF"

# Remove the carbon risk factor and work out the error
no_carbon_data <- all_data %>%
  select(-BMG)

no_carbon_data <- pdata.frame(no_carbon_data, index = c("Stock", "Date"))
no_carbon_regression <- plm(Returns ~ Mkt_less_RF + SMB + HML + WML, 
                            data = no_carbon_data,
                            effect = "individual",
                            model = "within")

no_carbon_residuals <- no_carbon_regression$residuals
carbon_residual_data_test <- data.frame(Date = all_data$Date,
                                        Stock = all_data$Stock,
                                        no_carbon_residuals = no_carbon_residuals, 
                                        BMG = all_data$BMG)

carbon_residual_data_test <- pdata.frame(carbon_residual_data_test,
                                         index = c("Stock",
                                                   "Date"))

test <- lm(no_carbon_residuals ~ BMG, data = carbon_residual_data_test)
test_2 <- plm(no_carbon_residuals ~ BMG, data = carbon_residual_data_test)
summary(test_2)

# test <- colnames(all_data)[-c(1:2)]
# test <- test <- c(test, "Stock", paste(test, "Stock", sep = ":"))
# test <- paste(test, collapse = "+")
# test <- paste0("Close~", test)
# test <- as.formula(test)
# 
# all_data$Stock <- as.factor(all_data$Stock)
# all_data$Stock <- relevel(all_data$Stock, "Market")
# 
# test2 <- all_data %>%
#   filter(Stock == "ALB") %>%
#   select(-Stock)
# test_reg <- lm(Close~., data = test2)
# 
# 
# ffc_reg <- lm(test, data = all_data)
