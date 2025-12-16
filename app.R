# ==============================================================================
# UPDATED app.R - WITH PROPER CORRELATION MODULE INTEGRATION
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
source("R/ui_overview.R")                  # Tab 2: Executive Overview ✅
source("R/ui_geographic_intelligence.R")   # Tab 3: Geographic Intelligence ✅
source("R/ui_correlation_analysis.R")      # Tab 4: Correlation Analysis ✅
source("R/ui_regression_models.R")         # Tab 5: Regression Models
source("R/ui_equity.R")                    # Tab 6: Equity & Disparities
source("R/ui_county_clustering.R")         # Tab 7: County Clustering
source("R/ui_timeseries_explorer.R")       # Tab 8: Time-Series Explorer
source("R/ui_policy_scenarios_expanded.R") # Tab 9: Policy Scenarios
source("R/ui_data_downloads.R")            # Tab 10: Data & Downloads
source("R/beautiful_kpi_cards.R")          # Custom KPI card UI function

# ==============================================================================
# LOAD SERVER MODULES
# ==============================================================================
source("R/server_overview.R")
source("R/server_exploration.R")
source("R/server_analysis.R")
source("R/server_geographic_intelligence.R")
source("R/server_correlation_analysis.R")  # ✅ CORRELATION MODULE

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
  
  theme = NULL,
  windowTitle = "U.S. Food Insecurity Dashboard",
  id = "navbar",
  
  # Tab 1: Home/Landing
  ui_landing,
  
  # Tab 2: Executive Overview
  ui_overview,
  
  # Tab 3: Geographic Intelligence
  ui_geographic_intelligence,
  
  # ============================================================================
  # ANALYSIS DROPDOWN MENU (5 ANALYTICAL TOOLS)
  # ============================================================================
  navbarMenu(
    title = div(icon("chart-line"), "Analysis"),
    icon = icon("chevron-down"),
    
    # Correlation Analysis
    tabPanel(
      title = div(icon("project-diagram"), "Correlation Analysis"),
      value = "correlation",
      ui_correlation_analysis
    ),
    
    # Regression Models
    tabPanel(
      title = div(icon("chart-line"), "Regression Models"),
      value = "regression",
      ui_regression_models
    ),
    
    # Equity & Disparities
    tabPanel(
      title = div(icon("balance-scale"), "Equity & Disparities"),
      value = "equity",
      ui_equity
    ),
    
    # County Clustering
    tabPanel(
      title = div(icon("layer-group"), "County Clustering"),
      value = "clustering",
      ui_county_clustering
    ),
    
    # Time-Series Explorer
    tabPanel(
      title = div(icon("clock"), "Time-Series Explorer"),
      value = "timeseries",
      ui_timeseries_explorer
    )
  ),
  
  # Tab 9: Policy Scenarios
  ui_policy_scenarios,
  
  # Tab 10: Data & Downloads
  ui_data_downloads,
  
  # ============================================================================
  # CUSTOM CSS
  # ============================================================================
  tags$head(
    # Premium Theme
    tags$link(rel = "stylesheet", type = "text/css", href = "premium_theme.css"),

    # Mobile viewport
    tags$meta(name = "viewport", content = "width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no"),
    
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
      
      /* Dropdown menu styling */
      .navbar-nav > li > .dropdown-menu {
        background: white;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        margin-top: 0;
        min-width: 250px;
        padding: 8px 0;
      }
      
      .navbar-nav > li > .dropdown-menu > li > a {
        padding: 12px 20px;
        color: #2c3e50;
        transition: all 0.2s;
        font-size: 14px;
        font-weight: 500;
      }
      
      .navbar-nav > li > .dropdown-menu > li > a:hover {
        background: #f8f9fa;
        color: #0033A0;
        padding-left: 25px;
      }
      
      .navbar-nav > li > .dropdown-menu > li.active > a {
        background: linear-gradient(135deg, #0033A0 0%, #003D82 100%);
        color: white;
        font-weight: 600;
      }
      
      .dropdown-menu i {
        margin-right: 10px;
        width: 16px;
        text-align: center;
        color: #0033A0;
      }
      
      .dropdown-menu .active i {
        color: white;
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
  
  cat("\n========================================\n")
  cat("SHINY SERVER STARTING\n")
  cat("========================================\n\n")
  
  # Data reactive
  data <- reactive({
    food_data
  })
  
  # Verify data is accessible
  cat("Data reactive created\n")
  cat("  Rows:", nrow(food_data), "\n")
  cat("  Columns:", ncol(food_data), "\n\n")

  # Landing page navigation
  observeEvent(input$start_exploring, {
    updateNavbarPage(session, "navbar", selected = "overview")
  })

  # ============================================================================
  # ACTIVE SERVER MODULES
  # ============================================================================
  
  cat("Initializing server modules...\n")
  
  # Executive Overview
  tryCatch({
    server_overview(input, output, session, data)
    cat("  ✓ Executive Overview\n")
  }, error = function(e) {
    cat("  ❌ Executive Overview error:", e$message, "\n")
  })
  
  # Exploration
  tryCatch({
    server_exploration(input, output, session, data)
    cat("  ✓ Exploration\n")
  }, error = function(e) {
    cat("  ❌ Exploration error:", e$message, "\n")
  })
  
  # Analysis
  tryCatch({
    server_analysis(input, output, session, data)
    cat("  ✓ Analysis\n")
  }, error = function(e) {
    cat("  ❌ Analysis error:", e$message, "\n")
  })
  
  # Geographic Intelligence
  tryCatch({
    server_geographic_intelligence(input, output, session, data)
    cat("  ✓ Geographic Intelligence\n")
  }, error = function(e) {
    cat("  ❌ Geographic Intelligence error:", e$message, "\n")
  })
  
  # ✨ CORRELATION ANALYSIS - THE KEY MODULE ✨
  tryCatch({
    server_correlation_analysis(input, output, session, data)
    cat("  ✓ Correlation Analysis\n")
  }, error = function(e) {
    cat("  ❌ Correlation Analysis error:", e$message, "\n")
    cat("     ", e$message, "\n")
  })
  
  cat("\n")
  
  # ============================================================================
  # PLACEHOLDER OUTPUTS FOR REMAINING TABS
  # ============================================================================
  
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
  
  cat("========================================\n")
  cat("✓ SERVER INITIALIZED SUCCESSFULLY\n")
  cat("========================================\n\n")
}

# ==============================================================================
# RUN APPLICATION
# ==============================================================================

cat("Starting Shiny application...\n\n")
shinyApp(ui = ui, server = server)