# R/ui_exploration.R

ui_exploration <- sidebarLayout(

  # Sidebar Filters 
  sidebarPanel(
    width = 3,
    h4("Filters"),
    hr(),

    selectInput(
      "state_select", "Select State(s):",
      choices = NULL,
      multiple = TRUE
    ),

    sliderInput(
      "year_range", "Select Year Range:",
      min = 2010,
      max = 2025,
      value = c(2019, 2023),
      sep = ""
    ),

    checkboxGroupInput(
  "variables", "Food Insecurity Indicators:",
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
)
,

    actionButton("update_map", "Update Map", class = "btn-primary")
  ),

  # Main Panel 
  mainPanel(
    tabsetPanel(

      tabPanel("Map",
        leaflet::leafletOutput("map_view", height = "550px")
      ),

      #  TREND PANEL 
      # Trends Panel Disclaimers 
tabPanel("Trends",
  tabsetPanel(

    # STATE TRENDS
    tabPanel("State Trends",
      htmltools::tags$div(
        style="color:#AA0000; font-size:12px; margin-bottom:10px;",
        "Note: All food insecurity estimates shown here are modeled approximations from Feeding America's Map the Meal Gap dataset."
      ),
      plotly::plotlyOutput("trend_state", height = "450px")
    ),

    # RACIAL DISPARITIES
    tabPanel("Racial Disparities",
      htmltools::tags$div(
        style="color:#AA5500; font-size:12px; margin-bottom:10px;",
        "Caution: Race/ethnicity estimates have wide uncertainty due to small sample sizes. Feeding America recommends interpreting these values directionally, not as precise measurements."
      ),
      plotly::plotlyOutput("trend_race", height = "450px")
    ),

    # CHILD FOOD INSECURITY
    tabPanel("Child Food Insecurity",
      htmltools::tags$div(
        style="color:#AA0000; font-size:12px; margin-bottom:10px;",
        "Note: Child food insecurity estimates are modeled values. Small geographic areas may have additional estimation uncertainty."
      ),
      plotly::plotlyOutput("trend_child", height = "450px")
    ),

    # COST BURDEN
    tabPanel("Cost Burden",
      htmltools::tags$div(
        style="color:#D95F0E; font-size:12px; margin-bottom:10px;",
        "Warning: Feeding America changed its methodology for calculating meal cost and food budget shortfall in 2023. Estimates in 2023 are NOT directly comparable to earlier years."
      ),
      plotly::plotlyOutput("trend_cost", height = "450px")
    ),

    # RURAL VS URBAN
    tabPanel("Rural vs Urban",
      htmltools::tags$div(
        style="color:#444444; font-size:12px; margin-bottom:10px;",
        "Note: Rural–Urban Continuum Codes reflect county classifications that may differ in interpretation across states."
      ),
      plotly::plotlyOutput("trend_rural", height = "450px")
    ),

    # REGIONAL TRENDS 
    tabPanel("Regional Trends",
      htmltools::tags$div(
        style="color:#4444AA; font-size:12px; margin-bottom:10px;",
        "Note: Regional averages combine modeled county estimates. Connecticut county boundaries changed in 2022–2023, which may affect regional aggregation."
      ),
      plotly::plotlyOutput("trend_region", height = "450px")
    ),

    # INEQUALITY GAPS 
    tabPanel("Inequality Gaps",
      htmltools::tags$div(
        style="color:#AA0000; font-size:12px; margin-bottom:10px;",
        "Important: Inequality gap metrics (Black–White FI gap, Child Income FI gap) are derived from modeled estimates and should be interpreted cautiously."
      ),
      plotly::plotlyOutput("trend_gap", height = "450px")
    )
  )
)
,

      tabPanel("Summary Table", DT::DTOutput("summary_table")),
      tabPanel("Data Viewer",   DT::DTOutput("data_viewer"))

    )
  )
)
