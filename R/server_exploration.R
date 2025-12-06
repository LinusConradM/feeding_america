# R/server_exploration.R
library(sf)
library(tigris)
options(tigris_use_cache = TRUE)

server_exploration <- function(input, output, session, data) {

  # -------------------------------------------------------
  # 1. Dynamic State Filter
  # -------------------------------------------------------
  observe({
    updateSelectInput(
      session,
      "state_select",
      choices = sort(unique(data()$state)),
      selected = "AL"
    )
  })

  # dynamic county filter
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


  # -------------------------------------------------------
  # 2. Dynamic County Filter (updates when state changes)
  # -------------------------------------------------------
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

  # -------------------------------------------------------
  # Helper: Uniform filtering by state + optional county
  # -------------------------------------------------------
  filter_state_county <- function(df) {

  df <- df %>%
    filter(state %in% input$state_select)

  # Only apply county filter when counties are selected
  if (!is.null(input$county_select) && length(input$county_select) > 0) {
    df <- df %>% filter(county_state %in% input$county_select)
  }

  return(df)
}


  # -------------------------------------------------------
# 3. STATE + COUNTY DYNAMIC LEAFLET MAP
# -------------------------------------------------------
output$map_view <- leaflet::renderLeaflet({

  req(data(), input$state_select, input$year_select)

  # Filter dataset by state, county, and year
  df <- data() %>%
    filter_state_county() %>%     # ← apply BOTH filters
    filter(year == input$year_select)

  validate(need(nrow(df) > 0,
                "No data available for this state/year/county selection."))

  # Use selected state abbreviations (AL, GA, etc.)
  st_arg <- input$state_select

  # Load county shapes for selected states
  counties_sf <- tigris::counties(state = st_arg, cb = TRUE, year = 2022) %>%
    sf::st_as_sf() %>%
    left_join(df, by = c("GEOID" = "fips"))

  # If counties are selected, filter the shapefile too
  if (!is.null(input$county_select) && length(input$county_select) > 0) {
    counties_sf <- counties_sf %>%
      filter(NAME %in% input$county_select |
               county_state %in% input$county_select)
  }

  pal <- leaflet::colorNumeric(
    palette = "plasma",
    domain  = counties_sf$overall_food_insecurity_rate,
    na.color = "transparent"
  )

  leaflet(counties_sf) %>%
    addProviderTiles("CartoDB.Positron") %>%
    addPolygons(
      fillColor   = ~pal(overall_food_insecurity_rate),
      color       = "#444",
      weight      = 0.5,
      fillOpacity = 0.6,
      popup = ~paste0(
        "<b>", NAME, "</b><br>",
        "Overall FI Rate: ", round(overall_food_insecurity_rate, 2)
      )
    ) %>%
    addLegend(
      pal    = pal,
      values = ~overall_food_insecurity_rate,
      title  = "Overall Food Insecurity Rate"
    )
})


  # -------------------------------------------------------
  # 4. WARNING ABOUT 2023 COST METHODOLOGY CHANGE
  # -------------------------------------------------------
  observe({
    if (input$year_range[2] >= 2023) {
      showNotification(
        "Note: Feeding America updated cost methodology in 2023; values are not directly comparable.",
        type = "warning", duration = 5
      )
    }
  })

  # -------------------------------------------------------
  # 5. Auto-update year slider based on dataset
  # -------------------------------------------------------
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


  # -------------------------------------------------------
  # 6. GGPlot Trend: State-Level Trends
  # -------------------------------------------------------
  output$trend_state <- renderPlot({

    df <- data() %>%
      filter_state_county() %>%
      filter(year >= input$year_range[1],
             year <= input$year_range[2]) %>%
      group_by(state, year) %>%
      summarise(across(all_of(input$variables),
                       mean, na.rm = TRUE), .groups = "drop") %>%
      pivot_longer(cols = input$variables,
                   names_to = "indicator",
                   values_to = "value")

    ggplot(df, aes(year, value, color = indicator, group = state)) +
      geom_line(linewidth = 1.2) +
      geom_point(size = 2) +
      labs(title = "State-Level Food Insecurity Trends",
           x = "Year", y = "Value") +
      scale_x_continuous(breaks = sort(unique(df$year)))
  })


  # -------------------------------------------------------
  # 7. GGPlot: Racial Disparity Trends
  # -------------------------------------------------------
  output$trend_race <- renderPlot({

    df <- data() %>%
      filter_state_county() %>%
      filter(year >= input$year_range[1],
             year <= input$year_range[2]) %>%
      group_by(state, year) %>%
      summarise(
        black    = mean(food_insecurity_rate_among_black_persons_all_ethnicities, na.rm = TRUE),
        hispanic = mean(food_insecurity_rate_among_hispanic_persons_any_race, na.rm = TRUE),
        white    = mean(food_insecurity_rate_among_white_non_hispanic_persons, na.rm = TRUE),
        .groups = "drop"
      ) %>%
      pivot_longer(cols = c(black, hispanic, white),
                   names_to = "group",
                   values_to = "value")

    ggplot(df, aes(year, value, color = group)) +
      geom_line(linewidth = 1.2) +
      geom_point(size = 2) +
      labs(title = "Racial Disparity in Food Insecurity",
           x = "Year", y = "Rate") +
      scale_x_continuous(breaks = sort(unique(df$year)))
  })


  # -------------------------------------------------------
  # 8. GGPlot: Child Food Insecurity Trends
  # -------------------------------------------------------
  output$trend_child <- renderPlot({

    df <- data() %>%
      filter_state_county() %>%
      filter(year >= input$year_range[1],
             year <= input$year_range[2]) %>%
      group_by(state, year) %>%
      summarise(
        child_fi  = mean(child_food_insecurity_rate, na.rm = TRUE),
        below_185 = mean(percent_food_insecure_children_in_hh_w_hh_incomes_below_185_fpl, na.rm = TRUE),
        above_185 = mean(percent_food_insecure_children_in_hh_w_hh_incomes_above_185_fpl, na.rm = TRUE),
        .groups = "drop"
      ) %>%
      pivot_longer(cols = c(child_fi, below_185, above_185),
                   names_to = "indicator",
                   values_to = "value")

    ggplot(df, aes(year, value, color = indicator)) +
      geom_line(linewidth = 1.2) +
      geom_point(size = 2) +
      labs(title = "Child Food Insecurity Trends",
           x = "Year", y = "Rate") +
      scale_x_continuous(breaks = sort(unique(df$year)))
  })


  # -------------------------------------------------------
  # 9. GGPlot: Cost Burden Trends
  # -------------------------------------------------------
  output$trend_cost <- renderPlot({

    df <- data() %>%
      filter_state_county() %>%
      filter(year >= input$year_range[1],
             year <= input$year_range[2]) %>%
      group_by(state, year) %>%
      summarise(
        cost_per_meal = mean(cost_per_meal, na.rm = TRUE),
        shortfall     = mean(weighted_annual_food_budget_shortfall, na.rm = TRUE),
        .groups = "drop"
      ) %>%
      pivot_longer(cols = c(cost_per_meal, shortfall),
                   names_to = "indicator",
                   values_to = "value")

    ggplot(df, aes(year, value, color = indicator)) +
      geom_line(linewidth = 1.2) +
      geom_point(size = 2) +
      labs(title = "Food Cost & Budget Shortfall Trends",
           x = "Year", y = "Value") +
      scale_x_continuous(breaks = sort(unique(df$year)))
  })


  # -------------------------------------------------------
  # 10. GGPlot: Rural vs Urban Trends
  # -------------------------------------------------------
  output$trend_rural <- renderPlot({

    df <- data() %>%
      filter_state_county() %>%
      mutate(
        rural_group = case_when(
          rural_urban_continuum_code_2013 <= 3 ~ "Metro",
          rural_urban_continuum_code_2013 <= 6 ~ "Non-Metro",
          TRUE ~ "Rural"
        )
      ) %>%
      filter(year >= input$year_range[1],
             year <= input$year_range[2]) %>%
      group_by(rural_group, year) %>%
      summarise(fi = mean(overall_food_insecurity_rate, na.rm = TRUE),
                .groups = "drop")

    ggplot(df, aes(year, fi, color = rural_group)) +
      geom_line(linewidth = 1.2) +
      geom_point(size = 2) +
      labs(title = "Rural vs Urban Food Insecurity Trends",
           x = "Year", y = "Rate") +
      scale_x_continuous(breaks = sort(unique(df$year)))
  })


  # -------------------------------------------------------
  # 11. GGPlot: Regional Trends
  # -------------------------------------------------------
  output$trend_region <- renderPlot({

    df <- data() %>%
      filter(year >= input$year_range[1],
             year <= input$year_range[2]) %>%
      group_by(census_region, year) %>%
      summarise(fi = mean(overall_food_insecurity_rate, na.rm = TRUE),
                .groups = "drop")

    ggplot(df, aes(year, fi, color = census_region)) +
      geom_line(linewidth = 1.2) +
      geom_point(size = 2) +
      labs(title = "Food Insecurity Across Census Regions",
           x = "Year", y = "Rate") +
      scale_x_continuous(breaks = sort(unique(df$year)))
  })


  # -------------------------------------------------------
  # 12. GGPlot: Inequality Gap Trends
  # -------------------------------------------------------
  output$trend_gap <- renderPlot({

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
      filter(year >= input$year_range[1],
             year <= input$year_range[2]) %>%
      group_by(state, year) %>%
      summarise(
        black_white_gap = mean(black_white_gap, na.rm = TRUE),
        child_income_gap = mean(child_income_gap, na.rm = TRUE),
        .groups = "drop"
      ) %>%
      pivot_longer(cols = c(black_white_gap, child_income_gap),
                   names_to = "gap",
                   values_to = "value")

    ggplot(df, aes(year, value, color = gap)) +
      geom_line(linewidth = 1.2) +
      geom_point(size = 2) +
      labs(title = "Food Insecurity Inequality Gaps",
           x = "Year", y = "Gap") +
      scale_x_continuous(breaks = sort(unique(df$year)))
  })


  # -------------------------------------------------------
  # 13. Summary Table
  # -------------------------------------------------------
  output$summary_table <- DT::renderDT({
    df <- data() %>% filter_state_county()
    DT::datatable(df, options = list(pageLength = 10, scrollX = TRUE))
  })

  # -------------------------------------------------------
  # 14. Full Data Viewer
  # -------------------------------------------------------
  output$data_viewer <- DT::renderDT({
    DT::datatable(
      data(),
      options = list(pageLength = 10, scrollX = TRUE),
      rownames = FALSE
    )
  })

}
