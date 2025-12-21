# ==============================================================================
# CORRECTED app.R - FIXED DUPLICATE ID ISSUE
# ==============================================================================
# Uses JavaScript to create submenu dynamically - NO duplicate IDs!
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
source("R/global_controls.R")
source("R/ui_landing.R")
source("R/ui_overview.R")
source("R/ui_geographic_intelligence.R")
source("R/ui_correlation_analysis.R")
source("R/ui_regression_models.R")
source("R/ui_equity.R")
source("R/ui_county_clustering.R")
source("R/ui_timeseries_explorer.R")
source("R/ui_policy_scenarios_expanded.R")
source("R/ui_data_downloads.R")
source("R/beautiful_kpi_cards.R")

# ==============================================================================
# LOAD SERVER MODULES
# ==============================================================================
source("R/server_overview.R")
source("R/server_exploration.R")
source("R/server_analysis.R")
source("R/server_geographic_intelligence.R")
source("R/server_correlation_analysis.R")
source("R/server_regression_models.R")

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
  # ANALYSIS DROPDOWN MENU
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
    
    # REGRESSION MODELS - SINGLE TAB (submenu created via JavaScript)
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
  # CUSTOM CSS + JAVASCRIPT FOR SUBMENU
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
      /* Modern Navbar */
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
      
      /* Dropdown menu */
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
      
      /* Nested submenu */
      .dropdown-submenu {
        position: relative;
      }
      
      .dropdown-submenu > .dropdown-menu {
        top: 0;
        left: 100%;
        margin-top: -6px;
        margin-left: -1px;
        max-height: 80vh;
        overflow-y: auto;
      }
      
      .dropdown-submenu:hover > .dropdown-menu {
        display: block;
      }
      
      .dropdown-submenu > a:after {
        content: '\\f054';
        font-family: 'FontAwesome';
        float: right;
        margin-left: 10px;
        opacity: 0.5;
        font-size: 10px;
      }
      
      /* Dropdown header */
      .dropdown-header {
        padding: 8px 20px;
        font-size: 11px;
        color: #6c757d;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
      }
      
      /* Divider */
      .dropdown-divider {
        height: 1px;
        margin: 8px 0;
        overflow: hidden;
        background-color: #e9ecef;
      }
      
      body {
        font-family: 'Inter', sans-serif;
        background-color: #f8f9fa;
      }
    ")),
    
    # JavaScript for submenu
    tags$script(HTML("
      $(document).ready(function() {
        
        // Find Regression Models link
        var regressionLink = $('a[data-value=\"regression\"]').parent();
        
        if (regressionLink.length > 0) {
          regressionLink.addClass('dropdown-submenu');
          
          // Create submenu
          var submenu = `
            <ul class='dropdown-menu'>
              <li class='dropdown-header'>Basic Regression</li>
              <li><a href='#' data-model='linear'><i class='fa fa-minus'></i> Linear Regression</a></li>
              <li><a href='#' data-model='poly2'><i class='fa fa-minus'></i> Polynomial (2)</a></li>
              <li><a href='#' data-model='poly3'><i class='fa fa-minus'></i> Polynomial (3)</a></li>
              
              <li class='dropdown-divider'></li>
              <li class='dropdown-header'>Regularized</li>
              <li><a href='#' data-model='ridge'><i class='fa fa-minus'></i> Ridge (L2)</a></li>
              <li><a href='#' data-model='lasso'><i class='fa fa-minus'></i> LASSO (L1)</a></li>
              <li><a href='#' data-model='elasticnet'><i class='fa fa-minus'></i> Elastic Net</a></li>
              
              <li class='dropdown-divider'></li>
              <li class='dropdown-header'>Panel & Distribution</li>
              <li><a href='#' data-model='fixed_effects'><i class='fa fa-minus'></i> Fixed Effects</a></li>
              <li><a href='#' data-model='quantile_50'><i class='fa fa-minus'></i> Quantile (50th)</a></li>
              <li><a href='#' data-model='quantile_75'><i class='fa fa-minus'></i> Quantile (75th)</a></li>
              
              <li class='dropdown-divider'></li>
              <li class='dropdown-header'>Ensemble</li>
              <li><a href='#' data-model='random_forest_reg'><i class='fa fa-minus'></i> Random Forest</a></li>
              <li><a href='#' data-model='xgboost_reg'><i class='fa fa-minus'></i> XGBoost</a></li>
              <li><a href='#' data-model='gam'><i class='fa fa-minus'></i> GAM</a></li>
              <li><a href='#' data-model='interaction'><i class='fa fa-minus'></i> Interactions</a></li>
              
              <li class='dropdown-divider'></li>
              <li class='dropdown-header'>Classification</li>
              <li><a href='#' data-model='logistic_binary'><i class='fa fa-minus'></i> Logistic (Binary)</a></li>
              <li><a href='#' data-model='logistic_multi'><i class='fa fa-minus'></i> Multinomial</a></li>
              <li><a href='#' data-model='random_forest_class'><i class='fa fa-minus'></i> RF Class</a></li>
              <li><a href='#' data-model='xgboost_class'><i class='fa fa-minus'></i> XGB Class</a></li>
              <li><a href='#' data-model='lda'><i class='fa fa-minus'></i> LDA</a></li>
            </ul>
          `;
          
          regressionLink.append(submenu);
          
          // Handle clicks
          regressionLink.find('a[data-model]').on('click', function(e) {
            e.preventDefault();
            var model = $(this).data('model');
            
            // Navigate to tab
            $('a[data-value=\"regression\"]').tab('show');
            
            // Set model type
            setTimeout(function() {
              $('#reg_model_type').val(model).trigger('change');
            }, 100);
          });
        }
      });
    "))
  )
)

