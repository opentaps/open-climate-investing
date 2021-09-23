library(shiny)
library(tidyverse)
library(shinydashboard)
library(broom)
library(lubridate)
library(shinyjs)
library(plm)

options(shiny.maxRequestSize = 100*1024^2)

ui <- fluidPage(
  useShinyjs(),
  titlePanel("BMG Loading Testing"),
  mainPanel(
    fluidPage(
      # To Load CSV ----
      fileInput(inputId = "raw_data",
                label = "Load Stock Return File (as CSV)",
                accept = c(
                  "text/csv",
                  "text/comma-separated-values,text/plain",
                  ".csv")),
      hidden(
        div(
          id = "returns_is_parsing",
          h5("Data is Parsing..."),
        )
      ),
      hidden(
        div(
          id = "date_stock_col_selector",
          uiOutput("date_selector"),
          uiOutput("stock_name_selector"),
          uiOutput("return_name_selector")
        )
      ),
      hidden(
        div(
          id = "factor_data_load",
          fileInput(inputId = "factor_data",
                    label = "Load Factor Data File (as CSV)",
                    accept = c(
                      "text/csv",
                      "text/comma-separated-values,text/plain",
                      ".csv"))
        )
      ),
      hidden(
        div(
          id = "factor_is_parsing",
          h5("Data is Parsing..."),
        )
      ),
      hidden(
        div(
          id = "factor_date_select",
          uiOutput("factor_date_selector")
        )
      ),
      
      hidden(
        div(
          id = "bmg_data_load",
          fileInput(inputId = "bmg_data",
                    label = "Load Carbon Factor Data File (as CSV)",
                    accept = c(
                      "text/csv",
                      "text/comma-separated-values,text/plain",
                      ".csv"))
        )
      ),
      hidden(
        div(
          id = "carbon_is_parsing",
          h5("Data is Parsing..."),
        )
      ),
      hidden(
        div(
          id = "carbon_date_select",
          uiOutput("carbon_date_selector")
        )
      ),
      
      hidden(
        div(id = "reg_options",
            selectInput(inputId = "regression_options",
                        label = "Select Variables",
                        choices = c("All Data",
                                    "By Variable"))
        )
      ),
      hidden(
        div(id = "bmg_breakdown",
            fileInput(inputId = "stock_details",
                      label = "Load Details of Stock Constituents (as CSV)",
                      accept = c(
                        "text/csv",
                        "text/comma-separated-values,text/plain",
                        ".csv"))
            )
        ),
      hidden(
        div(id = "bmg_breakdown_parsing",
            h5("Data is Parsing...")
            )
      ),
      hidden(
        div(id = "filter_stock_option",
            uiOutput("stock_breakdown"))
      ),
      hidden(
        div(id = "reg_button",
            actionButton(inputId = "run_regression",
                         label = "Run Regression")
        )
      )
    )
  )
)


