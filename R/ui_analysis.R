# ==============================================================================
# UI: ANALYSIS MODULE
# ==============================================================================
# User interface for statistical analysis:
# - Correlation analysis
# - Regression analysis
# - Group comparison
# ==============================================================================

ui_analysis <- tabPanel(
  "Analysis",
  
  fluidPage(
    
    titlePanel("Statistical Analysis"),
    
    # ========================================================================
    # SELECT ANALYSIS TYPE
    # ========================================================================
    
    sidebarLayout(
      
      sidebarPanel(
        width = 3,
        
        radioButtons(
          "analysis_type",
          "Select Analysis Type:",
          choices = c(
            "Correlation Analysis" = "correlation",
            "Regression Analysis" = "regression",
            "Group Comparison" = "group_comparison"
          ),
          selected = "correlation"
        ),
        
        hr(),
        
        # ==================================================================
        # CORRELATION INPUTS
        # ==================================================================
        
        conditionalPanel(
          condition = "input.analysis_type == 'correlation'",
          
          h4("Correlation Analysis"),
          
          selectInput(
            "corr_vars",
            "Select Variables (2 or more):",
            choices = NULL,
            multiple = TRUE,
            selectize = TRUE
          ),
          
          helpText("Select at least 2 numeric variables to analyze correlations."),
          
          actionButton(
            "run_correlation",
            "Run Correlation Analysis",
            class = "btn-primary btn-block",
            icon = icon("play")
          )
        ),
        
        # ==================================================================
        # REGRESSION INPUTS
        # ==================================================================
        
        conditionalPanel(
          condition = "input.analysis_type == 'regression'",
          
          h4("Regression Analysis"),
          
          selectInput(
            "reg_dependent",
            "Dependent Variable (Y):",
            choices = NULL,
            selected = NULL
          ),
          
          selectInput(
            "reg_independent",
            "Independent Variables (X):",
            choices = NULL,
            multiple = TRUE,
            selectize = TRUE
          ),
          
          helpText("Select one dependent variable and one or more independent variables."),
          
          actionButton(
            "run_regression",
            "Run Regression Analysis",
            class = "btn-primary btn-block",
            icon = icon("play")
          )
        ),
        
        # ==================================================================
        # GROUP COMPARISON INPUTS
        # ==================================================================
        
        conditionalPanel(
          condition = "input.analysis_type == 'group_comparison'",
          
          h4("Group Comparison"),
          
          selectInput(
            "group_var",
            "Grouping Variable:",
            choices = c(
              "Census Region",
              "Census Division",
              "Rural/Urban",
              "Poverty Category",
              "Income Category",
              "FI Category",
              "Race"
            ),
            selected = "Rural/Urban"
          ),
          
          selectInput(
            "group_target",
            "Outcome Variable:",
            choices = NULL,
            selected = NULL
          ),
          
          helpText("Compare means across groups using t-test or ANOVA."),
          
          actionButton(
            "run_group_comparison",
            "Run Group Comparison",
            class = "btn-primary btn-block",
            icon = icon("play")
          )
        )
      ),
      
      # ======================================================================
      # MAIN PANEL: RESULTS
      # ======================================================================
      
      mainPanel(
        width = 9,
        
        # ==================================================================
        # CORRELATION RESULTS
        # ==================================================================
        
        conditionalPanel(
          condition = "input.analysis_type == 'correlation'",
          
          h3("Correlation Analysis Results"),
          
          tabsetPanel(
            
            tabPanel(
              "Correlation Matrix",
              plotOutput("corr_plot", height = "600px")
            ),
            
            tabPanel(
              "Correlation Table",
              DT::DTOutput("corr_table")
            ),
            
            tabPanel(
              "Interpretation",
              uiOutput("corr_interpretation")
            )
          )
        ),
        
        # ==================================================================
        # REGRESSION RESULTS
        # ==================================================================
        
        conditionalPanel(
          condition = "input.analysis_type == 'regression'",
          
          h3("Regression Analysis Results"),
          
          tabsetPanel(
            
            tabPanel(
              "Model Summary",
              verbatimTextOutput("reg_summary")
            ),
            
            tabPanel(
              "Diagnostics",
              plotOutput("reg_diagnostics", height = "600px")
            ),
            
            tabPanel(
              "Predictions",
              plotOutput("reg_predictions", height = "500px")
            ),
            
            tabPanel(
              "Coefficients",
              plotOutput("reg_coefficients", height = "500px")
            )
          )
        ),
        
        # ==================================================================
        # GROUP COMPARISON RESULTS
        # ==================================================================
        
        conditionalPanel(
          condition = "input.analysis_type == 'group_comparison'",
          
          h3("Group Comparison Results"),
          
          tabsetPanel(
            
            tabPanel(
              "Visualization",
              plotOutput("group_comp_plot", height = "600px")
            ),
            
            tabPanel(
              "Statistical Test",
              verbatimTextOutput("group_stats")
            )
          )
        )
      )
    )
  )
)
