# ==============================================================================
# UI: EXPLORATION TAB - COMPLETE WORKING VERSION
# ==============================================================================

ui_exploration <- tabPanel(
  "Exploration",
  
  fluidPage(
    
    sidebarLayout(
      
      # ========================================================================
      # LEFT SIDEBAR - FILTERS
      # ========================================================================
      
      sidebarPanel(
        width = 3,
        
        h4("Filters", style = "margin-top: 0;"),
        
        # State Selector (FIXED - explicit state list)
        selectInput(
          "state_filter",
          "Select State(s):",
          choices = c(
            "All States" = "ALL",
            "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA",
            "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
            "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
            "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
            "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"
          ),
          selected = "ALL",
          multiple = TRUE
        ),
        
        # County Selector (will populate based on state)
        selectInput(
          "county_filter",
          "Select County:",
          choices = "Select one or more counties",
          multiple = TRUE
        ),
        
        # Year Selector
        selectInput(
          "year_filter",
          "Select Year:",
          choices = 2009:2023,
          selected = 2023
        ),
        
        # Period Slider
        sliderInput(
          "period_filter",
          "Select Period:",
          min = 2009,
          max = 2023,
          value = c(2009, 2023),
          step = 1,
          sep = ""
        ),
        
        # Indicator Radio Buttons
        radioButtons(
          "indicator_filter",
          "Food Insecurity Indicators:",
          choices = c(
            "Overall FI Rate",
            "# Food Insecure Persons",
            "Black FI Rate",
            "Hispanic FI Rate",
            "White FI Rate",
            "SNAP Threshold",
            "% FI < SNAP",
            "% FI > SNAP",
            "Child FI Rate",
            "# Food Insecure Children",
            "% FI Children <185% FPL",
            "% FI Children >185% FPL",
            "Cost Per Meal",
            "Weekly $ Needed",
            "Annual Shortfall"
          ),
          selected = "Overall FI Rate"
        ),
        
        # Update Map Button
        actionButton(
          "update_map",
          "Update Map",
          icon = icon("refresh"),
          class = "btn-primary",
          style = "width: 100%; margin-top: 20px;"
        )
      ),
      
      # ========================================================================
      # RIGHT MAIN PANEL - TABS
      # ========================================================================
      
      mainPanel(
        width = 9,
        
        tabsetPanel(
          id = "exploration_tabs",
          
          # ==================================================================
          # TAB 1: MAP
          # ==================================================================
          tabPanel(
            "Map",
            
            # THIS IS WHERE THE MAP GOES!
            leafletOutput("us_county_map", height = "700px")
          ),
          
          # ==================================================================
          # TAB 2: TRENDS
          # ==================================================================
          tabPanel(
            "Trends",
            
            plotlyOutput("trends_plot", height = "600px")
          ),
          
          # ==================================================================
          # TAB 3: SUMMARY TABLE
          # ==================================================================
          tabPanel(
            "Summary Table",
            
            DT::DTOutput("summary_table")  # Use explicit namespace
          ),
          
          # ==================================================================
          # TAB 4: DATA VIEWER
          # ==================================================================
          tabPanel(
            "Data Viewer",
            
            DT::DTOutput("data_viewer")  # Use explicit namespace
          )
        )
      )
    )
  )
)
