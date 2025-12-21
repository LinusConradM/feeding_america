# ==============================================================================
# UI MODULE: CORRELATION ANALYSIS
# ==============================================================================
# PURPOSE: Interactive bivariate and multivariate correlation analysis
# FEATURES: Scatter plots, correlation matrices, statistical tests, AI insights
# ==============================================================================

ui_correlation_analysis <- tabPanel(
  "Correlation Analysis",
  value = "correlation",
  
  fluidPage(
    # Page Header
    fluidRow(
      column(
        12,
        h2(
          icon("project-diagram"), " Correlation Analysis",
          style = "color: #2c3e50; font-weight: 600; margin-bottom: 10px;"
        ),
        p(
          "Explore relationships between food insecurity and socioeconomic variables",
          style = "color: #6c757d; font-size: 16px; margin-bottom: 30px;"
        )
      )
    ),
    
    # ========================================================================
    # ANALYSIS CONTROLS
    # ========================================================================
    fluidRow(
      column(
        4,
        div(
          style = "background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.08);",
          h4("Analysis Settings", style = "margin-top: 0; color: #0033A0;"),
          
          # Variable X selection
          selectInput(
            "corr_var_x",
            "X-Axis Variable:",
            choices = c(
              "Food Insecurity Rate" = "overall_food_insecurity_rate",
              "Child Food Insecurity Rate" = "child_food_insecurity_rate",
              "Poverty Rate" = "poverty_rate",
              "Median Income" = "median_income",
              "Unemployment Rate" = "unemployment_rate",
              "Cost per Meal" = "cost_per_meal"
            ),
            selected = "poverty_rate"
          ),
          
          # Variable Y selection
          selectInput(
            "corr_var_y",
            "Y-Axis Variable:",
            choices = c(
              "Food Insecurity Rate" = "overall_food_insecurity_rate",
              "Child Food Insecurity Rate" = "child_food_insecurity_rate",
              "Poverty Rate" = "poverty_rate",
              "Median Income" = "median_income",
              "Unemployment Rate" = "unemployment_rate",
              "Cost per Meal" = "cost_per_meal"
            ),
            selected = "overall_food_insecurity_rate"
          ),
          
          # Correlation method
          selectInput(
            "corr_method",
            "Correlation Method:",
            choices = c(
              "Pearson (linear)" = "pearson",
              "Spearman (rank)" = "spearman",
              "Kendall (rank)" = "kendall"
            ),
            selected = "pearson"
          ),
          
          hr(),
          
          # Year filter
          sliderInput(
            "corr_year",
            "Year:",
            min = 2009,
            max = 2023,
            value = 2023,
            step = 1,
            sep = ""
          ),
          
          # Geography filter
          selectInput(
            "corr_geography",
            "Geographic Level:",
            choices = c("All Counties", "State", "Region"),
            selected = "All Counties"
          ),
          
          # State filter (conditional)
          conditionalPanel(
            condition = "input.corr_geography == 'State'",
            selectInput(
              "corr_state",
              "Select State:",
              choices = c("All States" = "all"),
              selected = "all"
            )
          ),
          
          hr(),
          
          # Run analysis button
          actionButton(
            "run_correlation",
            "Run Analysis",
            icon = icon("play"),
            style = "width: 100%; background: #0033A0; color: white; border: none; padding: 12px;
                     font-weight: 600; border-radius: 8px;"
          )
        )
      ),
      
      column(
        8,
        # Scatter plot
        div(
          style = "background: white; padding: 25px; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.08);
                   margin-bottom: 20px;",
          h4(
            icon("chart-line"), " Bivariate Scatter Plot",
            style = "margin-top: 0; color: #2c3e50;"
          ),
          plotOutput("correlation_scatter", height = "450px")
        )
      )
    ),
    
    # ========================================================================
    # STATISTICS CARDS
    # ========================================================================
    fluidRow(
      style = "margin-top: 20px;",
      
      # Correlation coefficient
      column(
        3,
        div(
          style = "background: linear-gradient(135deg, #0033A0 0%, #003D82 100%);
                   padding: 25px; border-radius: 10px; color: white;
                   box-shadow: 0 4px 15px rgba(0, 51, 160, 0.3);",
          div(icon("link", style = "font-size: 2.5em; margin-bottom: 10px;")),
          h5("Correlation (r)", style = "margin: 10px 0 5px 0;"),
          h3(textOutput("bivariate_r"), style = "margin: 0; font-size: 36px;"),
          p("Strength of relationship", style = "margin-top: 10px; font-size: 13px; opacity: 0.9;")
        )
      ),
      
      # R-squared
      column(
        3,
        div(
          style = "background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
                   padding: 25px; border-radius: 10px; color: white;
                   box-shadow: 0 4px 15px rgba(40, 167, 69, 0.3);",
          div(icon("percentage", style = "font-size: 2.5em; margin-bottom: 10px;")),
          h5("R² (Variance)", style = "margin: 10px 0 5px 0;"),
          h3(textOutput("bivariate_r2"), style = "margin: 0; font-size: 36px;"),
          p("Variance explained", style = "margin-top: 10px; font-size: 13px; opacity: 0.9;")
        )
      ),
      
      # P-value
      column(
        3,
        div(
          style = "background: linear-gradient(135deg, #ffc107 0%, #ff9800 100%);
                   padding: 25px; border-radius: 10px; color: white;
                   box-shadow: 0 4px 15px rgba(255, 193, 7, 0.3);",
          div(icon("chart-line", style = "font-size: 2.5em; margin-bottom: 10px;")),
          h5("P-Value", style = "margin: 10px 0 5px 0;"),
          h3(textOutput("bivariate_p"), style = "margin: 0; font-size: 36px;"),
          p("Statistical significance", style = "margin-top: 10px; font-size: 13px; opacity: 0.9;")
        )
      ),
      
      # Sample size
      column(
        3,
        div(
          style = "background: linear-gradient(135deg, #6f42c1 0%, #563d7c 100%);
                   padding: 25px; border-radius: 10px; color: white;
                   box-shadow: 0 4px 15px rgba(111, 66, 193, 0.3);",
          div(icon("database", style = "font-size: 2.5em; margin-bottom: 10px;")),
          h5("Sample Size", style = "margin: 10px 0 5px 0;"),
          h3(textOutput("sample_size"), style = "margin: 0; font-size: 36px;"),
          p("Number of observations", style = "margin-top: 10px; font-size: 13px; opacity: 0.9;")
        )
      )
    ),
    
    # ========================================================================
    # INTERPRETATION CARDS
    # ========================================================================
    fluidRow(
      style = "margin-top: 20px;",
      
      column(
        4,
        div(
          style = "background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.08);",
          h5(icon("info-circle"), " Correlation Strength", style = "color: #0033A0; margin-top: 0;"),
          htmlOutput("correlation_strength")
        )
      ),
      
      column(
        4,
        div(
          style = "background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.08);",
          h5(icon("percentage"), " Variance Explained", style = "color: #28a745; margin-top: 0;"),
          htmlOutput("variance_explained")
        )
      ),
      
      column(
        4,
        div(
          style = "background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.08);",
          h5(icon("chart-bar"), " Significance", style = "color: #ffc107; margin-top: 0;"),
          htmlOutput("significance_label")
        )
      )
    ),
    
    # ========================================================================
    # CORRELATION MATRIX HEATMAP
    # ========================================================================
    fluidRow(
      style = "margin-top: 20px;",
      column(
        12,
        div(
          style = "background: white; padding: 25px; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.08);",
          h4(
            icon("th"), " Correlation Matrix",
            style = "margin-top: 0; color: #2c3e50;"
          ),
          p(
            "Pairwise correlations between all key variables",
            style = "color: #6c757d; margin-bottom: 20px;"
          ),
          plotOutput("correlation_matrix", height = "500px")
        )
      )
    ),
    
    # ========================================================================
    # AI-POWERED INTERPRETATION
    # ========================================================================
    fluidRow(
      style = "margin-top: 20px;",
      column(
        12,
        div(
          style = "background: linear-gradient(135deg, #06D6A0 0%, #04A777 100%);
                   padding: 30px; border-radius: 10px; color: white;
                   box-shadow: 0 4px 15px rgba(6, 214, 160, 0.3);",
          
          div(
            style = "display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;",
            h3(
              icon("robot"), " AI-Powered Interpretation",
              style = "margin: 0; font-weight: 600;"
            ),
            actionButton(
              "generate_correlation_interpretation",
              "Generate AI Interpretation",
              icon = icon("magic"),
              style = "background: rgba(255,255,255,0.2); color: white; border: 2px solid white;
                       padding: 10px 20px; font-weight: 600; border-radius: 8px;"
            )
          ),
          
          htmlOutput("correlation_ai_interpretation")
        )
      )
    )
  )
)