# R/ui_exploration.R

ui_exploration <- sidebarLayout(
  sidebarPanel(
    h4("Filters"),
    selectInput(
      "state_select", "Select State(s):",
      choices = NULL, multiple = TRUE
    ),
    sliderInput(
      "year_range", "Select Year Range:",
      min = 2010, max = 2025, value = c(2020, 2025), sep = ""
    ),
    checkboxGroupInput(
      "variables", "Socioeconomic Indicators:",
      choices = c("PovertyRate", "MedianIncome", "UnemploymentRate"),
      selected = "PovertyRate"
    ),
    actionButton("update_map", "Update Map", class = "btn-primary")
  ),
  mainPanel(
    tabsetPanel(
      tabPanel("Map", leaflet::leafletOutput("map_view", height = "550px")),
      tabPanel("Trends", plotly::plotlyOutput("trend_plot", height = "450px")),
      tabPanel("Summary Table", DT::DTOutput("summary_table")),
      tabPanel("Data Viewer", DT::DTOutput("data_viewer"))
    )
  )
)
