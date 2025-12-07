# ==============================================================================
# UI: OVERVIEW TAB - Clean Professional Version
# ==============================================================================

ui_overview <- tabPanel(
  "Overview",
  
  fluidPage(
    
    # ========================================================================
    # HEADER SECTION: What is Food Insecurity? (IMPROVED READABILITY)
    # ========================================================================
    
    fluidRow(
      column(12,
        div(
          style = "background-color: #f8f9fa; 
                   padding: 35px; 
                   border-radius: 10px; 
                   margin-bottom: 30px; 
                   border-left: 6px solid #667eea;
                   box-shadow: 0 2px 8px rgba(0,0,0,0.08);",
          
          # Clear Title with Food Icon
          h2(
            "🍞 Understanding Food Insecurity in America",
            style = "margin-top: 0; font-weight: 700; color: #2c3e50; margin-bottom: 25px;"
          ),
          
          # Definition and Why It Matters - SIDE BY SIDE
          fluidRow(
            
            # LEFT: What is Food Insecurity?
            column(6,
              div(
                style = "background-color: white; 
                         padding: 20px; 
                         border-radius: 8px;
                         border-left: 4px solid #667eea;
                         height: 100%;",
                
                h4("What is Food Insecurity?", 
                   style = "color: #667eea; margin-top: 0; margin-bottom: 12px;"),
                
                p(
                  style = "font-size: 15px; line-height: 1.6; color: #2c3e50; margin-bottom: 12px;",
                  "Food insecurity is the lack of consistent access to enough food for an active, 
                  healthy life (USDA Economic Research Service, 2024). It affects millions of Americans 
                  and is a critical indicator of household economic stability and public health."
                ),
                
                p(
                  style = "font-size: 13px; color: #6c757d; font-style: italic; margin-bottom: 0;",
                  "In 2023, 13.5% of U.S. households (44.2 million people) experienced food insecurity, 
                  with rural and southern counties showing the highest rates."
                )
              )
            ),
            
            # RIGHT: Why It Matters (Evidence-Based)
            column(6,
              div(
                style = "background-color: white; 
                         padding: 20px; 
                         border-radius: 8px;
                         border-left: 4px solid #dc3545;
                         height: 100%;",
                
                h4("Why It Matters:", 
                   style = "color: #dc3545; margin-top: 0; margin-bottom: 12px;"),
                
                tags$ul(
                  style = "font-size: 14px; line-height: 1.7; color: #2c3e50; margin-bottom: 0; padding-left: 20px;",
                  
                  tags$li(
                    strong("Health Impacts: "), 
                    "Food insecurity impairs physical and mental health, especially in children, 
                    leading to developmental delays and chronic disease (Coleman-Jensen et al., 2023)"
                  ),
                  
                  tags$li(
                    strong("Socioeconomic Links: "), 
                    "Strong correlations with poverty, unemployment, and low income across U.S. counties 
                    (Gundersen & Ziliak, 2015)"
                  ),
                  
                  tags$li(
                    strong("Geographic Disparities: "), 
                    "Rural and southern communities face consistently higher rates, with significant 
                    variation by race/ethnicity and household composition (Feeding America, 2024)"
                  ),
                  
                  tags$li(
                    strong("Policy Impact: "), 
                    "SNAP and other interventions reduce food insecurity by approximately 6%, demonstrating 
                    the importance of targeted support (Gundersen et al., 2017)"
                  )
                )
              )
            )
          )
        )
      )
    ),
    
    # ========================================================================
    # DATA SOURCES + VARIABLES ANALYZED (SIDE BY SIDE)
    # ========================================================================
    
    fluidRow(
      
      # LEFT: DATA SOURCES
      column(6,
        div(
          style = "background-color: white; 
                   padding: 25px; 
                   border-radius: 8px; 
                   box-shadow: 0 2px 8px rgba(0,0,0,0.08);
                   height: 100%;",
          
          h3(
            icon("database"), " Data Sources", 
            style = "margin-top: 0; color: #667eea; margin-bottom: 20px; font-size: 20px;"
          ),
          
          # Feeding America
          div(
            style = "margin-bottom: 20px; padding: 15px; background-color: #f8f9fa; border-radius: 6px;",
            
            h5(
              "1. Feeding America Map the Meal Gap (2009-2023)",
              style = "color: #2c3e50; margin-top: 0; margin-bottom: 10px;"
            ),
            
            p(
              style = "font-size: 14px; line-height: 1.6; color: #495057; margin-bottom: 10px;",
              "County-level estimates of food insecurity rates, cost per meal, and budget shortfalls"
            ),
            
            tags$a(
              href = "https://www.feedingamerica.org/research/map-the-meal-gap/by-county",
              target = "_blank",
              icon("external-link-alt"), " Visit Feeding America",
              style = "color: #667eea; text-decoration: none; font-size: 14px;"
            )
          ),
          
          # Census ACS
          div(
            style = "margin-bottom: 20px; padding: 15px; background-color: #f8f9fa; border-radius: 6px;",
            
            h5(
              "2. U.S. Census Bureau American Community Survey",
              style = "color: #2c3e50; margin-top: 0; margin-bottom: 10px;"
            ),
            
            p(
              style = "font-size: 14px; line-height: 1.6; color: #495057; margin-bottom: 10px;",
              "Socioeconomic indicators: poverty rates, median income, unemployment, education"
            ),
            
            tags$a(
              href = "https://www.census.gov/programs-surveys/acs",
              target = "_blank",
              icon("external-link-alt"), " Visit Census Bureau",
              style = "color: #667eea; text-decoration: none; font-size: 14px;"
            )
          ),
          
          # Coverage
          div(
            style = "padding: 12px; background-color: #e7f3ff; border-radius: 6px; border-left: 3px solid #0066cc;",
            p(
              style = "margin: 0; font-size: 14px; color: #2c3e50;",
              strong("Coverage: "), "3,156 U.S. counties across 15 years (2009-2023)"
            )
          )
        )
      ),
      
      # RIGHT: VARIABLES ANALYZED
      column(6,
        div(
          style = "background-color: white; 
                   padding: 25px; 
                   border-radius: 8px; 
                   box-shadow: 0 2px 8px rgba(0,0,0,0.08);
                   height: 100%;",
          
          h3(
            icon("table"), " Variables Analyzed", 
            style = "margin-top: 0; color: #667eea; margin-bottom: 20px; font-size: 20px;"
          ),
          
          div(
            style = "font-size: 15px; line-height: 2; color: #2c3e50;",
            
            p(
              style = "margin-bottom: 12px;",
              icon("bullseye", style = "color: #dc3545; margin-right: 8px;"),
              strong("Outcome: "), 
              "Food insecurity rate (overall & children)"
            ),
            
            p(
              style = "margin-bottom: 12px;",
              icon("dollar-sign", style = "color: #28a745; margin-right: 8px;"),
              strong("Economic: "), 
              "Cost per meal, budget shortfall"
            ),
            
            p(
              style = "margin-bottom: 12px;",
              icon("chart-bar", style = "color: #6f42c1; margin-right: 8px;"),
              strong("Socioeconomic: "), 
              "Poverty rate, median income, unemployment"
            ),
            
            p(
              style = "margin-bottom: 12px;",
              icon("users", style = "color: #17a2b8; margin-right: 8px;"),
              strong("Demographic: "), 
              "Education level, race/ethnicity, household type"
            ),
            
            p(
              style = "margin-bottom: 12px;",
              icon("map-marked-alt", style = "color: #fd7e14; margin-right: 8px;"),
              strong("Geographic: "), 
              "Urban/rural status, census region"
            ),
            
            p(
              style = "margin-bottom: 0;",
              icon("landmark", style = "color: #20c997; margin-right: 8px;"),
              strong("Policy: "), 
              "SNAP participation, eligibility thresholds"
            )
          )
        )
      )
    ),
    
    # ========================================================================
    # KEY METRICS (KPI TILES)
    # ========================================================================
    
    fluidRow(
      style = "margin-top: 30px;",
      column(12,
        h3(
          icon("chart-line"), " Key National Indicators (2023)", 
          style = "color: #667eea; margin-bottom: 20px; font-size: 22px;"
        )
      )
    ),
    
    # ROW 1: Food Insecurity Metrics
    fluidRow(
      
      # National FI Rate
      column(3,
        div(
          class = "kpi-box",
          style = "background: white; padding: 20px; border-radius: 8px; 
                   box-shadow: 0 2px 8px rgba(0,0,0,0.08); text-align: center;
                   border-top: 4px solid #dc3545; transition: transform 0.2s;",
          
          div(icon("utensils", style = "font-size: 2em; color: #dc3545; margin-bottom: 10px;")),
          div("National FI Rate", 
              style = "font-size: 13px; color: #6c757d; margin-bottom: 5px; font-weight: 600;"),
          div(textOutput("kpi_national_fi_rate"), 
              style = "font-size: 32px; font-weight: 700; color: #212529;"),
          div(uiOutput("kpi_fi_rate_change"), 
              style = "font-size: 12px; margin-top: 8px;")
        )
      ),
      
      # Food Insecure Persons
      column(3,
        div(
          class = "kpi-box",
          style = "background: white; padding: 20px; border-radius: 8px; 
                   box-shadow: 0 2px 8px rgba(0,0,0,0.08); text-align: center;
                   border-top: 4px solid #ffc107;",
          
          div(icon("users", style = "font-size: 2em; color: #ffc107; margin-bottom: 10px;")),
          div("Food Insecure Persons", 
              style = "font-size: 13px; color: #6c757d; margin-bottom: 5px; font-weight: 600;"),
          div(textOutput("kpi_total_food_insecure"), 
              style = "font-size: 32px; font-weight: 700; color: #212529;"),
          div(uiOutput("kpi_fi_persons_change"), 
              style = "font-size: 12px; margin-top: 8px;")
        )
      ),
      
      # Child FI Rate
      column(3,
        div(
          class = "kpi-box",
          style = "background: white; padding: 20px; border-radius: 8px; 
                   box-shadow: 0 2px 8px rgba(0,0,0,0.08); text-align: center;
                   border-top: 4px solid #17a2b8;",
          
          div(icon("child", style = "font-size: 2em; color: #17a2b8; margin-bottom: 10px;")),
          div("Child FI Rate", 
              style = "font-size: 13px; color: #6c757d; margin-bottom: 5px; font-weight: 600;"),
          div(textOutput("kpi_child_fi_rate"), 
              style = "font-size: 32px; font-weight: 700; color: #212529;"),
          div(uiOutput("kpi_child_fi_change"), 
              style = "font-size: 12px; margin-top: 8px;")
        )
      ),
      
      # Avg Cost per Meal
      column(3,
        div(
          class = "kpi-box",
          style = "background: white; padding: 20px; border-radius: 8px; 
                   box-shadow: 0 2px 8px rgba(0,0,0,0.08); text-align: center;
                   border-top: 4px solid #28a745;",
          
          div(icon("dollar-sign", style = "font-size: 2em; color: #28a745; margin-bottom: 10px;")),
          div("Avg. Cost per Meal", 
              style = "font-size: 13px; color: #6c757d; margin-bottom: 5px; font-weight: 600;"),
          div(textOutput("kpi_avg_cost_per_meal"), 
              style = "font-size: 32px; font-weight: 700; color: #212529;"),
          div(uiOutput("kpi_cost_change"), 
              style = "font-size: 12px; margin-top: 8px;")
        )
      )
    ),
    
    # ROW 2: Socioeconomic Drivers
    fluidRow(
      style = "margin-top: 20px;",
      
      # Poverty Rate
      column(3,
        div(
          class = "kpi-box",
          style = "background: white; padding: 20px; border-radius: 8px; 
                   box-shadow: 0 2px 8px rgba(0,0,0,0.08); text-align: center;
                   border-top: 4px solid #6f42c1;",
          
          div(icon("hand-holding-dollar", style = "font-size: 2em; color: #6f42c1; margin-bottom: 10px;")),
          div("National Poverty Rate", 
              style = "font-size: 13px; color: #6c757d; margin-bottom: 5px; font-weight: 600;"),
          div(textOutput("kpi_poverty_rate"), 
              style = "font-size: 32px; font-weight: 700; color: #212529;"),
          div(uiOutput("kpi_poverty_change"), 
              style = "font-size: 12px; margin-top: 8px;")
        )
      ),
      
      # Median Income
      column(3,
        div(
          class = "kpi-box",
          style = "background: white; padding: 20px; border-radius: 8px; 
                   box-shadow: 0 2px 8px rgba(0,0,0,0.08); text-align: center;
                   border-top: 4px solid #20c997;",
          
          div(icon("money-bill-wave", style = "font-size: 2em; color: #20c997; margin-bottom: 10px;")),
          div("Median Income", 
              style = "font-size: 13px; color: #6c757d; margin-bottom: 5px; font-weight: 600;"),
          div(textOutput("kpi_median_income"), 
              style = "font-size: 32px; font-weight: 700; color: #212529;"),
          div(uiOutput("kpi_income_change"), 
              style = "font-size: 12px; margin-top: 8px;")
        )
      ),
      
      # Unemployment Rate
      column(3,
        div(
          class = "kpi-box",
          style = "background: white; padding: 20px; border-radius: 8px; 
                   box-shadow: 0 2px 8px rgba(0,0,0,0.08); text-align: center;
                   border-top: 4px solid #fd7e14;",
          
          div(icon("briefcase", style = "font-size: 2em; color: #fd7e14; margin-bottom: 10px;")),
          div("Unemployment Rate", 
              style = "font-size: 13px; color: #6c757d; margin-bottom: 5px; font-weight: 600;"),
          div(textOutput("kpi_unemployment_rate"), 
              style = "font-size: 32px; font-weight: 700; color: #212529;"),
          div(uiOutput("kpi_unemployment_change"), 
              style = "font-size: 12px; margin-top: 8px;")
        )
      ),
      
      # Annual Budget Shortfall
      column(3,
        div(
          class = "kpi-box",
          style = "background: white; padding: 20px; border-radius: 8px; 
                   box-shadow: 0 2px 8px rgba(0,0,0,0.08); text-align: center;
                   border-top: 4px solid #e83e8c;",
          
          div(icon("chart-line", style = "font-size: 2em; color: #e83e8c; margin-bottom: 10px;")),
          div("Annual Budget Shortfall", 
              style = "font-size: 13px; color: #6c757d; margin-bottom: 5px; font-weight: 600;"),
          div(textOutput("kpi_budget_shortfall"), 
              style = "font-size: 32px; font-weight: 700; color: #212529;"),
          div(uiOutput("kpi_shortfall_change"), 
              style = "font-size: 12px; margin-top: 8px;")
        )
      )
    ),
    
    # ========================================================================
    # KEY INSIGHTS (MOVED TO BOTTOM, FULL WIDTH)
    # ========================================================================
    
    fluidRow(
      style = "margin-top: 40px; margin-bottom: 30px;",
      
      column(12,
        div(
          style = "background-color: white; 
                   padding: 30px; 
                   border-radius: 8px; 
                   box-shadow: 0 2px 8px rgba(0,0,0,0.08);
                   border-left: 6px solid #667eea;",
          
          h3(
            icon("lightbulb"), " Key Insights from 15 Years of Data", 
            style = "color: #667eea; margin-top: 0; margin-bottom: 25px; font-size: 22px;"
          ),
          
          fluidRow(
            column(6,
              tags$ul(
                style = "line-height: 2.2; font-size: 15px; color: #2c3e50;",
                tags$li(
                  strong("Great Recession Impact: "), 
                  "Food insecurity peaked at 16.3% during the 2009-2010 economic crisis, 
                  affecting rural communities disproportionately"
                ),
                tags$li(
                  strong("Recovery Period: "), 
                  "Steady decline from 2011-2019 as unemployment decreased and median income rose, 
                  reaching a low of 10.5% in 2019"
                ),
                tags$li(
                  strong("COVID-19 Disruption: "), 
                  "Sharp increase to 12.8% in 2020 due to pandemic-related job losses and 
                  economic uncertainty, especially among low-income households"
                )
              )
            ),
            
            column(6,
              tags$ul(
                style = "line-height: 2.2; font-size: 15px; color: #2c3e50;",
                tags$li(
                  strong("Geographic Disparities: "), 
                  "Rural and southern counties consistently experience 3-5 percentage points 
                  higher food insecurity rates than metropolitan areas (Feeding America, 2024)"
                ),
                tags$li(
                  strong("Racial Inequities: "), 
                  "Persistent gaps across racial/ethnic groups, with Black and Hispanic households 
                  experiencing food insecurity at 2-3 times the rate of white households"
                ),
                tags$li(
                  strong("Cost Burden: "), 
                  "Annual food budget shortfall reached $33.3 billion in 2023, with cost per meal 
                  rising 10% since 2022, disproportionately affecting high-poverty counties"
                )
              )
            )
          )
        )
      )
    )
  )
)
