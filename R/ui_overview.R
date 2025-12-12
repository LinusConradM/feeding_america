# ==============================================================================
# UI MODULE: EXECUTIVE OVERVIEW - WITH BEAUTIFUL GRADIENT CARDS
# ==============================================================================
# PURPOSE: High-level dashboard for executives and stakeholders
# FEATURES: KPIs, trends, rankings, demographics, geography, AI insights
# ==============================================================================

ui_overview <- tabPanel(
  title = "Executive Overview",
  value = "overview",
  icon = icon("home"),
  
  # Beautiful KPI Cards CSS
  tags$head(
    tags$link(rel = "stylesheet", href = "beautiful_kpi_cards.css")
  ),
  
  fluidPage(
    # Page Header
    div(
      style = "margin-bottom: 30px;",
      h1(
        icon("chart-line"), 
        "Executive Overview",
        style = "color: #1E3A5F; font-weight: 700; border-bottom: 3px solid #2A9D8F; padding-bottom: 12px;"
      ),
      p(
        "Comprehensive snapshot of U.S. food insecurity (2009-2023)",
        style = "color: #6C757D; font-size: 16px; margin-top: 8px;"
      )
    ),
    
    # ========================================================================
    # YEAR SELECTOR
    # ========================================================================
    fluidRow(
      column(
        width = 12,
        div(
          style = "background: white; padding: 16px 24px; border-radius: 12px; 
                   box-shadow: 0 2px 8px rgba(0,0,0,0.08); margin-bottom: 24px;",
          fluidRow(
            column(
              width = 6,
              selectInput(
                "overview_year_selector",
                label = tags$span(icon("calendar-alt"), " Select Year for Analysis"),
                choices = 2009:2023,
                selected = 2023,
                width = "100%"
              )
            ),
            column(
              width = 6,
              div(
                style = "padding-top: 25px;",
                actionButton(
                  "refresh_overview",
                  "Refresh Dashboard",
                  icon = icon("redo"),
                  class = "btn-primary",
                  style = "margin-right: 10px;"
                ),
                actionButton(
                  "generate_summary",
                  "Generate AI Summary",
                  icon = icon("robot"),
                  class = "btn-success"
                )
              )
            )
          )
        )
      )
    ),
    
    # ========================================================================
    # BEAUTIFUL GRADIENT KPI CARDS
    # ========================================================================
    beautiful_kpi_cards,
    
    # ========================================================================
    # AI SUMMARY (Conditional Display)
    # ========================================================================
    uiOutput("ai_executive_summary"),
    
    # ========================================================================
    # NATIONAL TREND & REGIONAL COMPARISON
    # ========================================================================
    fluidRow(
      # National Trend Chart
      column(
        width = 8,
        div(
          style = "background: white; padding: 20px; border-radius: 12px; 
                   box-shadow: 0 2px 12px rgba(0,0,0,0.08); margin-bottom: 24px;",
          h3(
            icon("chart-line"), 
            "National Trend (2009-2023)",
            style = "color: #1E3A5F; margin-top: 0;"
          ),
          plotOutput("national_trend", height = "400px")
        )
      ),
      
      # Regional Comparison
      column(
        width = 4,
        div(
          style = "background: white; padding: 20px; border-radius: 12px; 
                   box-shadow: 0 2px 12px rgba(0,0,0,0.08); margin-bottom: 24px;",
          h3(
            icon("map"), 
            "Regional Comparison",
            style = "color: #1E3A5F; margin-top: 0;"
          ),
          plotOutput("regional_comparison", height = "400px")
        )
      )
    ),
    
    # ========================================================================
    # KEY STATISTICS PANEL
    # ========================================================================
    fluidRow(
      column(
        width = 12,
        div(
          style = "background: linear-gradient(135deg, #1E3A5F 0%, #2C5282 100%); 
                   padding: 24px; border-radius: 12px; margin-bottom: 24px; color: white;
                   box-shadow: 0 4px 16px rgba(0,0,0,0.12);",
          h3(
            icon("info-circle"), 
            "Key Statistics",
            style = "color: white; margin-top: 0; border-bottom: 2px solid rgba(255,255,255,0.3); padding-bottom: 12px;"
          ),
          fluidRow(
            column(
              width = 3,
              div(
                style = "text-align: center; padding: 16px; background: rgba(255,255,255,0.1); 
                         border-radius: 8px; backdrop-filter: blur(10px);",
                h4("MEDIAN FI RATE", style = "color: rgba(255,255,255,0.9); font-size: 13px;"),
                h2(textOutput("stat_median_fi"), style = "color: white; margin: 8px 0;"),
                p("Middle value", style = "color: rgba(255,255,255,0.7); font-size: 12px; margin: 0;")
              )
            ),
            column(
              width = 3,
              div(
                style = "text-align: center; padding: 16px; background: rgba(255,255,255,0.1); 
                         border-radius: 8px; backdrop-filter: blur(10px);",
                h4("RANGE", style = "color: rgba(255,255,255,0.9); font-size: 13px;"),
                h2(textOutput("stat_range_fi"), style = "color: white; margin: 8px 0;"),
                p("Min to Max", style = "color: rgba(255,255,255,0.7); font-size: 12px; margin: 0;")
              )
            ),
            column(
              width = 3,
              div(
                style = "text-align: center; padding: 16px; background: rgba(255,255,255,0.1); 
                         border-radius: 8px; backdrop-filter: blur(10px);",
                h4("STD DEVIATION", style = "color: rgba(255,255,255,0.9); font-size: 13px;"),
                h2(textOutput("stat_sd_fi"), style = "color: white; margin: 8px 0;"),
                p("Variability", style = "color: rgba(255,255,255,0.7); font-size: 12px; margin: 0;")
              )
            ),
            column(
              width = 3,
              div(
                style = "text-align: center; padding: 16px; background: rgba(255,255,255,0.1); 
                         border-radius: 8px; backdrop-filter: blur(10px);",
                h4("ABOVE AVERAGE", style = "color: rgba(255,255,255,0.9); font-size: 13px;"),
                h2(textOutput("stat_above_avg"), style = "color: white; margin: 8px 0;"),
                p("Counties", style = "color: rgba(255,255,255,0.7); font-size: 12px; margin: 0;")
              )
            )
          )
        )
      )
    ),
    
    # ========================================================================
    # TOP 10 & BOTTOM 10 STATES
    # ========================================================================
    fluidRow(
      # Top 10 (Highest FI)
      column(
        width = 6,
        div(
          style = "background: white; padding: 20px; border-radius: 12px; 
                   box-shadow: 0 2px 12px rgba(0,0,0,0.08); margin-bottom: 24px;",
          h3(
            icon("exclamation-triangle"), 
            "Top 10 States - Highest Food Insecurity",
            style = "color: #E63946; margin-top: 0;"
          ),
          DT::dataTableOutput("top_10_states")
        )
      ),
      
      # Bottom 10 (Lowest FI)
      column(
        width = 6,
        div(
          style = "background: white; padding: 20px; border-radius: 12px; 
                   box-shadow: 0 2px 12px rgba(0,0,0,0.08); margin-bottom: 24px;",
          h3(
            icon("trophy"), 
            "Bottom 10 States - Lowest Food Insecurity",
            style = "color: #06D6A0; margin-top: 0;"
          ),
          DT::dataTableOutput("bottom_10_states")
        )
      )
    ),
    
    # ========================================================================
    # DEMOGRAPHIC DISPARITIES & STATE MAP
    # ========================================================================
    fluidRow(
      # Demographic Disparities
      column(
        width = 6,
        div(
          style = "background: white; padding: 20px; border-radius: 12px; 
                   box-shadow: 0 2px 12px rgba(0,0,0,0.08); margin-bottom: 24px;",
          h3(
            icon("users"), 
            "Demographic Disparities",
            style = "color: #1E3A5F; margin-top: 0;"
          ),
          plotOutput("demographic_chart", height = "400px")
        )
      ),
      
      # State-Level Map
      column(
        width = 6,
        div(
          style = "background: white; padding: 20px; border-radius: 12px; 
                   box-shadow: 0 2px 12px rgba(0,0,0,0.08); margin-bottom: 24px;",
          h3(
            icon("map-marked-alt"), 
            "Geographic Distribution",
            style = "color: #1E3A5F; margin-top: 0;"
          ),
          plotOutput("state_map", height = "400px")
        )
      )
    ),
    
    # ========================================================================
    # URBAN VS RURAL COMPARISON
    # ========================================================================
    fluidRow(
      column(
        width = 12,
        div(
          style = "background: white; padding: 20px; border-radius: 12px; 
                   box-shadow: 0 2px 12px rgba(0,0,0,0.08); margin-bottom: 24px;",
          h3(
            icon("city"), 
            "Urban vs Rural Food Insecurity",
            style = "color: #1E3A5F; margin-top: 0;"
          ),
          plotOutput("urban_rural_comparison", height = "300px")
        )
      )
    ),
    
    # Footer
    hr(),
    div(
      style = "text-align: center; color: #6C757D; padding: 20px;",
      p(
        icon("info-circle"),
        "Data sources: Feeding America Map the Meal Gap, U.S. Census Bureau (ACS)",
        style = "margin: 0;"
      ),
      p(
        "Last updated:",
        Sys.Date(),
        style = "margin: 8px 0 0 0; font-size: 14px;"
      )
    )
  )
)
