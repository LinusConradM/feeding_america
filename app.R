# ==============================================================================
# FOOD INSECURITY SHINY APP - DIAGNOSTIC VERSION
# ==============================================================================

cat("\n========================================\n")
cat("STARTING APP\n")
cat("========================================\n")

# Load global environment (data + theme)
cat("Sourcing global.R...\n")
source("global.R", local = TRUE)
cat("✓ global.R loaded\n")

# Check if food_data exists
if (exists("food_data")) {
  cat("✓ food_data exists:", nrow(food_data), "rows\n")
} else {
  cat("✗ food_data NOT FOUND!\n")
}

library(shiny)
library(bslib)

cat("✓ All app packages loaded\n")

# ==============================================================================
# LOAD UI MODULES
# ==============================================================================

cat("Loading UI modules...\n")
source("R/ui_overview.R")
source("R/ui_exploration.R")
source("R/ui_analysis.R")
cat("✓ UI modules loaded\n")

# ==============================================================================
# LOAD SERVER MODULES
# ==============================================================================

cat("Loading server modules...\n")
source("R/server_overview.R")
source("R/server_exploration.R")
source("R/server_analysis.R")
cat("✓ Server modules loaded\n")

# Test if server_analysis exists
cat("server_analysis function exists:", exists("server_analysis"), "\n")

# ==============================================================================
# UI DEFINITION
# ==============================================================================

ui <- fluidPage(
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
        tags$img(src = "AU-Logo-on-white-small.png", height = "32px")
      },
      span("Investigating U.S. Food Insecurity Through Data",
           style = "font-weight:700; font-size:1.4rem; color:white;")
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
  
  cat("\n========================================\n")
  cat("SERVER FUNCTION CALLED\n")
  cat("========================================\n")

  # Data already prepared in global.R
  data <- reactive({
    cat("Creating data reactive\n")
    food_data
  })
  
  # Test data reactive
  cat("Testing data reactive...\n")
  test_data <- isolate(data())
  cat("Data has", nrow(test_data), "rows\n")

  cat("\nCalling server modules...\n")
  server_overview(input, output, session, data)
  cat("✓ server_overview called\n")
  
  server_exploration(input, output, session, data)
  cat("✓ server_exploration called\n")
  
  server_analysis(input, output, session, data)
  cat("✓ server_analysis called\n")
  
  cat("\n========================================\n")
  cat("SERVER INITIALIZATION COMPLETE\n")
  cat("========================================\n\n")
}

# ==============================================================================
# RUN APP
# ==============================================================================

cat("\nStarting Shiny app...\n\n")
shinyApp(ui, server)