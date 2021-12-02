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


# Correlation function

init_data_script <- function(bmg_factor, ff_factors, interest_rates) {
  colnames(bmg_factor)[1] <- "Date"
  
  all_factors <- ff_factors %>%
    inner_join(bmg_factor, by = c("Date" = "Date")) %>%
    inner_join(interest_rates, by = c("Date" = "Date") )
  colnames(all_factors)[2] <- "Mkt_less_RF"
  
  fit <- lm(BMG ~ Mkt_less_RF + SMB + HML + WML + RateChg + CurveChg + HiYieldSpreadChg + BBBSpreadChg, data = all_factors)
  summary(fit)
  
  cor_matrix <- cor(all_factors %>%
                      select(-Date))
  
  bmg_cors <- cor_matrix[,5]
  
  sum_stats <- c(mean(unlist(bmg_factor[, 2]), na.rm = TRUE), 
                 var(unlist(bmg_factor[, 2]), na.rm = TRUE)^0.5)
  
  return(list(sum_stats = sum_stats,
              correls = bmg_cors,
              reg = fit))
}

ff_factors <- read_csv("data/ff_factors.csv")
interest_rates <- read_csv("data/interest_rates.csv")

bmg_factors <- c("data/carbon_risk_factor.csv",
                 "data/bmg_eu_ets.csv",
                 "data/bmg_acwi_crbn.csv",
                 "data/bmg_xop_smog.csv",
                 "data/bmg_xop_smog_orthogonalized_1.csv",
                 "data/bmg_xop_smog_orthogonalized_2.csv")

final_output <- list()
final_sum_stats <- c()
final_correls <- c()
final_coefficients <- c()
final_r2 <- c()

for (i in 1:length(bmg_factors)) {
  bmg_factor <- read_csv(bmg_factors[i])
  final_output[[i]] <- init_data_script(bmg_factor, ff_factors, interest_rates)
}

for (i in 1:length(bmg_factors)) {
  final_sum_stats <- cbind(final_sum_stats, final_output[[i]]$sum_stats)
  final_correls <- cbind(final_correls, final_output[[i]]$correls)
  final_coefficients <- rbind(final_coefficients,
                              summary(final_output[[i]]$reg)$coefficients)
  final_r2 <- rbind(final_r2, summary(final_output[[i]]$reg)$r.squared)
}

write.csv(final_coefficients, "test.csv")





library(tidyverse)
library(lubridate)
source("R/key_functions.R")

# Read in the Fama-French and BMG factors
carbon_data <- read_csv("data/bmg_wmat_crbn_mat.csv")
#carbon_data <- read_csv("data/paris_aligned_bmg.csv") %>%
#  select(-Green_Returns, - Brown_Returns)
ff_data <- read_csv("data/ff_factors.csv")
risk_free <- read_csv("data/risk_free.csv")

# final_stock_returns <- read_csv('data/msci_constituent_returns.csv') # for msci
final_stock_comparison_returns <- read_csv('data/stock_return.csv')
final_stock_returns <- data.frame(Date = final_stock_comparison_returns$date,
                                  Returns = final_stock_comparison_returns$return,
                                  Stock = final_stock_comparison_returns$ticker)
# final_stock_returns <- read.csv('data/spx_constituent_returns.csv') # for spx
final_stock_returns[, 1] <- as.Date(final_stock_returns[, 1])
final_stock_returns <- as_tibble(final_stock_returns)

# Read in the sector breakdowns
final_stock_breakdown <- read_csv("data/msci_constituent_details.csv") # for msci
#final_stock_breakdown <- read_csv("data/spx_sector_breakdown.csv") # for spx

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

all_factor_data <- all_factor_data %>%
  inner_join(risk_free, by = c("Date"="Date")) %>%
  drop_na()

all_data <- final_stock_returns %>%
  full_join(all_factor_data, by = c("Date" = "Date")) %>%
  drop_na()

all_data <- all_data %>%
  mutate(excess_returns=Returns-Rf)

# Change market return data column to be more compatible
colnames(all_data)[5] <- "Mkt_less_RF"

# Create a blank dataframe
saved_betas <- c()
saved_t <- c()
saved_p <- c()

# Get stocks
stock_names <- unique(all_data$Stock)

# Need to limit the dataset and do a roll
start_date <- min(all_data$Date)
end_date <- max(all_data$Date)
roll_length <- 60

min_data <- 60

num_rolls <- interval(ymd(start_date), ymd(end_date))%/%months(1) - roll_length + 2
# num_rolls <- num_rolls - 1
roll_start <- start_date
  
for (i in 1:num_rolls) {
  roll_end <- ymd(start_date) %m+% months(i) %m+% months(roll_length - 1)
  roll_end <- ceiling_date(roll_end, "month") - days(1)
  roll_start <- ymd(start_date) %m+% months(i - 1)
  roll_start <- ceiling_date(roll_start, "month") - days(1)
  
  roll_data <- all_data %>%
    filter(Date > roll_start,
           Date <= roll_end)
  
  # n_obs <- roll_data %>%
  #   group_by(Stock) %>%
  #   summarise(n = n())
  
  valid_stocks <- roll_data %>%
    filter(Date %in% c(roll_start, roll_end)) %>%
    select(Stock) %>%
    distinct()

  if (nrow(valid_stocks) > 0) {
  
    roll_data <- roll_data %>%
      filter(Stock %in% valid_stocks$Stock)
    
    roll_data <- roll_data %>%
      filter(if_all(where(is.double) & !where(is.Date), ~ . < 0.5),
             if_all(where(is.double) & !where(is.Date), ~ . > -0.5))
    
    # Get the regression of all stocks
    mass_reg_results <- mass_regression(roll_data,
                                        "Stock",
                                        c("excess_returns ~ BMG + Mkt_less_RF + SMB + HML + WML"))
    
    temp_data <- get_data_output(mass_reg_results, 1)
    
    saved_betas <- rbind(saved_betas,
                         cbind(roll_end,
                               temp_data$betas,
                               temp_data$t_data,
                               temp_data$p_data))
    
    print(roll_end)
  
  }  
  
  roll_start <- ymd(roll_start) %m+% months(1)
  roll_start <- ceiling_date(roll_start, "month") - days(1)
}

