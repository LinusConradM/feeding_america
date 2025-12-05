# R/server_overview.R

server_overview <- function(input, output, session, data) {

  # Shared styling for all plotly charts
  plotly_style <- function(p) {
    p %>% layout(
      font = list(size = 14, family = "Inter"),
      title = list(font = list(size = 20)),
      xaxis = list(tickfont = list(size = 14), titlefont = list(size = 16)),
      yaxis = list(tickfont = list(size = 14), titlefont = list(size = 16))
    )
  }

  df <- reactive({ data() })

  # ================================
  # EXECUTIVE KPI CALCULATIONS
  # ================================
  kpis <- reactive({
    compute_kpis(df())
  })

  # Apply to UI
  output$kpi_fi_rate       <- renderText(sprintf("%.1f%%", kpis()$national_fi_rate * 100))
  output$kpi_fi_persons    <- renderText(scales::comma(kpis()$fi_persons))
  output$kpi_child_fi_rate <- renderText(sprintf("%.1f%%", kpis()$child_fi_rate * 100))
  output$kpi_cost_per_meal <- renderText(sprintf("$%.2f", kpis()$cost_per_meal))
  output$kpi_gap_black     <- renderText(sprintf("%.1f%%", kpis()$racial_gap_black * 100))
  output$kpi_gap_hisp      <- renderText(sprintf("%.1f%%", kpis()$racial_gap_hisp * 100))
  output$kpi_shortfall     <- renderText(scales::dollar(kpis()$budget_shortfall))
  output$kpi_rural_gap     <- renderText(sprintf("%.1f%%", kpis()$rural_metro_gap * 100))

  # ================================
  # NATIONAL FI TREND PLOT
  # ================================
  output$national_trend_plot <- renderPlotly({

    df_trend <- df() %>%
      group_by(year) %>%
      summarise(national_fi_rate = mean(overall_food_insecurity_rate, na.rm = TRUE), .groups = "drop") %>%
      mutate(year = as.numeric(year))

    p <- plot_ly(
      df_trend,
      x = ~year,
      y = ~national_fi_rate * 100,
      type = "scatter",
      mode = "lines+markers",
      line = list(color = "#220BED")
    ) %>% 
      layout(
        title = "National Food Insecurity Trends",
        xaxis = list(
          type = "linear",
          tickvals = df_trend$year,
          ticktext = df_trend$year
        ),
        yaxis = list(title = "Food Insecurity Rate (%)")
      )

    plotly_style(p)
  })
}
