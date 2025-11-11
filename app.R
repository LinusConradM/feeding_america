
library(shiny)
library(plotly)
library(tidyverse)
library(leaflet)
library(DT)
library(bslib)

# Source modular files 
source("R/ui_overview.R")
source("R/ui_exploration.R")
source("R/ui_analysis.R")
source("R/server_overview.R")
source("R/server_exploration.R")
source("R/server_analysis.R")

# Sample dataset (replace later with real .rds) 
food_data <- tibble(
  State = c("Alabama", "Alaska", "Arizona"),
  FoodInsecurity = c(14.2, 11.0, 12.5),
  PovertyRate = c(15.1, 10.3, 13.2),
  MedianIncome = c(52000, 68000, 60000)
)

# UI
ui <- navbarPage(
  title = "Investigating U.S. Food Insecurity Through Data",
  theme = bs_theme(bootswatch = "flatly"),
  tabPanel("Overview", ui_overview),
  tabPanel("Exploration", ui_exploration),
  tabPanel("Analysis", ui_analysis)
)

# Server
server <- function(input, output, session) {
  data <- reactive({ food_data })

  server_overview(input, output, session, data)
  server_exploration(input, output, session, data)
  server_analysis(input, output, session, data)
}

# Run App
shinyApp(ui = ui, server = server)
