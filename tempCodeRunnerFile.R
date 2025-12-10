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
source("global.R", local = TRUE)

# ==============================================================================
# LOAD REQUIRED PACKAGES
# ==============================================================================
library(shiny)
library(bslib)

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
# UI DEFINITION
# ==============================================================================

ui <- fluidPage(
  # ============================================================================
  # LOAD EXTERNAL STYLES
  # ============================================================================
  tags$head(
    # Mobile viewport
    tags$meta(name = "viewport", content = "width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no"),
    
    # Link to custom CSS
    tags$link(rel = "stylesheet", type = "text/css", href = "custom.css")
  ),

  # ============================================================================
  # CUSTOM HEADER BAR
  # ============================================================================
  div(
    class = "custom-header",
    h1(
      if (file.exists("www/AU-Logo-on-white-small.png")) {
        tags$img(
          src = "AU-Logo-on-white-small.png",
          alt = "American University Logo"
        )
      },
      "Investigating U.S. Food Insecurity Through Data"
    )
  ),

  # ============================================================================
  # TAB NAVIGATION
  # ============================================================================
  tabsetPanel(
    id = "main_tabs",
    type = "tabs",
    
    tabPanel("Overview", ui_overview),
    tabPanel("Exploration", ui_exploration),
    tabPanel("Analysis", ui_analysis)
  )
)

# ==============================================================================
# SERVER DEFINITION
# ==============================================================================

server <- function(input, output, session) {
  data <- reactive({
    food_data
  })

  server_overview(input, output, session, data)
  server_exploration(input, output, session, data)
  server_analysis(input, output, session, data)
}

# ==============================================================================
# RUN APPLICATION
# ==============================================================================

shinyApp(ui = ui, server = server)