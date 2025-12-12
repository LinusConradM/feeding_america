# ==============================================================================
# UI MODULE: DATA TRANSPARENCY & DOWNLOADS
# ==============================================================================
# PURPOSE: Maintain credibility and enable reproducibility
# CAPABILITIES: Data dictionary, methodology, versioning, exports
# TEAM: Conrad, Sharon, Ryann, Alex
# ==============================================================================

ui_data_downloads <- tabPanel(
  "Data & Downloads",
  value = "data_downloads",
  
  fluidPage(
    # Page Header
    fluidRow(
      column(
        12,
        h2(
          icon("database"), " Data Transparency & Download Center",
          style = "color: #2c3e50; font-weight: 600; margin-bottom: 10px;"
        ),
        p(
          "Access data sources, methodology documentation, and export options",
          style = "color: #6c757d; font-size: 16px; margin-bottom: 30px;"
        )
      )
    ),
    
    # ========================================================================
    # DATA SOURCES & CITATIONS
    # ========================================================================
    fluidRow(
      column(
        12,
        div(
          style = "background: white; padding: 30px; border-radius: 10px;
                   box-shadow: 0 2px 8px rgba(0,0,0,0.08); margin-bottom: 30px;",
          h3(
            icon("book"), " Data Sources & Citations",
            style = "margin-top: 0; color: #2c3e50;"
          ),
          hr(),
          
          # Feeding America
          div(
            style = "background: #f8f9fa; padding: 20px; border-radius: 8px;
                     border-left: 4px solid #0033A0; margin-bottom: 20px;",
            h5("Feeding America Map the Meal Gap", style = "color: #0033A0; margin-top: 0;"),
            p(strong("Coverage:"), " 2009-2023, 3,156 counties", 
              style = "color: #495057; font-size: 14px; margin-bottom: 8px;"),
            p(strong("Variables:"), " Food insecurity rates (overall & child), 
              number of food insecure persons, cost per meal, budget shortfall", 
              style = "color: #495057; font-size: 14px; margin-bottom: 8px;"),
            p(strong("Citation:"), " Feeding America. (2024). Map the Meal Gap. 
              Retrieved from https://www.feedingamerica.org/research/map-the-meal-gap",
              style = "color: #6c757d; font-size: 13px; font-style: italic; margin: 0;")
          ),
          
          # U.S. Census Bureau
          div(
            style = "background: #f8f9fa; padding: 20px; border-radius: 8px;
                     border-left: 4px solid #C41E3A; margin-bottom: 20px;",
            h5("U.S. Census Bureau (ACS 5-Year Estimates)", 
               style = "color: #C41E3A; margin-top: 0;"),
            p(strong("Variables:"), " Poverty rate, median household income, 
              population demographics, education attainment, unemployment rate, 
              health insurance coverage", 
              style = "color: #495057; font-size: 14px; margin-bottom: 8px;"),
            p(strong("Citation:"), " U.S. Census Bureau. (2024). American Community Survey 
              5-Year Estimates. Retrieved from https://www.census.gov/programs-surveys/acs",
              style = "color: #6c757d; font-size: 13px; font-style: italic; margin: 0;")
          ),
          
          # Additional Sources
          div(
            style = "background: #f8f9fa; padding: 20px; border-radius: 8px;
                     border-left: 4px solid #28a745;",
            h5("USDA & SNAP Data", style = "color: #28a745; margin-top: 0;"),
            p(strong("Variables:"), " SNAP participation rates, benefit levels, 
              rural-urban continuum codes (RUCC)", 
              style = "color: #495057; font-size: 14px; margin-bottom: 8px;"),
            p(strong("Citation:"), " USDA Economic Research Service. (2024). 
              Food Security in the U.S. Retrieved from https://www.ers.usda.gov/topics/food-nutrition-assistance/food-security-in-the-us/",
              style = "color: #6c757d; font-size: 13px; font-style: italic; margin: 0;")
          )
        )
      )
    ),
    
    # ========================================================================
    # DATA DICTIONARY
    # ========================================================================
    fluidRow(
      column(
        12,
        div(
          style = "background: white; padding: 30px; border-radius: 10px;
                   box-shadow: 0 2px 8px rgba(0,0,0,0.08); margin-bottom: 30px;",
          h3(
            icon("list"), " Data Dictionary",
            style = "margin-top: 0; color: #2c3e50;"
          ),
          p("Complete variable definitions and data types",
            style = "color: #6c757d; margin-bottom: 20px;"),
          hr(),
          
          # Data dictionary table placeholder
          div(
            style = "min-height: 400px; display: flex; align-items: center; 
                     justify-content: center; background: #f8f9fa; 
                     border-radius: 8px; border: 2px dashed #dee2e6;",
            div(
              style = "text-align: center;",
              icon("table", style = "font-size: 60px; color: #0033A0; margin-bottom: 20px;"),
              h4("Searchable Data Dictionary", 
                 style = "color: #495057; margin-bottom: 10px;"),
              p("Interactive table with all 50 variables, definitions, units, and data types",
                style = "color: #6c757d; margin-bottom: 15px;"),
              tags$div(
                tags$strong("Columns:", style = "color: #0033A0;"),
                tags$ul(
                  style = "text-align: left; display: inline-block; color: #6c757d;",
                  tags$li("Variable Name"),
                  tags$li("Description"),
                  tags$li("Units (%, $, count)"),
                  tags$li("Data Type (numeric, factor, character)"),
                  tags$li("Source"),
                  tags$li("Missingness %")
                )
              )
            )
          )
        )
      )
    ),
    
    # ========================================================================
    # METHODOLOGY
    # ========================================================================
    fluidRow(
      column(
        12,
        div(
          style = "background: white; padding: 30px; border-radius: 10px;
                   box-shadow: 0 2px 8px rgba(0,0,0,0.08); margin-bottom: 30px;",
          h3(
            icon("flask"), " Methodology & Model Specifications",
            style = "margin-top: 0; color: #2c3e50;"
          ),
          hr(),
          
          # Data Processing
          h4("1. Data Processing & Integration", style = "color: #0033A0; margin-top: 0;"),
          p("Raw data from Feeding America and U.S. Census Bureau were merged by 
            FIPS county code and year. Counties with incomplete data were retained 
            but flagged. No imputation was performed to maintain data integrity.",
            style = "color: #495057; font-size: 15px; line-height: 1.7; margin-bottom: 25px;"),
          
          # Variable Transformations
          h4("2. Variable Transformations", style = "color: #C41E3A; margin-top: 0;"),
          tags$ul(
            style = "color: #495057; font-size: 15px; line-height: 1.7; margin-bottom: 25px;",
            tags$li("Rates converted from proportions to percentages (×100)"),
            tags$li("Median income log-transformed for regression models"),
            tags$li("Binary rural/urban indicator created from RUCC codes"),
            tags$li("Census regions standardized to 4-category system")
          ),
          
          # Model Specifications
          h4("3. Statistical Models", style = "color: #28a745; margin-top: 0;"),
          
          tags$div(
            style = "background: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 20px;",
            h5("OLS Regression (Cross-Sectional)", style = "color: #495057; margin-top: 0;"),
            tags$pre(
              style = "background: white; padding: 15px; border: 1px solid #dee2e6; 
                       border-radius: 4px; overflow-x: auto;",
              "FI_rate = β₀ + β₁(poverty_rate) + β₂(log_income) + 
       β₃(unemployment) + β₄(uninsured) + ε"
            )
          ),
          
          tags$div(
            style = "background: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 20px;",
            h5("Fixed Effects Panel Model", style = "color: #495057; margin-top: 0;"),
            tags$pre(
              style = "background: white; padding: 15px; border: 1px solid #dee2e6; 
                       border-radius: 4px; overflow-x: auto;",
              "FI_rate_it = β₁X_it + α_i + γ_t + ε_it

Where:
  α_i = county fixed effects
  γ_t = year fixed effects
  X_it = time-varying covariates"
            )
          ),
          
          # Limitations
          h4("4. Limitations & Caveats", style = "color: #ffc107; margin-top: 0;"),
          tags$ul(
            style = "color: #495057; font-size: 15px; line-height: 1.7;",
            tags$li("Observational data—causal claims are limited"),
            tags$li("Missing data for cost per meal (~13% of observations)"),
            tags$li("County-level aggregation masks within-county variation"),
            tags$li("Feeding America estimates use indirect methods (not direct surveys)"),
            tags$li("Policy simulations assume linear relationships")
          )
        )
      )
    ),
    
    # ========================================================================
    # DOWNLOAD CENTER
    # ========================================================================
    fluidRow(
      column(
        12,
        div(
          style = "background: white; padding: 30px; border-radius: 10px;
                   box-shadow: 0 2px 8px rgba(0,0,0,0.08); margin-bottom: 30px;",
          h3(
            icon("download"), " Download Center",
            style = "margin-top: 0; color: #2c3e50;"
          ),
          p("Export data, visualizations, and analysis results",
            style = "color: #6c757d; margin-bottom: 20px;"),
          hr(),
          
          fluidRow(
            # Data Downloads
            column(
              4,
              div(
                style = "background: #f8f9fa; padding: 25px; border-radius: 8px; 
                         text-align: center; height: 220px;",
                icon("file-csv", style = "font-size: 50px; color: #28a745; margin-bottom: 15px;"),
                h5("Raw Data", style = "color: #2c3e50; margin-bottom: 10px;"),
                p("Complete dataset (2009-2023)", 
                  style = "color: #6c757d; font-size: 14px; margin-bottom: 15px;"),
                actionButton(
                  "download_full_csv",
                  "Download CSV",
#                   icon removed for debugging
                  style = "width: 100%; background: #28a745; color: white; border: none;"
                )
              )
            ),
            
            # Summary Tables
            column(
              4,
              div(
                style = "background: #f8f9fa; padding: 25px; border-radius: 8px; 
                         text-align: center; height: 220px;",
                icon("table", style = "font-size: 50px; color: #0033A0; margin-bottom: 15px;"),
                h5("Summary Tables", style = "color: #2c3e50; margin-bottom: 10px;"),
                p("State/national aggregates", 
                  style = "color: #6c757d; font-size: 14px; margin-bottom: 15px;"),
                actionButton(
                  "download_summary",
                  "Download Excel",
#                   icon removed for debugging
                  style = "width: 100%; background: #0033A0; color: white; border: none;"
                )
              )
            ),
            
            # Visualizations
            column(
              4,
              div(
                style = "background: #f8f9fa; padding: 25px; border-radius: 8px; 
                         text-align: center; height: 220px;",
                icon("chart-line", style = "font-size: 50px; color: #C41E3A; margin-bottom: 15px;"),
                h5("All Visualizations", style = "color: #2c3e50; margin-bottom: 10px;"),
                p("High-res PNG exports", 
                  style = "color: #6c757d; font-size: 14px; margin-bottom: 15px;"),
                actionButton(
                  "download_charts",
                  "Download ZIP",
#                   icon removed for debugging
                  style = "width: 100%; background: #C41E3A; color: white; border: none;"
                )
              )
            )
          ),
          
          fluidRow(
            style = "margin-top: 20px;",
            
            # Model Results
            column(
              4,
              div(
                style = "background: #f8f9fa; padding: 25px; border-radius: 8px; 
                         text-align: center; height: 220px;",
                icon("calculator", style = "font-size: 50px; color: #17a2b8; margin-bottom: 15px;"),
                h5("Regression Results", style = "color: #2c3e50; margin-bottom: 10px;"),
                p("Model coefficients & diagnostics", 
                  style = "color: #6c757d; font-size: 14px; margin-bottom: 15px;"),
                actionButton(
                  "download_models",
                  "Download Excel",
#                   icon removed for debugging
                  style = "width: 100%; background: #17a2b8; color: white; border: none;"
                )
              )
            ),
            
            # County Rankings
            column(
              4,
              div(
                style = "background: #f8f9fa; padding: 25px; border-radius: 8px; 
                         text-align: center; height: 220px;",
                icon("trophy", style = "font-size: 50px; color: #ffc107; margin-bottom: 15px;"),
                h5("County Rankings", style = "color: #2c3e50; margin-bottom: 10px;"),
                p("Best/worst performers", 
                  style = "color: #6c757d; font-size: 14px; margin-bottom: 15px;"),
                actionButton(
                  "download_rankings",
                  "Download CSV",
#                   icon removed for debugging
                  style = "width: 100%; background: #ffc107; color: #212529; border: none;"
                )
              )
            ),
            
            # Full Report
            column(
              4,
              div(
                style = "background: #f8f9fa; padding: 25px; border-radius: 8px; 
                         text-align: center; height: 220px;",
                icon("file-pdf", style = "font-size: 50px; color: #6f42c1; margin-bottom: 15px;"),
                h5("Comprehensive Report", style = "color: #2c3e50; margin-bottom: 10px;"),
                p("All tabs in PDF format", 
                  style = "color: #6c757d; font-size: 14px; margin-bottom: 15px;"),
                actionButton(
                  "download_report",
                  "Download PDF",
#                   icon removed for debugging
                  style = "width: 100%; background: #6f42c1; color: white; border: none;"
                )
              )
            )
          )
        )
      )
    ),
    
    # ========================================================================
    # VERSION HISTORY
    # ========================================================================
    fluidRow(
      column(
        12,
        div(
          style = "background: white; padding: 30px; border-radius: 10px;
                   box-shadow: 0 2px 8px rgba(0,0,0,0.08); margin-bottom: 30px;",
          h3(
            icon("code-branch"), " Version History",
            style = "margin-top: 0; color: #2c3e50;"
          ),
          hr(),
          
          # Version 2.0
          div(
            style = "border-left: 4px solid #0033A0; padding-left: 20px; margin-bottom: 25px;",
            h5("Version 2.0 — December 2025", style = "color: #0033A0; margin: 0 0 10px 0;"),
            p("Added 2023 data from Feeding America. Updated Census ACS estimates to 2023. 
              Revised regression models to include fixed effects specifications.",
              style = "color: #495057; font-size: 14px; line-height: 1.6; margin: 0;")
          ),
          
          # Version 1.5
          div(
            style = "border-left: 4px solid #6c757d; padding-left: 20px; margin-bottom: 25px;",
            h5("Version 1.5 — July 2024", style = "color: #6c757d; margin: 0 0 10px 0;"),
            p("Integrated 2022 data. Added clustering analysis module. 
              Improved data validation and quality checks.",
              style = "color: #495057; font-size: 14px; line-height: 1.6; margin: 0;")
          ),
          
          # Version 1.0
          div(
            style = "border-left: 4px solid #6c757d; padding-left: 20px;",
            h5("Version 1.0 — January 2024", style = "color: #6c757d; margin: 0 0 10px 0;"),
            p("Initial release with 2009-2021 data. Core dashboard functionality established.",
              style = "color: #495057; font-size: 14px; line-height: 1.6; margin: 0;")
          )
        )
      )
    ),
    
    # ========================================================================
    # REPRODUCIBILITY
    # ========================================================================
    fluidRow(
      column(
        12,
        div(
          style = "background: white; padding: 30px; border-radius: 10px;
                   box-shadow: 0 2px 8px rgba(0,0,0,0.08);",
          h3(
            icon("code"), " Reproducibility & Code Access",
            style = "margin-top: 0; color: #2c3e50;"
          ),
          hr(),
          
          p("This dashboard was built using R Shiny with the following packages:",
            style = "color: #495057; font-size: 15px; margin-bottom: 15px;"),
          
          fluidRow(
            column(
              6,
              tags$ul(
                style = "color: #495057; font-size: 14px; line-height: 1.8;",
                tags$li(tags$code("shiny"), " v1.11.1 — Dashboard framework"),
                tags$li(tags$code("bslib"), " v0.9.0 — Bootstrap theming"),
                tags$li(tags$code("tidyverse"), " v2.0.0 — Data manipulation"),
                tags$li(tags$code("ggplot2"), " v3.5.1 — Visualizations"),
                tags$li(tags$code("leaflet"), " v2.2.2 — Interactive maps")
              )
            ),
            
            column(
              6,
              tags$ul(
                style = "color: #495057; font-size: 14px; line-height: 1.8;",
                tags$li(tags$code("plotly"), " v4.10.4 — Interactive charts"),
                tags$li(tags$code("DT"), " v0.33 — Data tables"),
                tags$li(tags$code("nnet"), " v7.3-21 — Multinomial regression"),
                tags$li(tags$code("rpart"), " v4.1.23 — Decision trees"),
                tags$li(tags$code("pROC"), " v1.18.5 — ROC analysis")
              )
            )
          ),
          
          hr(),
          
          div(
            style = "background: #f8f9fa; padding: 20px; border-radius: 8px; text-align: center;",
            icon("code", style = "font-size: 40px; color: #212529; margin-bottom: 10px;"),
            h5("Full source code available on GitHub", style = "color: #2c3e50;"),
            p("github.com/your-username/food-insecurity-dashboard", 
              style = "color: #6c757d; font-size: 14px; font-family: monospace;")
          )
        )
      )
    )
  )
)
