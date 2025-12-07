# ==============================================================================
# FOOD INSECURITY SHINY APP
# ==============================================================================

# Load global environment (data + theme)
source("global.R", local = TRUE)

# Required packages not in global
library(shiny)
library(bslib)
library(broom)  # regression output
library(car)    # VIF

# ==============================================================================
# LOAD HELPERS
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
# UI DEFINITION  ✅ SINGLE HEADER / WORKING STYLE
# ==============================================================================

ui <- fluidPage(

  # Custom CSS (KPI cards, typography, shadows)
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

  navbarPage(
    title = div(
      style = "display:flex; align-items:center; gap:12px;",
      if (file.exists("www/AU-Logo-on-white-small.png")) {
        tags$img(
          src = "AU-Logo-on-white-small.png",
          height = "32px"
        )
      },
      span(
        "Investigating U.S. Food Insecurity Through Data",
        style = "font-weight:700; font-size:1.4rem; color:white;"
      )
    ),

    theme = bs_theme(
      version = 5,
      bootswatch = "flatly",
      primary   = "#220BED",
      secondary = "#00B884",
      success   = "#00B884",
      info      = "#1E90FF",
      warning   = "#FFA500",
      danger    = "#FF6433",
      base_font    = font_google("Inter"),
      heading_font = font_google("Inter"),
      bg = "#F5F8FC",
      fg = "#212529"
    ),

    tabPanel("Overview", ui_overview),
    tabPanel("Exploration", ui_exploration),
    tabPanel("Analysis", ui_analysis)
  )
)

# ==============================================================================
# DEFINE SERVER
# ==============================================================================

server <- function(input, output, session) {

  # Data already prepared in global.R
  data <- reactive({
    food_data
  })

  server_overview(input, output, session, data)
  server_exploration(input, output, session, data)
  server_analysis(input, output, session, data)
}

# ==============================================================================
# RUN APP
# ==============================================================================

shinyApp(ui, server)
