# ==============================================================================
# UI MODULE: TIME-SERIES & TREND EXPLORATION
# ==============================================================================
# PURPOSE: Understand dynamics, shocks, and temporal patterns
# CAPABILITIES: Multi-level trends, YoY changes, COVID comparisons, leaderboards
# TEAM: Conrad, Sharon, Ryann, Alex
# ==============================================================================

ui_timeseries_explorer <- tabPanel(
  "Time-Series Explorer",
  value = "timeseries",
  
  fluidPage(
    # Page Header
    fluidRow(
      column(
        12,
        h2(
          icon("history"), " Time-Series & Trend Exploration",
          style = "color: #2c3e50; font-weight: 600; margin-bottom: 10px;"
        ),
        p(
          "Analyze temporal dynamics, year-over-year changes, and economic shocks",
          style = "color: #6c757d; font-size: 16px; margin-bottom: 30px;"
        )
      )
    ),
    
    # ========================================================================
    # MULTI-LEVEL TREND VIEWER
    # ========================================================================
    fluidRow(
      column(
        3,
        div(
          style = "background: white; padding: 20px; border-radius: 10px;
                   box-shadow: 0 2px 8px rgba(0,0,0,0.08);",
          h5("Trend Configuration", style = "margin-top: 0;"),
          
          selectInput(
            "trend_level",
            "Geographic Level:",
            choices = c(
              "National" = "national",
              "State" = "state",
              "County" = "county"
            ),
            selected = "national"
          ),
          
          conditionalPanel(
            condition = "input.trend_level == 'state'",
            selectInput(
              "trend_state",
              "Select State:",
              choices = c("All States", state.abb),
              selected = "All States"
            )
          ),
          
          conditionalPanel(
            condition = "input.trend_level == 'county'",
            selectInput(
              "trend_county",
              "Select County:",
              choices = "Select after running",
              selected = NULL
            )
          ),
          
          hr(),
          
          selectInput(
            "trend_variable",
            "Variable to Plot:",
            choices = c(
              "Food Insecurity Rate" = "fi_rate",
              "Child FI Rate" = "child_fi",
              "Poverty Rate" = "poverty",
              "Unemployment Rate" = "unemployment",
              "Median Income" = "income"
            ),
            selected = "fi_rate"
          ),
          
          hr(),
          
          checkboxInput("show_covid_bands", "Highlight COVID Period", TRUE),
          checkboxInput("show_recession_bands", "Highlight Great Recession", TRUE),
          checkboxInput("show_trend_line", "Show Trend Line", FALSE)
        )
      ),
      
      column(
        9,
        div(
          style = "background: white; padding: 25px; border-radius: 10px;
                   box-shadow: 0 2px 8px rgba(0,0,0,0.08);",
          h4(
            icon("chart-line"), " Time-Series Trend (2009-2023)",
            style = "margin-top: 0; color: #2c3e50;"
          ),
          hr(),
          
          # Trend plot placeholder
          div(
            style = "height: 450px; display: flex; align-items: center; 
                     justify-content: center; background: #f8f9fa; 
                     border-radius: 8px; border: 2px dashed #dee2e6;",
            div(
              style = "text-align: center;",
              icon("chart-area", style = "font-size: 60px; color: #0033A0; margin-bottom: 20px;"),
              h4("Interactive Time-Series Chart", 
                 style = "color: #495057; margin-bottom: 10px;"),
              p("15-year trend with event annotations and optional smoothing",
                style = "color: #6c757d;")
            )
          )
        )
      )
    ),
    
    # ========================================================================
    # YEAR-OVER-YEAR CHANGE ANALYSIS
    # ========================================================================
    fluidRow(
      style = "margin-top: 30px;",
      column(
        12,
        div(
          style = "background: white; padding: 25px; border-radius: 10px;
                   box-shadow: 0 2px 8px rgba(0,0,0,0.08);",
          h4(
            icon("exchange-alt"), " Year-over-Year Change Analysis",
            style = "margin-top: 0; color: #2c3e50;"
          ),
          p("Track annual growth/decline rates across the time series",
            style = "color: #6c757d; margin-bottom: 20px;"),
          hr(),
          
          # YoY change plot placeholder
          div(
            style = "height: 300px; display: flex; align-items: center; 
                     justify-content: center; background: #f8f9fa; 
                     border-radius: 8px; border: 2px dashed #dee2e6;",
            div(
              style = "text-align: center;",
              icon("chart-bar", style = "font-size: 50px; color: #C41E3A; margin-bottom: 15px;"),
              h5("Annual Percentage Change", style = "color: #495057;"),
              p("Bar chart showing YoY % change, colored by direction", 
                style = "color: #6c757d; font-size: 13px;")
            )
          )
        )
      )
    ),
    
    # ========================================================================
    # COVID-19 IMPACT COMPARISON
    # ========================================================================
    fluidRow(
      style = "margin-top: 30px;",
      column(
        12,
        div(
          style = "background: white; padding: 25px; border-radius: 10px;
                   box-shadow: 0 2px 8px rgba(0,0,0,0.08);",
          h4(
            icon("virus"), " COVID-19 Impact Comparison",
            style = "margin-top: 0; color: #2c3e50;"
          ),
          hr(),
          
          fluidRow(
            column(
              4,
              div(
                style = "background: #f8f9fa; padding: 20px; border-radius: 8px;
                         border-left: 4px solid #0033A0;",
                h5("Pre-Pandemic Baseline", style = "color: #0033A0; margin-top: 0;"),
                h3(textOutput("pre_covid_avg"), style = "font-size: 36px; margin: 10px 0;"),
                p("Average FI Rate (2009-2019)", style = "color: #6c757d; font-size: 14px;")
              )
            ),
            
            column(
              4,
              div(
                style = "background: #f8f9fa; padding: 20px; border-radius: 8px;
                         border-left: 4px solid #C41E3A;",
                h5("COVID Years", style = "color: #C41E3A; margin-top: 0;"),
                h3(textOutput("covid_avg"), style = "font-size: 36px; margin: 10px 0;"),
                p("Average FI Rate (2020-2021)", style = "color: #6c757d; font-size: 14px;")
              )
            ),
            
            column(
              4,
              div(
                style = "background: #f8f9fa; padding: 20px; border-radius: 8px;
                         border-left: 4px solid #28a745;",
                h5("Post-Pandemic", style = "color: #28a745; margin-top: 0;"),
                h3(textOutput("post_covid_avg"), style = "font-size: 36px; margin: 10px 0;"),
                p("Average FI Rate (2022-2023)", style = "color: #6c757d; font-size: 14px;")
              )
            )
          )
        )
      )
    ),
    
    # ========================================================================
    # GROWTH/DECLINE LEADERBOARDS
    # ========================================================================
    fluidRow(
      style = "margin-top: 30px;",
      
      column(
        6,
        div(
          style = "background: white; padding: 25px; border-radius: 10px;
                   box-shadow: 0 2px 8px rgba(0,0,0,0.08);",
          h4(
            icon("trophy"), " Most Improved Counties (2009-2023)",
            style = "margin-top: 0; color: #28a745;"
          ),
          p("Largest decreases in food insecurity rate",
            style = "color: #6c757d; margin-bottom: 15px;"),
          hr(),
          
          # Top improvers table placeholder
          div(
            style = "min-height: 300px; display: flex; align-items: center; 
                     justify-content: center; background: #f8f9fa; 
                     border-radius: 8px; border: 2px dashed #dee2e6;",
            div(
              style = "text-align: center;",
              icon("caret-down", style = "font-size: 50px; color: #28a745; margin-bottom: 15px;"),
              h5("Top 20 Counties", style = "color: #495057;"),
              p("Ranked by absolute percentage point decrease", 
                style = "color: #6c757d; font-size: 13px;")
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
            icon("exclamation-triangle"), " Worst Deteriorations (2009-2023)",
            style = "margin-top: 0; color: #dc3545;"
          ),
          p("Largest increases in food insecurity rate",
            style = "color: #6c757d; margin-bottom: 15px;"),
          hr(),
          
          # Top deteriorations table placeholder
          div(
            style = "min-height: 300px; display: flex; align-items: center; 
                     justify-content: center; background: #f8f9fa; 
                     border-radius: 8px; border: 2px dashed #dee2e6;",
            div(
              style = "text-align: center;",
              icon("caret-up", style = "font-size: 50px; color: #dc3545; margin-bottom: 15px;"),
              h5("Top 20 Counties", style = "color: #495057;"),
              p("Ranked by absolute percentage point increase", 
                style = "color: #6c757d; font-size: 13px;")
            )
          )
        )
      )
    ),
    
    # ========================================================================
    # VOLATILITY ANALYSIS
    # ========================================================================
    fluidRow(
      style = "margin-top: 30px;",
      column(
        12,
        div(
          style = "background: white; padding: 25px; border-radius: 10px;
                   box-shadow: 0 2px 8px rgba(0,0,0,0.08);",
          h4(
            icon("wave-square"), " Volatility Analysis",
            style = "margin-top: 0; color: #2c3e50;"
          ),
          p("Identify counties with most/least stable food insecurity rates over time",
            style = "color: #6c757d; margin-bottom: 20px;"),
          hr(),
          
          fluidRow(
            column(
              6,
              div(
                style = "background: #f8f9fa; padding: 20px; border-radius: 8px; text-align: center;",
                icon("chart-line", style = "font-size: 40px; color: #ffc107; margin-bottom: 10px;"),
                h5("Highest Volatility", style = "color: #495057; margin: 10px 0;"),
                p("Counties with largest year-to-year swings", 
                  style = "color: #6c757d; font-size: 14px; margin: 0;")
              )
            ),
            
            column(
              6,
              div(
                style = "background: #f8f9fa; padding: 20px; border-radius: 8px; text-align: center;",
                icon("minus", style = "font-size: 40px; color: #17a2b8; margin-bottom: 10px;"),
                h5("Most Stable", style = "color: #495057; margin: 10px 0;"),
                p("Counties with consistent rates over time", 
                  style = "color: #6c757d; font-size: 14px; margin: 0;")
              )
            )
          )
        )
      )
    )
  )
)
