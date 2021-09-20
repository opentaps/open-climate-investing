packages <- c("quantmod", 
              "tidyverse", 
              "lubridate", 
              "plm",
              "shiny",
              "shinydashboard")
  
install.packages(setdiff(packages, rownames(installed.packages())))
