library(tidyverse)

stock_returns <- read_csv("data/spx_constituent_returns.csv")
paris_aligned_stocks <- read_csv("data/paris_aligned_tickers.csv")

spx_tickers <- stock_returns %>%
  select(Stock) %>%
  unique()

paris_aligned_stocks <- paris_aligned_stocks %>%
  filter(Ticker %in% spx_tickers$Stock)

non_paris_aligned_stocks <- spx_tickers %>%
  filter(!(Stock %in% paris_aligned_stocks$Ticker))

paris_aligned_returns <- stock_returns %>%
  filter(Stock %in% paris_aligned_stocks$Ticker)

non_paris_aligned_returns <- stock_returns %>%
  filter(Stock %in% non_paris_aligned_stocks$Stock)

paris_aligned_returns_mean <- paris_aligned_returns  %>%
  group_by(Date) %>%
  summarise(Green_Returns = mean(Returns))

non_paris_aligned_returns_mean <- non_paris_aligned_returns  %>%
  group_by(Date) %>%
  summarise(Brown_Returns = mean(Returns))

bmg_portfolio <- paris_aligned_returns_mean %>%
  inner_join(non_paris_aligned_returns_mean, by = c("Date" = "Date"))

bmg_portfolio <- bmg_portfolio %>%
  mutate(BMG = Brown_Returns - Green_Returns)

write.csv(bmg_portfolio, "data/paris_aligned_bmg.csv", row.names = FALSE)

