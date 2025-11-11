server_overview <- function(input, output, session, data) {
  output$national_trend_plot <- renderPlotly({
    df <- data()
    plot_ly(df, x = ~State, y = ~FoodInsecurity, type = "bar") %>%
      layout(title = "Food Insecurity by State (Placeholder)")
  })
}
