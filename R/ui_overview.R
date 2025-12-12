# ==============================================================================
# UI MODULE: EXECUTIVE OVERVIEW
# ==============================================================================
# PURPOSE: Executive-level dashboard - answer "What is happening?"
# FEATURES: KPIs, trend visualization, insight callouts
# TEAM: Conrad, Sharon, Ryann, Alex
# ==============================================================================

ui_overview <- tabPanel(
  "Executive Overview",
  value = "overview",
  
  fluidPage(
    # Global Controls
    global_controls_ui(),
    
    # Page Title
    fluidRow(
      style = "margin-bottom: 20px;",
      column(
        12,
        h2(
          "Executive Overview Dashboard",
          style = "color: #2c3e50; font-weight: 600; margin-bottom: 10px;"
        ),
        p(
          "High-level metrics and trends at a glance",
          style = "color: #6c757d; font-size: 16px;"
        )
      )
    ),
    
    # ========================================================================
    # KPI ROW 1: FOOD INSECURITY METRICS
    # ========================================================================
    fluidRow(
      style = "margin-bottom: 20px;",
      
      column(
        3,
        div(
          class = "kpi-box",
          style = "background: white; padding: 25px; border-radius: 10px;
                   box-shadow: 0 2px 8px rgba(0,0,0,0.08); text-align: center;
                   border-top: 4px solid #dc3545; height: 180px;
                   transition: transform 0.2s;",
          div(icon("utensils", style = "font-size: 2.5em; color: #dc3545; margin-bottom: 15px;")),
          div("National FI Rate", style = "font-size: 14px; color: #6c757d; margin-bottom: 8px; font-weight: 600;"),
          div(textOutput("kpi_national_fi_rate"), style = "font-size: 40px; font-weight: 700; color: #212529;"),
          div(uiOutput("kpi_fi_rate_change"), style = "font-size: 13px; margin-top: 10px;")
        )
      ),
      
      column(
        3,
        div(
          class = "kpi-box",
          style = "background: white; padding: 25px; border-radius: 10px;
                   box-shadow: 0 2px 8px rgba(0,0,0,0.08); text-align: center;
                   border-top: 4px solid #ffc107; height: 180px;
                   transition: transform 0.2s;",
          div(icon("users", style = "font-size: 2.5em; color: #ffc107; margin-bottom: 15px;")),
          div("Food Insecure Persons", style = "font-size: 14px; color: #6c757d; margin-bottom: 8px; font-weight: 600;"),
          div(textOutput("kpi_total_food_insecure"), style = "font-size: 40px; font-weight: 700; color: #212529;"),
          div(uiOutput("kpi_fi_persons_change"), style = "font-size: 13px; margin-top: 10px;")
        )
      ),
      
      column(
        3,
        div(
          class = "kpi-box",
          style = "background: white; padding: 25px; border-radius: 10px;
                   box-shadow: 0 2px 8px rgba(0,0,0,0.08); text-align: center;
                   border-top: 4px solid #17a2b8; height: 180px;
                   transition: transform 0.2s;",
          div(icon("user", style = "font-size: 2.5em; color: #17a2b8; margin-bottom: 15px;")),
          div("Child FI Rate", style = "font-size: 14px; color: #6c757d; margin-bottom: 8px; font-weight: 600;"),
          div(textOutput("kpi_child_fi_rate"), style = "font-size: 40px; font-weight: 700; color: #212529;"),
          div(uiOutput("kpi_child_fi_change"), style = "font-size: 13px; margin-top: 10px;")
        )
      ),
      
      column(
        3,
        div(
          class = "kpi-box",
          style = "background: white; padding: 25px; border-radius: 10px;
                   box-shadow: 0 2px 8px rgba(0,0,0,0.08); text-align: center;
                   border-top: 4px solid #28a745; height: 180px;
                   transition: transform 0.2s;",
          div(icon("money-bill-wave", style = "font-size: 2.5em; color: #28a745; margin-bottom: 15px;")),
          div("Avg. Cost per Meal", style = "font-size: 14px; color: #6c757d; margin-bottom: 8px; font-weight: 600;"),
          div(textOutput("kpi_avg_cost_per_meal"), style = "font-size: 40px; font-weight: 700; color: #212529;"),
          div(uiOutput("kpi_cost_change"), style = "font-size: 13px; margin-top: 10px;")
        )
      )
    ),
    
    # ========================================================================
    # KPI ROW 2: SOCIOECONOMIC DRIVERS
    # ========================================================================
    fluidRow(
      style = "margin-bottom: 30px;",
      
      column(
        3,
        div(
          class = "kpi-box",
          style = "background: white; padding: 25px; border-radius: 10px;
                   box-shadow: 0 2px 8px rgba(0,0,0,0.08); text-align: center;
                   border-top: 4px solid #6f42c1; height: 180px;
                   transition: transform 0.2s;",
          div(icon("usd", style = "font-size: 2.5em; color: #6f42c1; margin-bottom: 15px;")),
          div("National Poverty Rate", style = "font-size: 14px; color: #6c757d; margin-bottom: 8px; font-weight: 600;"),
          div(textOutput("kpi_poverty_rate"), style = "font-size: 40px; font-weight: 700; color: #212529;"),
          div(uiOutput("kpi_poverty_change"), style = "font-size: 13px; margin-top: 10px;")
        )
      ),
      
      column(
        3,
        div(
          class = "kpi-box",
          style = "background: white; padding: 25px; border-radius: 10px;
                   box-shadow: 0 2px 8px rgba(0,0,0,0.08); text-align: center;
                   border-top: 4px solid #20c997; height: 180px;
                   transition: transform 0.2s;",
          div(icon("money-bill-wave", style = "font-size: 2.5em; color: #20c997; margin-bottom: 15px;")),
          div("Median Income", style = "font-size: 14px; color: #6c757d; margin-bottom: 8px; font-weight: 600;"),
          div(textOutput("kpi_median_income"), style = "font-size: 40px; font-weight: 700; color: #212529;"),
          div(uiOutput("kpi_income_change"), style = "font-size: 13px; margin-top: 10px;")
        )
      ),
      
      column(
        3,
        div(
          class = "kpi-box",
          style = "background: white; padding: 25px; border-radius: 10px;
                   box-shadow: 0 2px 8px rgba(0,0,0,0.08); text-align: center;
                   border-top: 4px solid #fd7e14; height: 180px;
                   transition: transform 0.2s;",
          div(icon("briefcase", style = "font-size: 2.5em; color: #fd7e14; margin-bottom: 15px;")),
          div("Unemployment Rate", style = "font-size: 14px; color: #6c757d; margin-bottom: 8px; font-weight: 600;"),
          div(textOutput("kpi_unemployment_rate"), style = "font-size: 40px; font-weight: 700; color: #212529;"),
          div(uiOutput("kpi_unemployment_change"), style = "font-size: 13px; margin-top: 10px;")
        )
      ),
      
      column(
        3,
        div(
          class = "kpi-box",
          style = "background: white; padding: 25px; border-radius: 10px;
                   box-shadow: 0 2px 8px rgba(0,0,0,0.08); text-align: center;
                   border-top: 4px solid #e83e8c; height: 180px;
                   transition: transform 0.2s;",
          div(icon("chart-line", style = "font-size: 2.5em; color: #e83e8c; margin-bottom: 15px;")),
          div("Annual Budget Shortfall", style = "font-size: 14px; color: #6c757d; margin-bottom: 8px; font-weight: 600;"),
          div(textOutput("kpi_budget_shortfall"), style = "font-size: 40px; font-weight: 700; color: #212529;"),
          div(uiOutput("kpi_shortfall_change"), style = "font-size: 13px; margin-top: 10px;")
        )
      )
    ),
    
    # ========================================================================
    # HIGH-LEVEL TREND CHART (WIDE)
    # ========================================================================
    fluidRow(
      column(
        12,
        div(
          style = "background: white; padding: 30px; border-radius: 10px;
                   box-shadow: 0 2px 8px rgba(0,0,0,0.08); margin-bottom: 30px;",
          h4(
            icon("chart-line"), " National Food Insecurity Trend (2009-2023)",
            style = "color: #2c3e50; margin-top: 0; margin-bottom: 20px;"
          ),
          plotOutput("overview_trend_plot", height = "350px")
        )
      )
    ),
    
    # ========================================================================
    # KEY INSIGHT CALLOUTS
    # ========================================================================
    fluidRow(
      column(
        4,
        div(
          style = "background: linear-gradient(135deg, #0033A0 0%, #003D82 100%);
                   padding: 25px; border-radius: 10px; color: white;
                   box-shadow: 0 4px 15px rgba(0, 51, 160, 0.3);
                   height: 200px;",
          div(icon("exclamation-circle", style = "font-size: 2em; margin-bottom: 15px;")),
          h5("Great Recession Impact", style = "margin-top: 0; font-weight: 600;"),
          p("Food insecurity peaked at 16.3% during 2009-2010, affecting rural communities disproportionately.",
            style = "font-size: 14px; line-height: 1.6; margin: 0;")
        )
      ),
      
      column(
        4,
        div(
          style = "background: linear-gradient(135deg, #C41E3A 0%, #A01830 100%);
                   padding: 25px; border-radius: 10px; color: white;
                   box-shadow: 0 4px 15px rgba(196, 30, 58, 0.3);
                   height: 200px;",
          div(icon("virus", style = "font-size: 2em; margin-bottom: 15px;")),
          h5("COVID-19 Disruption", style = "margin-top: 0; font-weight: 600;"),
          p("Sharp increase to 12.8% in 2020 due to pandemic-related job losses and economic uncertainty.",
            style = "font-size: 14px; line-height: 1.6; margin: 0;")
        )
      ),
      
      column(
        4,
        div(
          style = "background: linear-gradient(135deg, #17a2b8 0%, #138496 100%);
                   padding: 25px; border-radius: 10px; color: white;
                   box-shadow: 0 4px 15px rgba(23, 162, 184, 0.3);
                   height: 200px;",
          div(icon("map-marked-alt", style = "font-size: 2em; margin-bottom: 15px;")),
          h5("Geographic Disparities", style = "margin-top: 0; font-weight: 600;"),
          p("Rural and southern counties show 3-5 percentage points higher rates than metropolitan areas.",
            style = "font-size: 14px; line-height: 1.6; margin: 0;")
        )
      )
    )
  )
)
