# ==============================================================================
# UI MODULE: REGRESSION MODELS (CLEAN - NO MODEL TYPE DROPDOWN)
# ==============================================================================
# Model type is selected via submenu in navigation, not in the UI!
# ==============================================================================

ui_regression_models <- tabPanel(
  "Regression Models",
  value = "regression",
  
  fluidPage(
    # Page Header
    fluidRow(
      column(
        12,
        h2(
          icon("chart-line"), " Regression Models",
          style = "color: #2c3e50; font-weight: 600; margin-bottom: 10px;"
        ),
        p(
          "Build predictive models and understand relationships between variables",
          style = "color: #6c757d; font-size: 16px; margin-bottom: 30px;"
        )
      )
    ),
    
    # Model Configuration
    fluidRow(
      column(
        12,
        div(
          style = "background: white; padding: 20px; border-radius: 10px; 
                   box-shadow: 0 2px 8px rgba(0,0,0,0.08);",
          h4("Model Configuration", style = "margin-top: 0; color: #0033A0;"),
          
          fluidRow(
            column(
              6,
              # Dependent Variable
              selectInput(
                "reg_dependent",
                label = tags$b("Dependent Variable (Y):"),
                choices = c(
                  "Food Insecurity Rate" = "overall_food_insecurity_rate",
                  "Child Food Insecurity Rate" = "child_food_insecurity_rate"
                ),
                selected = "overall_food_insecurity_rate"
              )
            ),
            
            column(
              6,
              # Year
              sliderInput(
                "reg_year",
                label = tags$b("Year:"),
                min = 2009,
                max = 2023,
                value = 2023,
                step = 1,
                sep = "",
                width = "100%"
              )
            )
          ),
          
          hr(style = "margin: 20px 0;"),
          
          # Hidden input for model type (set by JavaScript submenu)
          tags$input(
            id = "reg_model_type",
            type = "text",
            value = "linear",
            style = "display: none;"
          ),
          
          # Independent Variables
          selectInput(
            "reg_independent",
            label = tags$b("Independent Variables (X):"),
            choices = NULL,
            selected = NULL,
            multiple = TRUE,
            selectize = TRUE,
            width = "100%"
          ),
          
          tags$p(
            "Select one or more predictors (type to search). Model type is selected from the Analysis menu.",
            style = "color: #6c757d; font-size: 13px; margin-top: -10px; margin-bottom: 15px;"
          ),
          
          # Scale Variables
          checkboxInput(
            "reg_scale",
            label = "Scale variables (standardize)",
            value = FALSE
          ),
          
          tags$p(
            icon("info-circle"), " Scaling converts all variables to z-scores (mean=0, SD=1)",
            style = "color: #6c757d; font-size: 11px; margin-top: -10px;"
          ),
          
          hr(style = "margin: 20px 0;"),
          
          # Build Model Button
          actionButton(
            "build_model",
            label = "Build Model",
            icon = icon("cogs"),
            style = "width: 100%; background: #0033A0; color: white; border: none; 
                     padding: 12px; font-weight: 600; border-radius: 8px;
                     font-size: 16px; margin-top: 10px;"
          ),
          
          tags$p(
            icon("info-circle"), " Select variables and model type from the Analysis menu, then click Build Model",
            style = "color: #6c757d; font-size: 12px; margin-top: 10px; text-align: center;"
          )
        )
      )
    ),
    
    # Results Section
    fluidRow(
      style = "margin-top: 20px;",
      column(12,
        div(style = "background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); margin-bottom: 20px;",
          h4(icon("calculator"), " Model Equation", style = "margin-top: 0; color: #2c3e50;"),
          uiOutput("model_equation")
        ),
        div(style = "background: white; padding: 25px; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); margin-bottom: 20px;",
          h4(icon("table"), " Model Summary", style = "margin-top: 0; color: #2c3e50;"),
          p("Detailed regression output and statistics", style = "color: #6c757d; margin-bottom: 15px;"),
          verbatimTextOutput("model_summary")
        ),
        div(style = "background: white; padding: 25px; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.08);",
          h4(icon("chart-area"), " Fitted vs. Actual Values", style = "margin-top: 0; color: #2c3e50;"),
          plotOutput("fitted_vs_actual", height = "400px")
        )
      )
    ),
    
    # Metrics
    fluidRow(style = "margin-top: 20px;",
      column(3, div(style = "background: linear-gradient(135deg, #0033A0 0%, #003D82 100%); padding: 25px; border-radius: 10px; color: white; box-shadow: 0 4px 15px rgba(0, 51, 160, 0.3);",
        div(icon("bullseye", style = "font-size: 2.5em; margin-bottom: 10px;")),
        h5("R²", style = "margin: 10px 0 5px 0;"),
        h3(textOutput("model_r2"), style = "margin: 0; font-size: 36px;"),
        p("Variance explained", style = "margin-top: 10px; font-size: 13px; opacity: 0.9;")
      )),
      column(3, div(style = "background: linear-gradient(135deg, #28a745 0%, #20c997 100%); padding: 25px; border-radius: 10px; color: white; box-shadow: 0 4px 15px rgba(40, 167, 69, 0.3);",
        div(icon("balance-scale", style = "font-size: 2.5em; margin-bottom: 10px;")),
        h5("Adj. R²", style = "margin: 10px 0 5px 0;"),
        h3(textOutput("model_adj_r2"), style = "margin: 0; font-size: 36px;"),
        p("Adjusted for predictors", style = "margin-top: 10px; font-size: 13px; opacity: 0.9;")
      )),
      column(3, div(style = "background: linear-gradient(135deg, #ffc107 0%, #ff9800 100%); padding: 25px; border-radius: 10px; color: white; box-shadow: 0 4px 15px rgba(255, 193, 7, 0.3);",
        div(icon("chart-bar", style = "font-size: 2.5em; margin-bottom: 10px;")),
        h5("F-Statistic", style = "margin: 10px 0 5px 0;"),
        h3(textOutput("model_fstat"), style = "margin: 0; font-size: 36px;"),
        p("Model significance", style = "margin-top: 10px; font-size: 13px; opacity: 0.9;")
      )),
      column(3, div(style = "background: linear-gradient(135deg, #6f42c1 0%, #563d7c 100%); padding: 25px; border-radius: 10px; color: white; box-shadow: 0 4px 15px rgba(111, 66, 193, 0.3);",
        div(icon("database", style = "font-size: 2.5em; margin-bottom: 10px;")),
        h5("Observations", style = "margin: 10px 0 5px 0;"),
        h3(textOutput("model_n"), style = "margin: 0; font-size: 36px;"),
        p("Sample size", style = "margin-top: 10px; font-size: 13px; opacity: 0.9;")
      ))
    ),
    
    # Multicollinearity
    fluidRow(style = "margin-top: 20px;",
      column(6, div(style = "background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%); padding: 25px; border-radius: 10px; color: white; box-shadow: 0 4px 15px rgba(231, 76, 60, 0.3);",
        div(icon("exclamation-triangle", style = "font-size: 2.5em; margin-bottom: 10px;")),
        h5("Condition Index", style = "margin: 10px 0 5px 0;"),
        h3(textOutput("model_condition_index"), style = "margin: 0; font-size: 36px;"),
        p("Multicollinearity indicator", style = "margin-top: 10px; font-size: 13px; opacity: 0.9;"),
        p(HTML("<small>< 10: Good | 10-30: Moderate | > 30: Severe</small>"), style = "margin-top: 5px; font-size: 11px; opacity: 0.8;")
      )),
      column(6, div(style = "background: linear-gradient(135deg, #9b59b6 0%, #8e44ad 100%); padding: 25px; border-radius: 10px; color: white; box-shadow: 0 4px 15px rgba(155, 89, 182, 0.3);",
        div(icon("code-branch", style = "font-size: 2.5em; margin-bottom: 10px;")),
        h5("Max VIF", style = "margin: 10px 0 5px 0;"),
        h3(textOutput("model_max_vif"), style = "margin: 0; font-size: 36px;"),
        p("Variance inflation factor", style = "margin-top: 10px; font-size: 13px; opacity: 0.9;"),
        p(HTML("<small>< 5: Good | 5-10: Moderate | > 10: High</small>"), style = "margin-top: 5px; font-size: 11px; opacity: 0.8;")
      ))
    ),
    
    # Coefficients
    fluidRow(style = "margin-top: 20px;",
      column(12, div(style = "background: white; padding: 25px; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.08);",
        h4(icon("list-ol"), " Coefficient Interpretations", style = "margin-top: 0; color: #2c3e50; margin-bottom: 20px;"),
        uiOutput("coefficient_cards")
      ))
    ),
    
    # Diagnostics
    fluidRow(style = "margin-top: 20px;",
      column(6, div(style = "background: white; padding: 25px; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.08);",
        h4(icon("chart-area"), " Residuals vs. Fitted", style = "margin-top: 0; color: #2c3e50;"),
        p("Check for homoscedasticity (constant variance)", style = "color: #6c757d; margin-bottom: 15px; font-size: 13px;"),
        plotOutput("residuals_fitted", height = "350px")
      )),
      column(6, div(style = "background: white; padding: 25px; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.08);",
        h4(icon("chart-line"), " Normal Q-Q Plot", style = "margin-top: 0; color: #2c3e50;"),
        p("Check for normality of residuals", style = "color: #6c757d; margin-bottom: 15px; font-size: 13px;"),
        plotOutput("qq_plot", height = "350px")
      ))
    ),
    
    # AI
    fluidRow(style = "margin-top: 20px; margin-bottom: 30px;",
      column(12, div(style = "background: linear-gradient(135deg, #6c5ce7 0%, #a29bfe 100%); padding: 30px; border-radius: 10px; color: white; box-shadow: 0 4px 15px rgba(108, 92, 231, 0.3);",
        div(style = "display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; flex-wrap: wrap;",
          h3(icon("brain"), " AI Model Interpretation", style = "margin: 0; font-weight: 600;"),
          actionButton("generate_model_interpretation", label = "Generate AI Analysis", icon = icon("magic"),
            style = "background: rgba(255,255,255,0.2); color: white; border: 2px solid white; padding: 10px 20px; font-weight: 600; border-radius: 8px; margin-top: 10px;")
        ),
        htmlOutput("model_ai_interpretation")
      ))
    )
  )
)