# ==============================================================================
# SERVER
# ==============================================================================

server <- function(input, output, session) {
  
  cat("\n========================================\n")
  cat("SHINY SERVER STARTING\n")
  cat("========================================\n\n")
  
  data <- reactive({ food_data })
  
  cat("Data reactive created\n")
  cat("  Rows:", nrow(food_data), "\n")
  cat("  Columns:", ncol(food_data), "\n\n")

  observeEvent(input$start_exploring, {
    updateNavbarPage(session, "navbar", selected = "overview")
  })

  cat("Initializing server modules...\n")
  
  tryCatch({ server_overview(input, output, session, data); cat("  ✓ Executive Overview\n") }, error = function(e) { cat("  ❌ Overview:", e$message, "\n") })
  tryCatch({ server_exploration(input, output, session, data); cat("  ✓ Exploration\n") }, error = function(e) { cat("  ❌ Exploration:", e$message, "\n") })
  tryCatch({ server_analysis(input, output, session, data); cat("  ✓ Analysis\n") }, error = function(e) { cat("  ❌ Analysis:", e$message, "\n") })
  tryCatch({ server_geographic_intelligence(input, output, session, data); cat("  ✓ Geographic Intelligence\n") }, error = function(e) { cat("  ❌ Geographic:", e$message, "\n") })
  tryCatch({ server_correlation_analysis(input, output, session, data); cat("  ✓ Correlation Analysis\n") }, error = function(e) { cat("  ❌ Correlation:", e$message, "\n") })
  tryCatch({ server_regression_models(input, output, session, data); cat("  ✓ Regression Models\n") }, error = function(e) { cat("  ❌ Regression:", e$message, "\n") })
  
  # Placeholders
  output$absolute_disparity <- renderText({ "--" })
  output$relative_disparity <- renderText({ "--" })
  output$gini_coef <- renderText({ "--" })
  output$iqr_value <- renderText({ "--" })
  output$metro_fi_rate <- renderText({ "--" })
  output$rural_fi_rate <- renderText({ "--" })
  output$rural_metro_gap <- renderText({ "--" })
  output$total_clusters <- renderText({ "--" })
  output$cluster_ss <- renderText({ "--" })
  output$cluster_variance <- renderText({ "--" })
  output$cluster_interpretations <- renderUI({ HTML("<p style='text-align: center; color: #6c757d;'>Run clustering</p>") })
  output$pre_covid_avg <- renderText({ "--" })
  output$covid_avg <- renderText({ "--" })
  output$post_covid_avg <- renderText({ "--" })
  output$baseline_fi <- renderText({ "--" })
  output$projected_fi <- renderText({ "--" })
  output$fi_reduction <- renderText({ "--" })
  output$people_helped <- renderText({ "--" })
  output$cost_estimate <- renderText({ "--" })
  
  cat("\n✓ SERVER INITIALIZED\n\n")
}

shinyApp(ui = ui, server = server)