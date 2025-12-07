# ==============================================================================
# FOOD INSECURITY SHINY APP
# ==============================================================================

# Load global environment (data + theme)
source("global.R", local = TRUE)

# ==============================================================================
# LOAD REQUIRED PACKAGES
# ==============================================================================

# Core Shiny packages
library(shiny)
library(bslib)

# Visualization packages
library(leaflet)
library(plotly)
library(DT)

# Analysis packages
library(broom)
library(car)

cat("✓ All app packages loaded\n")

# ==============================================================================
# LOAD UI MODULES
# ==============================================================================

source("R/ui_overview.R")
source("R/ui_exploration.R")
source("R/ui_analysis.R")

# ==============================================================================
# LOAD SERVER MODULES
# ==============================================================================

source("R/server_overview.R")
source("R/server_exploration.R")
source("R/server_analysis.R")

# ==============================================================================
# DEFINE UI - IMPROVED LAYOUT
# ==============================================================================

ui <- fluidPage(
  
  theme = bslib::bs_theme(bootswatch = "flatly"),
  
  # Custom CSS for header
  tags$head(
    tags$style(HTML("
      .app-header {
        background-color: #34495e;
        color: white;
        padding: 15px 20px;
        margin-bottom: 0;
      }
      .app-header h1 {
        margin: 0;
        font-size: 24px;
        font-weight: 600;
      }
      .app-header img {
        vertical-align: middle;
        margin-right: 15px;
      }
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
      }
      .nav-tabs > li > a:hover {
        background-color: #34495e;
        color: white;
      }
      .nav-tabs > li.active > a {
        background-color: #18bc9c !important;
        color: white !important;
        border: none !important;
      }
    "))
  ),
  
  # Header section
  div(
    class = "app-header",
    h1(
      img(src = "AU-Logo-on-white-small.png", height = "30px"),
      "Investigating U.S. Food Insecurity Through Data"
    )
  ),
  
  # Tabs section
  navbarPage(
    title = NULL,  # No title in navbar since we have header above
    id = "main_tabs",
    position = "static-top",
    
    ui_overview,
    ui_exploration,
    ui_analysis
  )
)

# ==============================================================================
# DEFINE SERVER
# ==============================================================================

server <- function(input, output, session) {
  
  # Create reactive data from global.R
  data <- reactive({ food_data })
  
  # Call server modules
  server_overview(input, output, session, data)
  server_exploration(input, output, session, data)
  server_analysis(input, output, session, data)
}

# ==============================================================================
# RUN APP
# ==============================================================================

shinyApp(ui, server)
