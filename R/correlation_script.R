library(tidyverse)
library(corrplot)

ff_factors <- read_csv("data/ff_factors.csv")
bmg_factor <- read_csv("data/carbon_risk_factor.csv")

all_factors <- ff_factors %>%
  inner_join(bmg_factor, by = c("Date" = "month"))

cor_matrix <- cor(all_factors %>% 
                    select(-Date))

corrplot(cor_matrix,
         method="number",
         diag = FALSE)
