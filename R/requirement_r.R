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
              "RPostgres")

install.packages(setdiff(packages, rownames(installed.packages())))
