# ==============================================================================
# FOOD INSECURITY SHINY APP - COMPLETE 10-TAB VERSION
# ==============================================================================
# PURPOSE: Comprehensive analytics platform for U.S. food insecurity (2009-2023)
# COURSE: DATA-613 (Graduate Level)
# TEAM: Conrad, Sharon, Ryann, Alex
# INSTITUTION: American University
# ==============================================================================

# ==============================================================================
# LOAD GLOBAL ENVIRONMENT
# ==============================================================================
source("global.R", local = TRUE)

# ==============================================================================
# LOAD REQUIRED PACKAGES
# ==============================================================================
library(shiny)
library(bslib)
library(shinyWidgets)

cat("✓ All app packages loaded\n")

# ==============================================================================
# LOAD UI MODULES (10 TABS)
# ==============================================================================
source("R/global_controls.R")              # Global filter controls
source("R/ui_landing.R")                   # Tab 1: Landing/Home
source("R/ui_overview.R")                  # Tab 2: Executive Overview ✅ WORKING
source("R/ui_geographic_intelligence.R")   # Tab 3: Geographic Intelligence
source("R/ui_correlation_analysis.R")      # Tab 4: Correlation Analysis
source("R/ui_regression_models.R")         # Tab 5: Regression Models
source("R/ui_equity.R")                    # Tab 6: Equity & Disparities
source("R/ui_county_clustering.R")         # Tab 7: County Clustering
source("R/ui_timeseries_explorer.R")       # Tab 8: Time-Series Explorer
source("R/ui_policy_scenarios_expanded.R") # Tab 9: Policy Scenarios
source("R/ui_data_downloads.R")            # Tab 10: Data & Downloads
source("R/beautiful_kpi_cards.R")  # Custom KPI card UI function

# ==============================================================================
# LOAD SERVER MODULES
# ==============================================================================
source("R/server_overview.R")
source("R/server_exploration.R")
source("R/server_analysis.R")

cat("✓ All modules loaded\n")

# ==============================================================================
# UI DEFINITION
# ==============================================================================

