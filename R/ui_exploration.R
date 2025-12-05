# R/ui_exploration.R

ui_exploration <- sidebarLayout(

  ############################
  # SIDEBAR
  ############################
  sidebarPanel(
    width = 3,
    h4("Filters"),
    hr(),

    # Multi-state filter
    selectizeInput(
      inputId = "state_select",
      label = "Select State(s):",
      choices = NULL,
      multiple = TRUE,
      options = list(placeholder = "Select one or more states")
    ),

    # Single year select
    selectInput(
      inputId = "year_select",
      label = "Select Year:",
      choices = 2010:2025,
      selected = 2020
    ),

    # Year range slider
    sliderInput(
      inputId = "year_range",
      label = "Select Period:",
      min = 2000,
      max = 2050,
      value = c(2010, 2025),
      sep = ""
    ),

    # Indicator selection
    checkboxGroupInput(
      inputId = "variables",
      label = "Food Insecurity Indicators:",
      choices = c(
        "Overall FI Rate" = "overall_food_insecurity_rate",
        "# Food Insecure Persons" = "number_of_food_insecure_persons_overall",

        "Black FI Rate" = "food_insecurity_rate_among_black_persons_all_ethnicities",
        "Hispanic FI Rate" = "food_insecurity_rate_among_hispanic_persons_any_race",
        "White FI Rate" = "food_insecurity_rate_among_white_non_hispanic_persons",

        "SNAP Threshold" = "snap_threshold",
        "% FI ≤ SNAP" = "percent_fi_snap_threshold",
        "% FI > SNAP" = "percent_fi_snap_threshold_2",

        "Child FI Rate" = "child_food_insecurity_rate",
        "# Food Insecure Children" = "number_of_food_insecure_children",
        "% FI Children ≤185% FPL" = "percent_food_insecure_children_in_hh_w_hh_incomes_below_185_fpl",
        "% FI Children >185% FPL" = "percent_food_insecure_children_in_hh_w_hh_incomes_above_185_fpl",

        "Cost Per Meal" = "cost_per_meal",
        "Weekly $ Needed" = "weighted_weekly_needed_by_fi",
        "Annual Shortfall" = "weighted_annual_food_budget_shortfall"
      ),
      selected = "overall_food_insecurity_rate"
    ),

    actionButton("update_map", "Update Map", class = "btn-primary")
  ),

  ############################
  # MAIN PANEL
  ############################
  mainPanel(
    tabsetPanel(

      # MAP TAB
      tabPanel("Map",
        leaflet::leafletOutput("map_view", height = "550px")
      ),

      ############################
      # TRENDS TAB
      ############################
      tabPanel("Trends",
        tabsetPanel(

          tabPanel("State Trends",
            htmltools::tags$div(
              style = "color:#AA0000; font-size:12px; margin-bottom:10px;",
              "Note: All food insecurity estimates shown are modeled approximations from Feeding America's Map the Meal Gap dataset."
            ),
            plotly::plotlyOutput("trend_state", height = "450px")
          ),

          tabPanel("Racial Disparities",
            htmltools::tags$div(
              style = "color:#AA5500; font-size:12px; margin-bottom:10px;",
              "Caution: Race/ethnicity estimates have wide uncertainty due to small sample sizes."
            ),
            plotly::plotlyOutput("trend_race", height = "450px")
          ),

          tabPanel("Child Food Insecurity",
            htmltools::tags$div(
              style = "color:#AA0000; font-size:12px; margin-bottom:10px;",
              "Note: Child food insecurity estimates are modeled values."
            ),
            plotly::plotlyOutput("trend_child", height = "450px")
          ),

          tabPanel("Cost Burden",
            htmltools::tags$div(
              style = "color:#D95F0E; font-size:12px; margin-bottom:10px;",
              "Warning: Feeding America changed cost methodology in 2023 — values are not directly comparable."
            ),
            plotly::plotlyOutput("trend_cost", height = "450px")
          ),

          tabPanel("Rural vs Urban",
            htmltools::tags$div(
              style = "color:#444444; font-size:12px; margin-bottom:10px;",
              "Rural–Urban Continuum Codes vary by state."
            ),
            plotly::plotlyOutput("trend_rural", height = "450px")
          ),

          tabPanel("Regional Trends",
            htmltools::tags$div(
              style = "color:#4444AA; font-size:12px; margin-bottom:10px;",
              "Regional averages combine modeled county estimates."
            ),
            plotly::plotlyOutput("trend_region", height = "450px")
          ),

          tabPanel("Inequality Gaps",
            htmltools::tags$div(
              style = "color:#AA0000; font-size:12px; margin-bottom:10px;",
              "Gap metrics should be interpreted cautiously."
            ),
            plotly::plotlyOutput("trend_gap", height = "450px")
          )
        )
      ),

      ############################
      # SUMMARY TABLE TAB
      ############################
      tabPanel("Summary Table",
        DT::DTOutput("summary_table")
      ),

      ############################
      # DATA VIEWER TAB
      ############################
      tabPanel("Data Viewer",
        DT::DTOutput("data_viewer")
      )
    )
  )
)
