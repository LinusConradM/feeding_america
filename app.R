# ==============================================================================
# FOOD INSECURITY SHINY APP
# ==============================================================================

# Load global environment (data + theme)
source("global.R", local = TRUE)

# Load required packages not in global
library(broom)  # For regression tidy output
library(car)    # For VIF calculation

# ==============================================================================
# LOAD HELPER FUNCTIONS
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
# UI DEFINITION
# ==============================================================================

ui <- fluidPage(
  
  # Custom CSS
  tags$head(
    tags$link(rel = "stylesheet", type = "text/css", href = "custom.css")
  ),
  
  # Title Bar Header
  div(
    class = "app-header",
    style = "display: flex; align-items: center; gap: 12px; padding-left: 40px; 
             background-color: #220BED; color: white; padding: 12px;",
    
    # AU Logo (if exists)
    if (file.exists("www/AU-Logo-on-white-small.png")) {
      tags$img(
        src = "AU-Logo-on-white-small.png",
        height = "38px",
        style = "margin-right: 10px;"
      )
    },
    
    # App Title
    span(
      "Investigating U.S. Food Insecurity Through Data",
      style = "font-weight: 700; font-size: 1.6rem;"
    )
  ),
  
  # Navigation Tabs
  navbarPage(
    title = NULL,
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
  
  # Make food_data reactive (loaded from global.R)
  data <- reactive({
    food_data  # This comes from global.R after bind_rows(fa_pre, fa_post)
  })
  
  # Call server modules
  server_overview(input, output, session, data)
  server_exploration(input, output, session, data)
  server_analysis(input, output, session, data)
}

# ==============================================================================
# LAUNCH APP
# ==============================================================================

shinyApp(ui = ui, server = server)
