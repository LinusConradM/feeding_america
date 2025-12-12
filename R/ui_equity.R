# ==============================================================================
# UI MODULE: EQUITY & DISPARITIES
# ==============================================================================
# PURPOSE: Answer "Who is most affected?" - examine demographic gaps
# FEATURES: Disparity visuals, gap metrics, structural insights
# TEAM: Conrad, Sharon, Ryann, Alex
# ==============================================================================

ui_equity <- tabPanel(
  "Equity & Disparities",
  value = "equity",
  
  fluidPage(
    # Global Controls
    # global_controls_ui(),  # Removed to prevent duplicate IDs
    
    # Page Title
    fluidRow(
      style = "margin-bottom: 20px;",
      column(
        12,
        h2(
          icon("balance-scale"), " Equity & Disparities",
          style = "color: #2c3e50; font-weight: 600; margin-bottom: 10px;"
        ),
        p(
          "Examining food insecurity gaps across demographic groups",
          style = "color: #6c757d; font-size: 16px;"
        )
      )
    ),
    
    # ========================================================================
    # DISPARITY VISUALIZATION
    # ========================================================================
    fluidRow(
      column(
        12,
        div(
          style = "background: white; padding: 30px; border-radius: 10px;
                   box-shadow: 0 2px 8px rgba(0,0,0,0.08); margin-bottom: 30px;",
          h4("Food Insecurity Rates by Demographic Group", 
             style = "margin-top: 0; color: #2c3e50; margin-bottom: 20px;"),
          
          # Control: Select demographic dimension
          fluidRow(
            column(
              4,
              selectInput(
                "equity_dimension",
                "Demographic Dimension",
                choices = c(
                  "Race/Ethnicity" = "race_ethnicity",
                  "Household Type" = "household_type",
                  "Urban/Rural Status" = "urban_rural",
                  "Education Level" = "education"
                ),
                selected = "race_ethnicity",
                width = "100%"
              )
            )
          ),
          
          # Placeholder for disparity chart
          plotOutput("disparity_chart", height = "400px")
        )
      )
    ),
    
    # ========================================================================
    # GAP METRICS (3 CARDS)
    # ========================================================================
    fluidRow(
      column(
        4,
        div(
          style = "background: white; padding: 25px; border-radius: 10px;
                   box-shadow: 0 2px 8px rgba(0,0,0,0.08); text-align: center;
                   height: 220px;",
          icon("exclamation-triangle", style = "font-size: 3em; color: #dc3545; margin-bottom: 15px;"),
          h3("2.3x", style = "color: #2c3e50; margin: 10px 0; font-size: 40px;"),
          p("Black households experience food insecurity at 2.3 times the rate of white households",
            style = "color: #6c757d; font-size: 15px; margin: 0; line-height: 1.5;")
        )
      ),
      
      column(
        4,
        div(
          style = "background: white; padding: 25px; border-radius: 10px;
                   box-shadow: 0 2px 8px rgba(0,0,0,0.08); text-align: center;
                   height: 220px;",
          icon("home", style = "font-size: 3em; color: #ffc107; margin-bottom: 15px;"),
          h3("3.8x", style = "color: #2c3e50; margin: 10px 0; font-size: 40px;"),
          p("Single-parent households face 3.8 times higher food insecurity than married couples",
            style = "color: #6c757d; font-size: 15px; margin: 0; line-height: 1.5;")
        )
      ),
      
      column(
        4,
        div(
          style = "background: white; padding: 25px; border-radius: 10px;
                   box-shadow: 0 2px 8px rgba(0,0,0,0.08); text-align: center;
                   height: 220px;",
          icon("map-pin", style = "font-size: 3em; color: #17a2b8; margin-bottom: 15px;"),
          h3("+4.2%", style = "color: #2c3e50; margin: 10px 0; font-size: 40px;"),
          p("Rural counties show 4.2 percentage points higher food insecurity than metropolitan areas",
            style = "color: #6c757d; font-size: 15px; margin: 0; line-height: 1.5;")
        )
      )
    ),
    
    # ========================================================================
    # TREND ANALYSIS BY GROUP
    # ========================================================================
    fluidRow(
      style = "margin-top: 30px;",
      column(
        12,
        div(
          style = "background: white; padding: 30px; border-radius: 10px;
                   box-shadow: 0 2px 8px rgba(0,0,0,0.08); margin-bottom: 30px;",
          h4("Food Insecurity Trends by Group (2009-2023)", 
             style = "margin-top: 0; color: #2c3e50; margin-bottom: 20px;"),
          
          # Placeholder for trend comparison chart
          plotOutput("equity_trend_chart", height = "350px")
        )
      )
    ),
    
    # ========================================================================
    # STRUCTURAL INSIGHT CALLOUT
    # ========================================================================
    fluidRow(
      column(
        12,
        div(
          style = "background: white; padding: 30px; border-radius: 10px;
                   box-shadow: 0 2px 8px rgba(0,0,0,0.08);
                   border-left: 6px solid #6f42c1;",
          h4(icon("info-circle"), " Understanding Structural Inequality", 
             style = "color: #6f42c1; margin-top: 0; margin-bottom: 20px;"),
          p("These disparities reflect systemic barriers including historical discrimination, 
            unequal access to economic opportunities, and geographic isolation. Addressing food 
            insecurity requires targeted interventions that account for these structural factors.",
            style = "font-size: 16px; line-height: 1.8; color: #495057; margin-bottom: 20px;"),
          
          h5("Key Factors Contributing to Disparities:", 
             style = "color: #2c3e50; margin-bottom: 15px;"),
          
          fluidRow(
            column(
              6,
              tags$ul(
                style = "font-size: 15px; line-height: 1.8; color: #495057;",
                tags$li("Historical redlining and housing discrimination"),
                tags$li("Unequal access to quality education and employment"),
                tags$li("Limited public transportation in rural areas")
              )
            ),
            column(
              6,
              tags$ul(
                style = "font-size: 15px; line-height: 1.8; color: #495057;",
                tags$li("Food deserts in low-income neighborhoods"),
                tags$li("Wage disparities across racial and gender lines"),
                tags$li("Geographic concentration of economic opportunity")
              )
            )
          )
        )
      )
    )
  )
)
