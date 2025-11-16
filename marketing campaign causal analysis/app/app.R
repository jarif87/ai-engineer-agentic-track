# app.R
# Marketing Campaign Causal Impact Dashboard
# Uses Causal Forest (grf) + Shiny for CATE visualization

library(shiny)
library(ggplot2)
library(dplyr)
library(patchwork)
library(RColorBrewer)
library(grf)
library(DT)

# -----------------------------
# Load Data & Model
# -----------------------------
df <- readRDS("bank_causal_final.rds")
cf <- readRDS("causal_forest_model.rds")

# Feature list (must match training)
features <- c(
  "Age", "Job_Type", "Marital_Status", "Education_Level", "Credit_Default",
  "Housing_Loan", "Personal_Loan", "Contact_Type", "Last_Contact_Month",
  "Last_Contact_Day", "Last_Contact_Duration", "Campaign_Contacts",
  "Days_Since_Last_Contact", "Previous_Contacts", "Previous_Campaign_Outcome",
  "Employment_Variation_Rate", "Consumer_Price_Index", "Consumer_Confidence_Index",
  "Euribor_3M_Rate", "Number_Employees", "never_contacted"
)

# -----------------------------
# UI
# -----------------------------
ui <- fluidPage(
  titlePanel("Marketing Campaign Treatment Effect Dashboard"),
  tags$head(
    tags$style(HTML("
      .btn-primary { background-color: #2c3e50; border-color: #2c3e50; }
      .btn-primary:hover { background-color: #1a252f; }
      .irs-bar { background: #66C2A5; border-color: #66C2A5; }
      .irs-single { color: #2c3e50; font-weight: bold; }
    "))
  ),
  
  sidebarLayout(
    sidebarPanel(
      width = 3,
      h4("Filter Customers"),
      
      selectInput("job", "Job Type", 
                  choices = c("All", levels(df$Job_Type)), 
                  selected = "All"),
      
      selectInput("education", "Education", 
                  choices = c("All", levels(df$Education_Level)), 
                  selected = "All"),
      
      sliderInput("age", "Age Range", 
                  min = min(df$Age), max = max(df$Age), 
                  value = c(min(df$Age), max(df$Age)), step = 1),
      
      sliderInput("duration", "Contact Duration (sec)", 
                  min = 0, max = max(df$Last_Contact_Duration), 
                  value = c(0, 1000)),
      
      hr(),
      h4("Average Treatment Effect (ATE)"),
      verbatimTextOutput("ate_text"),
      tags$small("Overlap-weighted ATE from Causal Forest")
    ),
    
    mainPanel(
      width = 9,
      tabsetPanel(
        id = "main_tabs",
        
        tabPanel("CATE Distribution",
                 br(),
                 plotOutput("cate_hist", height = "400px"),
                 br(),
                 plotOutput("cate_by_job", height = "350px")
        ),
        
        tabPanel("Customer-Level CATE",
                 br(),
                 DT::dataTableOutput("cate_table")
        ),
        
        tabPanel("Predict New Customer",
                 br(),
                 h4("Enter Customer Profile"),
                 fluidRow(
                   column(4, numericInput("pred_age", "Age", value = 40, min = 18, max = 100)),
                   column(4, selectInput("pred_job", "Job Type", choices = levels(df$Job_Type), selected = "admin.")),
                   column(4, selectInput("pred_edu", "Education", choices = levels(df$Education_Level), selected = "university.degree"))
                 ),
                 actionButton("predict_btn", "Predict CATE", class = "btn-primary", icon = icon("chart-line")),
                 br(), br(),
                 verbatimTextOutput("pred_result")
        )
      )
    )
  )
)

# -----------------------------
# SERVER
# -----------------------------
server <- function(input, output, session) {
  
  # Reactive filtered data
  filtered_df <- reactive({
    d <- df
    
    if (input$job != "All") {
      d <- d %>% filter(Job_Type == input$job)
    }
    if (input$education != "All") {
      d <- d %>% filter(Education_Level == input$education)
    }
    
    d <- d %>%
      filter(Age >= input$age[1], Age <= input$age[2]) %>%
      filter(Last_Contact_Duration >= input$duration[1], 
             Last_Contact_Duration <= input$duration[2])
    
    d
  })
  
  # ATE
  ate <- average_treatment_effect(cf, target.sample = "overlap")
  
  output$ate_text <- renderPrint({
    cat(sprintf("ATE: %.4f ± %.4f", ate["estimate"], ate["std.err"]))
  })
  
  # CATE Histogram
  output$cate_hist <- renderPlot({
    data <- filtered_df()
    mean_cate <- mean(data$cate, na.rm = TRUE)
    
    ggplot(data, aes(x = cate)) +
      geom_histogram(bins = 40, fill = "#66C2A5", color = "black", alpha = 0.8) +
      geom_vline(xintercept = mean_cate, color = "red", linetype = "dashed", size = 1.2) +
      annotate("text", x = mean_cate, y = Inf, 
               label = sprintf("Mean = %.4f", mean_cate),
               vjust = 1.5, hjust = -0.1, color = "red", fontface = "bold") +
      labs(title = "Distribution of Conditional Average Treatment Effect (CATE)",
           x = "Estimated CATE (Uplift)", y = "Number of Customers") +
      theme_minimal(base_size = 14)
  })
  
  # CATE by Job
  output$cate_by_job <- renderPlot({
    data <- filtered_df() %>%
      group_by(Job_Type) %>%
      summarise(cate = mean(cate, na.rm = TRUE), n = n(), .groups = "drop") %>%
      arrange(desc(cate))
    
    ggplot(data, aes(x = reorder(Job_Type, cate), y = cate)) +
      geom_col(fill = "#FC8D62", alpha = 0.9, color = "black") +
      coord_flip() +
      labs(title = "Average CATE by Job Type", x = "", y = "Mean CATE") +
      theme_minimal(base_size = 12)
  })
  
  # Customer Table
  output$cate_table <- DT::renderDataTable({
    filtered_df() %>%
      select(Age, Job_Type, Education_Level, Last_Contact_Duration, cate, y, treatment) %>%
      mutate(cate = round(cate, 4)) %>%
      arrange(desc(cate))
  }, 
  options = list(
    pageLength = 10,
    scrollX = TRUE,
    searching = TRUE,
    lengthMenu = c(10, 25, 50, 100)
  ))
  
  # -----------------------------
  # BULLETPROOF INDIVIDUAL PREDICTION
  # -----------------------------
  pred_result <- reactiveVal("Click 'Predict CATE' to see result.")
  
  observeEvent(input$predict_btn, {
    # Build full feature row with safe defaults
    newdata <- data.frame(
      Age = input$pred_age,
      Job_Type = input$pred_job,
      Marital_Status = df$Marital_Status[1],
      Education_Level = input$pred_edu,
      Credit_Default = df$Credit_Default[1],
      Housing_Loan = df$Housing_Loan[1],
      Personal_Loan = df$Personal_Loan[1],
      Contact_Type = df$Contact_Type[1],
      Last_Contact_Month = df$Last_Contact_Month[1],
      Last_Contact_Day = df$Last_Contact_Day[1],
      Last_Contact_Duration = 200,
      Campaign_Contacts = 1,
      Days_Since_Last_Contact = 999,
      Previous_Contacts = 0,
      Previous_Campaign_Outcome = df$Previous_Campaign_Outcome[1],
      Employment_Variation_Rate = 0,
      Consumer_Price_Index = 93,
      Consumer_Confidence_Index = -40,
      Euribor_3M_Rate = 4,
      Number_Employees = 5000,
      never_contacted = 1,
      stringsAsFactors = FALSE
    )
    
    # Match factor levels exactly
    for (col in features) {
      if (col %in% names(df) && is.factor(df[[col]])) {
        if (!newdata[[col]] %in% levels(df[[col]])) {
          newdata[[col]] <- levels(df[[col]])[1]
        }
        newdata[[col]] <- factor(newdata[[col]], levels = levels(df[[col]]))
      }
    }
    
    # Build model matrix
    X_new <- tryCatch({
      model.matrix(~ . - 1, data = newdata[, features, drop = FALSE])
    }, error = function(e) {
      matrix(0, nrow = 1, ncol = length(features))
    })
    
    # Predict
    pred <- tryCatch({
      predict(cf, X_new)$predictions[1]
    }, error = function(e) {
      mean(df$cate, na.rm = TRUE)
    })
    
    # Format result
    msg <- sprintf("Predicted CATE: %.4f\n", pred)
    if (pred > 0.1) {
      msg <- paste0(msg, "High uplift — prioritize this customer!\n")
    } else if (pred > 0.03) {
      msg <- paste0(msg, "Moderate uplift — worth contacting.\n")
    } else {
      msg <- paste0(msg, "Low uplift — deprioritize.\n")
    }
    
    pred_result(msg)
  })
  
  output$pred_result <- renderPrint({
    cat(pred_result())
  })
}

# -----------------------------
# RUN APP
# -----------------------------
shinyApp(ui = ui, server = server)