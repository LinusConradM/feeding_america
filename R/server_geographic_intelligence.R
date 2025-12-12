# ==============================================================================
# SERVER MODULE: GEOGRAPHIC INTELLIGENCE
# ==============================================================================
# PURPOSE: Interactive geospatial analysis with hot-spot detection
# CAPABILITIES: Leaflet choropleth, spatial statistics, county profiles
# ==============================================================================

server_geographic_intelligence <- function(input, output, session, data) {
  
  # ============================================================================
  # REACTIVE DATA FILTERING
  # ============================================================================
  
  # Filter data by selected year
  year_data <- reactive({
    req(input$map_year_slider)
    data() %>%  # Call data() not data - it's a reactive!
      filter(year == input$map_year_slider) %>%
      filter(!is.na(fips), !is.na(overall_food_insecurity_rate))
  })
  
  # ============================================================================
  # LOAD AND PREPARE COUNTY SHAPEFILES
  # ============================================================================
  
  # Load US county boundaries (cached)
  us_counties <- reactive({
    req(year_data())
    
    # Get unique states in our data
    states_in_data <- unique(year_data()$state)
    
    # Load county boundaries for these states
    counties_sf <- tigris::counties(state = states_in_data, cb = TRUE, year = 2021) %>%
      st_transform(4326) %>%
      mutate(
        fips = GEOID,
        county_name = NAME,
        state_abbr = STUSPS
      ) %>%
      select(fips, county_name, state_abbr, geometry)
    
    counties_sf
  })
  
  # Join shapefile with data
  map_data <- reactive({
    req(us_counties(), year_data())
    
    # Join county boundaries with food insecurity data
    counties_with_data <- us_counties() %>%
      left_join(
        year_data() %>% select(fips, county, state, 
                                overall_food_insecurity_rate,
                                poverty_rate, median_income, 
                                cost_per_meal, unemployment_rate),
        by = "fips"
      )
    
    counties_with_data
  })
  
  # ============================================================================
  # CREATE COLOR PALETTE
  # ============================================================================
  
  color_pal <- reactive({
    req(map_data(), input$map_variable)
    
    # Get the variable to map
    var_col <- switch(input$map_variable,
                      "fi_rate" = "overall_food_insecurity_rate",
                      "poverty" = "poverty_rate",
                      "unemployment" = "unemployment_rate",
                      "income" = "median_income",
                      "cost" = "cost_per_meal")
    
    # Get values
    values <- map_data()[[var_col]]
    values <- values[!is.na(values)]
    
    # Create color palette
    if (input$map_variable %in% c("fi_rate", "poverty", "unemployment", "cost")) {
      # Higher is worse - use red scale
      colorNumeric(
        palette = c("#06D6A0", "#FFD60A", "#F4A261", "#E63946"),
        domain = values,
        na.color = "#E0E0E0"
      )
    } else {
      # Income - higher is better - use green scale
      colorNumeric(
        palette = c("#E63946", "#F4A261", "#FFD60A", "#06D6A0"),
        domain = values,
        na.color = "#E0E0E0"
      )
    }
  })
  
  # ============================================================================
  # RENDER LEAFLET MAP
  # ============================================================================
  
  output$county_map <- renderLeaflet({
    req(map_data(), color_pal(), input$map_variable)
    
    # Get the variable to map
    var_col <- switch(input$map_variable,
                      "fi_rate" = "overall_food_insecurity_rate",
                      "poverty" = "poverty_rate",
                      "unemployment" = "unemployment_rate",
                      "income" = "median_income",
                      "cost" = "cost_per_meal")
    
    var_label <- switch(input$map_variable,
                        "fi_rate" = "Food Insecurity Rate",
                        "poverty" = "Poverty Rate",
                        "unemployment" = "Unemployment Rate",
                        "income" = "Median Income",
                        "cost" = "Cost per Meal")
    
    # Create popup labels
    map_data_with_labels <- map_data() %>%
      mutate(
        popup_label = paste0(
          "<strong>", county_name, ", ", state_abbr, "</strong><br>",
          var_label, ": ",
          if (input$map_variable == "income") {
            paste0("$", scales::comma(!!sym(var_col)))
          } else if (input$map_variable == "cost") {
            paste0("$", round(!!sym(var_col), 2))
          } else {
            paste0(round(!!sym(var_col) * 100, 1), "%")
          }
        )
      )
    
    # Create leaflet map
    leaflet(map_data_with_labels) %>%
      addTiles() %>%
      addPolygons(
        fillColor = ~color_pal()(get(var_col)),
        fillOpacity = 0.7,
        color = if (input$show_state_borders) "#0033A0" else "white",
        weight = if (input$show_state_borders) 2 else 0.5,
        opacity = 1,
        popup = ~popup_label,
        layerId = ~fips,
        highlightOptions = highlightOptions(
          weight = 3,
          color = "#C41E3A",
          fillOpacity = 0.9,
          bringToFront = TRUE
        )
      ) %>%
      addLegend(
        pal = color_pal(),
        values = ~get(var_col),
        title = var_label,
        position = "bottomright",
        opacity = 0.9,
        labFormat = labelFormat(
          prefix = if (input$map_variable == "income") "$" else "",
          suffix = if (input$map_variable %in% c("fi_rate", "poverty", "unemployment")) "%" else "",
          transform = function(x) {
            if (input$map_variable %in% c("fi_rate", "poverty", "unemployment")) {
              x * 100
            } else {
              x
            }
          }
        )
      ) %>%
      setView(lng = -98.5795, lat = 39.8283, zoom = 4)
  })
  
  # ============================================================================
  # COUNTY CLICK HANDLER
  # ============================================================================
  
  selected_county <- reactiveVal(NULL)
  
  observeEvent(input$county_map_shape_click, {
    click <- input$county_map_shape_click
    if (!is.null(click$id)) {
      selected_county(click$id)
    }
  })
  
  # ============================================================================
  # COUNTY PROFILE OUTPUT
  # ============================================================================
  
  output$selected_county_profile <- renderUI({
    req(selected_county())
    
    # Get county data
    county_info <- year_data() %>%
      filter(fips == selected_county()) %>%
      slice(1)
    
    if (nrow(county_info) == 0) {
      return(
        div(
          style = "text-align: center; padding: 20px; color: #6c757d;",
          icon("exclamation-circle"),
          p("No data available for this county")
        )
      )
    }
    
    tagList(
      div(
        style = "background: #f8f9fa; padding: 15px; border-radius: 8px; margin-bottom: 15px;",
        h5(paste0(county_info$county, ", ", county_info$state),
           style = "margin: 0; color: #0033A0; font-weight: bold;"),
        p(paste0("FIPS: ", county_info$fips),
          style = "margin: 5px 0 0 0; color: #6c757d; font-size: 12px;")
      ),
      
      div(
        style = "margin-bottom: 10px;",
        strong("Food Insecurity Rate:"),
        span(
          paste0(round(county_info$overall_food_insecurity_rate * 100, 1), "%"),
          style = "float: right; color: #E63946; font-weight: bold;"
        )
      ),
      
      div(
        style = "margin-bottom: 10px;",
        strong("Poverty Rate:"),
        span(
          paste0(round(county_info$poverty_rate * 100, 1), "%"),
          style = "float: right; color: #495057;"
        )
      ),
      
      div(
        style = "margin-bottom: 10px;",
        strong("Median Income:"),
        span(
          scales::dollar(county_info$median_income),
          style = "float: right; color: #495057;"
        )
      ),
      
      div(
        style = "margin-bottom: 10px;",
        strong("Cost per Meal:"),
        span(
          paste0("$", round(county_info$cost_per_meal, 2)),
          style = "float: right; color: #495057;"
        )
      ),
      
      if (!is.na(county_info$unemployment_rate)) {
        div(
          style = "margin-bottom: 10px;",
          strong("Unemployment Rate:"),
          span(
            paste0(round(county_info$unemployment_rate * 100, 1), "%"),
            style = "float: right; color: #495057;"
          )
        )
      }
    )
  })
  
  # ============================================================================
  # COUNTY TREND CHART
  # ============================================================================
  
  output$county_trend_chart <- renderPlot({
    req(selected_county())
    
    # Get historical data for selected county
    trend_data <- data() %>%  # Call data() not data - it's a reactive!
      filter(fips == selected_county()) %>%
      arrange(year)
    
    if (nrow(trend_data) == 0) {
      return(NULL)
    }
    
    ggplot(trend_data, aes(x = year, y = overall_food_insecurity_rate * 100)) +
      geom_line(color = "#0033A0", size = 1.5) +
      geom_point(color = "#0033A0", size = 3) +
      geom_area(fill = "#0033A0", alpha = 0.2) +
      scale_x_continuous(breaks = seq(2009, 2023, by = 2)) +
      labs(
        title = paste0("Food Insecurity Trend: ", unique(trend_data$county)[1]),
        x = NULL,
        y = "Food Insecurity Rate (%)"
      ) +
      theme_minimal() +
      theme(
        plot.title = element_text(face = "bold", size = 14, color = "#1E3A5F"),
        panel.grid.minor = element_blank(),
        axis.text = element_text(size = 11),
        axis.title.y = element_text(size = 12, color = "#495057")
      )
  }, height = 250, res = 96)
  
  # ============================================================================
  # SPATIAL STATISTICS
  # ============================================================================
  
  # Hot-spot count (placeholder - requires spatial analysis)
  output$hotspot_count <- renderText({
    "TBD"
  })
  
  # Cold-spot count (placeholder)
  output$coldspot_count <- renderText({
    "TBD"
  })
  
  # Moran's I (placeholder)
  output$morans_i <- renderText({
    "TBD"
  })
  
  # Geographic disparity
  output$geo_disparity <- renderText({
    req(year_data())
    
    disparity <- max(year_data()$overall_food_insecurity_rate, na.rm = TRUE) - 
                 min(year_data()$overall_food_insecurity_rate, na.rm = TRUE)
    
    paste0(round(disparity * 100, 1), "%")
  })
  
}