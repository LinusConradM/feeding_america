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

  # Warn user if cost trends include 2023 (methodology change)
observe({
  if (input$year_range[2] >= 2023) {
    showNotification(
      "Reminder: 2023 cost estimates are not directly comparable to prior years due to methodology changes.",
      type = "warning",
      duration = 5
    )
  }
})

# Warn user about race/ethnicity uncertainty
observe({
  if ("trend_race" %in% input$tabs) {
    showNotification(
      "Race/ethnicity estimates have wide uncertainty and should be interpreted directionally.",
      type = "message",
      duration = 5
    )
  }
})


  # 2. MAP VIEW (placeholder)
  output$map_view <- leaflet::renderLeaflet({
    leaflet::leaflet() %>%
      leaflet::addTiles() %>%
      leaflet::setView(lng = -98.5795, lat = 39.8283, zoom = 4) %>%
      leaflet::addPopups(
        lng = -98.5795, lat = 39.8283,
        popup = "A geographic map requires joining county FIPS to a shapefile."
      )
  })

  # 3. ALL TREND PLOTS
  # Set a Global Font Size for ALL Plotly Plots
# Apply consistent axis + title font sizes to all Plotly charts
plotly_style <- function(p) {
  p %>% layout(
    font = list(size = 14, family = "Inter"),
    title = list(font = list(size = 20)),
    xaxis = list(
      tickfont = list(size = 14),
      titlefont = list(size = 16)
    ),
    yaxis = list(
      tickfont = list(size = 14),
      titlefont = list(size = 16)
    )
  )
}


  # STATE-LEVEL TREND
  # STATE-LEVEL TREND
