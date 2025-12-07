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

source("R/helpers.R", local = TRUE)
source("R/kpi_helpers.R", local = TRUE)

# ==============================================================================
# LOAD UI MODULES
# ==============================================================================

source("R/ui_overview.R", local = TRUE)
source("R/ui_exploration.R", local = TRUE)
source("R/ui_analysis.R", local = TRUE)

# ==============================================================================
# LOAD SERVER MODULES
# ==============================================================================

source("R/server_overview.R", local = TRUE)
source("R/server_exploration.R", local = TRUE)
source("R/server_analysis.R", local = TRUE)

# ==============================================================================
# UI DEFINITION  ✅ SINGLE HEADER / WORKING STYLE
# ==============================================================================

ui <- fluidPage(

  # Custom CSS (KPI cards, typography, shadows)
  tags$head(
    tags$link(rel = "stylesheet", type = "text/css", href = "custom.css")
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
# SERVER DEFINITION
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
# LAUNCH APP
# ==============================================================================

shinyApp(ui = ui, server = server)
