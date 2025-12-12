# ==============================================================================
# SERVER MODULE: OVERVIEW TAB
# ==============================================================================
# PURPOSE: Calculate and display Key Performance Indicators (KPIs)
# FEATURES: Current metrics, year-over-year changes, trend indicators, trend chart
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

  # ==========================================================================
  # NATIONAL TREND CHART (ggplot2)
  # ==========================================================================

  output$national_trend <- renderPlot({
    # Prepare trend data
    trend_data <- data() %>%
      group_by(year) %>%
      summarise(
        avg_fi_rate = mean(overall_food_insecurity_rate, na.rm = TRUE),
        .groups = "drop"
      )
    
    # Create professional ggplot
    ggplot(trend_data, aes(x = year, y = avg_fi_rate * 100)) +
      
      # Add shaded recession/COVID periods FIRST (background)
      annotate("rect", 
               xmin = 2007, xmax = 2009, 
               ymin = -Inf, ymax = Inf,
               alpha = 0.15, fill = "#E63946") +
      
      annotate("rect",
               xmin = 2020, xmax = 2021,
               ymin = -Inf, ymax = Inf,
               alpha = 0.15, fill = "#9D4EDD") +
      
      # Main line and points
      geom_line(color = "#1E3A5F", size = 1.5, lineend = "round") +
      geom_point(color = "#1E3A5F", size = 4, shape = 21, 
                 fill = "white", stroke = 2) +
      
      # Highlight COVID spike
      geom_point(data = filter(trend_data, year == 2020),
                 aes(x = year, y = avg_fi_rate * 100),
                 color = "#E63946", size = 6, shape = 21,
                 fill = "#E63946", stroke = 2) +
      
      # Event labels
      annotate("text",
               x = 2008, y = 15.5,
               label = "Great Recession",
               size = 4, color = "#E63946", 
               fontface = "bold", hjust = 0.5) +
      
      annotate("text",
               x = 2020.5, y = 15.5,
               label = "COVID-19",
               size = 4, color = "#9D4EDD", 
               fontface = "bold", hjust = 0.5) +
      
      # Scales and labels
      scale_y_continuous(
        labels = function(x) paste0(x, "%"),
        limits = c(9, 16),
        breaks = seq(9, 16, 1),
        expand = c(0, 0)
      ) +
      
      scale_x_continuous(
        breaks = seq(2009, 2023, 2),
        expand = c(0.02, 0.02)
      ) +
      
      labs(
        title = "National Food Insecurity Trend (2009-2023)",
        subtitle = "Percentage of U.S. population experiencing food insecurity",
        x = NULL,
        y = "Food Insecurity Rate",
        caption = "Source: Feeding America, U.S. Census Bureau (ACS)"
      ) +
      
      # Professional theme
      theme_minimal(base_size = 15, base_family = "sans") +
      theme(
        # Title styling
        plot.title = element_text(
          face = "bold", 
          size = 18, 
          hjust = 0.5,
          color = "#1E3A5F",
          margin = margin(b = 8)
        ),
        plot.subtitle = element_text(
          size = 13,
          hjust = 0.5,
          color = "#6C757D",
          margin = margin(b = 16)
        ),
        plot.caption = element_text(
          color = "#6C757D", 
          size = 10,
          hjust = 1,
          margin = margin(t = 12)
        ),
        
        # Axis styling
        axis.title.y = element_text(
          face = "bold",
          color = "#2D3142",
          size = 13,
          margin = margin(r = 10)
        ),
        axis.text = element_text(
          color = "#2D3142",
          size = 12
        ),
        
        # Grid
        panel.grid.major.y = element_line(
          color = "#E5E5E5",
          size = 0.5
        ),
        panel.grid.minor = element_blank(),
        panel.grid.major.x = element_blank(),
        
        # Background
        plot.background = element_rect(fill = "white", color = NA),
        panel.background = element_rect(fill = "white", color = NA),
        
        # Margins
        plot.margin = margin(20, 20, 20, 20)
      )
    
  }, height = 450, res = 96)
}