## 1. Business Logic Section 
library(shiny)
library(plotly)
library(tidyverse)
library(leaflet)
library(DT)
library(bslib)
library(readxl)
library(janitor)

# Load dataset
source("global.R", local = TRUE)

# Helper function
percent_change <- function(current, previous) {
  if (is.na(current) || is.na(previous) || previous == 0) return(NA_real_)
  round(((current - previous) / previous) * 100, 1)
}

# Custom theme
my_theme <- theme_minimal() +
  theme(
    text = element_text(size = 12),
    plot.title = element_text(hjust = 0.5, size = 16, face = "bold"),
    axis.title = element_text(size = rel(1.2)),
    axis.text  = element_text(size = rel(1.1)),
    panel.grid.major = element_line(color = "grey85")
  )

# ---- IMPORTANT: Theme must come BEFORE UI files ----
theme_modern <- bs_theme(
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
)

# UI Layout
source("R/ui_overview.R", local = TRUE)
source("R/ui_exploration.R", local = TRUE)
source("R/ui_analysis.R", local = TRUE)

# ------------------------------
# FINAL / CORRECT UI DEFINITION
# ------------------------------
ui <- fluidPage(

  # Title Bar Header
  div(
    class = "app-header",
    style = "display: flex; align-items: center; gap: 12px; padding-left: 40px; background-color:#220BED; color:white; padding:12px;",

    if (file.exists("www/AU-Logo-on-white-small.png")) {
      tags$img(
        src = "AU-Logo-on-white-small.png",
        height = "38px",
        style = "margin-right:10px;"
      )
    },

    span(
      "Investigating U.S. Food Insecurity Through Data",
      style = "font-weight:700; font-size:1.6rem;"
    )
  ),

  # Navigation Tabs
  navbarPage(
    title = NULL,
    theme = theme_modern,

    header = tags$head(
      tags$link(rel = "stylesheet", type = "text/css", href = "custom.css")
    ),

    tabPanel("Overview",    ui_overview),
    tabPanel("Exploration", ui_exploration),
    tabPanel("Analysis",    ui_analysis)
  )
)

## 3. Server Section

source("R/kpi_helpers.R", local = TRUE)
source("R/server_overview.R", local = TRUE)
source("R/server_exploration.R", local = TRUE)
source("R/server_analysis.R", local = TRUE)

server <- function(input, output, session) {
  dataset <- reactive({ fd_basket })

  server_overview(input, output, session, dataset)
  server_exploration(input, output, session, dataset)
  server_analysis(input, output, session, dataset)
}

## 4. Launch Shiny App
shinyApp(ui = ui, server = server)
