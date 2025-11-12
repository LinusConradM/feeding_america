## 1. Business Logic Section 
## U.S. Food Insecurity Dashboard

# Load Core Libraries
library(shiny)
library(plotly)
library(tidyverse)
library(leaflet)
library(DT)
library(bslib)

# Placeholder for Data Loading
food_data <- tibble(
  State = c("Alabama", "Alaska", "Arizona", "Arkansas", "California", 
            "Colorado", "Connecticut", "Delaware", "Florida", "Georgia"),
  FoodInsecurity = c(14.2, 11.0, 12.5, 15.3, 10.8, 9.2, 9.5, 11.3, 12.1, 13.5),
  PovertyRate = c(15.1, 10.3, 13.2, 16.2, 12.3, 9.3, 9.8, 11.4, 12.7, 13.9),
  MedianIncome = c(52000, 68000, 60000, 49000, 78000, 72000, 79000, 68000, 57000, 58000),
  Population = c(5024279, 733391, 7151502, 3011524, 39538223, 5773714, 3605944, 989948, 21538187, 10711908),
  lat = c(32.806671, 61.370716, 33.729759, 34.969704, 36.116203, 39.059811, 41.597782, 39.318523, 27.766279, 33.040619),
  lng = c(-86.791130, -152.404419, -111.431221, -92.373123, -119.681564, -105.311104, -72.755371, -75.507141, -81.686783, -83.643074)
)

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

# Define Modern Theme 
theme_modern <- bs_theme(
  version = 5,
  bootswatch = "flatly",
  primary = "#220BED",      
  secondary = "#00B884",    
  success = "#00B884",
  info = "#1E90FF",
  warning = "#FFA500",
  danger = "#FF6433",       
  base_font = font_google("Inter"),
  heading_font = font_google("Inter"),
  bg = "#F5F8FC",
  fg = "#212529"
)

# Define UI
ui <- tagList(

  # App Header Bar
  div(
    class = "app-header",
    "Investigating U.S. Food Insecurity Through Data"
  ),

  # Navigation Bar
  navbarPage(
    title = NULL,
    theme = theme_modern,
    tabPanel("Overview", ui_overview),
    tabPanel("Exploration", ui_exploration),
    tabPanel("Analysis", ui_analysis)
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

# Define Server
server <- function(input, output, session) {
  data <- reactive({ food_data })
  
  server_overview(input, output, session, data)
  server_exploration(input, output, session, data)
  server_analysis(input, output, session, data)
}

## 4. Launch Shiny Application

shinyApp(ui, server)
