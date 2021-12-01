library(tidyverse)
library(lubridate)
library(reshape2)
library(corrplot)

# final_stock_returns <- read.csv('data/msci_constituent_returns.csv') # for msci
final_stock_returns <- read.csv('data/spx_constituent_returns.csv') # for spx
final_stock_returns[, 1] <- as.Date(final_stock_returns[, 1])
final_stock_returns <- as_tibble(final_stock_returns)
final_stock_breakdown <- read_csv("data/spx_sector_breakdown.csv")
final_stock_returns <- final_stock_returns %>%
  left_join(final_stock_breakdown, by = c("Stock" = "Symbol"))

colnames(final_stock_returns)[(length(colnames(final_stock_returns)) - 1):length(colnames(final_stock_returns))] <- c("Sector", "Sub_Sector")

final_stock_returns <- final_stock_returns %>%
  group_by(Sector, Date) %>%
  summarise(sector_return = mean(Returns))

final_stock_returns_tabulated <- dcast(final_stock_returns, Date ~ Sector, value.var = "sector_return")
final_stock_returns_tabulated <- tibble(final_stock_returns_tabulated)

final_stock_returns_tabulated <- final_stock_returns_tabulated %>%
  filter(Date >= "2010-01-31",
         Date <= "2018-12-31")

pca_data <- final_stock_returns_tabulated %>%
  select(-Date)

pca_results <- princomp(pca_data)

components_through_time <- pca_results$scores

ff_data <- read_csv("data/ff_factors.csv")
risk_free <- read_csv("data/risk_free.csv")
carbon_data <- read_csv("data/bmg_carima.csv")

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

comb_data <- cbind(components_through_time, all_factor_data)
comb_data <- comb_data %>%
  select("Comp.1",
         "Comp.2",
         "Comp.3",
         "Comp.4",
         "Comp.5",
         "BMG",
         "Mkt-RF",
         "SMB",
         "HML",
         "WML")

cor_matrix <- cor(comb_data)

corrplot(cor_matrix,
         method="number",
         diag = FALSE)
