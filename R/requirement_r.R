packages <- c("quantmod", 
              "tidyverse", 
              "lubridate", 
              "plm",
              "shiny",
              "shinydashboard",
              "shinyjs",
              "broom",
              "DT",
              "corrplot",
              "car",
              "lmtest",
              "purrr",
              "ggplot")
  
install.packages(setdiff(packages, rownames(installed.packages())))
