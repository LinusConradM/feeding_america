# ==============================================================================
# SERVER: EXPLORATION TAB - AUTO-UPDATING VERSION
# ==============================================================================

server_exploration <- function(input, output, session, data) {
  
  # ==========================================================================
  # REACTIVE: FILTERED DATA (UPDATES AUTOMATICALLY)
  # ==========================================================================
  
  filtered_data <- reactive({
    
    # Start with full dataset
    result <- data()
    
    # Apply state filter
    if (!is.null(input$state_filter) && !identical(input$state_filter, "ALL")) {
      # Remove "ALL" if it's in the selection with other states
      states_to_filter <- setdiff(input$state_filter, "ALL")
      
      if (length(states_to_filter) > 0) {
        result <- result %>%
          filter(state %in% states_to_filter)
      }
    }
    
    # Apply year filter
    if (!is.null(input$year_filter)) {
      result <- result %>%
        filter(year == input$year_filter)
    }
    
    # Apply county filter (if state is selected)
    if (!is.null(input$county_filter) && !identical(input$county_filter, "ALL")) {
      counties_to_filter <- setdiff(input$county_filter, "ALL")
      
      if (length(counties_to_filter) > 0) {
        result <- result %>%
          filter(county_state %in% counties_to_filter)
      }
    }
    
    # Remove NA coordinates
    result <- result %>%
      filter(!is.na(lon), !is.na(lat))
    
    # Debug: Print what we're filtering
    cat("\n=== FILTER DEBUG ===\n")
    cat("State filter:", paste(input$state_filter, collapse = ", "), "\n")
    cat("Year filter:", input$year_filter, "\n")
    cat("Rows after filtering:", nrow(result), "\n")
    
    return(result)
  })
  
  # ==========================================================================
  # REACTIVE: SELECTED INDICATOR COLUMN
  # ==========================================================================
  
  indicator_column <- reactive({
    
    selected <- input$indicator_filter
    
    column_name <- case_when(
      selected == "Overall FI Rate" ~ "overall_food_insecurity_rate",
      selected == "# Food Insecure Persons" ~ "no_of_food_insecure_persons_overall",
      selected == "Black FI Rate" ~ "food_insecurity_rate_among_black_persons_all_ethnicities",
      selected == "Hispanic FI Rate" ~ "food_insecurity_rate_among_hispanic_persons_any_race",
      selected == "White FI Rate" ~ "food_insecurity_rate_among_white_non_hispanic_persons",
      selected == "Child FI Rate" ~ "child_food_insecurity_rate",
      selected == "Cost Per Meal" ~ "cost_per_meal",
      selected == "Annual Shortfall" ~ "weighted_annual_food_budget_shortfall",
      TRUE ~ "overall_food_insecurity_rate"
    )
    
    return(column_name)
  })
  
  # ==========================================================================
  # RENDER MAP (AUTO-UPDATES WHEN FILTERS CHANGE)
  # ==========================================================================
  
  output$us_county_map <- renderLeaflet({
    
    # Get filtered data
    map_data <- filtered_data()
    
    # Get indicator column name
    ind_col <- indicator_column()
    
    # Remove NA values for selected indicator
    # Use !!sym() for proper column reference
    map_data <- map_data %>%
      filter(!is.na(!!sym(ind_col)))
    
    # Check if data exists
    if (nrow(map_data) == 0) {
      # Create empty map with message
      return(
        leaflet() %>%
          addTiles() %>%
          setView(lng = -98.5, lat = 39.5, zoom = 4) %>%
          addControl(
            html = "<div style='background: white; padding: 10px; border-radius: 5px; font-size: 14px;'>
                    <strong>No data available for this selection</strong><br/>
                    Try different filters or select 'All States'
                    </div>",
            position = "topright"
          )
      )
    }
    
    # Create color palette using the column values
    col_values <- map_data[[ind_col]]
    
    pal <- colorNumeric(
      palette = "YlOrRd",
      domain = col_values,
      na.color = "#808080"
    )
    
    # Determine if indicator is a rate (for formatting)
    is_rate <- grepl("rate|Rate", input$indicator_filter)
    
    # Create map
    map <- leaflet(map_data) %>%
      addTiles() %>%
      setView(lng = -98.5, lat = 39.5, zoom = 4)
    
    # Add markers - build popup text separately
    map_data$popup_text <- paste0(
      "<div style='font-family: Arial; font-size: 13px; min-width: 200px;'>",
      "<strong style='font-size: 15px;'>", map_data$county_state, "</strong><br/>",
      "<hr style='margin: 8px 0; border: none; border-top: 1px solid #ccc;'/>",
      "<strong>", input$indicator_filter, ":</strong> ",
      if (is_rate) {
        paste0(round(map_data[[ind_col]] * 100, 1), "%")
      } else {
        format(round(map_data[[ind_col]]), big.mark = ",")
      },
      "<br/>",
      "<strong>Year:</strong> ", map_data$year, "<br/>",
      "<strong>Population:</strong> ", format(map_data$population, big.mark = ","),
      "</div>"
    )
    
    # Build hover label
    map_data$label_text <- paste0(
      map_data$county_state, ": ",
      if (is_rate) {
        paste0(round(map_data[[ind_col]] * 100, 1), "%")
      } else {
        format(round(map_data[[ind_col]]), big.mark = ",")
      }
    )
    
    # Add circle markers
    map <- map %>%
      addCircleMarkers(
        data = map_data,
        lng = ~lon,
        lat = ~lat,
        radius = 3,
        fillColor = ~pal(map_data[[ind_col]]),
        fillOpacity = 0.8,
        stroke = TRUE,
        weight = 0.5,
        color = "white",
        popup = ~popup_text,
        label = ~label_text
      ) %>%
      
      # Add legend
      addLegend(
        position = "bottomright",
        pal = pal,
        values = col_values,
        title = input$indicator_filter,
        labFormat = labelFormat(
          suffix = if (is_rate) "%" else "",
          transform = function(x) {
            if (is_rate) {
              round(x * 100, 1)
            } else {
              round(x, 0)
            }
          }
        ),
        opacity = 1
      )
    
    return(map)
  })
  
  # ==========================================================================
  # AUTO-ZOOM TO STATE WHEN SELECTED
  # ==========================================================================
  
  observe({
    
    # Only zoom if exactly one state selected (not "ALL")
    if (!is.null(input$state_filter) && 
        length(input$state_filter) == 1 && 
        input$state_filter != "ALL") {
      
      # Get state center
      state_data <- data() %>%
        filter(state == input$state_filter) %>%
        filter(!is.na(lon), !is.na(lat)) %>%
        slice(1)
      
      if (nrow(state_data) > 0) {
        leafletProxy("us_county_map") %>%
          setView(
            lng = state_data$lon,
            lat = state_data$lat,
            zoom = 6
          )
      }
    } else {
      # Reset to US view for multiple states or "ALL"
      leafletProxy("us_county_map") %>%
        setView(lng = -98.5, lat = 39.5, zoom = 4)
    }
  })
  
  # ==========================================================================
  # DYNAMIC COUNTY SELECTOR
  # ==========================================================================
  
  observe({
    
    selected_state <- input$state_filter
    
    if (!is.null(selected_state) && 
        length(selected_state) == 1 && 
        selected_state != "ALL") {
      
      # Get counties for selected state
      counties <- data() %>%
        filter(state == selected_state) %>%
        select(county_state) %>%
        distinct() %>%
        arrange(county_state) %>%
        pull(county_state)
      
      updateSelectInput(
        session,
        "county_filter",
        choices = c("All Counties" = "ALL", counties),
        selected = "ALL"
      )
    } else {
      updateSelectInput(
        session,
        "county_filter",
        choices = "Select a state first"
      )
    }
  })
  
  # ==========================================================================
  # TRENDS PLOT
  # ==========================================================================
  
  output$trends_plot <- renderPlotly({
    
    # Get filtered data
    trend_data <- filtered_data()
    
    if (nrow(trend_data) == 0) {
      return(
        plot_ly() %>%
          layout(
            title = "No data available for this selection",
            xaxis = list(title = ""),
            yaxis = list(title = "")
          )
      )
    }
    
    # Aggregate by year
    trend_summary <- trend_data %>%
      group_by(year) %>%
      summarise(
        fi_rate = mean(overall_food_insecurity_rate, na.rm = TRUE) * 100,
        child_fi_rate = mean(child_food_insecurity_rate, na.rm = TRUE) * 100,
        .groups = "drop"
      )
    
    # Create plot
    plot_ly(trend_summary) %>%
      add_trace(
        x = ~year, 
        y = ~fi_rate, 
        type = 'scatter', 
        mode = 'lines+markers',
        name = "Overall FI Rate",
        line = list(color = '#e74c3c', width = 2),
        marker = list(size = 6)
      ) %>%
      add_trace(
        x = ~year,
        y = ~child_fi_rate,
        type = 'scatter',
        mode = 'lines+markers',
        name = "Child FI Rate",
        line = list(color = '#3498db', width = 2),
        marker = list(size = 6)
      ) %>%
      layout(
        title = "Food Insecurity Trend Over Time",
        xaxis = list(title = "Year"),
        yaxis = list(title = "Food Insecurity Rate (%)"),
        hovermode = "x unified"
      )
  })
  
  # ==========================================================================
  # SUMMARY TABLE
  # ==========================================================================
  
  output$summary_table <- renderDT({
    
    # Get filtered data
    summary_data <- filtered_data()
    
    if (nrow(summary_data) == 0) {
      return(datatable(data.frame(Message = "No data available for this selection")))
    }
    
    # Create summary by state (avoid .data syntax)
    summary_by_state <- summary_data %>%
      group_by(state) %>%
      summarise(
        Counties = n_distinct(fips),
        `Avg FI Rate (%)` = round(mean(overall_food_insecurity_rate, na.rm = TRUE) * 100, 1),
        `Total Food Insecure` = sum(no_of_food_insecure_persons_overall, na.rm = TRUE),
        `Avg Poverty Rate (%)` = round(mean(poverty_rate, na.rm = TRUE) * 100, 1),
        `Median Income` = round(mean(median_income, na.rm = TRUE)),
        .groups = "drop"
      ) %>%
      arrange(desc(`Avg FI Rate (%)`))
    
    datatable(
      summary_by_state,
      options = list(
        pageLength = 15, 
        scrollX = TRUE
      ),
      rownames = FALSE
    )
  })
  
  # ==========================================================================
  # DATA VIEWER
  # ==========================================================================
  
  output$data_viewer <- renderDT({
    
    # Get filtered data
    view_data <- filtered_data() %>%
      select(
        year, state, county_state, 
        overall_food_insecurity_rate,
        child_food_insecurity_rate,
        poverty_rate, median_income, unemployment_rate,
        cost_per_meal, population
      ) %>%
      arrange(desc(year), state, county_state)
    
    if (nrow(view_data) == 0) {
      return(datatable(data.frame(Message = "No data available for this selection")))
    }
    
    datatable(
      view_data,
      options = list(
        pageLength = 25, 
        scrollX = TRUE
      ),
      rownames = FALSE,
      filter = "top"
    )
  })
  
} # ← CLOSING BRACE
