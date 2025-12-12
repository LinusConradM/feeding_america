# ==============================================================================
# UI MODULE: REGRESSION & EXPLAINABILITY ENGINE
# ==============================================================================
# PURPOSE: Quantify causal drivers and model food insecurity predictors
# CAPABILITIES: OLS, fixed-effects, diagnostics, interpretations
# TEAM: Conrad, Sharon, Ryann, Alex
# ==============================================================================

ui_regression_models <- tabPanel(
  "Regression Models",
  value = "regression",
  
  fluidPage(
    # Global Controls
    # global_controls_ui(),  # Removed to prevent duplicate IDs
    
    # Page Header
    fluidRow(
      column(
        12,
        h2(
          icon("calculator"), " Regression & Explainability Engine",
          style = "color: #2c3e50; font-weight: 600; margin-bottom: 10px;"
        ),
        p(
          "Quantify causal drivers of food insecurity with statistical models",
          style = "color: #6c757d; font-size: 16px; margin-bottom: 30px;"
        )
      )
    ),
    
    # ========================================================================
    # MODEL SPECIFICATION PANEL
    # ========================================================================
    fluidRow(
      column(
        4,
        div(
          style = "background: white; padding: 25px; border-radius: 10px;
                   box-shadow: 0 2px 8px rgba(0,0,0,0.08);",
          h4("Model Specification", style = "margin-top: 0; color: #2c3e50;"),
          hr(),
          
          # Dependent variable
          selectInput(
            "model_dv",
            "Dependent Variable:",
            choices = c(
              "Food Insecurity Rate" = "fi_rate",
              "Child FI Rate" = "child_fi",
              "Budget Shortfall" = "shortfall"
            ),
            selected = "fi_rate"
          ),
          
          # Independent variables
          checkboxGroupInput(
            "model_ivs",
            "Independent Variables:",
            choices = c(
              "Poverty Rate" = "poverty",
              "Median Income (log)" = "log_income",
              "Unemployment Rate" = "unemployment",
              "Uninsured Rate" = "uninsured",
              "SNAP Participation" = "snap",
              "Education (College+)" = "education",
              "Cost per Meal" = "cost"
            ),
            selected = c("poverty", "log_income", "unemployment")
          ),
          
          hr(),
          
          # Model type
          selectInput(
            "model_type",
            "Model Type:",
            choices = c(
              "OLS (Cross-Sectional)" = "ols",
              "Fixed Effects (Panel)" = "fe",
              "Random Effects (Panel)" = "re"
            ),
            selected = "ols"
          ),
          
          # Time period
          selectInput(
            "model_period",
            "Time Period:",
            choices = c(
              "Full Sample (2009-2023)" = "full",
              "Pre-Pandemic (2009-2019)" = "pre",
              "Pandemic Era (2020-2023)" = "post"
            ),
            selected = "full"
          ),
          
          hr(),
          
          actionButton(
            "run_regression",
            "Run Regression",
#             icon removed for debugging
            style = "width: 100%; background: #0033A0; color: white; 
                     border: none; padding: 12px; font-weight: 600;"
          )
        )
      ),
      
      # ========================================================================
      # MODEL OUTPUT PANEL
      # ========================================================================
      column(
        8,
        # Model Summary Card
        div(
          style = "background: white; padding: 25px; border-radius: 10px;
                   box-shadow: 0 2px 8px rgba(0,0,0,0.08); margin-bottom: 20px;",
          h4(
            icon("table"), " Regression Output",
            style = "margin-top: 0; color: #2c3e50;"
          ),
          hr(),
          
          # Placeholder for regression table
          div(
            style = "min-height: 350px; display: flex; align-items: center; 
                     justify-content: center; background: #f8f9fa; 
                     border-radius: 8px; border: 2px dashed #dee2e6;",
            div(
              style = "text-align: center;",
              icon("table", style = "font-size: 60px; color: #0033A0; margin-bottom: 20px;"),
              h4("Regression Coefficients Table", 
                 style = "color: #495057; margin-bottom: 10px;"),
              p("Estimates, standard errors, t-statistics, and p-values",
                style = "color: #6c757d; margin-bottom: 20px;"),
              tags$div(
                tags$strong("Table Columns:", style = "color: #0033A0;"),
                tags$ul(
                  style = "text-align: left; display: inline-block; color: #6c757d;",
                  tags$li("Variable name"),
                  tags$li("Coefficient estimate (β)"),
                  tags$li("Standard error"),
                  tags$li("t-statistic"),
                  tags$li("p-value & significance stars")
                )
              )
            )
          )
        ),
        
        # Model Fit Statistics
        fluidRow(
          column(
            3,
            div(
              style = "background: #0033A0; padding: 20px; border-radius: 8px;
                       color: white; text-align: center;",
              h6("R-Squared", style = "margin: 0 0 10px 0; opacity: 0.9;"),
              h3(textOutput("model_r2"), style = "margin: 0; font-size: 36px;"),
              p("Variance explained", style = "margin-top: 10px; font-size: 12px; opacity: 0.8;")
            )
          ),
          
          column(
            3,
            div(
              style = "background: #C41E3A; padding: 20px; border-radius: 8px;
                       color: white; text-align: center;",
              h6("Adj. R-Squared", style = "margin: 0 0 10px 0; opacity: 0.9;"),
              h3(textOutput("model_adj_r2"), style = "margin: 0; font-size: 36px;"),
              p("Adjusted for # vars", style = "margin-top: 10px; font-size: 12px; opacity: 0.8;")
            )
          ),
          
          column(
            3,
            div(
              style = "background: #17a2b8; padding: 20px; border-radius: 8px;
                       color: white; text-align: center;",
              h6("F-Statistic", style = "margin: 0 0 10px 0; opacity: 0.9;"),
              h3(textOutput("model_fstat"), style = "margin: 0; font-size: 36px;"),
              p("Model significance", style = "margin-top: 10px; font-size: 12px; opacity: 0.8;")
            )
          ),
          
          column(
            3,
            div(
              style = "background: #28a745; padding: 20px; border-radius: 8px;
                       color: white; text-align: center;",
              h6("Observations", style = "margin: 0 0 10px 0; opacity: 0.9;"),
              h3(textOutput("model_n"), style = "margin: 0; font-size: 36px;"),
              p("Sample size", style = "margin-top: 10px; font-size: 12px; opacity: 0.8;")
            )
          )
        )
      )
    ),
    
    # ========================================================================
    # COEFFICIENT INTERPRETATION CARDS
    # ========================================================================
    fluidRow(
      style = "margin-top: 30px;",
      column(
        12,
        div(
          style = "background: white; padding: 25px; border-radius: 10px;
                   box-shadow: 0 2px 8px rgba(0,0,0,0.08);",
          h4(
            icon("comment-dots"), " Plain-Language Interpretations",
            style = "margin-top: 0; color: #2c3e50;"
          ),
          p("Automated explanations of what each coefficient means for policy",
            style = "color: #6c757d; margin-bottom: 20px;"),
          hr(),
          
          htmlOutput("coefficient_cards")
        )
      )
    ),
    
    # ========================================================================
    # MODEL DIAGNOSTICS
    # ========================================================================
    fluidRow(
      style = "margin-top: 30px;",
      
      column(
        6,
        div(
          style = "background: white; padding: 25px; border-radius: 10px;
                   box-shadow: 0 2px 8px rgba(0,0,0,0.08);",
          h4(
            icon("chart-area"), " Residual Plot",
            style = "margin-top: 0; color: #2c3e50;"
          ),
          hr(),
          
          # Residual plot placeholder
          div(
            style = "height: 300px; display: flex; align-items: center; 
                     justify-content: center; background: #f8f9fa; 
                     border-radius: 8px; border: 2px dashed #dee2e6;",
            div(
              style = "text-align: center;",
              icon("braille", style = "font-size: 50px; color: #6f42c1; margin-bottom: 15px;"),
              h5("Residuals vs. Fitted Values", style = "color: #495057;"),
              p("Check for heteroscedasticity", style = "color: #6c757d; font-size: 13px;")
            )
          )
        )
      ),
      
      column(
        6,
        div(
          style = "background: white; padding: 25px; border-radius: 10px;
                   box-shadow: 0 2px 8px rgba(0,0,0,0.08);",
          h4(
            icon("chart-bar"), " Multicollinearity (VIF)",
            style = "margin-top: 0; color: #2c3e50;"
          ),
          hr(),
          
          # VIF table placeholder
          div(
            style = "height: 300px; display: flex; align-items: center; 
                     justify-content: center; background: #f8f9fa; 
                     border-radius: 8px; border: 2px dashed #dee2e6;",
            div(
              style = "text-align: center;",
              icon("exclamation-triangle", style = "font-size: 50px; color: #ffc107; margin-bottom: 15px;"),
              h5("Variance Inflation Factors", style = "color: #495057;"),
              p("VIF > 10 indicates multicollinearity concern", 
                style = "color: #6c757d; font-size: 13px;")
            )
          )
        )
      )
    ),
    
    # ========================================================================
    # MODEL COMPARISON
    # ========================================================================
    fluidRow(
      style = "margin-top: 30px;",
      column(
        12,
        div(
          style = "background: white; padding: 25px; border-radius: 10px;
                   box-shadow: 0 2px 8px rgba(0,0,0,0.08);",
          h4(
            icon("balance-scale"), " Model Comparison (Pre- vs. Post-COVID)",
            style = "margin-top: 0; color: #2c3e50;"
          ),
          p("Compare how relationships changed during the pandemic",
            style = "color: #6c757d; margin-bottom: 20px;"),
          hr(),
          
          # Comparison table placeholder
          div(
            style = "height: 250px; display: flex; align-items: center; 
                     justify-content: center; background: #f8f9fa; 
                     border-radius: 8px; border: 2px dashed #dee2e6;",
            div(
              style = "text-align: center;",
              icon("table", style = "font-size: 50px; color: #17a2b8; margin-bottom: 15px;"),
              h5("Side-by-Side Coefficient Comparison", style = "color: #495057;"),
              p("Pre-pandemic (2009-2019) vs. Pandemic (2020-2023)", 
                style = "color: #6c757d; font-size: 13px;")
            )
          )
        )
      )
    )
  )
)
