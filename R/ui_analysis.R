# R/ui_analysis.R
ui_analysis <- tabPanel(
  "Analysis",
  sidebarLayout(
    sidebarPanel(
      selectInput("model_type", "Select Analysis Type:",
                  choices = c("Correlation", "Regression", "Group Comparison")),
      conditionalPanel(
        condition = "input.model_type == 'Regression'",
        selectInput("dep_var", "Dependent Variable:", choices = c("FoodInsecurity")),
        selectInput("indep_vars", "Independent Variables:",
                    choices = c("PovertyRate", "MedianIncome"),
                    multiple = TRUE)
      ),
      actionButton("run_model", "Run Analysis")
    ),
    mainPanel(
      tabsetPanel(
        id = "analysis_tabs",
        tabPanel("Correlation", plotly::plotlyOutput("corr_plot")),
        tabPanel("Regression", verbatimTextOutput("reg_summary")),
        tabPanel("Group Comparison", plotly::plotlyOutput("group_plot"))
      )
    )
  )
)
