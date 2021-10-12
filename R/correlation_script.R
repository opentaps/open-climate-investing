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
# bmg_ff_factors <- dbFetch(res)

ff_factors <- read_csv("data/ff_factors.csv")
#bmg_factor <- read_csv("data/carbon_risk_factor.csv")
bmg_factor <- read_csv("data/paris_aligned_bmg.csv") %>%
  select(-Green_Returns, - Brown_Returns)

# all_factors <- ff_factors %>%
#  inner_join(bmg_factor, by = c("Date" = "month"))

all_factors <- ff_factors %>%
  inner_join(bmg_factor, by = c("Date" = "Date"))

cor_matrix <- cor(all_factors %>%
                   select(-Date))

# cor_matrix <- cor(bmg_ff_factors %>%
#                     select(-date))

corrplot(cor_matrix,
         method="number",
         diag = FALSE)
