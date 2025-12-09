# ==============================================================================
# FOOD INSECURITY SHINY APP
# ==============================================================================
# PURPOSE: Interactive exploration and statistical analysis of U.S. food
#          insecurity data (2009-2023)
# COURSE: DATA-613 (Graduate Level)
# TEAM: Conrad, Sharon, Ryann, Alex
# INSTITUTION: American University
# ==============================================================================

# ==============================================================================
# LOAD GLOBAL ENVIRONMENT
# ==============================================================================
# Loads data, sets theme, defines required packages
source("global.R", local = TRUE)

# ==============================================================================
# LOAD REQUIRED PACKAGES
# ==============================================================================
library(shiny) # Shiny framework
library(bslib) # Bootstrap themes

cat("✓ All app packages loaded\n")

# ==============================================================================
# LOAD UI MODULES
# ==============================================================================
source("R/ui_overview.R") # Overview tab UI
source("R/ui_exploration.R") # Exploration tab UI
source("R/ui_analysis.R") # Analysis tab UI

# ==============================================================================
# LOAD SERVER MODULES
# ==============================================================================
source("R/server_overview.R") # Overview tab server
source("R/server_exploration.R") # Exploration tab server
source("R/server_analysis.R") # Analysis tab server

# ==============================================================================
# UI DEFINITION
# ==============================================================================

ui <- fluidPage(
  # ============================================================================
  # CUSTOM CSS STYLING
  # ============================================================================
  # FIXED: Title bar (#2c3e50) now matches tab bars (#2c3e50)
  # Professional color scheme with teal accents
  tags$head(
    tags$style(HTML("
    /* Navbar styling - THIS is what controls the title bar */
    .navbar-default {
      background-color: #2c3e50 !important;  /* Dark blue-gray */
      border: none !important;
    }

    .navbar-default .navbar-brand {
      color: white !important;
    }

    .navbar-default .navbar-nav > li > a {
      color: white !important;
    }

    /* Navigation tabs styling */
    .nav-tabs {
      background-color: #2c3e50;
      margin-bottom: 20px;
      border-bottom: none;
    }

    .nav-tabs > li > a {
      color: #ecf0f1;
      background-color: #2c3e50;
      border: none;
      margin-right: 2px;
      padding: 12px 20px;
    }

    .nav-tabs > li > a:hover {
      background-color: #34495e;
      color: white;
    }

    .nav-tabs > li.active > a,
    .nav-tabs > li.active > a:hover,
    .nav-tabs > li.active > a:focus {
      background-color: #18bc9c !important;  /* Teal accent */
      color: white !important;
      border: none !important;
    }
  "))
  ),

  # ============================================================================
  # NAVIGATION BAR
  # ============================================================================
  # Tabs are placed UNDER the title as requested

  navbarPage(
    # --------------------------------------------------------------------------
    # APP TITLE WITH LOGO
    # --------------------------------------------------------------------------
    title = div(
      style = "display:flex; align-items:center; gap:12px;",
      if (file.exists("www/AU-Logo-on-white-small.png")) {
        tags$img(
          src = "AU-Logo-on-white-small.png",
          height = "32px",
          alt = "American University Logo"
        )
      },
      span(
        "Investigating U.S. Food Insecurity Through Data",
        style = "font-weight:700; font-size:1.4rem; color:white;"
      )
    ),

    # --------------------------------------------------------------------------
    # THEME CONFIGURATION
    # --------------------------------------------------------------------------
    # FIXED: Primary color now #2c3e50 to match visual design

    theme = bs_theme(
      version = 5,
      bootswatch = "flatly", # Professional theme
      primary = "#2c3e50", # CHANGED: Match header/tabs
      secondary = "#18bc9c", # Teal accent
      success = "#18bc9c", # Match accent
      info = "#1E90FF", # Blue
      warning = "#FFA500", # Orange
      danger = "#FF6433", # Red
      base_font = font_google("Inter"),
      heading_font = font_google("Inter"),
      bg = "#F5F8FC", # Light background
      fg = "#212529" # Dark text
    ),

    # --------------------------------------------------------------------------
    # TAB PANELS (Under title as requested)
    # --------------------------------------------------------------------------
    tabPanel("Overview", ui_overview), # Introduction & KPIs
    tabPanel("Exploration", ui_exploration), # Maps & trends
    tabPanel("Analysis", ui_analysis) # Statistical modeling
  )
)

# ==============================================================================
# SERVER DEFINITION
# ==============================================================================

server <- function(input, output, session) {
  # ==========================================================================
  # REACTIVE DATA
  # ==========================================================================
  # Creates reactive expression for food_data from global.R

  data <- reactive({
    food_data
  })

  # ==========================================================================
  # CALL SERVER MODULES
  # ==========================================================================
  # Each module handles its tab's server logic

  server_overview(input, output, session, data) # KPI calculations
  server_exploration(input, output, session, data) # Maps & trends
  server_analysis(input, output, session, data) # Statistical models
}

# ==============================================================================
# RUN APPLICATION
# ==============================================================================

shinyApp(ui = ui, server = server)

# ==============================================================================
# END OF APP.R
# ==============================================================================
