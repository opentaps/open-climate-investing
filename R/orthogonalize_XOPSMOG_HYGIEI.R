library(tidyverse)
library(corrplot)
library(RPostgres)
library(DBI)

 con <- dbConnect(RPostgres::Postgres(), dbname = 'open_climate_investing',
                  host = '127.0.0.1',
                  port = 5432,
                  user = 'opentaps',
                  password = 'opentaps')
 
 res <- dbSendQuery(con, "SELECT CR.date as Date, CR.bmg, FF.mkt_rf, FF.smb, FF.hml, FF.wml, AF.factor_value as hmt FROM carbon_risk_factor as CR join ff_factor as FF on CR.date=FF.date and CR.frequency = FF.frequency join additional_factors as AF on CR.date = AF.date and CR.frequency = AF.frequency where CR.factor_name = 'XOP-SMOG' and CR.frequency = 'DAILY' and AF.factor_name = 'HYG-IEI' and CR.date > '2017-10-18'")

 all_factors <- dbFetch(res)

fit <- lm(bmg ~ mkt_rf + smb + hml + wml + hmt, data = all_factors)

summary(fit)

plot(bmg ~ hml, data=all_factors)
plot(bmg ~ hmt, data=all_factors)


corrplot(cor_matrix,
         method="number",
         diag = FALSE)

dbDisconnect(con)
