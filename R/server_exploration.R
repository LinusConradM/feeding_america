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

    # Your dataset does NOT contain lat/lng coordinates
    leaflet::leaflet() %>%
      leaflet::addTiles() %>%
      leaflet::setView(lng = -98.5795, lat = 39.8283, zoom = 4) %>%
      leaflet::addPopups(
        lng = -98.5795, lat = 39.8283,
        popup = "A geographic map requires joining county FIPS to a shapefile."
      )
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
