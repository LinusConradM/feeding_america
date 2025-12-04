## 1. Business Logic Section 
##    U.S. Food Insecurity Dashboard

## 1. Business Logic Section 
library(shiny)
library(plotly)
library(tidyverse)
library(leaflet)
library(DT)
library(bslib)
library(readxl)
library(janitor)

# dataset loads
source("global.R", local = TRUE)


# Helper Function
percent_change <- function(current, previous) {
  if (is.na(current) || is.na(previous) || previous == 0) return(NA_real_)
  round(((current - previous) / previous) * 100, 1)
}

# Custom ggplot Theme
my_theme <- theme_minimal() +
  theme(
    text = element_text(size = 12),
    plot.title = element_text(hjust = 0.5, size = 16, face = "bold"),
    axis.title = element_text(size = rel(1.2)),
    axis.text  = element_text(size = rel(1.1)),
    panel.grid.major = element_line(color = "grey85"),
    strip.text = element_text(size = 13, face = "bold"),
    strip.background = element_rect(fill = "grey90", color = NA)
  )

## 2. User Interface Section

# Source Modular UI Components
if (!file.exists("R/ui_overview.R")) stop("Missing R/ui_overview.R file.")
if (!file.exists("R/ui_exploration.R")) stop("Missing R/ui_exploration.R file.")
if (!file.exists("R/ui_analysis.R")) stop("Missing R/ui_analysis.R file.")

source("R/ui_overview.R", local = TRUE)
source("R/ui_exploration.R", local = TRUE)
source("R/ui_analysis.R", local = TRUE)


# Defining theme
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

ui <- tagList(

  # App Header
  div(
    class = "app-header",
    style = "padding: 12px; font-size: 22px; font-weight: bold; 
             background-color: #220BED; color: white; text-align: center;",
    "Investigating U.S. Food Insecurity Through Data"
  ),

  # Navigation Bar With Theme Applied
  navbarPage(
    title = NULL,
    theme = theme_modern,

    tabPanel("Overview",    ui_overview),
    tabPanel("Exploration", ui_exploration),
    tabPanel("Analysis",    ui_analysis)
  )
)


## 3. Server Section

# Source Modular Server Components
if (!file.exists("R/server_overview.R")) stop("Missing R/server_overview.R file.")
if (!file.exists("R/server_exploration.R")) stop("Missing R/server_exploration.R file.")
if (!file.exists("R/server_analysis.R")) stop("Missing R/server_analysis.R file.")

source("R/server_overview.R", local = TRUE)
source("R/server_exploration.R", local = TRUE)
source("R/server_analysis.R", local = TRUE)


# Server Logic

server <- function(input, output, session) {

  # Reactive dataset coming from global.R
  data <- reactive({
    fd_basket   # dataset loaded in global.R
  })

  # Call each module
  server_overview(input, output, session, data)
  server_exploration(input, output, session, data)
  server_analysis(input, output, session, data)
}


## 4. Launch Shiny Application
shinyApp(ui, server)
