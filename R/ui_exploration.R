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
        
        # State Selector
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
        
        # County Selector
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
          # MAP TAB
          # ==================================================================
          tabPanel(
            "Map",
            leaflet::leafletOutput("us_county_map", height = "700px")
          ),
          
          # ==================================================================
          # TRENDS TAB (WITH 7 SUB-TABS)
          # ==================================================================
          tabPanel(
            "Trends",
            
            tabsetPanel(
              
              tabPanel(
                "State Trends",
                tags$div(
                  style = "color:#AA0000; font-size:12px; margin-bottom:10px;",
                  "Note: All food insecurity estimates shown are modeled approximations."
                ),
                plotly::plotlyOutput("trend_state", height = "600px")
              ),
              
              tabPanel(
                "Racial Disparities",
                tags$div(
                  style = "color:#AA5500; font-size:12px; margin-bottom:10px;",
                  "Caution: Race/ethnicity estimates have wide uncertainty."
                ),
                plotly::plotlyOutput("trend_race", height = "600px")
              ),
              
              tabPanel(
                "Child Food Insecurity",
                tags$div(
                  style = "color:#AA0000; font-size:12px; margin-bottom:10px;",
                  "Note: Child food insecurity estimates are modeled values."
                ),
                plotly::plotlyOutput("trend_child", height = "600px")
              ),
              
              tabPanel(
                "Cost Burden",
                tags$div(
                  style = "color:#D95F0E; font-size:12px; margin-bottom:10px;",
                  "Warning: Cost methodology changed in 2023."
                ),
                plotly::plotlyOutput("trend_cost", height = "600px")
              ),
              
              tabPanel(
                "Rural vs Urban",
                tags$div(
                  style = "color:#444444; font-size:12px; margin-bottom:10px;",
                  "Rural–Urban Continuum Codes vary by state."
                ),
                plotly::plotlyOutput("trend_rural", height = "600px")
              ),
              
              tabPanel(
                "Regional Trends",
                tags$div(
                  style = "color:#4444AA; font-size:12px; margin-bottom:10px;",
                  "Regional averages combine modeled county estimates."
                ),
                plotly::plotlyOutput("trend_region", height = "600px")
              ),
              
              tabPanel(
                "Inequality Gaps",
                tags$div(
                  style = "color:#AA0000; font-size:12px; margin-bottom:10px;",
                  "Gap metrics should be interpreted cautiously."
                ),
                plotly::plotlyOutput("trend_gap", height = "600px")
              )
            )
          ),
          
          # ==================================================================
          # SUMMARY TABLE TAB
          # ==================================================================
          tabPanel(
            "Summary Table",
            DT::DTOutput("summary_table")
          ),
          
          # ==================================================================
          # DATA VIEWER TAB
          # ==================================================================
          tabPanel(
            "Data Viewer",
            DT::DTOutput("data_viewer")
          )
        )
      )
    )
  )
)
