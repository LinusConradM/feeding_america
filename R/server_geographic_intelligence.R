# ==============================================================================
# SERVER MODULE: GEOGRAPHIC INTELLIGENCE
# ==============================================================================
# PURPOSE: Interactive geospatial analysis with hot-spot detection
# CAPABILITIES: Leaflet choropleth, spatial statistics, county profiles
# TEAM: Conrad, Sharon, Ryann, Alex
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
  
  # Calculate spatial statistics (hot-spots, cold-spots, Moran's I)
  spatial_stats <- reactive({
    req(map_data())
    
    tryCatch({
      # Get complete cases only (no missing values)
      spatial_data <- map_data() %>%
        filter(!is.na(overall_food_insecurity_rate))
      
      # Need at least 10 counties for spatial analysis
      if (nrow(spatial_data) < 10) {
        return(list(
          hotspots = 0,
          coldspots = 0,
          morans_i = NA,
          error = "Insufficient data"
        ))
      }
      
      # Create spatial weights matrix based on contiguity (queen)
      neighbors <- spdep::poly2nb(spatial_data, queen = TRUE)
      
      # Convert to weights list
      weights <- spdep::nb2listw(neighbors, style = "W", zero.policy = TRUE)
      
      # Calculate Getis-Ord Gi* statistic for hot-spots
      fi_values <- spatial_data$overall_food_insecurity_rate
      
      gi_star <- spdep::localG(fi_values, weights)
      
      # Extract z-scores and p-values
      z_scores <- as.vector(gi_star)
      
      # Significant hot-spots: z > 1.96 (p < 0.05, high values surrounded by high)
      hotspots <- sum(z_scores > 1.96 & fi_values > median(fi_values, na.rm = TRUE), na.rm = TRUE)
      
      # Significant cold-spots: z < -1.96 (p < 0.05, low values surrounded by low)
      coldspots <- sum(z_scores < -1.96 & fi_values < median(fi_values, na.rm = TRUE), na.rm = TRUE)
      
      # Calculate Moran's I for spatial autocorrelation
      moran_test <- spdep::moran.test(fi_values, weights, zero.policy = TRUE)
      morans_i <- moran_test$estimate[1]
      
      list(
        hotspots = hotspots,
        coldspots = coldspots,
        morans_i = morans_i,
        z_scores = z_scores,
        error = NULL
      )
      
    }, error = function(e) {
      # Return safe defaults if spatial analysis fails
      list(
        hotspots = 0,
        coldspots = 0,
        morans_i = NA,
        error = as.character(e$message)
      )
    })
  })
  
  # Hot-spot count
  output$hotspot_count <- renderText({
    req(spatial_stats())
    
    if (!is.null(spatial_stats()$error) && spatial_stats()$error != "Insufficient data") {
      return("--")
    }
    
    as.character(spatial_stats()$hotspots)
  })
  
  # Cold-spot count
  output$coldspot_count <- renderText({
    req(spatial_stats())
    
    if (!is.null(spatial_stats()$error) && spatial_stats()$error != "Insufficient data") {
      return("--")
    }
    
    as.character(spatial_stats()$coldspots)
  })
  
  # Moran's I
  output$morans_i <- renderText({
    req(spatial_stats())
    
    if (is.na(spatial_stats()$morans_i)) {
      return("--")
    }
    
    # Format to 3 decimal places
    sprintf("%.3f", spatial_stats()$morans_i)
  })
  
  # Geographic disparity
  output$geo_disparity <- renderText({
    req(year_data())
    
    disparity <- max(year_data()$overall_food_insecurity_rate, na.rm = TRUE) - 
                 min(year_data()$overall_food_insecurity_rate, na.rm = TRUE)
    
    paste0(round(disparity * 100, 1), "%")
  })
  
  # ============================================================================
  # AI-POWERED EXPLANATIONS (MODAL DIALOGS)
  # ============================================================================
  
  # Hot-Spot Explanation
  observeEvent(input$hotspot_info, {
    req(spatial_stats())
    
    count <- spatial_stats()$hotspots
    year <- input$map_year_slider
    
    # Generate context-aware explanation
    explanation <- paste0(
      "<div style='line-height: 1.6;'>",
      "<h4 style='color: #0033A0; margin-top: 0;'>🔥 Hot-Spot Counties Explained</h4>",
      "<p><strong>What is a hot-spot?</strong><br>",
      "A hot-spot is a county with <em>high</em> food insecurity that is surrounded by other counties with <em>high</em> food insecurity. These represent statistically significant geographic clusters of need.</p>",
      
      "<p><strong>Your Data (", year, "):</strong><br>",
      "With <strong>", count, " hot-spot counties</strong>, ",
      if (count > 400) {
        "approximately 13% of U.S. counties are experiencing concentrated food insecurity. This high number suggests widespread regional challenges affecting multiple contiguous counties."
      } else if (count > 200) {
        "about 6-7% of U.S. counties show significant clustering of food insecurity. This indicates notable regional patterns of need."
      } else {
        "a smaller portion of counties show extreme clustering. This suggests food insecurity, while present, is less geographically concentrated."
      },
      "</p>",
      
      "<p><strong>Why does this matter?</strong><br>",
      "• <strong>Regional Solutions:</strong> Hot-spots suggest problems that cross county lines, requiring coordinated regional interventions<br>",
      "• <strong>Resource Targeting:</strong> Federal and state programs can focus resources on these identified clusters<br>",
      "• <strong>Root Causes:</strong> Geographic clustering often indicates shared economic, infrastructure, or policy challenges</p>",
      
      "<p><strong>Statistical Method:</strong><br>",
      "Uses <em>Getis-Ord Gi*</em> statistic with 95% confidence (p < 0.05). Each county is compared to its neighbors to identify significant local clustering patterns.</p>",
      "</div>"
    )
    
    showModal(modalDialog(
      HTML(explanation),
      title = NULL,
      footer = modalButton("Close"),
      size = "l",
      easyClose = TRUE
    ))
  })
  
  # Cold-Spot Explanation
  observeEvent(input$coldspot_info, {
    req(spatial_stats())
    
    count <- spatial_stats()$coldspots
    year <- input$map_year_slider
    
    explanation <- paste0(
      "<div style='line-height: 1.6;'>",
      "<h4 style='color: #28a745; margin-top: 0;'>✅ Cold-Spot Counties Explained</h4>",
      "<p><strong>What is a cold-spot?</strong><br>",
      "A cold-spot is a county with <em>low</em> food insecurity that is surrounded by other counties with <em>low</em> food insecurity. These represent geographic clusters of relative food security.</p>",
      
      "<p><strong>Your Data (", year, "):</strong><br>",
      "With <strong>", count, " cold-spot counties</strong>, ",
      if (count > 400) {
        "a significant portion of the U.S. shows clustered food security. This suggests effective regional systems and strong local economies in these areas."
      } else if (count > 200) {
        "several regions demonstrate stable food security patterns. These areas may offer models for intervention strategies."
      } else {
        "relatively few regions show consistent low food insecurity. This highlights the widespread nature of food insecurity challenges."
      },
      "</p>",
      
      "<p><strong>Why does this matter?</strong><br>",
      "• <strong>Success Stories:</strong> Cold-spots can be studied to understand what works in reducing food insecurity<br>",
      "• <strong>Best Practices:</strong> Policies and programs in these regions may be worth replicating<br>",
      "• <strong>Regional Strength:</strong> Clustering of low FI suggests strong regional economies and support systems</p>",
      
      "<p><strong>Comparison:</strong><br>",
      if (spatial_stats()$hotspots > count) {
        paste0("Note: There are ", spatial_stats()$hotspots - count, " more hot-spots than cold-spots, indicating food insecurity is more geographically concentrated than food security.")
      } else {
        paste0("Note: Cold-spots outnumber hot-spots by ", count - spatial_stats()$hotspots, ", suggesting broader geographic distribution of food security.")
      },
      "</p>",
      "</div>"
    )
    
    showModal(modalDialog(
      HTML(explanation),
      title = NULL,
      footer = modalButton("Close"),
      size = "l",
      easyClose = TRUE
    ))
  })
  
  # Moran's I Explanation
  observeEvent(input$morans_info, {
    req(spatial_stats())
    
    morans <- spatial_stats()$morans_i
    year <- input$map_year_slider
    
    # Interpret Moran's I value
    interpretation <- if (is.na(morans)) {
      "Unable to calculate - insufficient data variation"
    } else if (morans > 0.7) {
      "very strong positive spatial autocorrelation"
    } else if (morans > 0.5) {
      "strong positive spatial autocorrelation"
    } else if (morans > 0.3) {
      "moderate positive spatial autocorrelation"
    } else if (morans > 0.1) {
      "weak positive spatial autocorrelation"
    } else {
      "minimal spatial autocorrelation"
    }
    
    explanation <- paste0(
      "<div style='line-height: 1.6;'>",
      "<h4 style='color: #ffc107; margin-top: 0;'>📊 Moran's I Explained</h4>",
      "<p><strong>What is Moran's I?</strong><br>",
      "Moran's I measures <em>spatial autocorrelation</em> - the degree to which counties with similar food insecurity rates are located near each other. It ranges from -1 to +1.</p>",
      
      "<p><strong>Your Data (", year, "):</strong><br>",
      if (!is.na(morans)) {
        paste0(
          "Moran's I = <strong>", sprintf("%.3f", morans), "</strong><br>",
          "This indicates <strong>", interpretation, "</strong>. ",
          if (morans > 0.5) {
            "Food insecurity shows clear geographic patterns - similar counties cluster together. This suggests regional factors (economic conditions, infrastructure, policies) strongly influence food insecurity."
          } else if (morans > 0.3) {
            "Food insecurity shows notable geographic patterns, but county-level factors also play a significant role."
          } else {
            "Food insecurity is relatively dispersed geographically. County-specific factors may be more important than regional patterns."
          }
        )
      } else {
        "Unable to calculate Moran's I for this dataset."
      },
      "</p>",
      
      "<p><strong>Interpretation Scale:</strong><br>",
      "• <strong>0.7 to 1.0:</strong> Very strong clustering (rare in real data)<br>",
      "• <strong>0.5 to 0.7:</strong> Strong clustering (typical for socioeconomic data)<br>",
      "• <strong>0.3 to 0.5:</strong> Moderate clustering<br>",
      "• <strong>0.0 to 0.3:</strong> Weak clustering or random pattern<br>",
      "• <strong>Negative:</strong> Dissimilar values cluster (very rare)</p>",
      
      "<p><strong>Policy Implications:</strong><br>",
      if (!is.na(morans) && morans > 0.5) {
        paste0(
          "• Strong clustering suggests <strong>regional interventions</strong> may be more effective than isolated county programs<br>",
          "• Consider <strong>multi-county partnerships</strong> and regional food banks<br>",
          "• Policies should address <strong>regional economic and infrastructure challenges</strong>"
        )
      } else {
        paste0(
          "• Weaker clustering suggests <strong>county-specific interventions</strong> may be appropriate<br>",
          "• Focus on <strong>local factors</strong> driving food insecurity<br>",
          "• One-size-fits-all regional solutions may be less effective"
        )
      },
      "</p>",
      "</div>"
    )
    
    showModal(modalDialog(
      HTML(explanation),
      title = NULL,
      footer = modalButton("Close"),
      size = "l",
      easyClose = TRUE
    ))
  })
  
  # Geographic Disparity Explanation
  observeEvent(input$disparity_info, {
    req(year_data())
    
    disparity <- max(year_data()$overall_food_insecurity_rate, na.rm = TRUE) - 
                 min(year_data()$overall_food_insecurity_rate, na.rm = TRUE)
    max_county <- year_data() %>%
      filter(overall_food_insecurity_rate == max(overall_food_insecurity_rate, na.rm = TRUE)) %>%
      slice(1)
    min_county <- year_data() %>%
      filter(overall_food_insecurity_rate == min(overall_food_insecurity_rate, na.rm = TRUE)) %>%
      slice(1)
    
    year <- input$map_year_slider
    
    explanation <- paste0(
      "<div style='line-height: 1.6;'>",
      "<h4 style='color: #6f42c1; margin-top: 0;'>📏 Geographic Disparity Explained</h4>",
      "<p><strong>What is geographic disparity?</strong><br>",
      "Geographic disparity measures the difference between the highest and lowest food insecurity rates across all counties. It shows the range of inequality in food insecurity.</p>",
      
      "<p><strong>Your Data (", year, "):</strong><br>",
      "The disparity is <strong>", round(disparity * 100, 1), " percentage points</strong><br><br>",
      "• <strong>Highest:</strong> ", max_county$county, ", ", max_county$state, " (", 
      round(max_county$overall_food_insecurity_rate * 100, 1), "%)<br>",
      "• <strong>Lowest:</strong> ", min_county$county, ", ", min_county$state, " (", 
      round(min_county$overall_food_insecurity_rate * 100, 1), "%)</p>",
      
      "<p><strong>What does this mean?</strong><br>",
      if (disparity > 0.25) {
        "A disparity above 25 percentage points indicates <strong>substantial inequality</strong> in food security across the U.S. Some counties face challenges 3-4 times greater than others."
      } else if (disparity > 0.20) {
        "A disparity around 20-25 points shows <strong>significant variation</strong> in food insecurity. This is typical but still indicates meaningful geographic inequality."
      } else {
        "A disparity below 20 points suggests <strong>relatively less variation</strong> compared to historical patterns, though inequality still exists."
      },
      "</p>",
      
      "<p><strong>Historical Context:</strong><br>",
      "• <strong>Pre-2008:</strong> Disparity typically 15-20 points<br>",
      "• <strong>2009-2012:</strong> Rose to 25-30 points during recession<br>",
      "• <strong>2015-2019:</strong> Declined to 20-25 points<br>",
      "• <strong>2020-2021:</strong> Spiked again during COVID-19<br>",
      "• <strong>2022-2023:</strong> Gradually declining again</p>",
      
      "<p><strong>Policy Implications:</strong><br>",
      "• Higher disparity suggests <strong>uneven</strong> distribution of resources and opportunities<br>",
      "• Indicates need for <strong>targeted federal programs</strong> in highest-need counties<br>",
      "• Consider <strong>place-based policies</strong> that address local conditions</p>",
      "</div>"
    )
    
    showModal(modalDialog(
      HTML(explanation),
      title = NULL,
      footer = modalButton("Close"),
      size = "l",
      easyClose = TRUE
    ))
  })
  
  # ============================================================================
  # AI-GENERATED SPATIAL SUMMARY (CLAUDE API)
  # ============================================================================
  
  # Initialize summary as empty
  spatial_summary <- reactiveVal(NULL)
  
  # Generate summary when button clicked
  observeEvent(input$generate_spatial_summary, {
    req(spatial_stats(), year_data())
    
    # Show loading state
    spatial_summary(paste0(
      "<div style='text-align: center; padding: 40px;'>",
      "<i class='fa fa-spinner fa-spin' style='font-size: 48px; color: #0033A0;'></i>",
      "<p style='margin-top: 20px; font-size: 16px; color: #6c757d;'>",
      "Generating AI analysis... This may take 10-15 seconds.",
      "</p>",
      "</div>"
    ))
    
    # Get statistics
    hotspots <- spatial_stats()$hotspots
    coldspots <- spatial_stats()$coldspots
    morans_i <- spatial_stats()$morans_i
    
    max_fi <- max(year_data()$overall_food_insecurity_rate, na.rm = TRUE) * 100
    min_fi <- min(year_data()$overall_food_insecurity_rate, na.rm = TRUE) * 100
    disparity <- max_fi - min_fi
    
    year <- input$map_year_slider
    
    # Check if ask_claude function exists
    if (!exists("generate_spatial_summary")) {
      spatial_summary(paste0(
        "<div style='background: #FFF3CD; border-left: 4px solid #FFC107; padding: 20px; border-radius: 8px;'>",
        "<h4 style='color: #856404; margin-top: 0;'>⚠️ AI Module Not Loaded</h4>",
        "<p style='color: #856404; margin: 0;'>",
        "To enable AI-generated summaries, load the AI explanations module:<br><br>",
        "<strong>Step 1:</strong> Add to global.R:<br>",
        "<code>source('R/ai_explanations.R')</code><br><br>",
        "<strong>Step 2:</strong> Set your API key:<br>",
        "<code>Sys.setenv(ANTHROPIC_API_KEY = 'your-key-here')</code><br><br>",
        "Get your key from <a href='https://console.anthropic.com/' target='_blank'>console.anthropic.com</a>",
        "</p>",
        "</div>"
      ))
      return(NULL)
    }
    
    # Call Claude API
    ai_response <- generate_spatial_summary(
      year = year,
      hotspots = hotspots,
      coldspots = coldspots,
      morans_i = morans_i,
      disparity = round(disparity, 1),
      max_fi = max_fi,
      min_fi = min_fi
    )
    
    # Update summary with API response
    spatial_summary(ai_response)
  })
  
  # Render the summary
  output$spatial_ai_summary <- renderUI({
    if (is.null(spatial_summary())) {
      HTML(paste0(
        "<div style='text-align: center; padding: 40px; color: white; opacity: 0.9;'>",
        "<p style='font-size: 16px; margin: 0;'>",
        "Click <strong>'Generate AI Summary'</strong> to create a comprehensive analysis ",
        "of spatial patterns, hot-spots, cold-spots, and clustering using Claude AI.",
        "</p>",
        "</div>"
      ))
    } else {
      HTML(spatial_summary())
    }
  })
  
}