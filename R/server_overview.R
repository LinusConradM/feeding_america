# ==============================================================================
# SERVER MODULE: OVERVIEW TAB
# ==============================================================================
# PURPOSE: Calculate and display Key Performance Indicators (KPIs)
# FEATURES: Current metrics, year-over-year changes, trend indicators
# TEAM: Conrad, Sharon, Ryann, Alex
# ==============================================================================

server_overview <- function(input, output, session, data) {
  # Get current year (latest year in data)
  current_year <- reactive({
    max(data()$year, na.rm = TRUE)
  })

  # Get previous year
  previous_year <- reactive({
    current_year() - 1
  })

  # ==========================================================================
  # KPI: NATIONAL FOOD INSECURITY RATE
  # ==========================================================================

  output$kpi_national_fi_rate <- renderText({
    current_rate <- data() %>%
      filter(year == current_year()) %>%
      summarise(rate = mean(overall_food_insecurity_rate, na.rm = TRUE)) %>%
      pull(rate)

    if (is.na(current_rate) || length(current_rate) == 0) {
      return("N/A")
    }

    paste0(round(current_rate * 100, 1), "%")
  })

  output$kpi_fi_rate_change <- renderUI({
    current_rate <- data() %>%
      filter(year == current_year()) %>%
      summarise(rate = mean(overall_food_insecurity_rate, na.rm = TRUE)) %>%
      pull(rate)

    previous_rate <- data() %>%
      filter(year == previous_year()) %>%
      summarise(rate = mean(overall_food_insecurity_rate, na.rm = TRUE)) %>%
      pull(rate)

    if (is.na(current_rate) || is.na(previous_rate)) {
      return("")
    }

    change <- current_rate - previous_rate
    pct_change <- (change / previous_rate) * 100

    arrow <- if (change > 0) "↑" else "↓"
    color <- if (change > 0) "#dc3545" else "#28a745"

    HTML(paste0(
      "<span style='color: ", color, "; font-weight: 600;'>",
      arrow, " ", abs(round(pct_change, 1)), "% vs ", previous_year(),
      "</span>"
    ))
  })

  # ==========================================================================
  # KPI: TOTAL FOOD INSECURE PERSONS
  # ==========================================================================

  output$kpi_total_food_insecure <- renderText({
    total <- data() %>%
      filter(year == current_year()) %>%
      summarise(total = sum(no_of_food_insecure_persons_overall, na.rm = TRUE)) %>%
      pull(total)

    if (is.na(total) || length(total) == 0) {
      return("N/A")
    }

    # Format in millions
    paste0(round(total / 1e6, 1), "M")
  })

  output$kpi_fi_persons_change <- renderUI({
    current_total <- data() %>%
      filter(year == current_year()) %>%
      summarise(total = sum(no_of_food_insecure_persons_overall, na.rm = TRUE)) %>%
      pull(total)

    previous_total <- data() %>%
      filter(year == previous_year()) %>%
      summarise(total = sum(no_of_food_insecure_persons_overall, na.rm = TRUE)) %>%
      pull(total)

    if (is.na(current_total) || is.na(previous_total)) {
      return("")
    }

    change <- current_total - previous_total
    pct_change <- (change / previous_total) * 100

    arrow <- if (change > 0) "↑" else "↓"
    color <- if (change > 0) "#dc3545" else "#28a745"

    HTML(paste0(
      "<span style='color: ", color, "; font-weight: 600;'>",
      arrow, " ", abs(round(pct_change, 1)), "% vs ", previous_year(),
      "</span>"
    ))
  })

  # ==========================================================================
  # KPI: CHILD FOOD INSECURITY RATE
  # ==========================================================================

  output$kpi_child_fi_rate <- renderText({
    current_rate <- data() %>%
      filter(year == current_year()) %>%
      summarise(rate = mean(child_food_insecurity_rate, na.rm = TRUE)) %>%
      pull(rate)

    if (is.na(current_rate) || length(current_rate) == 0) {
      return("N/A")
    }

    paste0(round(current_rate * 100, 1), "%")
  })

  output$kpi_child_fi_change <- renderUI({
    current_rate <- data() %>%
      filter(year == current_year()) %>%
      summarise(rate = mean(child_food_insecurity_rate, na.rm = TRUE)) %>%
      pull(rate)

    previous_rate <- data() %>%
      filter(year == previous_year()) %>%
      summarise(rate = mean(child_food_insecurity_rate, na.rm = TRUE)) %>%
      pull(rate)

    if (is.na(current_rate) || is.na(previous_rate)) {
      return("")
    }

    change <- current_rate - previous_rate
    pct_change <- (change / previous_rate) * 100

    arrow <- if (change > 0) "↑" else "↓"
    color <- if (change > 0) "#dc3545" else "#28a745"

    HTML(paste0(
      "<span style='color: ", color, "; font-weight: 600;'>",
      arrow, " ", abs(round(pct_change, 1)), "% vs ", previous_year(),
      "</span>"
    ))
  })

  # ==========================================================================
  # KPI: AVERAGE COST PER MEAL
  # ==========================================================================

  output$kpi_avg_cost_per_meal <- renderText({
    avg_cost <- data() %>%
      filter(year == current_year()) %>%
      summarise(cost = mean(cost_per_meal, na.rm = TRUE)) %>%
      pull(cost)

    if (is.na(avg_cost) || length(avg_cost) == 0) {
      return("N/A")
    }

    paste0("$", round(avg_cost, 2))
  })

  output$kpi_cost_change <- renderUI({
    current_cost <- data() %>%
      filter(year == current_year()) %>%
      summarise(cost = mean(cost_per_meal, na.rm = TRUE)) %>%
      pull(cost)

    previous_cost <- data() %>%
      filter(year == previous_year()) %>%
      summarise(cost = mean(cost_per_meal, na.rm = TRUE)) %>%
      pull(cost)

    if (is.na(current_cost) || is.na(previous_cost)) {
      return("")
    }

    change <- current_cost - previous_cost
    pct_change <- (change / previous_cost) * 100

    arrow <- if (change > 0) "↑" else "↓"
    color <- if (change > 0) "#dc3545" else "#28a745"

    HTML(paste0(
      "<span style='color: ", color, "; font-weight: 600;'>",
      arrow, " ", abs(round(pct_change, 1)), "% vs ", previous_year(),
      "</span>"
    ))
  })

  # ==========================================================================
  # KPI: POVERTY RATE
  # ==========================================================================

  output$kpi_poverty_rate <- renderText({
    current_rate <- data() %>%
      filter(year == current_year()) %>%
      summarise(rate = mean(poverty_rate, na.rm = TRUE)) %>%
      pull(rate)

    if (is.na(current_rate) || length(current_rate) == 0) {
      return("N/A")
    }

    paste0(round(current_rate * 100, 1), "%")
  })

  output$kpi_poverty_change <- renderUI({
    current_rate <- data() %>%
      filter(year == current_year()) %>%
      summarise(rate = mean(poverty_rate, na.rm = TRUE)) %>%
      pull(rate)

    previous_rate <- data() %>%
      filter(year == previous_year()) %>%
      summarise(rate = mean(poverty_rate, na.rm = TRUE)) %>%
      pull(rate)

    if (is.na(current_rate) || is.na(previous_rate)) {
      return("")
    }

    change <- current_rate - previous_rate
    pct_change <- (change / previous_rate) * 100

    arrow <- if (change > 0) "↑" else "↓"
    color <- if (change > 0) "#dc3545" else "#28a745"

    HTML(paste0(
      "<span style='color: ", color, "; font-weight: 600;'>",
      arrow, " ", abs(round(pct_change, 1)), "% vs ", previous_year(),
      "</span>"
    ))
  })

  # ==========================================================================
  # KPI: MEDIAN INCOME
  # ==========================================================================

  output$kpi_median_income <- renderText({
    median_inc <- data() %>%
      filter(year == current_year()) %>%
      summarise(income = mean(median_income, na.rm = TRUE)) %>%
      pull(income)

    if (is.na(median_inc) || length(median_inc) == 0) {
      return("N/A")
    }

    paste0("$", format(round(median_inc), big.mark = ","))
  })

  output$kpi_income_change <- renderUI({
    current_income <- data() %>%
      filter(year == current_year()) %>%
      summarise(income = mean(median_income, na.rm = TRUE)) %>%
      pull(income)

    previous_income <- data() %>%
      filter(year == previous_year()) %>%
      summarise(income = mean(median_income, na.rm = TRUE)) %>%
      pull(income)

    if (is.na(current_income) || is.na(previous_income)) {
      return("")
    }

    change <- current_income - previous_income
    pct_change <- (change / previous_income) * 100

    arrow <- if (change > 0) "↑" else "↓"
    color <- if (change > 0) "#28a745" else "#dc3545" # Reversed: higher income is good

    HTML(paste0(
      "<span style='color: ", color, "; font-weight: 600;'>",
      arrow, " ", abs(round(pct_change, 1)), "% vs ", previous_year(),
      "</span>"
    ))
  })

  # ==========================================================================
  # KPI: UNEMPLOYMENT RATE
  # ==========================================================================

  output$kpi_unemployment_rate <- renderText({
    current_rate <- data() %>%
      filter(year == current_year()) %>%
      summarise(rate = mean(unemployment_rate, na.rm = TRUE)) %>%
      pull(rate)

    if (is.na(current_rate) || length(current_rate) == 0) {
      return("N/A")
    }

    paste0(round(current_rate * 100, 1), "%")
  })

  output$kpi_unemployment_change <- renderUI({
    current_rate <- data() %>%
      filter(year == current_year()) %>%
      summarise(rate = mean(unemployment_rate, na.rm = TRUE)) %>%
      pull(rate)

    previous_rate <- data() %>%
      filter(year == previous_year()) %>%
      summarise(rate = mean(unemployment_rate, na.rm = TRUE)) %>%
      pull(rate)

    if (is.na(current_rate) || is.na(previous_rate)) {
      return("")
    }

    change <- current_rate - previous_rate
    pct_change <- (change / previous_rate) * 100

    arrow <- if (change > 0) "↑" else "↓"
    color <- if (change > 0) "#dc3545" else "#28a745"

    HTML(paste0(
      "<span style='color: ", color, "; font-weight: 600;'>",
      arrow, " ", abs(round(pct_change, 1)), "% vs ", previous_year(),
      "</span>"
    ))
  })

  # ==========================================================================
  # KPI: BUDGET SHORTFALL
  # ==========================================================================

  output$kpi_budget_shortfall <- renderText({
    total_shortfall <- data() %>%
      filter(year == current_year()) %>%
      summarise(shortfall = sum(weighted_annual_food_budget_shortfall, na.rm = TRUE)) %>%
      pull(shortfall)

    if (is.na(total_shortfall) || length(total_shortfall) == 0) {
      return("N/A")
    }

    # Format in billions
    paste0("$", round(total_shortfall / 1e9, 1), "B")
  })

  output$kpi_shortfall_change <- renderUI({
    current_shortfall <- data() %>%
      filter(year == current_year()) %>%
      summarise(shortfall = sum(weighted_annual_food_budget_shortfall, na.rm = TRUE)) %>%
      pull(shortfall)

    previous_shortfall <- data() %>%
      filter(year == previous_year()) %>%
      summarise(shortfall = sum(weighted_annual_food_budget_shortfall, na.rm = TRUE)) %>%
      pull(shortfall)

    if (is.na(current_shortfall) || is.na(previous_shortfall)) {
      return("")
    }

    change <- current_shortfall - previous_shortfall
    pct_change <- (change / previous_shortfall) * 100

    arrow <- if (change > 0) "↑" else "↓"
    color <- if (change > 0) "#dc3545" else "#28a745"

    HTML(paste0(
      "<span style='color: ", color, "; font-weight: 600;'>",
      arrow, " ", abs(round(pct_change, 1)), "% vs ", previous_year(),
      "</span>"
    ))
  })

  # Note: Trend plot removed - it's in the Exploration tab
}
