# ==============================================================================
# SERVER: ANALYSIS MODULE
# ==============================================================================

server_analysis <- function(input, output, session, data) {
  
  # ============================================================================
  # REACTIVE: Get numeric variables
  # ============================================================================
  
  numeric_vars <- reactive({
    df <- data()
    df %>%
      select(where(is.numeric)) %>%
      names() %>%
      sort()
  })
  
  # ============================================================================
  # POPULATE DROPDOWNS
  # ============================================================================
  
  observe({
    updateSelectInput(session, "corr_vars", choices = numeric_vars())
  })
  
  observe({
    updateSelectInput(session, "reg_dependent",
                      choices = numeric_vars(),
                      selected = "overall_food_insecurity_rate")
  })
  
  observe({
    updateSelectInput(session, "reg_independent", choices = numeric_vars())
  })
  
  observe({
    updateSelectInput(session, "group_target",
                      choices = numeric_vars(),
                      selected = "overall_food_insecurity_rate")
  })
  
  # ============================================================================
  # CORRELATION ANALYSIS
  # ============================================================================
  # (UNCHANGED — omitted for brevity, exactly your original code)
  # ============================================================================
  
  # ============================================================================
  # REGRESSION ANALYSIS
  # ============================================================================
  # (UNCHANGED — omitted for brevity, exactly your original code)
  # ============================================================================
  
  # ============================================================================
  # GROUP COMPARISON
  # ============================================================================
  
  observeEvent(input$run_group_comparison, {
    
    req(input$group_var)
    req(input$group_target)
    
    df <- data()
    
    # -------------------------
    # Build grouping variable
    # -------------------------
    if (input$group_var == "Census Region")      df$grp <- df$census_region
    if (input$group_var == "Census Division")    df$grp <- df$census_division
    if (input$group_var == "Rural/Urban")        df$grp <- df$urban_rural
    if (input$group_var == "Poverty Category")   df$grp <- df$poverty_category
    if (input$group_var == "Income Category")    df$grp <- df$income_category
    if (input$group_var == "FI Category")        df$grp <- df$fi_category
    
    # -------------------------
    # Special handling for Race
    # -------------------------
    if (input$group_var == "Race") {
      
      df <- df %>%
        select(
          county_state, year,
          black = food_insecurity_rate_among_black_persons_all_ethnicities,
          hispanic = food_insecurity_rate_among_hispanic_persons_any_race,
          white = food_insecurity_rate_among_white_non_hispanic_persons
        ) %>%
        pivot_longer(cols = c(black, hispanic, white),
                     names_to = "grp", values_to = "value") %>%
        drop_na()
      
      target_var <- "value"
      
    } else {
      target_var <- input$group_target
      df <- df %>% drop_na(grp, .data[[target_var]])
    }
    
    if (nrow(df) == 0) {
      output$group_comp_plot <- renderPlot({
        plot.new()
        text(0.5, 0.5, "No data available", cex = 1.5, col = "red")
      })
      return()
    }
    
    # -------------------------
    # BOXPLOT (UNCHANGED)
    # -------------------------
    output$group_comp_plot <- renderPlot({
      ggplot(df, aes(x = grp, y = .data[[target_var]], fill = grp)) +
        geom_boxplot(alpha = 0.7, outlier.alpha = 0.3) +
        stat_summary(fun = mean, geom = "point", shape = 23,
                     size = 3, fill = "white") +
        labs(
          title = paste("Group Comparison:", input$group_var),
          x = input$group_var,
          y = target_var
        ) +
        theme(legend.position = "none",
              axis.text.x = element_text(angle = 45, hjust = 1))
    })
    
    # -------------------------
    # STATISTICAL TEST (UNCHANGED)
    # -------------------------
    output$group_stats <- renderPrint({
      
      grp_count <- n_distinct(df$grp)
      
      summary_stats <- df %>%
        group_by(grp) %>%
        summarise(
          n = n(),
          mean = mean(.data[[target_var]], na.rm = TRUE),
          sd = sd(.data[[target_var]], na.rm = TRUE),
          median = median(.data[[target_var]], na.rm = TRUE),
          .groups = "drop"
        )
      
      print(summary_stats)
      cat("\n")
      
      if (grp_count == 2) {
        print(t.test(df[[target_var]] ~ df$grp))
      } else {
        aov_res <- aov(df[[target_var]] ~ df$grp)
        print(summary(aov_res))
      }
    })
    
    # =====================================================================
    # ✅ NEW ADDITIONS BELOW (ONLY ADDITIONAL OUTPUTS)
    # =====================================================================
    
    # -------------------------
    # GROUP MEANS TABLE
    # -------------------------
    output$group_means_table <- renderDT({
      datatable(
        df %>%
          group_by(grp) %>%
          summarise(
            n = n(),
            mean = mean(.data[[target_var]], na.rm = TRUE),
            sd = sd(.data[[target_var]], na.rm = TRUE),
            median = median(.data[[target_var]], na.rm = TRUE),
            .groups = "drop"
          ),
        options = list(pageLength = 10),
        rownames = FALSE
      ) %>% formatRound(c("mean", "sd", "median"), 2)
    })
    
    # -------------------------
    # EFFECT SIZE
    # -------------------------
    output$group_effect_size <- renderPrint({
      
      grp_count <- n_distinct(df$grp)
      
      if (grp_count == 2) {
        g <- unique(df$grp)
        g1 <- df %>% filter(grp == g[1]) %>% pull(.data[[target_var]])
        g2 <- df %>% filter(grp == g[2]) %>% pull(.data[[target_var]])
        
        d <- (mean(g1, na.rm = TRUE) - mean(g2, na.rm = TRUE)) /
          sqrt((sd(g1, na.rm = TRUE)^2 + sd(g2, na.rm = TRUE)^2) / 2)
        
        cat("Cohen's d:", round(d, 3))
        
      } else {
        aov_res <- aov(df[[target_var]] ~ df$grp)
        eta_sq <- summary(aov_res)[[1]][["Sum Sq"]][1] /
                  sum(summary(aov_res)[[1]][["Sum Sq"]])
        cat("Eta-squared (η²):", round(eta_sq, 3))
      }
    })
    
    # -------------------------
    # DISTRIBUTION PLOT
    # -------------------------
    output$group_distribution_plot <- renderPlot({
      ggplot(df, aes(x = grp, y = .data[[target_var]], fill = grp)) +
        geom_violin(trim = FALSE, alpha = 0.4) +
        geom_boxplot(width = 0.2, outlier.alpha = 0.3) +
        stat_summary(fun = mean, geom = "point", shape = 23,
                     size = 3, fill = "white") +
        theme(legend.position = "none",
              axis.text.x = element_text(angle = 45, hjust = 1))
    })
    
    # -------------------------
    # INTERPRETATION
    # -------------------------
    output$group_interpretation <- renderUI({
      
      means <- df %>% group_by(grp) %>%
        summarise(mean = mean(.data[[target_var]], na.rm = TRUE),
                  .groups = "drop")
      
      max_grp <- means %>% arrange(desc(mean)) %>% slice(1)
      min_grp <- means %>% arrange(mean) %>% slice(1)
      
      HTML(paste0(
        "<p>",
        "<strong>", max_grp$grp, "</strong> has the highest average ",
        target_var, " (", round(max_grp$mean, 2), "), while ",
        "<strong>", min_grp$grp, "</strong> has the lowest (",
        round(min_grp$mean, 2), ").",
        "</p>"
      ))
    })
  })
}
