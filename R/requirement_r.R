packages <- c("quantmod", 
              "tidyverse", 
              "lubridate", 
              "plm",
              "shiny",
              "shinydashboard",
              "broom")
  
install.packages(setdiff(packages, rownames(installed.packages())))
