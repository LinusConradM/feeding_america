# R/server_exploration.R
library(sf)
library(tigris)
options(tigris_use_cache = TRUE)

server_exploration <- function(input, output, session, data) {

  # 1. Dynamic State Filter
  observe({
    updateSelectInput(
      session,
      "state_select",
      choices = sort(unique(data()$state)),
      selected = "AL"   # all states by default
    )
  })

  # 2. Dynamic County Filter
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

  # Helper: state + county filter
  filter_state_county <- function(df) {
    df %>%
      filter(
        state %in% input$state_select,
        if (!is.null(input$county_select) && length(input$county_select) > 0)
          county_state %in% input$county_select
        else TRUE
      )
  }

  # 3. Display warning for 2023 methodology change
  observe({
    if (input$year_range[2] >= 2023) {
      showNotification(
        "Reminder: 2023 cost estimates are not directly comparable to prior years due to methodology changes.",
        type = "warning",
        duration = 5
      )
    }
  })
  
  # 4. Year slider dynamic updating
  observe({
    years <- sort(unique(data()$year))

    updateSliderInput(
      session,
      "year_range",
      min = min(years, na.rm = TRUE),
      max = max(years, na.rm = TRUE),
      value = c(min(years), max(years))
    )
  })

# ===================================================
# STATE-LEVEL TREND — ggplot
# ===================================================
output$trend_state <- renderPlot({

  req(input$state_select)
  req(input$variables)

  df <- data() %>%
    filter_state_county() %>%
    filter(year >= input$year_range[1], year <= input$year_range[2]) %>%
    group_by(state, year) %>%
    summarise(across(all_of(input$variables), mean, na.rm = TRUE), .groups = "drop") %>%
    pivot_longer(cols = input$variables, names_to = "indicator", values_to = "value")

  ggplot(df, aes(x = year, y = value, color = state, linetype = indicator)) +
    geom_line(size = 1.2) +
    geom_point(size = 2) +
    labs(title = "State-Level Food Insecurity Trends",
         x = "Year", y = "Value") +
    scale_x_continuous(breaks = sort(unique(df$year)))
})


# ===================================================
# RACIAL DISPARITY TREND — ggplot
# ===================================================
output$trend_race <- renderPlot({

  df <- data() %>%
    filter_state_county() %>%
    filter(year >= input$year_range[1], year <= input$year_range[2]) %>%
    group_by(state, year) %>%
    summarise(
      black = mean(food_insecurity_rate_among_black_persons_all_ethnicities, na.rm = TRUE),
      hispanic = mean(food_insecurity_rate_among_hispanic_persons_any_race, na.rm = TRUE),
      white = mean(food_insecurity_rate_among_white_non_hispanic_persons, na.rm = TRUE),
      .groups = "drop"
    ) %>%
    pivot_longer(cols = c(black, hispanic, white),
                 names_to = "group", values_to = "value")

  ggplot(df, aes(x = year, y = value, color = group)) +
    geom_line(size = 1.2) +
    geom_point(size = 2) +
    labs(title = "Racial Disparity in Food Insecurity",
         x = "Year", y = "Rate") +
    scale_x_continuous(breaks = sort(unique(df$year)))
})


# ===================================================
# CHILD FOOD INSECURITY TREND — ggplot
# ===================================================
output$trend_child <- renderPlot({

  df <- data() %>%
    filter_state_county() %>%
    filter(year >= input$year_range[1], year <= input$year_range[2]) %>%
    group_by(state, year) %>%
    summarise(
      child_fi = mean(child_food_insecurity_rate, na.rm = TRUE),
      below_185 = mean(percent_food_insecure_children_in_hh_w_hh_incomes_below_185_fpl, na.rm = TRUE),
      above_185 = mean(percent_food_insecure_children_in_hh_w_hh_incomes_above_185_fpl, na.rm = TRUE),
      .groups = "drop"
    ) %>%
    pivot_longer(cols = c(child_fi, below_185, above_185),
                 names_to = "indicator", values_to = "value")

  ggplot(df, aes(x = year, y = value, color = indicator)) +
    geom_line(size = 1.2) +
    geom_point(size = 2) +
    labs(title = "Child Food Insecurity Trends",
         x = "Year", y = "Rate") +
    scale_x_continuous(breaks = sort(unique(df$year)))
})


# ===================================================
# COST BURDEN TREND — ggplot
# ===================================================
output$trend_cost <- renderPlot({

  df <- data() %>%
    filter_state_county() %>%
    filter(year >= input$year_range[1], year <= input$year_range[2]) %>%
    group_by(state, year) %>%
    summarise(
      cost_per_meal = mean(cost_per_meal, na.rm = TRUE),
      shortfall = mean(weighted_annual_food_budget_shortfall, na.rm = TRUE),
      .groups = "drop"
    ) %>%
    pivot_longer(cols = c(cost_per_meal, shortfall),
                 names_to = "indicator", values_to = "value")

  ggplot(df, aes(x = year, y = value, color = indicator)) +
    geom_line(size = 1.2) +
    geom_point(size = 2) +
    labs(title = "Food Cost & Budget Shortfall Trends",
         x = "Year", y = "Value") +
    scale_x_continuous(breaks = sort(unique(df$year)))
})


# ===================================================
# RURAL vs URBAN TREND — ggplot
# ===================================================
output$trend_rural <- renderPlot({

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
    summarise(fi = mean(overall_food_insecurity_rate, na.rm = TRUE), .groups = "drop")

  ggplot(df, aes(x = year, y = fi, color = rural_group)) +
    geom_line(size = 1.2) +
    geom_point(size = 2) +
    labs(title = "Rural vs Urban Food Insecurity Trends",
         x = "Year", y = "Rate") +
    scale_x_continuous(breaks = sort(unique(df$year)))
})


# ===================================================
# REGIONAL TREND — ggplot
# ===================================================
output$trend_region <- renderPlot({

  df <- data() %>%
    filter(year >= input$year_range[1], year <= input$year_range[2]) %>%
    group_by(census_region, year) %>%
    summarise(fi = mean(overall_food_insecurity_rate, na.rm = TRUE), .groups = "drop")

  ggplot(df, aes(x = year, y = fi, color = census_region)) +
    geom_line(size = 1.2) +
    geom_point(size = 2) +
    labs(title = "Food Insecurity Trends Across Census Regions",
         x = "Year", y = "Rate") +
    scale_x_continuous(breaks = sort(unique(df$year)))
})


# ===================================================
# INEQUALITY GAP TREND — ggplot
# ===================================================
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
    filter(year >= input$year_range[1], year <= input$year_range[2]) %>%
    group_by(state, year) %>%
    summarise(
      black_white_gap = mean(black_white_gap, na.rm = TRUE),
      child_income_gap = mean(child_income_gap, na.rm = TRUE),
      .groups = "drop"
    ) %>%
    pivot_longer(cols = c(black_white_gap, child_income_gap),
                 names_to = "gap", values_to = "value")

  ggplot(df, aes(x = year, y = value, color = gap)) +
    geom_line(size = 1.2) +
    geom_point(size = 2) +
    labs(title = "Food Insecurity Inequality Gaps",
         x = "Year", y = "Gap") +
    scale_x_continuous(breaks = sort(unique(df$year)))
})

  # ===================================================
  # SUMMARY TABLE
  # ===================================================
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
