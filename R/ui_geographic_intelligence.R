# ==============================================================================
# UI MODULE: GEOGRAPHIC INTELLIGENCE
# ==============================================================================
# PURPOSE: Interactive geospatial analysis with hot-spot detection
# CAPABILITIES: Choropleth maps, time-slider, county profiles, hot-spot overlay
# TEAM: Conrad, Sharon, Ryann, Alex
# ==============================================================================

ui_geographic_intelligence <- tabPanel(
  "Geographic Intelligence",
  value = "geographic",
  
  fluidPage(
    # Page Header
    fluidRow(
      column(
        12,
        h2(
          icon("map-marked-alt"), " Interactive Geospatial Intelligence",
          style = "color: #2c3e50; font-weight: 600; margin-bottom: 10px;"
        ),
        p(
          "Identify geographic patterns, hot spots, and spatial clusters of food insecurity",
          style = "color: #6c757d; font-size: 16px; margin-bottom: 30px;"
        )
      )
    ),
    
    # ========================================================================
    # MAP CONTROLS ROW
    # ========================================================================
    fluidRow(
      style = "margin-bottom: 20px;",
      
      column(
        3,
        div(
          style = "background: white; padding: 20px; border-radius: 10px;
                   box-shadow: 0 2px 8px rgba(0,0,0,0.08);",
          h5("Map Variable", style = "margin-top: 0;"),
          selectInput(
            "map_variable",
            NULL,
            choices = c(
              "Food Insecurity Rate" = "fi_rate",
              "Poverty Rate" = "poverty",
              "Unemployment Rate" = "unemployment",
              "Median Income" = "income",
              "Cost per Meal" = "cost"
            ),
            selected = "fi_rate"
          ),
          
          hr(),
          
          h5("Display Options"),
          checkboxInput("show_hotspots", "Show Hot-Spot Clusters", FALSE),
          checkboxInput("show_labels", "Show County Labels", FALSE),
          checkboxInput("show_state_borders", "Emphasize State Borders", TRUE),
          
          hr(),
          
          actionButton(
            "export_map",
            "Export Map",
            icon = icon("download"),
            style = "width: 100%; background: #0033A0; color: white; border: none;"
          )
        )
      ),
      
      column(
        9,
        div(
          style = "background: white; padding: 20px; border-radius: 10px;
                   box-shadow: 0 2px 8px rgba(0,0,0,0.08); height: 600px;",
          
          # Interactive Leaflet Map
          leaflet::leafletOutput("county_map", height = "550px")
        )
      )
    ),
    
    # ========================================================================
    # TIME SLIDER & ANIMATION
    # ========================================================================
    fluidRow(
      style = "margin-bottom: 20px;",
      column(
        12,
        div(
          style = "background: white; padding: 20px; border-radius: 10px;
                   box-shadow: 0 2px 8px rgba(0,0,0,0.08);",
          fluidRow(
            column(
              10,
              sliderInput(
                "map_year_slider",
                "Time Period",
                min = 2009,
                max = 2023,
                value = 2023,
                step = 1,
                sep = "",
                width = "100%"
              )
            ),
            column(
              2,
              style = "padding-top: 25px;",
              actionButton(
                "animate_map",
                "Animate",
                icon = icon("play"),
                style = "width: 100%;"
              )
            )
          )
        )
      )
    ),
    
    # ========================================================================
    # COUNTY PROFILE PANEL (Click-through)
    # ========================================================================
    fluidRow(
      column(
        4,
        div(
          style = "background: white; padding: 25px; border-radius: 10px;
                   box-shadow: 0 2px 8px rgba(0,0,0,0.08);",
          h4(
            icon("map-pin"), " Selected County Profile",
            style = "margin-top: 0; color: #2c3e50;"
          ),
          hr(),
          
          div(
            style = "text-align: center; padding: 40px 0; color: #6c757d;",
            icon("hand", style = "font-size: 40px; color: #0033A0; margin-bottom: 15px;"),
            p("Click a county on the map to view detailed profile",
              style = "font-size: 14px;")
          ),
          
          # Placeholder for selected county data
          htmlOutput("selected_county_profile")
        )
      ),
      
      column(
        8,
        div(
          style = "background: white; padding: 25px; border-radius: 10px;
                   box-shadow: 0 2px 8px rgba(0,0,0,0.08);",
          h4(
            icon("chart-area"), " County Trend (2009-2023)",
            style = "margin-top: 0; color: #2c3e50;"
          ),
          hr(),
          
          # County trend chart
          plotOutput("county_trend_chart", height = "250px")
        )
      )
    ),
    
    # ========================================================================
    # SPATIAL STATISTICS SUMMARY
    # ========================================================================
    fluidRow(
      style = "margin-top: 20px;",
      
      column(
        3,
        div(
          style = "background: linear-gradient(135deg, #0033A0 0%, #003D82 100%);
                   padding: 25px; border-radius: 10px; color: white;
                   box-shadow: 0 4px 15px rgba(0, 51, 160, 0.3);",
          div(icon("exclamation-triangle", style = "font-size: 2.5em; margin-bottom: 10px;")),
          h5("Hot-Spot Counties", style = "margin: 10px 0 5px 0;"),
          h3(textOutput("hotspot_count"), style = "margin: 0; font-size: 36px;"),
          p("High-high clusters (p < 0.05)", style = "margin-top: 10px; font-size: 13px; opacity: 0.9;")
        )
      ),
      
      column(
        3,
        div(
          style = "background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
                   padding: 25px; border-radius: 10px; color: white;
                   box-shadow: 0 4px 15px rgba(40, 167, 69, 0.3);",
          div(icon("check-circle", style = "font-size: 2.5em; margin-bottom: 10px;")),
          h5("Cold-Spot Counties", style = "margin: 10px 0 5px 0;"),
          h3(textOutput("coldspot_count"), style = "margin: 0; font-size: 36px;"),
          p("Low-low clusters (p < 0.05)", style = "margin-top: 10px; font-size: 13px; opacity: 0.9;")
        )
      ),
      
      column(
        3,
        div(
          style = "background: linear-gradient(135deg, #ffc107 0%, #ff9800 100%);
                   padding: 25px; border-radius: 10px; color: white;
                   box-shadow: 0 4px 15px rgba(255, 193, 7, 0.3);",
          div(icon("chart-area", style = "font-size: 2.5em; margin-bottom: 10px;")),
          h5("Spatial Autocorrelation", style = "margin: 10px 0 5px 0;"),
          h3(textOutput("morans_i"), style = "margin: 0; font-size: 36px;"),
          p("Moran's I statistic", style = "margin-top: 10px; font-size: 13px; opacity: 0.9;")
        )
      ),
      
      column(
        3,
        div(
          style = "background: linear-gradient(135deg, #6f42c1 0%, #563d7c 100%);
                   padding: 25px; border-radius: 10px; color: white;
                   box-shadow: 0 4px 15px rgba(111, 66, 193, 0.3);",
          div(icon("layer-group", style = "font-size: 2.5em; margin-bottom: 10px;")),
          h5("Geographic Disparity", style = "margin: 10px 0 5px 0;"),
          h3(textOutput("geo_disparity"), style = "margin: 0; font-size: 36px;"),
          p("Max - Min county rate", style = "margin-top: 10px; font-size: 13px; opacity: 0.9;")
        )
      )
    )
  )
)