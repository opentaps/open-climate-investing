library(quantmod)
library(tidyverse)
library(lubridate)


test_stocks <- read.csv("stock_tickers.csv", header = FALSE)
carbon_data <- read_csv("carbon_risk_factor.csv")
ff_data <- read_csv("ff_factors.csv")

final_stock_returns <- c()

for (i in 1:nrow(test_stocks)) {
  temp_holder<- getSymbols(test_stocks[i, 1], 
                           auto.assign = FALSE)
  print(temp_holder[i, 1])
  temp_holder <- temp_holder[, 4]
  temp_holder <- monthlyReturn(temp_holder)
  
  temp_holder <- data.frame(index(temp_holder), temp_holder)
  colnames(temp_holder) <- c("Date", "Close")
  temp_holder$Date <- as.Date(temp_holder$Date)
  temp_holder <- as_tibble(temp_holder)
  temp_holder <- temp_holder %>%
    mutate(Stock = test_stocks[i, 1])
  
  final_stock_returns <- rbind(final_stock_returns, temp_holder)
}

final_stock_returns$Date <- ceiling_date(final_stock_returns$Date, "month") - 1

all_data <- final_stock_returns %>%
  full_join(carbon_data, by = c("Date" = "month")) %>%
  full_join(ff_data, by = c("Date" = "Date")) %>%
  drop_na()

all_data <- all_data %>% 
  filter(Stock != "CNRG")

market_data <- ff_data %>% select(Date, `Mkt-RF`)
market_data <- market_data %>%
  mutate(Stock = 'Market') %>%
  full_join(carbon_data, by = c("Date" = "month")) %>%
  full_join(ff_data, by = c("Date" = "Date")) %>%
  drop_na()
  
colnames(market_data) <- colnames(all_data)

all_data <- rbind(all_data, market_data)

all_data <- all_data %>%
  select(-Date)
colnames(all_data) <- gsub("Mkt-RF", "Mkt_less_RF", colnames(all_data))

test <- colnames(all_data)[-c(1:2)]
test <- test <- c(test, "Stock", paste(test, "Stock", sep = ":"))
test <- paste(test, collapse = "+")
test <- paste0("Close~", test)
test <- as.formula(test)

all_data$Stock <- as.factor(all_data$Stock)
all_data$Stock <- relevel(all_data$Stock, "Market")

test2 <- all_data %>%
  filter(Stock == "ALB") %>%
  select(-Stock)
test_reg <- lm(Close~., data = test2)


ffc_reg <- lm(test, data = all_data)
