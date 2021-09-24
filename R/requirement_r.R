packages <- c("quantmod", 
              "tidyverse", 
              "lubridate", 
              "plm",
              "shiny",
              "shinydashboard",
              "shinyjs",
              "broom",
              "DT",
              "corrplot")
  
install.packages(setdiff(packages, rownames(installed.packages())))
