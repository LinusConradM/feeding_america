library(sf)
library(tigris)
library(plotly)
library(dplyr)
library(tidyr)
options(tigris_use_cache = TRUE)

server_exploration <- function(input, output, session, data) {

  # ---------------------------
  # 1. DYNAMIC STATE FILTER
  # ---------------------------
  observe({
    updateSelectInput(
      session,
      "state_select",
      choices = sort(unique(data()$state)),
      selected = "AL"
    )
  })

  # ---------------------------
  # 2. DYNAMIC COUNTY FILTER
  # ---------------------------
  observeEvent(input$state_select, {
    req(input$state_select)

    county_choices <- data() %>%
      filter(state %in% input$state_select) %>%
      arrange(county_state) %>%
      pull(county_state) %>%
      unique()

    updateSelectInput(
      session,
      "county_select",
      choices = county_choices,
      selected = NULL
    )
  })

  # Helper function
  filter_state_county <- function(df) {
    df %>%
      filter(
        state %in% input$state_select,
        if (!is.null(input$county_select) && length(input$county_select) > 0)
          county_state %in% input$county_select else TRUE
      )
  }

  # ---------------------------
  # 3. MAP VIEW
  # ---------------------------
  output$map_view <- leaflet::renderLeaflet({

    req(input$state_select, input$year_select)

    df <- data() %>%
      filter(state %in% input$state_select, year == input$year_select)

    validate(need(nrow(df) > 0, "No data for these states in this year."))

    st_title <- tools::toTitleCase(input$state_select)
    st_abbr  <- state.abb[match(st_title, state.name)]
    st_arg   <- ifelse(is.na(st_abbr), st_title, st_abbr)

    counties_sf <- tigris::counties(state = st_arg, cb = TRUE, year = 2022) %>%
      st_as_sf() %>%
      left_join(df, by = c("GEOID" = "fips"))

    pal <- leaflet::colorNumeric(
      palette = "plasma",
      domain = counties_sf$overall_food_insecurity_rate,
      na.color = "transparent"
    )

    leaflet(counties_sf) %>%
      addProviderTiles("CartoDB.Positron") %>%
      addPolygons(
        fillColor = ~pal(overall_food_insecurity_rate),
        weight = 0.5,
        color = "#444",
        fillOpacity = 0.6,
        popup = ~paste0(
          "<b>", NAME, "</b><br>",
          "Overall FI Rate: ", round(overall_food_insecurity_rate, 2)
        )
      ) %>%
      addLegend(
        pal = pal,
        values = ~overall_food_insecurity_rate,
        title = "Overall Food Insecurity Rate"
      )
  })

  # ---------------------------
  # NOTIFICATIONS
  # ---------------------------
  observe({
    if (input$year_range[2] >= 2023) {
      showNotification(
        "Reminder: 2023 cost estimates changed methodology and are not comparable.",
        type = "warning", duration = 5
      )
    }
  })

  # Dynamic slider update
  observe({
    years <- sort(unique(data()$year))
    updateSliderInput(
      session,
      "year_range",
      min = min(years),
      max = max(years),
      value = c(min(years), max(years))
    )
  })

  # ----------------------------------------
  # GLOBAL PLOTLY STYLE FUNCTION
  # ----------------------------------------
  plotly_style <- function(p) {
    p %>% layout(
      font = list(size = 14, family = "Inter"),
      title = list(font = list(size = 20)),
      xaxis = list(titlefont = list(size = 16)),
      yaxis = list(titlefont = list(size = 16))
    )
  }

  # =====================================================
  # TRENDS — PLOTLY ONLY
  # =====================================================

  # ---------------------------
  # STATE TREND
  # ---------------------------
  output$trend_state <- renderPlotly({
    req(input$state_select, input$variables)

    df <- data() %>%
      filter_state_county() %>%
      filter(year >= input$year_range[1], year <= input$year_range[2]) %>%
      group_by(state, year) %>%
      summarise(across(all_of(input$variables), mean, na.rm = TRUE), .groups="drop") %>%
      pivot_longer(cols = input$variables, names_to = "indicator", values_to = "value")

    p <- plot_ly(
      df,
      x = ~year, y = ~value,
      color = ~state,
      linetype = ~indicator,
      type = "scatter", mode = "lines+markers"
    ) %>% layout(title = "State-Level Food Insecurity Trends")

    plotly_style(p)
  })

  # ---------------------------
  # RACIAL TREND
  # ---------------------------
  output$trend_race <- renderPlotly({

    df <- data() %>%
      filter_state_county() %>%
      filter(year >= input$year_range[1], year <= input$year_range[2]) %>%
      group_by(state, year) %>%
      summarise(
        black = mean(food_insecurity_rate_among_black_persons_all_ethnicities, na.rm = TRUE),
        hispanic = mean(food_insecurity_rate_among_hispanic_persons_any_race, na.rm = TRUE),
        white = mean(food_insecurity_rate_among_white_non_hispanic_persons, na.rm = TRUE),
        .groups="drop"
      ) %>%
      pivot_longer(cols = c(black, hispanic, white), names_to = "group", values_to = "value")

    p <- plot_ly(
      df, x = ~year, y = ~value, color = ~group,
      type = "scatter", mode = "lines+markers"
    ) %>% layout(title = "Racial Disparity Trends")

    plotly_style(p)
  })

  # ---------------------------
  # CHILD TREND
  # ---------------------------
  output$trend_child <- renderPlotly({

    df <- data() %>%
      filter_state_county() %>%
      filter(year >= input$year_range[1], year <= input$year_range[2]) %>%
      group_by(state, year) %>%
      summarise(
        child_fi = mean(child_food_insecurity_rate, na.rm = TRUE),
        below_185 = mean(percent_food_insecure_children_in_hh_w_hh_incomes_below_185_fpl, na.rm = TRUE),
        above_185 = mean(percent_food_insecure_children_in_hh_w_hh_incomes_above_185_fpl, na.rm = TRUE),
        .groups="drop"
      ) %>%
      pivot_longer(cols = c(child_fi, below_185, above_185), names_to = "indicator", values_to = "value")

    p <- plot_ly(df, x = ~year, y = ~value, color = ~indicator,
                 type = "scatter", mode = "lines+markers") %>%
      layout(title = "Child Food Insecurity Trends")

    plotly_style(p)
  })

  # ---------------------------
  # COST BURDEN TREND
  # ---------------------------
  output$trend_cost <- renderPlotly({

    df <- data() %>%
      filter_state_county() %>%
      filter(year >= input$year_range[1], year <= input$year_range[2]) %>%
      group_by(state, year) %>%
      summarise(
        cost_per_meal = mean(cost_per_meal, na.rm = TRUE),
        shortfall = mean(weighted_annual_food_budget_shortfall, na.rm = TRUE),
        .groups="drop"
      ) %>%
      pivot_longer(cols = c(cost_per_meal, shortfall), names_to = "indicator", values_to = "value")

    p <- plot_ly(df, x = ~year, y = ~value, color = ~indicator,
                 type = "scatter", mode = "lines+markers") %>%
      layout(title = "Food Cost & Shortfall Trends")

    plotly_style(p)
  })

  # ---------------------------
  # RURAL vs URBAN TREND
  # ---------------------------
  output$trend_rural <- renderPlotly({

    df <- data() %>%
      mutate(
        rural_group = case_when(
          rural_urban_continuum_code_2013 <= 3 ~ "Metro",
          rural_urban_continuum_code_2013 <= 6 ~ "Non-Metro",
          TRUE ~ "Rural"
        )
      ) %>%
      filter_state_county() %>%
      filter(year >= input$year_range[1], year <= input$year_range[2]) %>%
      group_by(rural_group, year) %>%
      summarise(fi = mean(overall_food_insecurity_rate, na.rm = TRUE), .groups="drop")

    p <- plot_ly(df, x = ~year, y = ~fi, color = ~rural_group,
                 type = "scatter", mode = "lines+markers") %>%
      layout(title = "Rural vs Urban Food Insecurity Trends")

    plotly_style(p)
  })

  # ---------------------------
  # REGIONAL TREND
  # ---------------------------
  output$trend_region <- renderPlotly({

    df <- data() %>%
      filter(year >= input$year_range[1], year <= input$year_range[2]) %>%
      group_by(census_region, year) %>%
      summarise(fi = mean(overall_food_insecurity_rate, na.rm = TRUE), .groups="drop")

    p <- plot_ly(df, x = ~year, y = ~fi, color = ~census_region,
                 type = "scatter", mode = "lines+markers") %>%
      layout(title = "Regional Food Insecurity Trends")

    plotly_style(p)
  })

  # ---------------------------
  # INEQUALITY GAP TREND
  # ---------------------------
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
      filter_state_county() %>%
      filter(year >= input$year_range[1], year <= input$year_range[2]) %>%
      group_by(state, year) %>%
      summarise(
        black_white_gap = mean(black_white_gap, na.rm = TRUE),
        child_income_gap = mean(child_income_gap, na.rm = TRUE),
        .groups="drop"
      ) %>%
      pivot_longer(cols = c(black_white_gap, child_income_gap),
                   names_to = "gap", values_to = "value")

    p <- plot_ly(df, x = ~year, y = ~value, color = ~gap,
                 type = "scatter", mode = "lines+markers") %>%
      layout(title = "Inequality Gap Trends")

    plotly_style(p)
  })

  # ---------------------------
  # SUMMARY TABLE
  # ---------------------------
  output$summary_table <- DT::renderDT({
    df <- data() %>% filter_state_county()
    DT::datatable(df, options = list(pageLength = 10, scrollX = TRUE))
  })

  # FULL DATA VIEWER
  output$data_viewer <- DT::renderDT({
    DT::datatable(
      data(),
      options = list(pageLength = 10, scrollX = TRUE),
      rownames = FALSE
    )
  })

}
