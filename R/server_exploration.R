# R/server_exploration.R

server_exploration <- function(input, output, session, data) {

  # ---- Dynamic filter initialization ----
  observe({
    updateSelectInput(
      session,
      "state_select",
      choices = unique(data()$State),
      selected = "Alabama"
    )
  })

  # ---- Map (placeholder) ----
  output$map_view <- leaflet::renderLeaflet({
  df <- data()

  # Check if lat/lon columns exist — if not, show placeholder map
  if (!("lat" %in% names(df)) || !("lng" %in% names(df))) {
    leaflet::leaflet() %>%
      leaflet::addTiles() %>%
      leaflet::setView(lng = -98.5795, lat = 39.8283, zoom = 4) %>%  # U.S. center
      leaflet::addPopups(
        lng = -98.5795, lat = 39.8283,
        popup = "Map data not yet available at this geographic level."
      )
  } else {
    leaflet::leaflet(df) %>%
      leaflet::addTiles() %>%
      leaflet::addCircleMarkers(
        lng = ~lng, lat = ~lat,
        label = ~State,
        popup = ~paste0("Food Insecurity: ", FoodInsecurity, "%")
      )
  }
})


  # ---- Trend plot ----
  output$trend_plot <- plotly::renderPlotly({
    df <- data()
    plotly::plot_ly(
      df, x = ~State, y = ~PovertyRate,
      type = "scatter", mode = "lines+markers"
    ) %>%
      plotly::layout(title = "Socioeconomic Trends (Placeholder)")
  })

  # ---- Summary table ----
  output$summary_table <- DT::renderDT({
    DT::datatable(data(), options = list(pageLength = 5))
  })

  # ---- NEW: Data Viewer (full dataset) ----
  output$data_viewer <- DT::renderDT({
    DT::datatable(
      data(),
      options = list(pageLength = 10, scrollX = TRUE),
      rownames = FALSE
    )
  })
}
