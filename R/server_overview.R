# ==============================================================================
# SERVER MODULE: EXECUTIVE OVERVIEW - COMPREHENSIVE VERSION
# ==============================================================================
# PURPOSE: Calculate and display comprehensive executive dashboard
# FEATURES: KPIs, trends, rankings, demographics, geography, statistics
# ==============================================================================

server_overview <- function(input, output, session, data) {
  
  # ==========================================================================
  # REACTIVE: SELECTED YEAR
  # ==========================================================================
  
  selected_year <- reactive({
    if (!is.null(input$overview_year_selector)) {
      return(as.numeric(input$overview_year_selector))
    }
    return(max(data()$year, na.rm = TRUE))
  })
  
  previous_year <- reactive({
    selected_year() - 1
  })
  
  # ==========================================================================
  # REACTIVE: FILTERED DATA FOR SELECTED YEAR
  # ==========================================================================
  
  year_data <- reactive({
    data() %>%
      filter(year == selected_year())
  })
  
  previous_year_data <- reactive({
    data() %>%
      filter(year == previous_year())
  })
  
  # ==========================================================================
  # KPI: NATIONAL FOOD INSECURITY RATE
  # ==========================================================================
  
  output$kpi_national_fi_rate <- renderText({
    current_rate <- year_data() %>%
      summarise(rate = mean(overall_food_insecurity_rate, na.rm = TRUE)) %>%
      pull(rate)
    
    if (is.na(current_rate) || length(current_rate) == 0) {
      return("N/A")
    }
    
    paste0(round(current_rate * 100, 1), "%")
  })
  
  output$kpi_fi_rate_change <- renderUI({
    current_rate <- year_data() %>%
      summarise(rate = mean(overall_food_insecurity_rate, na.rm = TRUE)) %>%
      pull(rate)
    
    previous_rate <- previous_year_data() %>%
      summarise(rate = mean(overall_food_insecurity_rate, na.rm = TRUE)) %>%
      pull(rate)
    
    if (is.na(current_rate) || is.na(previous_rate)) {
      return(HTML(""))
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
    total <- year_data() %>%
      summarise(total = sum(no_of_food_insecure_persons_overall, na.rm = TRUE)) %>%
      pull(total)
    
    if (is.na(total) || length(total) == 0) {
      return("N/A")
    }
    
    paste0(round(total / 1e6, 1), "M")
  })
  
  output$kpi_fi_persons_change <- renderUI({
    current_total <- year_data() %>%
      summarise(total = sum(no_of_food_insecure_persons_overall, na.rm = TRUE)) %>%
      pull(total)
    
    previous_total <- previous_year_data() %>%
      summarise(total = sum(no_of_food_insecure_persons_overall, na.rm = TRUE)) %>%
      pull(total)
    
    if (is.na(current_total) || is.na(previous_total)) {
      return(HTML(""))
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
    current_rate <- year_data() %>%
      summarise(rate = mean(child_food_insecurity_rate, na.rm = TRUE)) %>%
      pull(rate)
    
    if (is.na(current_rate) || length(current_rate) == 0) {
      return("N/A")
    }
    
    paste0(round(current_rate * 100, 1), "%")
  })
  
  output$kpi_child_fi_change <- renderUI({
    current_rate <- year_data() %>%
      summarise(rate = mean(child_food_insecurity_rate, na.rm = TRUE)) %>%
      pull(rate)
    
    previous_rate <- previous_year_data() %>%
      summarise(rate = mean(child_food_insecurity_rate, na.rm = TRUE)) %>%
      pull(rate)
    
    if (is.na(current_rate) || is.na(previous_rate)) {
      return(HTML(""))
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
    avg_cost <- year_data() %>%
      summarise(cost = mean(cost_per_meal, na.rm = TRUE)) %>%
      pull(cost)
    
    if (is.na(avg_cost) || length(avg_cost) == 0) {
      return("N/A")
    }
    
    paste0("$", round(avg_cost, 2))
  })
  
  output$kpi_cost_change <- renderUI({
    current_cost <- year_data() %>%
      summarise(cost = mean(cost_per_meal, na.rm = TRUE)) %>%
      pull(cost)
    
    previous_cost <- previous_year_data() %>%
      summarise(cost = mean(cost_per_meal, na.rm = TRUE)) %>%
      pull(cost)
    
    if (is.na(current_cost) || is.na(previous_cost)) {
      return(HTML(""))
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
    current_rate <- year_data() %>%
      summarise(rate = mean(poverty_rate, na.rm = TRUE)) %>%
      pull(rate)
    
    if (is.na(current_rate) || length(current_rate) == 0) {
      return("N/A")
    }
    
    paste0(round(current_rate * 100, 1), "%")
  })
  
  output$kpi_poverty_change <- renderUI({
    current_rate <- year_data() %>%
      summarise(rate = mean(poverty_rate, na.rm = TRUE)) %>%
      pull(rate)
    
    previous_rate <- previous_year_data() %>%
      summarise(rate = mean(poverty_rate, na.rm = TRUE)) %>%
      pull(rate)
    
    if (is.na(current_rate) || is.na(previous_rate)) {
      return(HTML(""))
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
    median_inc <- year_data() %>%
      summarise(income = mean(median_income, na.rm = TRUE)) %>%
      pull(income)
    
    if (is.na(median_inc) || length(median_inc) == 0) {
      return("N/A")
    }
    
    paste0("$", format(round(median_inc), big.mark = ","))
  })
  
  output$kpi_income_change <- renderUI({
    current_income <- year_data() %>%
      summarise(income = mean(median_income, na.rm = TRUE)) %>%
      pull(income)
    
    previous_income <- previous_year_data() %>%
      summarise(income = mean(median_income, na.rm = TRUE)) %>%
      pull(income)
    
    if (is.na(current_income) || is.na(previous_income)) {
      return(HTML(""))
    }
    
    change <- current_income - previous_income
    pct_change <- (change / previous_income) * 100
    
    arrow <- if (change > 0) "↑" else "↓"
    color <- if (change > 0) "#28a745" else "#dc3545"
    
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
    current_rate <- year_data() %>%
      summarise(rate = mean(unemployment_rate, na.rm = TRUE)) %>%
      pull(rate)
    
    if (is.na(current_rate) || length(current_rate) == 0) {
      return("N/A")
    }
    
    paste0(round(current_rate * 100, 1), "%")
  })
  
  output$kpi_unemployment_change <- renderUI({
    current_rate <- year_data() %>%
      summarise(rate = mean(unemployment_rate, na.rm = TRUE)) %>%
      pull(rate)
    
    previous_rate <- previous_year_data() %>%
      summarise(rate = mean(unemployment_rate, na.rm = TRUE)) %>%
      pull(rate)
    
    if (is.na(current_rate) || is.na(previous_rate)) {
      return(HTML(""))
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
    total_shortfall <- year_data() %>%
      summarise(shortfall = sum(weighted_annual_food_budget_shortfall, na.rm = TRUE)) %>%
      pull(shortfall)
    
    if (is.na(total_shortfall) || length(total_shortfall) == 0) {
      return("N/A")
    }
    
    paste0("$", round(total_shortfall / 1e9, 1), "B")
  })
  
  output$kpi_shortfall_change <- renderUI({
    current_shortfall <- year_data() %>%
      summarise(shortfall = sum(weighted_annual_food_budget_shortfall, na.rm = TRUE)) %>%
      pull(shortfall)
    
    previous_shortfall <- previous_year_data() %>%
      summarise(shortfall = sum(weighted_annual_food_budget_shortfall, na.rm = TRUE)) %>%
      pull(shortfall)
    
    if (is.na(current_shortfall) || is.na(previous_shortfall)) {
      return(HTML(""))
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
  # KEY STATISTICS PANEL
  # ==========================================================================
  
  output$stat_median_fi <- renderText({
    median_fi <- year_data() %>%
      summarise(med = median(overall_food_insecurity_rate, na.rm = TRUE)) %>%
      pull(med)
    
    paste0(round(median_fi * 100, 1), "%")
  })
  
  output$stat_range_fi <- renderText({
    range_fi <- year_data() %>%
      summarise(
        min = min(overall_food_insecurity_rate, na.rm = TRUE),
        max = max(overall_food_insecurity_rate, na.rm = TRUE)
      )
    
    paste0(round(range_fi$min * 100, 1), "% - ", round(range_fi$max * 100, 1), "%")
  })
  
  output$stat_sd_fi <- renderText({
    sd_fi <- year_data() %>%
      summarise(sd = sd(overall_food_insecurity_rate, na.rm = TRUE)) %>%
      pull(sd)
    
    paste0(round(sd_fi * 100, 2), "%")
  })
  
  output$stat_above_avg <- renderText({
    avg_fi <- mean(year_data()$overall_food_insecurity_rate, na.rm = TRUE)
    
    above_avg <- year_data() %>%
      filter(overall_food_insecurity_rate > avg_fi) %>%
      nrow()
    
    format(above_avg, big.mark = ",")
  })
  
  # ==========================================================================
  # NATIONAL TREND CHART (UNCHANGED)
  # ==========================================================================
  
  output$national_trend <- renderPlot({
    trend_data <- data() %>%
      group_by(year) %>%
      summarise(
        avg_fi_rate = mean(overall_food_insecurity_rate, na.rm = TRUE),
        .groups = "drop"
      )
    
    ggplot(trend_data, aes(x = year, y = avg_fi_rate * 100)) +
      annotate("rect", 
               xmin = 2007, xmax = 2009, 
               ymin = -Inf, ymax = Inf,
               alpha = 0.15, fill = "#E63946") +
      annotate("rect",
               xmin = 2020, xmax = 2021,
               ymin = -Inf, ymax = Inf,
               alpha = 0.15, fill = "#9D4EDD") +
      geom_line(color = "#1E3A5F", size = 1.5, lineend = "round") +
      geom_point(color = "#1E3A5F", size = 4, shape = 21, 
                 fill = "white", stroke = 2) +
      geom_point(data = filter(trend_data, year == 2020),
                 aes(x = year, y = avg_fi_rate * 100),
                 color = "#E63946", size = 6, shape = 21,
                 fill = "#E63946", stroke = 2) +
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
      theme_minimal(base_size = 15, base_family = "sans") +
      theme(
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
        panel.grid.major.y = element_line(
          color = "#E5E5E5",
          size = 0.5
        ),
        panel.grid.minor = element_blank(),
        panel.grid.major.x = element_blank(),
        plot.background = element_rect(fill = "white", color = NA),
        panel.background = element_rect(fill = "white", color = NA),
        plot.margin = margin(20, 20, 20, 20)
      )
  }, height = 450, res = 96)
  
  # ==========================================================================
  # REGIONAL COMPARISON CHART (NEW)
  # ==========================================================================
  
  output$regional_comparison <- renderPlot({
    regional_data <- year_data() %>%
      filter(!is.na(census_region)) %>%
      group_by(census_region) %>%
      summarise(
        avg_fi = mean(overall_food_insecurity_rate, na.rm = TRUE),
        .groups = "drop"
      ) %>%
      arrange(desc(avg_fi))
    
    ggplot(regional_data, aes(x = reorder(census_region, avg_fi), y = avg_fi * 100)) +
      geom_col(fill = "#2A9D8F", alpha = 0.9) +
      geom_text(
        aes(label = paste0(round(avg_fi * 100, 1), "%")),
        hjust = -0.2,
        size = 5,
        fontface = "bold",
        color = "#1E3A5F"
      ) +
      coord_flip() +
      scale_y_continuous(
        labels = function(x) paste0(x, "%"),
        expand = expansion(mult = c(0, 0.15))
      ) +
      labs(
        title = paste0("Regional FI Rates (", selected_year(), ")"),
        x = NULL,
        y = "Food Insecurity Rate"
      ) +
      theme_minimal(base_size = 13) +
      theme(
        plot.title = element_text(face = "bold", size = 14, color = "#1E3A5F"),
        axis.text = element_text(size = 12, color = "#2D3142"),
        panel.grid.major.x = element_line(color = "#E5E5E5", size = 0.5),
        panel.grid.major.y = element_blank(),
        panel.grid.minor = element_blank()
      )
  }, height = 400, res = 96)
  
  # ==========================================================================
  # TOP 10 STATES (HIGHEST FI)
  # ==========================================================================
  
  output$top_10_states <- DT::renderDataTable({
    top_states <- year_data() %>%
      group_by(state) %>%
      summarise(
        `FI Rate (%)` = round(mean(overall_food_insecurity_rate, na.rm = TRUE) * 100, 1),
        Counties = n_distinct(fips),
        `Total Food Insecure` = format(sum(no_of_food_insecure_persons_overall, na.rm = TRUE), big.mark = ","),
        .groups = "drop"
      ) %>%
      arrange(desc(`FI Rate (%)`)) %>%
      head(10)
    
    DT::datatable(
      top_states,
      options = list(
        pageLength = 10,
        dom = 't',
        ordering = FALSE
      ),
      rownames = FALSE
    ) %>%
      DT::formatStyle(
        'FI Rate (%)',
        backgroundColor = DT::styleInterval(
          cuts = c(12, 14, 16),
          values = c('#fff', '#ffe6e6', '#ffcccc', '#ff9999')
        ),
        fontWeight = 'bold'
      )
  })
  
  # ==========================================================================
  # BOTTOM 10 STATES (LOWEST FI)
  # ==========================================================================
  
  output$bottom_10_states <- DT::renderDataTable({
    bottom_states <- year_data() %>%
      group_by(state) %>%
      summarise(
        `FI Rate (%)` = round(mean(overall_food_insecurity_rate, na.rm = TRUE) * 100, 1),
        Counties = n_distinct(fips),
        `Total Food Insecure` = format(sum(no_of_food_insecure_persons_overall, na.rm = TRUE), big.mark = ","),
        .groups = "drop"
      ) %>%
      arrange(`FI Rate (%)`) %>%
      head(10)
    
    DT::datatable(
      bottom_states,
      options = list(
        pageLength = 10,
        dom = 't',
        ordering = FALSE
      ),
      rownames = FALSE
    ) %>%
      DT::formatStyle(
        'FI Rate (%)',
        backgroundColor = DT::styleInterval(
          cuts = c(8, 10, 12),
          values = c('#ccffcc', '#e6ffe6', '#f0fff0', '#fff')
        ),
        fontWeight = 'bold'
      )
  })
  
  # ==========================================================================
  # DEMOGRAPHIC DISPARITIES CHART (NEW)
  # ==========================================================================
  
  output$demographic_chart <- renderPlot({
    demo_data <- year_data() %>%
      summarise(
        Overall = mean(overall_food_insecurity_rate, na.rm = TRUE),
        Children = mean(child_food_insecurity_rate, na.rm = TRUE),
        Black = mean(food_insecurity_rate_among_black_persons_all_ethnicities, na.rm = TRUE),
        Hispanic = mean(food_insecurity_rate_among_hispanic_persons_any_race, na.rm = TRUE),
        White = mean(food_insecurity_rate_among_white_non_hispanic_persons, na.rm = TRUE),
        .groups = "drop"
      ) %>%
      pivot_longer(everything(), names_to = "Group", values_to = "Rate") %>%
      mutate(Group = factor(Group, levels = c("White", "Overall", "Hispanic", "Black", "Children")))
    
    ggplot(demo_data, aes(x = Group, y = Rate * 100, fill = Group)) +
      geom_col(alpha = 0.9, width = 0.7) +
      geom_text(
        aes(label = paste0(round(Rate * 100, 1), "%")),
        vjust = -0.5,
        size = 5,
        fontface = "bold"
      ) +
      scale_fill_manual(values = c(
        "Overall" = "#457B9D",
        "Children" = "#9D4EDD",
        "Black" = "#E63946",
        "Hispanic" = "#F4A261",
        "White" = "#2A9D8F"
      )) +
      scale_y_continuous(
        labels = function(x) paste0(x, "%"),
        expand = expansion(mult = c(0, 0.15))
      ) +
      labs(
        title = paste0("Food Insecurity by Group (", selected_year(), ")"),
        x = NULL,
        y = "Food Insecurity Rate"
      ) +
      theme_minimal(base_size = 13) +
      theme(
        plot.title = element_text(face = "bold", size = 14, color = "#1E3A5F"),
        axis.text = element_text(size = 11, color = "#2D3142"),
        legend.position = "none",
        panel.grid.major.x = element_blank(),
        panel.grid.minor = element_blank()
      )
  }, height = 400, res = 96)
  
  # ==========================================================================
  # STATE-LEVEL MAP (NEW)
  # ==========================================================================
  
  output$state_map <- renderPlot({
    state_data <- year_data() %>%
      group_by(state) %>%
      summarise(
        avg_fi = mean(overall_food_insecurity_rate, na.rm = TRUE),
        .groups = "drop"
      ) %>%
      mutate(state = tolower(state))
    
    # Get US map data
    if (require("maps", quietly = TRUE)) {
      us_map <- map_data("state")
      
      map_data_merged <- us_map %>%
        left_join(state_data, by = c("region" = "state"))
      
      ggplot(map_data_merged, aes(x = long, y = lat, group = group, fill = avg_fi * 100)) +
        geom_polygon(color = "white", size = 0.5) +
        scale_fill_gradient2(
          low = "#06D6A0",
          mid = "#F4A261",
          high = "#E63946",
          midpoint = 12,
          na.value = "gray90",
          name = "FI Rate (%)",
          limits = c(5, 20)
        ) +
        coord_map("albers", lat0 = 39, lat1 = 45) +
        labs(
          title = paste0("State-Level Food Insecurity (", selected_year(), ")")
        ) +
        theme_void() +
        theme(
          plot.title = element_text(face = "bold", size = 14, color = "#1E3A5F", hjust = 0.5),
          legend.position = "right",
          legend.title = element_text(face = "bold", size = 11),
          plot.margin = margin(10, 10, 10, 10)
        )
    } else {
      # Fallback if maps package not available
      plot.new()
      text(0.5, 0.5, "Install 'maps' package to view state map\n\ninstall.packages('maps')", 
           cex = 1.2, col = "#6C757D")
    }
  }, height = 400, res = 96)
  
  # ==========================================================================
  # URBAN VS RURAL COMPARISON (NEW)
  # ==========================================================================
  
  output$urban_rural_comparison <- renderPlot({
    ur_data <- year_data() %>%
      filter(!is.na(urban_rural)) %>%
      group_by(urban_rural) %>%
      summarise(
        avg_fi = mean(overall_food_insecurity_rate, na.rm = TRUE),
        count = n(),
        .groups = "drop"
      )
    
    ggplot(ur_data, aes(x = urban_rural, y = avg_fi * 100, fill = urban_rural)) +
      geom_col(alpha = 0.9, width = 0.6) +
      geom_text(
        aes(label = paste0(round(avg_fi * 100, 1), "%\n(n=", format(count, big.mark = ","), ")")),
        vjust = -0.5,
        size = 5,
        fontface = "bold"
      ) +
      scale_fill_manual(values = c(
        "Metro" = "#457B9D",
        "Non-metro" = "#F4A261",
        "Rural" = "#E63946"
      )) +
      scale_y_continuous(
        labels = function(x) paste0(x, "%"),
        expand = expansion(mult = c(0, 0.20))
      ) +
      labs(
        title = paste0("Urban vs Rural Food Insecurity (", selected_year(), ")"),
        x = NULL,
        y = "Food Insecurity Rate"
      ) +
      theme_minimal(base_size = 14) +
      theme(
        plot.title = element_text(face = "bold", size = 15, color = "#1E3A5F", hjust = 0.5),
        axis.text = element_text(size = 12, color = "#2D3142"),
        legend.position = "none",
        panel.grid.major.x = element_blank(),
        panel.grid.minor = element_blank()
      )
  }, height = 300, res = 96)
  
  # ==========================================================================
  # AI EXECUTIVE SUMMARY (OPTIONAL)
  # ==========================================================================
  
  output$ai_executive_summary <- renderUI({
    req(input$generate_summary)
    
    # Check if AI module is available
    if (!exists("ask_claude")) {
      return(HTML(
        '<div style="background: #FFF3CD; border-left: 4px solid #FFC107; padding: 16px 20px; border-radius: 8px; margin: 24px 0;">
          <p style="margin: 0; color: #856404;">
            <i class="fa fa-exclamation-triangle"></i> 
            AI summary requires the AI explanations module. Load it with: <code>source("R/ai_explanations.R")</code>
          </p>
        </div>'
      ))
    }
    
    # Generate summary (placeholder - implement when AI module is loaded)
    HTML(
      '<div style="background: linear-gradient(135deg, #2A9D8F 0%, #3CBAA8 100%); 
                   padding: 24px; border-radius: 12px; margin: 24px 0; color: white;
                   box-shadow: 0 4px 16px rgba(0,0,0,0.12);">
        <h3 style="color: white; margin-top: 0; border-bottom: 2px solid rgba(255,255,255,0.3); padding-bottom: 12px;">
          <i class="fa fa-robot"></i> Executive Summary (AI-Generated)
        </h3>
        <p style="line-height: 1.8; margin: 16px 0;">
          AI summary generation will be implemented when you load the AI explanations module.
          This will provide intelligent insights based on the current data.
        </p>
        <p style="margin: 0; font-size: 14px; opacity: 0.8;">
          <i class="fa fa-info-circle"></i> To enable: <code>source("R/ai_explanations.R")</code>
        </p>
      </div>'
    )
  })
  
  # ==========================================================================
  # REFRESH BUTTON
  # ==========================================================================
  
  observeEvent(input$refresh_overview, {
    session$reload()
  })
}
