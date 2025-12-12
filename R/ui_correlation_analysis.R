# ==============================================================================
# UI MODULE: CORRELATION ANALYSIS
# ==============================================================================
# PURPOSE: Explore bivariate relationships and correlation patterns
# CAPABILITIES: Heatmaps, scatterplots, regression lines, time comparisons
# TEAM: Conrad, Sharon, Ryann, Alex
# ==============================================================================

ui_correlation_analysis <- tabPanel(
  "Correlation Analysis",
  value = "correlation",
  
  fluidPage(
    # Global Controls
    # global_controls_ui(),  # Removed to prevent duplicate IDs
    
    # Page Header
    fluidRow(
      column(
        12,
        h2(
          icon("project-diagram"), " Driver & Correlation Analysis",
          style = "color: #2c3e50; font-weight: 600; margin-bottom: 10px;"
        ),
        p(
          "Understand relationships between food insecurity and socioeconomic factors",
          style = "color: #6c757d; font-size: 16px; margin-bottom: 30px;"
        )
      )
    ),
    
    # ========================================================================
    # CORRELATION HEATMAP
    # ========================================================================
    fluidRow(
      column(
        3,
        div(
          style = "background: white; padding: 20px; border-radius: 10px;
                   box-shadow: 0 2px 8px rgba(0,0,0,0.08);",
          h5("Variable Selection", style = "margin-top: 0;"),
          
          checkboxGroupInput(
            "heatmap_vars",
            "Include in Heatmap:",
            choices = c(
              "Food Insecurity Rate" = "fi_rate",
              "Poverty Rate" = "poverty",
              "Median Income" = "income",
              "Unemployment Rate" = "unemployment",
              "Uninsured Rate" = "uninsured",
              "Cost per Meal" = "cost",
              "SNAP Participation" = "snap",
              "Education (College+)" = "education"
            ),
            selected = c("fi_rate", "poverty", "income", "unemployment")
          ),
          
          hr(),
          
          h5("Display Options"),
          selectInput(
            "correlation_method",
            "Method:",
            choices = c("Pearson" = "pearson", "Spearman" = "spearman"),
            selected = "pearson"
          ),
          
          checkboxInput("show_values", "Show Correlation Values", TRUE),
          checkboxInput("cluster_vars", "Cluster Variables", FALSE)
        )
      ),
      
      column(
        9,
        div(
          style = "background: white; padding: 25px; border-radius: 10px;
                   box-shadow: 0 2px 8px rgba(0,0,0,0.08);",
          h4(
            icon("th"), " Correlation Heatmap",
            style = "margin-top: 0; color: #2c3e50;"
          ),
          hr(),
          
          # Heatmap placeholder
          div(
            style = "height: 500px; display: flex; align-items: center; 
                     justify-content: center; background: #f8f9fa; 
                     border-radius: 8px; border: 2px dashed #dee2e6;",
            div(
              style = "text-align: center;",
              icon("th", style = "font-size: 60px; color: #0033A0; margin-bottom: 20px;"),
              h4("Interactive Correlation Matrix", 
                 style = "color: #495057; margin-bottom: 10px;"),
              p("Color-coded heatmap showing pairwise correlations",
                style = "color: #6c757d; margin-bottom: 20px;"),
              tags$div(
                tags$strong("Features:", style = "color: #0033A0;"),
                tags$ul(
                  style = "text-align: left; display: inline-block; color: #6c757d;",
                  tags$li("Custom variable selection (2-15 variables)"),
                  tags$li("Pearson or Spearman correlation"),
                  tags$li("Interactive tooltips with significance tests"),
                  tags$li("Hierarchical clustering option"),
                  tags$li("Export to PNG/CSV")
                )
              )
            )
          )
        )
      )
    ),
    
    # ========================================================================
    # BIVARIATE SCATTERPLOT EXPLORER
    # ========================================================================
    fluidRow(
      style = "margin-top: 30px;",
      column(
        12,
        div(
          style = "background: white; padding: 25px; border-radius: 10px;
                   box-shadow: 0 2px 8px rgba(0,0,0,0.08);",
          h4(
            icon("braille"), " Bivariate Scatterplot Explorer",
            style = "margin-top: 0; color: #2c3e50;"
          ),
          hr(),
          
          fluidRow(
            column(
              3,
              selectInput(
                "scatter_x",
                "X-Axis Variable:",
                choices = c(
                  "Poverty Rate" = "poverty",
                  "Median Income" = "income",
                  "Unemployment Rate" = "unemployment",
                  "Uninsured Rate" = "uninsured",
                  "SNAP Participation" = "snap"
                ),
                selected = "poverty"
              ),
              
              selectInput(
                "scatter_y",
                "Y-Axis Variable:",
                choices = c(
                  "Food Insecurity Rate" = "fi_rate",
                  "Child FI Rate" = "child_fi",
                  "Budget Shortfall" = "shortfall"
                ),
                selected = "fi_rate"
              ),
              
              selectInput(
                "scatter_color",
                "Color By:",
                choices = c(
                  "None" = "none",
                  "Region" = "region",
                  "Metro/Rural" = "metro",
                  "Year" = "year"
                ),
                selected = "region"
              ),
              
              hr(),
              
              checkboxInput("show_regression", "Show Regression Line", TRUE),
              checkboxInput("show_ci", "Show Confidence Interval", TRUE),
              checkboxInput("log_scale_x", "Log Scale (X-axis)", FALSE),
              checkboxInput("log_scale_y", "Log Scale (Y-axis)", FALSE)
            ),
            
            column(
              9,
              # Scatterplot placeholder
              div(
                style = "height: 450px; display: flex; align-items: center; 
                         justify-content: center; background: #f8f9fa; 
                         border-radius: 8px; border: 2px dashed #dee2e6;",
                div(
                  style = "text-align: center;",
                  icon("braille", style = "font-size: 60px; color: #C41E3A; margin-bottom: 20px;"),
                  h4("Interactive Scatterplot with Regression", 
                     style = "color: #495057; margin-bottom: 10px;"),
                  p("Explore bivariate relationships with statistical overlays",
                    style = "color: #6c757d;")
                )
              )
            )
          )
        )
      )
    ),
    
    # ========================================================================
    # CORRELATION STATISTICS CARDS
    # ========================================================================
    fluidRow(
      style = "margin-top: 20px;",
      
      column(
        3,
        div(
          style = "background: linear-gradient(135deg, #0033A0 0%, #003D82 100%);
                   padding: 25px; border-radius: 10px; color: white;
                   box-shadow: 0 4px 15px rgba(0, 51, 160, 0.3);",
          h5("Correlation (r)", style = "margin: 0 0 10px 0;"),
          h2(textOutput("bivariate_r"), style = "margin: 0; font-size: 48px;"),
          p(htmlOutput("correlation_strength"), 
            style = "margin-top: 15px; font-size: 14px; opacity: 0.9;")
        )
      ),
      
      column(
        3,
        div(
          style = "background: linear-gradient(135deg, #C41E3A 0%, #A01830 100%);
                   padding: 25px; border-radius: 10px; color: white;
                   box-shadow: 0 4px 15px rgba(196, 30, 58, 0.3);",
          h5("R-Squared (R²)", style = "margin: 0 0 10px 0;"),
          h2(textOutput("bivariate_r2"), style = "margin: 0; font-size: 48px;"),
          p(htmlOutput("variance_explained"), 
            style = "margin-top: 15px; font-size: 14px; opacity: 0.9;")
        )
      ),
      
      column(
        3,
        div(
          style = "background: linear-gradient(135deg, #17a2b8 0%, #138496 100%);
                   padding: 25px; border-radius: 10px; color: white;
                   box-shadow: 0 4px 15px rgba(23, 162, 184, 0.3);",
          h5("P-Value", style = "margin: 0 0 10px 0;"),
          h2(textOutput("bivariate_p"), style = "margin: 0; font-size: 48px;"),
          p(htmlOutput("significance_label"), 
            style = "margin-top: 15px; font-size: 14px; opacity: 0.9;")
        )
      ),
      
      column(
        3,
        div(
          style = "background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
                   padding: 25px; border-radius: 10px; color: white;
                   box-shadow: 0 4px 15px rgba(40, 167, 69, 0.3);",
          h5("Sample Size", style = "margin: 0 0 10px 0;"),
          h2(textOutput("sample_size"), style = "margin: 0; font-size: 48px;"),
          p("Counties in analysis", 
            style = "margin-top: 15px; font-size: 14px; opacity: 0.9;")
        )
      )
    ),
    
    # ========================================================================
    # YEAR-BY-YEAR CORRELATION COMPARISON
    # ========================================================================
    fluidRow(
      style = "margin-top: 30px;",
      column(
        12,
        div(
          style = "background: white; padding: 25px; border-radius: 10px;
                   box-shadow: 0 2px 8px rgba(0,0,0,0.08);",
          h4(
            icon("calendar-alt"), " Correlation Stability Over Time",
            style = "margin-top: 0; color: #2c3e50;"
          ),
          p("Track how the relationship between variables changes across years",
            style = "color: #6c757d; margin-bottom: 20px;"),
          hr(),
          
          # Time-series correlation plot placeholder
          div(
            style = "height: 300px; display: flex; align-items: center; 
                     justify-content: center; background: #f8f9fa; 
                     border-radius: 8px; border: 2px dashed #dee2e6;",
            div(
              style = "text-align: center;",
              icon("chart-line", style = "font-size: 50px; color: #6f42c1; margin-bottom: 15px;"),
              h4("Year-by-Year Correlation Trend (2009-2023)", 
                 style = "color: #495057; margin-bottom: 10px;"),
              p("Shows if relationships strengthen/weaken over time",
                style = "color: #6c757d;")
            )
          )
        )
      )
    )
  )
)
