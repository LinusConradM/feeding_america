# R/ui_exploration.R

ui_exploration <- sidebarLayout(

  # Sidebar Filters ----------------------------------------------------
  sidebarPanel(
    h4("Filters"),

    # Multi-state filter
    selectInput(
      "state_select", "Select State(s):",
      choices = NULL, multiple = TRUE
    ),

    # Year range filter
    sliderInput(
      "year_range", "Select Year Range:",
      min = 2010, max = 2025,
      value = c(2019, 2023), sep = ""
    ),

    # Actual variables from fd_basket
    checkboxGroupInput(
      "variables", "Food Insecurity Indicators:",
      choices = c(
        "Overall Food Insecurity Rate"   = "overall_food_insecurity_rate",
        "Child Food Insecurity Rate"     = "child_food_insecurity_rate",
        "Cost per Meal"                  = "cost_per_meal",
        "SNAP Threshold"                 = "snap_threshold",
        "Rural/Urban Code (2013)"        = "rural_urban_continuum_code_2013"
      ),
      selected = "overall_food_insecurity_rate"
    ),

    actionButton("update_map", "Update Map", class = "btn-primary")
  ),

  # Main Panel ---------------------------------------------------------
  mainPanel(
    tabsetPanel(
      tabPanel("Map", leaflet::leafletOutput("map_view", height = "550px")),
      tabPanel("Trends", plotly::plotlyOutput("trend_plot", height = "450px")),
      tabPanel("Summary Table", DT::DTOutput("summary_table")),
      tabPanel("Data Viewer", DT::DTOutput("data_viewer"))
    )
  )
)