ui <- navbarPage(
  title = div(
    if (file.exists("www/AU-Logo-on-white-small.png")) {
      tags$img(
        src = "AU-Logo-on-white-small.png",
        alt = "American University Logo",
        style = "height: 30px; margin-right: 10px;"
      )
    },
    "U.S. Food Insecurity Analytics Platform"
  ),
  
  # Use custom Bootstrap theme with AU colors
  theme = NULL,
  
  windowTitle = "U.S. Food Insecurity Dashboard",
  
  id = "navbar",
  
  # ============================================================================
  # ALL 10 TABS IN LOGICAL ORDER
  # ============================================================================
  
  ui_landing,                    # Tab 1: Home/Landing ✅
  ui_overview,                   # Tab 2: Executive Overview ✅ WORKING
  ui_geographic_intelligence,    # Tab 3: Geographic Intelligence
  ui_correlation_analysis,       # Tab 4: Correlation Analysis
  ui_regression_models,          # Tab 5: Regression Models
  ui_equity,                     # Tab 6: Equity & Disparities
  ui_county_clustering,          # Tab 7: County Clustering
  ui_timeseries_explorer,        # Tab 8: Time-Series Explorer
  ui_policy_scenarios,  # Tab 9: Policy Scenarios
  ui_data_downloads,             # Tab 10: Data & Downloads
  
  # ============================================================================
  # CUSTOM CSS
  # ============================================================================
  tags$head(

    # Premium Theme
    tags$link(rel = "stylesheet", type = "text/css", href = "premium_theme.css"),

    # Mobile viewport
    tags$meta(name = "viewport", content = "width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no"),
    
    # Load custom Bootstrap with AU colors
    # tags$link(rel = "stylesheet", type = "text/css", href = "bootstrap.css"),
    
    # Google Fonts
    tags$link(
      rel = "stylesheet",
      href = "https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap"
    ),
    
    # Custom styles
    tags$style(HTML("
      /* Modern Navbar with AU Blue */
      .navbar { 
        background: linear-gradient(135deg, #0033A0 0%, #003D82 100%) !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.15);
        padding: 10px 20px;
      }
      .navbar-brand { 
        color: white !important; 
        font-weight: 600;
        font-size: 18px;
      }
      .navbar-nav .nav-link { 
        color: rgba(255,255,255,0.85) !important; 
        font-weight: 500;
        margin: 0 5px;
        transition: all 0.2s;
        font-size: 14px;
      }
      .navbar-nav .nav-link:hover { 
        color: white !important;
        transform: translateY(-2px);
      }
      .navbar-nav .active { 
        color: white !important; 
        background-color: rgba(255,255,255,0.15);
        border-radius: 5px;
      }
      
      /* KPI Card Hover Effect */
      .kpi-box:hover {
        transform: translateY(-5px);
        box-shadow: 0 4px 15px rgba(0,0,0,0.12) !important;
        transition: all 0.2s;
      }
      
      /* Body & Typography */
      body {
        font-family: 'Inter', sans-serif;
        background-color: #f8f9fa;
      }
      h1, h2, h3, h4, h5 {
        font-family: 'Inter', sans-serif;
      }
      
      /* Smooth transitions */
      .tab-content {
        animation: fadeIn 0.3s ease-in;
      }
      
      @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
      }
    "))
  )
)

# ==============================================================================
# SERVER DEFINITION
# ==============================================================================

server <- function(input, output, session) {
  # Data reactive
  data <- reactive({
    food_data
  })

  # Landing page navigation
  observeEvent(input$start_exploring, {
    updateNavbarPage(session, "navbar", selected = "overview")
  })

  # ============================================================================
  # EXISTING SERVER MODULES (WORKING)
  # ============================================================================
  server_overview(input, output, session, data)
  server_exploration(input, output, session, data)
  server_analysis(input, output, session, data)
  
  # ============================================================================
  # PLACEHOLDER OUTPUTS FOR NEW TABS
  # ============================================================================
  # These prevent errors when tabs load. Replace with actual server logic.
  
  # Geographic Intelligence placeholders
  output$hotspot_count <- renderText({ "TBD" })
  output$coldspot_count <- renderText({ "TBD" })
  output$morans_i <- renderText({ "TBD" })
  output$geo_disparity <- renderText({ "TBD" })
  output$selected_county_profile <- renderUI({ 
    HTML("<p style='text-align: center; color: #6c757d;'>Select a county on the map</p>")
  })
  
  # Correlation Analysis placeholders
  output$bivariate_r <- renderText({ "--" })
  output$bivariate_r2 <- renderText({ "--" })
  output$bivariate_p <- renderText({ "--" })
  output$sample_size <- renderText({ "--" })
  output$correlation_strength <- renderUI({ HTML("Run analysis to see results") })
  output$variance_explained <- renderUI({ HTML("") })
  output$significance_label <- renderUI({ HTML("") })
  
  # Regression Models placeholders
  output$model_r2 <- renderText({ "--" })
  output$model_adj_r2 <- renderText({ "--" })
  output$model_fstat <- renderText({ "--" })
  output$model_n <- renderText({ "--" })
  output$coefficient_cards <- renderUI({ 
    HTML("<p style='text-align: center; color: #6c757d;'>Run a regression model to see interpretations</p>")
  })
  
  # Equity Analysis placeholders
  output$absolute_disparity <- renderText({ "--" })
  output$relative_disparity <- renderText({ "--" })
  output$gini_coef <- renderText({ "--" })
  output$iqr_value <- renderText({ "--" })
  output$metro_fi_rate <- renderText({ "--" })
  output$rural_fi_rate <- renderText({ "--" })
  output$rural_metro_gap <- renderText({ "--" })
  
  # County Clustering placeholders
  output$total_clusters <- renderText({ "--" })
  output$cluster_ss <- renderText({ "--" })
  output$cluster_variance <- renderText({ "--" })
  output$cluster_interpretations <- renderUI({ 
    HTML("<p style='text-align: center; color: #6c757d;'>Run clustering to see interpretations</p>")
  })
  
  # Time-Series Explorer placeholders
  output$pre_covid_avg <- renderText({ "--" })
  output$covid_avg <- renderText({ "--" })
  output$post_covid_avg <- renderText({ "--" })
  
  # Policy Scenarios placeholders
  output$baseline_fi <- renderText({ "--" })
  output$projected_fi <- renderText({ "--" })
  output$fi_reduction <- renderText({ "--" })
  output$people_helped <- renderText({ "--" })
  output$cost_estimate <- renderText({ "--" })
  
  cat("✓ Server initialized with placeholder outputs\n")
}

# ==============================================================================
# RUN APPLICATION
# ==============================================================================

shinyApp(ui = ui, server = server)
