# R/server_exploration.R

server_exploration <- function(input, output, session, data) {

  # 1. Dynamic State Filter
  observe({
    updateSelectInput(
      session,
      "state_select",
      choices = sort(unique(data()$state)),
      selected = "alabama"
    )
  })

  # 2. MAP VIEW (placeholder until spatial join is added)
  output$map_view <- leaflet::renderLeaflet({

    #  Your dataset does NOT contain lat/lng coordinates
    # leaflet::leaflet() %>%
    #   leaflet::addTiles() %>%
    #   leaflet::setView(lng = -98.5795, lat = 39.8283, zoom = 4) %>%
    #   leaflet::addPopups(
    #     lng = -98.5795, lat = 39.8283,
    #     popup = "A geographic map requires joining county FIPS to a shapefile."
    #   )
    
    # state specific maps
    shiny::req(data(), input$state_select, input$year_select)
    
    df <- data() %>%
      dplyr::filter(
        state %in% input$state_select,
        year  == input$year_select)
    
    # safety check
    validate(
      need(nrow(df) > 0, "No data for these states in this year."))
    
    st_title <- tools::toTitleCase(input$state_select)
    st_abbr  <- state.abb[match(st_title, state.name)]
    st_arg   <- ifelse(is.na(st_abbr), st_title, st_abbr)
    
    counties_sf <- tigris::counties(
      state = st_arg,
      cb    = TRUE,
      year  = 2022) %>%
      sf::st_as_sf() %>%
      dplyr::left_join(df, by = c("GEOID" = "fips"))
    
    pal <- leaflet::colorNumeric(
      palette = "plasma",
      domain  = counties_sf$overall_food_insecurity_rate,
      na.color = "transparent")
    
    leaflet::leaflet(counties_sf) %>%
      leaflet::addProviderTiles("CartoDB.Positron") %>% #leaflet::addTiles() %>%
      leaflet::addPolygons(
        fillColor   = ~pal(overall_food_insecurity_rate),
        color       = "#444",
        weight      = 0.5,
        fillOpacity = 0.6, #fillOpacity = 0.8, 
        popup = ~paste0(
          "<b>", NAME, "</b><br>",
          "Overall FI Rate: ",
          round(overall_food_insecurity_rate, 2))) %>%
      leaflet::addLegend(
        pal    = pal,
        values = ~overall_food_insecurity_rate,
        title  = "Overall Food Insecurity Rate")
    
  })
  

  # 3. TREND PLOT (FI rate over time by state)
  output$trend_plot <- plotly::renderPlotly({
    df <- data() %>%
      filter(state == input$state_select) %>%
      arrange(year)

    plotly::plot_ly(
      df,
      x = ~year,
      y = ~overall_food_insecurity_rate,
      type = "scatter",
      mode = "lines+markers",
      line = list(color = "#220BED")
    ) %>%
      plotly::layout(
        title = paste("Food Insecurity Trend in", tools::toTitleCase(input$state_select))
      )
  })

  # 4. SUMMARY TABLE
  output$summary_table <- DT::renderDT({
    df <- data() %>% filter(state == input$state_select)
    DT::datatable(df, options = list(pageLength = 10, scrollX = TRUE))
  })

  # 5. FULL DATA VIEWER
  output$data_viewer <- DT::renderDT({
    DT::datatable(
      data(),
      options = list(pageLength = 10, scrollX = TRUE),
      rownames = FALSE
    )
  })

}
