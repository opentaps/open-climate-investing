library(shiny)
library(tidyverse)
library(shinydashboard)
library(broom)
library(lubridate)
library(shinyjs)
library(plm)
library(DT)

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
        div(id = "reg_button",
            actionButton(inputId = "run_regression",
                         label = "Run Regression")
        )
      ),
      hidden(
        div(id = "full_reg_table",
            tableOutput('full_reg_tbl')
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
        div(id = "stock_breakdown",
            fileInput(inputId = "stock_details",
                      label = "Load Details of Stock Constituents (as CSV)",
                      accept = c(
                        "text/csv",
                        "text/comma-separated-values,text/plain",
                        ".csv"))
        )
      ),
      hidden(
        div(id = "stock_breakdown_is_parsing",
            h5("Data is Parsing...")
        )
      ),
      hidden(
        div(id = "filter_stock_col_var",
            uiOutput("stock_breakdown_selector"),
            uiOutput("stock_breakdown_ticker_selector"))
      ),
      hidden(
        div(id = "decompose_reg_button_js",
            actionButton(inputId = "decompose_reg_button",
                         label = "Run Decomposition Regression")
        )
      ),
      hidden(
        div(id = "decompose_reg_table",
            dataTableOutput('decompose_reg_tbl')
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
                               stock_return_colnames = FALSE,
                               returns_load = FALSE,
                               factor_load = FALSE,
                               carbon_load = FALSE,
                               ret_load_select = FALSE,
                               factor_load_select = FALSE,
                               carbon_load_select = FALSE,
                               stock_breakdown_load = FALSE,
                               stock_breakdown_load_select = FALSE,
                               first_reg = FALSE)
  
  data <- reactiveValues(df = NULL,
                         factor_df = NULL,
                         stock_breakdown = NULL,
                         stock_return_name = "",
                         stock_date_name = "",
                         stock_ticker_name = "",
                         stock_breakdown_colnames = "",
                         no_carbon_data = NULL,
                         var_names = NULL)
  
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
    if (ui_control$returns_load == FALSE) {
      shinyjs::toggle(id = "date_stock_col_selector")
      ui_control$returns_load <- TRUE
    }
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
      if (ui_control$ret_load_select == FALSE) {
        shinyjs::toggle("factor_data_load")
        ui_control$ret_load_select <- TRUE
      }
    }
  })
  
  observeEvent(input$factor_data, {
    shinyjs::toggle("factor_is_parsing")
    data$factor_df = read_csv(input$factor_data$datapath,
                       guess_max = 100000)
    shinyjs::toggle("factor_is_parsing")
    if (ui_control$factor_load == FALSE) {
      shinyjs::toggle("factor_date_select")
      ui_control$factor_load <- TRUE
    }
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
        if (ui_control$factor_load_select == FALSE) {
          shinyjs::toggle("bmg_data_load")
          ui_control$factor_load_select <- TRUE
        }
      }
    })

  observeEvent(input$bmg_data, {
    shinyjs::toggle("carbon_is_parsing")
    data$carbon_df = read_csv(input$bmg_data$datapath,
                              guess_max = 100000)
    shinyjs::toggle("carbon_is_parsing")
    if (ui_control$carbon_load == FALSE) {
      shinyjs::toggle("carbon_date_select")
      ui_control$carbon_load <- TRUE
    }
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
        if (ui_control$carbon_load_select == FALSE) {
          shinyjs::toggle(id = "reg_button")
          ui_control$carbon_load_select <- TRUE
        }
      }
    })

  observeEvent(input$run_regression, {
    
    data$factor_df["Date_Col"] <- data$factor_df[, which(colnames(
        data$factor_df) == input$factor_date_col_name)]
    data$factor_df <- data$factor_df %>%
      select(-input$factor_date_col_name)
    
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
    
    var_names <- list(
      "BMG" = colnames(data$carbon_df)[which(colnames(data$carbon_df) != "Date_Col")],
      "FF" = colnames(data$factor_df)[which(colnames(data$factor_df) != "Date_Col")],
      "Ticker" = input$ticker_col_name,
      "Returns" = input$returns_col_name
    )
    

    all_data <- data$finalDF

    # Create a blank dataframe
    no_carbon_residuals <- c()
    stock_names <- all_data %>%
      select(var_names$Ticker)
    stock_names <- unique(stock_names)
  
    ff_only_data <- all_data %>%
      select(-var_names$BMG)
    
    withProgress(message = 'Running FF Regressions', value = 0, {
      
      n <- nrow(stock_names)
    
      # Start look to go through all the stocks in stock_names
      for (i in 1:nrow(stock_names)) {
        # Get the stocks name
        temp_stock_name <- as.character(stock_names[i, 1])
        # Filter all the data to only include that stock
        temp_data <- ff_only_data %>%
          dplyr::filter(Stock == temp_stock_name)
        temp_data_x <- temp_data %>%
          select(var_names$FF)
        temp_data_y <- temp_data %>%
          select(var_names$Returns)
        temp_data_y <- as.matrix(temp_data_y)
        temp_data_x <- as.matrix(temp_data_x)
        # If there is more than 12 months of data, run the FF (no BMG) regression
        if (nrow(temp_data) >= 12) {
          temp_reg <- lm(temp_data_y ~ temp_data_x)
        }
        # Create a dataframe
        temp_no_carbon_residuals <- data.frame(Stock = temp_stock_name,
                                               Res = temp_reg$residuals,
                                               Date_Col = temp_data$Date_Col,
                                               Returns = temp_data_y)
        
        # Append to a dataframe
        no_carbon_residuals <- rbind(no_carbon_residuals, temp_no_carbon_residuals)
        
        incProgress(1/n, detail = paste("Doing regression ", i, "/", n, "", " ", temp_stock_name))
        
      }
    })
    
    # Ensure that there are no duplicated residuals
    no_carbon_residuals <- no_carbon_residuals %>%
      unique()
    
    carbon_data <- data$carbon_df %>%
      select("Date_Col",
             var_names$BMG)
    
    colnames(carbon_data)[2] <- "BMG"
    
    # Join the BMG factor to the residuals
    no_carbon_residuals <- no_carbon_residuals %>%
      left_join(carbon_data, by = c("Date_Col" = "Date_Col"))
    
    # Create a panel dataframe on the above dataframe (required for PLM)
    no_carbon_data <- pdata.frame(no_carbon_residuals, index = c("Stock", "Date_Col"))

    # Remove duplicates that have somehow creeped in
    if (length(which(duplicated(index(no_carbon_data))) == TRUE) > 0) {
      no_carbon_data <- no_carbon_data[-which(duplicated(index(no_carbon_data))), ]
    }

    # Run the panel regression of the BMG factor on the residuals
    no_carbon_regression <- plm(Res ~ BMG,
                                data = no_carbon_data,
                                effect = "individual",
                                model = "within")
    
    output$full_reg_tbl <- renderTable(summary(no_carbon_regression)$coefficients)
    
    data$no_carbon_residuals <- no_carbon_residuals
    data$var_names <- var_names
    
    if (ui_control$first_reg == FALSE) {
      shinyjs::toggle(id = "full_reg_table")
      shinyjs::toggle(id = "stock_breakdown")
      ui_control$first_reg <- TRUE
    }
  })

  
  observeEvent(input$stock_details, {
    shinyjs::toggle("stock_breakdown_is_parsing")
    data$stock_breakdown = read_csv(input$stock_details$datapath,
                              guess_max = 100000)
    shinyjs::toggle("stock_breakdown_is_parsing")
    if (ui_control$stock_breakdown_load == FALSE) {
      shinyjs::toggle("filter_stock_col_var")
      ui_control$stock_breakdown_load <- TRUE
    }
    ui_control$stock_breakdown_colnames <- c("", colnames(data$stock_breakdown))
    
    output$stock_breakdown_selector <- renderUI(
      selectInput(inputId = "stock_breakdown_col_name",
                  label = "What is the variable you want to use for stock decomposition?",
                  choices = ui_control$stock_breakdown_colnames,
                  selected = "")
    )
    
    output$stock_breakdown_ticker_selector <- renderUI(
      selectInput(inputId = "stock_breakdown_ticker_col_name",
                  label = "What is the variable that has the stock ticker?",
                  choices = ui_control$stock_breakdown_colnames,
                  selected = "")
    )
    
  })
  
  observeEvent(
    input$stock_breakdown_col_name, {
      if (input$stock_breakdown_col_name != "") {
        if (ui_control$stock_breakdown_load_select == FALSE) {
          shinyjs::toggle(id = "decompose_reg_button_js")
          ui_control$stock_breakdown_load_select <- TRUE
        }
      }
    })
  
  observeEvent(
    input$decompose_reg_button, {
      no_carbon_residuals <- data$no_carbon_residuals
      stock_breakdown <- data$stock_breakdown
      stock_breakdown["Stock"] <- stock_breakdown[, which(colnames(stock_breakdown) == input$stock_breakdown_ticker_col_name)]
      stock_breakdown["Stock_Decompose"] <- stock_breakdown[, which(colnames(stock_breakdown) == input$stock_breakdown_col_name)]
      stock_breakdown <- stock_breakdown %>%
        select("Stock",
               "Stock_Decompose")
      
      decompose_df <- left_join(no_carbon_residuals,
                                     stock_breakdown,
                                     by = c("Stock" = "Stock"))
      
      decompose_var <- unique(stock_breakdown$Stock_Decompose)
      
      decomp_coefs <- c()
      
      for (i in 1:length(decompose_var)) {
        temp_residuals <- decompose_df %>%
          filter(Stock_Decompose == decompose_var[i])
        
        if (nrow(temp_residuals) > 0) {
          # Create a panel dataframe on the above dataframe (required for PLM)
          no_carbon_data <- pdata.frame(temp_residuals, index = c("Stock", "Date_Col"))

          # Remove duplicates that have somehow creeped in
          if (length(which(duplicated(index(no_carbon_data))) == TRUE) > 0) {
            no_carbon_data <- no_carbon_data[-which(duplicated(index(no_carbon_data))), ]
          }

          # Run the panel regression of the BMG factor on the residuals
          no_carbon_regression <- plm(Res ~ BMG,
                                        data = no_carbon_data,
                                        effect = "individual",
                                        model = "within")
        }
        
        print(summary(no_carbon_regression)$coefficients)
        decomp_coefs <- rbind(decomp_coefs, 
                              data.frame(decompose_var[i],
                                         summary(no_carbon_regression)$coefficients))
        
        }
      print(decomp_coefs)
      colnames(decomp_coefs) <- c(input$stock_breakdown_col_name,
                                  "Carbon Loading",
                                  "Std Error",
                                  "t-Statistic",
                                  "p-Value")
      decomp_coefs[, -1] <- round(decomp_coefs[, -1], 4)
      
      decomp_coefs <- datatable(decomp_coefs,
                                rownames = FALSE)
      
      shinyjs::toggle(id = "decompose_reg_table")
      output$decompose_reg_tbl <- DT::renderDataTable(decomp_coefs)
    })
}

# Run the application 
shinyApp(ui = ui, server = server)