output$trend_state <- plotly::renderPlotly({

  req(input$state_select)
  req(input$variables)

  df <- data() %>%
    filter(
      state %in% input$state_select,
      year >= input$year_range[1],
      year <= input$year_range[2]
    )

  df_agg <- df %>%
    group_by(state, year) %>%
    summarise(across(all_of(input$variables), mean, na.rm = TRUE)) %>%
    pivot_longer(cols = input$variables,
                 names_to = "indicator",
                 values_to = "value")

  # Create plot ----
  p <- plot_ly(
    df_agg,
    x = ~year, y = ~value,
    color = ~state,
    linetype = ~indicator,
    type = "scatter", mode = "lines+markers"
  ) %>%
    layout(
      title = "State-Level Food Insecurity Trends",
      xaxis = list(tickformat = ".0f")
    )

  # Apply global plot style ----
  plotly_style(p)
})



  # RACIAL DISPARITY TREND
  output$trend_race <- plotly::renderPlotly({

    df <- data() %>%
      filter(
        state %in% input$state_select,
        year >= input$year_range[1],
        year <= input$year_range[2]
      ) %>%
      group_by(state, year) %>%
      summarise(
        black = mean(food_insecurity_rate_among_black_persons_all_ethnicities, na.rm = TRUE),
        hispanic = mean(food_insecurity_rate_among_hispanic_persons_any_race, na.rm = TRUE),
        white = mean(food_insecurity_rate_among_white_non_hispanic_persons, na.rm = TRUE)
      ) %>%
      pivot_longer(cols = c(black, hispanic, white),
                   names_to = "group", values_to = "value")

    plot_ly(
      df,
      x = ~year, y = ~value,
      color = ~group,
      type = "scatter", mode = "lines+markers"
    ) %>%
      layout(title = "Racial Disparity in Food Insecurity (State-Level)",
             xaxis = list(tickformat = ".0f"))
  })


  # CHILD FOOD INSECURITY TREND
  output$trend_child <- renderPlotly({

    df <- data() %>%
      filter(
        state %in% input$state_select,
        year >= input$year_range[1],
        year <= input$year_range[2]
      ) %>%
      group_by(state, year) %>%
      summarise(
        child_fi = mean(child_food_insecurity_rate, na.rm = TRUE),
        below_185 = mean(percent_food_insecure_children_in_hh_w_hh_incomes_below_185_fpl, na.rm = TRUE),
        above_185 = mean(percent_food_insecure_children_in_hh_w_hh_incomes_above_185_fpl, na.rm = TRUE)
      ) %>%
      pivot_longer(cols = c(child_fi, below_185, above_185),
                   names_to = "indicator", values_to = "value")

    plot_ly(
      df,
      x = ~year, y = ~value,
      color = ~indicator,
      type = "scatter", mode = "lines+markers"
    ) %>%
      layout(title = "Child Food Insecurity Trends",
             xaxis = list(tickformat = ".0f"))
  })


  # COST BURDEN TREND
  output$trend_cost <- renderPlotly({

    df <- data() %>%
      filter(
        state %in% input$state_select,
        year >= input$year_range[1],
        year <= input$year_range[2]
      ) %>%
      group_by(state, year) %>%
      summarise(
        cost_per_meal = mean(cost_per_meal, na.rm = TRUE),
        shortfall = mean(weighted_annual_food_budget_shortfall, na.rm = TRUE)
      ) %>%
      pivot_longer(cols = c(cost_per_meal, shortfall),
                   names_to = "indicator", values_to = "value")

    plot_ly(
      df,
      x = ~year, y = ~value,
      color = ~indicator,
      type = "scatter", mode = "lines+markers"
    ) %>%
      layout(title = "Food Cost & Budget Shortfall Trends",
             xaxis = list(tickformat = ".0f"))
  })


  # RURAL vs URBAN TREND
  output$trend_rural <- renderPlotly({

    df <- data() %>%
      mutate(
        rural_group = case_when(
          rural_urban_continuum_code_2013 <= 3 ~ "Metro",
          rural_urban_continuum_code_2013 <= 6 ~ "Non-Metro",
          TRUE ~ "Rural"
        )
      ) %>%
      filter(
        state %in% input$state_select,
        year >= input$year_range[1],
        year <= input$year_range[2]
      ) %>%
      group_by(rural_group, year) %>%
      summarise(fi = mean(overall_food_insecurity_rate, na.rm = TRUE))

    plot_ly(
      df,
      x = ~year, y = ~fi,
      color = ~rural_group,
      type = "scatter", mode = "lines+markers"
    ) %>%
      layout(title = "Rural vs Urban Food Insecurity Trends",
             xaxis = list(tickformat = ".0f"))
  })


  # REGIONAL TREND
  output$trend_region <- renderPlotly({

    df <- data() %>%
      filter(
        year >= input$year_range[1],
        year <= input$year_range[2]
      ) %>%
      group_by(census_region, year) %>%
      summarise(fi = mean(overall_food_insecurity_rate, na.rm = TRUE))

    plot_ly(
      df,
      x = ~year, y = ~fi,
      color = ~census_region,
      type = "scatter", mode = "lines+markers"
    ) %>%
      layout(title = "FI Trends Across Census Regions",
             xaxis = list(tickformat = ".0f"))
  })


  # INEQUALITY GAP TREND
  output$trend_gap <- renderPlotly({

    df <- data() %>%
      mutate(
        black_white_gap =
          food_insecurity_rate_among_black_persons_all_ethnicities -
          food_insecurity_rate_among_white_non_hispanic_persons,
        
        child_income_gap =
          percent_food_insecure_children_in_hh_w_hh_incomes_below_185_fpl -
          percent_food_insecure_children_in_hh_w_hh_incomes_above_185_fpl
      ) %>%
      filter(
        state %in% input$state_select,
        year >= input$year_range[1],
        year <= input$year_range[2]
      ) %>%
      group_by(state, year) %>%
      summarise(
        black_white_gap = mean(black_white_gap, na.rm = TRUE),
        child_income_gap = mean(child_income_gap, na.rm = TRUE)
      ) %>%
      pivot_longer(cols = c(black_white_gap, child_income_gap),
                   names_to = "gap", values_to = "value")

    plot_ly(
      df,
      x = ~year, y = ~value,
      color = ~gap,
      type = "scatter", mode = "lines+markers"
    ) %>%
      layout(title = "Food Insecurity Inequality Gap Trends",
             xaxis = list(tickformat = ".0f"))
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
