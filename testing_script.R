library(quantmod)
library(tidyverse)

getSymbols("XOM")
carbon_data <- read_csv("carbon_risk_factor.csv")
ff_data <- read_csv("ff_factors.csv")

XOM <- XOM$XOM.Close
XOM <- monthlyReturn(XOM)

XOM <- data.frame(index(XOM), XOM)
colnames(XOM) <- c("Date", "Close")
XOM$Date <- as.Date(XOM$Date)
XOM <- as_tibble(XOM)

all_data <- XOM %>%
  inner_join(carbon_data, by = c("Date" = "month")) %>%
  inner_join(ff_data, by = c("Date" = "Date"))

all_data <- all_data %>%
  select(-Date)

ffc_reg <- lm(Close ~ ., data = all_data)
