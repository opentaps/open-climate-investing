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
              "RPostgres",
              "car",
              "lmtest",
              "purrr",
              "ggplot")
  
install.packages(setdiff(packages, rownames(installed.packages())))