# Define server logic
server <- function(input, output, session) {
  
  ui_control <- reactiveValues(read_data = FALSE,
                               breakdown_true = FALSE,
                               bmg_breakdown_menu = FALSE,
                               bmg_breakdown_var_select_menu = FALSE,
                               stock_return_colnames = FALSE)
  
  data <- reactiveValues(df = NULL,
                         factor_df = NULL,
                         stock_breakdown = NULL,
                         stock_return_name = "",
                         stock_date_name = "",
                         stock_ticker_name = "")
  
  observeEvent(input$raw_data, {
    shinyjs::toggle("returns_is_parsing")
    data$df = read_csv(input$raw_data$datapath,
                       guess_max = 100000)
    ui_control$stock_return_colnames <- c("", colnames(data$df))
    
    output$date_selector <- renderUI(
      selectInput(inputId = "date_col_name",
             label = "What is the date column name?",
             choices = ui_control$stock_return_colnames,
             selected = "")
    )
    output$stock_name_selector <- renderUI(
      selectInput(inputId = "ticker_col_name",
                  label = "What is the stock ticker column name?",
                  choices = ui_control$stock_return_colnames,
                  selected = ""
                  )
    )
    output$return_name_selector <- renderUI(
      selectInput(inputId = "returns_col_name",
                  label = "What is the returns column name?",
                  choices = ui_control$stock_return_colnames,
                  selected = "")
    )
    shinyjs::toggle(id = "date_stock_col_selector")
    shinyjs::toggle("returns_is_parsing")
    # shinyjs::toggle(id = "reg_options")     
  })
  
  observeEvent(c(
    input$date_col_name,
    input$ticker_col_name,
    input$returns_col_name), {
    if (input$date_col_name != "" &
        input$ticker_col_name != "" &
        input$returns_col_name != "") {

      shinyjs::toggle("factor_data_load")
    }
  })
  
  observeEvent(input$factor_data, {
    shinyjs::toggle("factor_is_parsing")
    data$factor_df = read_csv(input$factor_data$datapath,
                       guess_max = 100000)
    shinyjs::toggle("factor_is_parsing")
    shinyjs::toggle("factor_date_select")
    ui_control$factor_date_colnames <- c("", colnames(data$factor_df))
    
    output$factor_date_selector <- renderUI(
      selectInput(inputId = "factor_date_col_name",
                  label = "What is the factor date column name?",
                  choices = ui_control$factor_date_colnames,
                  selected = "")
    )
  })
  
  observeEvent(
    input$factor_date_col_name, {
      if (input$factor_date_col_name != "") {
        shinyjs::toggle("bmg_data_load")
      }
    })

  observeEvent(input$bmg_data, {
    shinyjs::toggle("carbon_is_parsing")
    data$carbon_df = read_csv(input$bmg_data$datapath,
                              guess_max = 100000)
    shinyjs::toggle("carbon_is_parsing")
    shinyjs::toggle("carbon_date_select")
    ui_control$carbon_date_colnames <- c("", colnames(data$carbon_df))
    
    output$carbon_date_selector <- renderUI(
      selectInput(inputId = "carbon_date_col_name",
                  label = "What is the carbon risk factor date column name?",
                  choices = ui_control$carbon_date_colnames,
                  selected = "")
    )
  })
  
  observeEvent(
    input$carbon_date_col_name, {
      if (input$carbon_date_col_name != "") {
        shinyjs::toggle(id = "reg_button")
      }
    })
    
  # observeEvent(input$stock_details, {
  #   shinyjs::toggle("bmg_breakdown_parsing")
  #   data$breakdown_df = read_csv(input$stock_details$datapath,
  #                                guess_max = 100000)
  #   shinyjs::toggle("bmg_breakdown_parsing")
  #   ui_control$bmg_breakdown_menu <- TRUE
  #   data$stock_breakdown <- colnames(data$breakdown_df)
  #   output$stock_breakdown <- renderUI({
  #     selectInput(inputId = "breakdown_variable", 
  #                 label = "Breakdown Stocks By: ",
  #                 choices = data$stock_breakdown)
  #   })
  #   shinyjs::toggle("filter_stock_option")
  #   ui_control$bmg_breakdown_var_select_menu <- TRUE
  # })
  
  # observeEvent(input$regression_options, {
  #   if (input$regression_options == "By Variable") {
  #     ui_control$breakdown_true <- TRUE
  #     shinyjs::toggle("bmg_breakdown")
  #   } else if (input$regression_options == "All Data") {
  #     if (ui_control$breakdown_true  == TRUE) {
  #       # data$stock_breakdown <- NULL
  #       shinyjs::toggle("bmg_breakdown")
  #       ui_control$breakdown_true <- FALSE
  #     }
  #     if (ui_control$bmg_breakdown_var_select_menu == TRUE) {
  #       shinyjs::toggle("filter_stock_option")
  #       ui_control$bmg_breakdown_var_select_menu <- FALSE
  #     }
  #   }
  # })


  observeEvent(input$run_regression, {
    
    data$factor_df["Date_Col"] <- data$factor_df[, which(colnames(
        data$factor_df) == input$factor_date_col_name)]
    
    data$factor_df <- data$factor_df %>%
      select(-input$factor_date_col_name)
    
    print(data$factor_df)
    data$carbon_df["Date_Col"] <- data$carbon_df[, which(colnames(
      data$carbon_df) == input$carbon_date_col_name)]
    data$carbon_df <- data$carbon_df %>%
      select(-input$carbon_date_col_name)
    
    data$df["Date_Col"] <- data$df[, which(colnames(
      data$df) == input$date_col_name)]
    data$df <- data$df %>%
      select(-input$date_col_name)
    
    data$finalDF <- data$factor_df %>%
      inner_join(data$carbon_df,
                 by = c("Date_Col" = "Date_Col")) %>%
      full_join(data$df, by = c("Date_Col" = "Date_Col")) %>%
      drop_na()
    
    print(data$finalDF)

    
    # data$panel_df <- data.frame("Date" = data$finalDF[input$date_col_name],
    #                             "Stock" = data$finalDF[input$ticker_col_name],
    #                             "Returns" = data$finalDF[input$returns_col_name])
    # 
    # data$panel_df <- pdata.frame(data$panel_df, index = c(
    #   "Stock",
    #   "Date"
    # ))
    # panel_reg <- plm(input$returns_col_name)
  })
}

# Run the application 
shinyApp(ui = ui, server = server)
