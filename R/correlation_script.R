library(tidyverse)
library(corrplot)
library(RPostgres)
library(DBI)

# con <- dbConnect(RPostgres::Postgres(), dbname = 'open_climate_investing',
#                  host = '127.0.0.1',
#                  port = 5432,
#                  user = 'sichen',
#                  password = 'opentaps')
#
# res <- dbSendQuery(con, "SELECT CR.date as Date, CR.bmg, FF.mkt_rf, FF.smb, FF.hml, FF.wml FROM carbon_risk_factor as CR join ff_factor as FF on CR.date=FF.date")
# res <- dbSendQuery(con, "SELECT FF.date, (0.5*SD2.return + 0.5*SD3.return) - SD1.return AS XOPXLB_SMOG, FF.mkt_rf, FF.smb, FF.hml, FF.wml FROM ff_factor as FF join stock_data as SD1 on SD1.date = FF.date join stock_data as SD2 on SD1.date = SD2.date join stock_data as SD3 on SD1.date = SD3.date where SD1.ticker = 'XOP' and SD1.date > '2010-01-01' and SD2.ticker = 'SMOG' and SD3.ticker = 'XLB'")# bmg_ff_factors <- dbFetch(res)

# bmg_ff_factors <- dbFetch(res)

ff_factors <- read_csv("data/ff_factors.csv")
bmg_factor <- read_csv("data/bmg_carima.csv")  
#bmg_factor <- read_csv("data/bmg_acwi_crbn.csv")
#bmg_factor <- read_csv("data/bmg_eu_ets.csv")
#bmg_factor <- read_csv("data/bmg_xop_smog.csv")
#bmg_factor <- read_csv("data/bmg_wmat_crbn_mat.csv")
#bmg_factor <- read_csv("data/bmg_xop_smog_orthogonalized_1.csv") # XOP-SMOG orthogonalized for Rate Change, Curve Change, BBB Spread Change
#bmg_factor <- read_csv("data/bmg_xop_smog_orthogonalized_2.csv")  # XOP-SMOG additionally orthogonalized for HML Fama-French factor
#bmg_factor <- read_csv("data/bmg_carima_orthogonalized.csv")

#bmg_factor <- read_csv("data/paris_aligned_bmg.csv") %>%
#  select(-Green_Returns, - Brown_Returns)
interest_rates <- read_csv("data/interest_rates.csv")

all_factors <- ff_factors %>%
  inner_join(bmg_factor, by = c("Date" = "month")) %>%
  inner_join(interest_rates, by = c("Date" = "Date") ) %>%
  select(-factor_name)
colnames(all_factors)[2] <- "Mkt_less_RF"
#all_factors <- ff_factors %>%
#  inner_join(bmg_factor, by = c("Date" = "Date"))

fit <- lm(BMG ~ Mkt_less_RF + SMB + HML + WML + RateChg + CurveChg + HiYieldSpreadChg + BBBSpreadChg, data = all_factors)
summary(fit)

cor_matrix <- cor(all_factors %>%
                    select(-Date))

plot(BMG ~ SMB, data=all_factors)
plot(BMG ~ HML, data=all_factors)
plot(BMG ~ HiYieldSpreadChg, data=all_factors)
plot(BMG ~ CurveChg, data=all_factors)


corrplot(cor_matrix,
         method="number",
         diag = FALSE)
