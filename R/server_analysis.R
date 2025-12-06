# ==============================================================================
# SERVER: ANALYSIS MODULE
# ==============================================================================
# Complete statistical analysis module with:
# - Correlation analysis
# - Regression analysis  
# - Group comparison (t-test/ANOVA)
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
  
  # Update correlation variable selector
  observe({
    updateSelectInput(
      session, "corr_vars",
      choices = numeric_vars()
    )
  })
  
  # Update regression dependent variable
  observe({
    updateSelectInput(
      session, "reg_dependent",
      choices = numeric_vars(),
      selected = "overall_food_insecurity_rate"
    )
  })
  
  # Update regression independent variables
  observe({
    updateSelectInput(
      session, "reg_independent",
      choices = numeric_vars()
    )
  })
  
  # Update group comparison outcome variable
  observe({
    updateSelectInput(
      session, "group_target",
      choices = numeric_vars(),
      selected = "overall_food_insecurity_rate"
    )
  })
  
  # ============================================================================
  # CORRELATION ANALYSIS
  # ============================================================================
  
  observeEvent(input$run_correlation, {
    
    req(input$corr_vars)
    req(length(input$corr_vars) >= 2)
    
    df <- data()
    
    # Filter to selected variables
    corr_data <- df %>%
      select(all_of(input$corr_vars)) %>%
      drop_na()
    
    if (nrow(corr_data) == 0) {
      output$corr_plot <- renderPlot({
        plot.new()
        text(0.5, 0.5, "No data available for selected variables",
             cex = 1.5, col = "red")
      })
      return()
    }
    
    # Calculate correlation matrix
    corr_matrix <- cor(corr_data, use = "pairwise.complete.obs")
    
    # -------------------------
    # CORRELATION HEATMAP
    # -------------------------
    output$corr_plot <- renderPlot({
      
      # Convert to long format for ggplot
      corr_long <- corr_matrix %>%
        as.data.frame() %>%
        rownames_to_column("var1") %>%
        pivot_longer(cols = -var1, names_to = "var2", values_to = "correlation")
      
      # Create heatmap
      ggplot(corr_long, aes(x = var1, y = var2, fill = correlation)) +
        geom_tile(color = "white") +
        geom_text(aes(label = round(correlation, 2)), size = 4) +
        scale_fill_gradient2(
          low = "#d73027", 
          mid = "white", 
          high = "#4575b4",
          midpoint = 0,
          limits = c(-1, 1),
          name = "Correlation"
        ) +
        labs(
          title = "Correlation Matrix",
          x = NULL,
          y = NULL
        ) +
        theme(
          axis.text.x = element_text(angle = 45, hjust = 1),
          panel.background = element_blank()
        )
    })
    
    # -------------------------
    # CORRELATION TABLE
    # -------------------------
    output$corr_table <- renderDT({
      
      # Create pairwise correlation table
      corr_pairs <- corr_matrix %>%
        as.data.frame() %>%
        rownames_to_column("Variable_1") %>%
        pivot_longer(cols = -Variable_1, names_to = "Variable_2", values_to = "Correlation") %>%
        filter(Variable_1 < Variable_2) %>%  # Remove duplicates
        arrange(desc(abs(Correlation)))
      
      datatable(
        corr_pairs,
        options = list(pageLength = 10, dom = 'tp'),
        rownames = FALSE
      ) %>%
        formatRound("Correlation", 3)
    })
    
    # -------------------------
    # CORRELATION INTERPRETATION
    # -------------------------
    output$corr_interpretation <- renderUI({
      
      # Find strongest correlations
      corr_pairs <- corr_matrix %>%
        as.data.frame() %>%
        rownames_to_column("Variable_1") %>%
        pivot_longer(cols = -Variable_1, names_to = "Variable_2", values_to = "Correlation") %>%
        filter(Variable_1 < Variable_2) %>%
        arrange(desc(abs(Correlation)))
      
      strong_corrs <- corr_pairs %>%
        filter(abs(Correlation) >= 0.7) %>%
        head(3)
      
      if (nrow(strong_corrs) > 0) {
        HTML(paste0(
          "<h4>Key Findings:</h4>",
          "<ul>",
          paste0(
            "<li><strong>", strong_corrs$Variable_1, "</strong> and <strong>",
            strong_corrs$Variable_2, "</strong>: r = ",
            round(strong_corrs$Correlation, 2),
            " (", ifelse(abs(strong_corrs$Correlation) >= 0.9, "Very Strong",
                  ifelse(abs(strong_corrs$Correlation) >= 0.7, "Strong", "Moderate")),
            " ", ifelse(strong_corrs$Correlation > 0, "positive", "negative"),
            " correlation)</li>",
            collapse = ""
          ),
          "</ul>"
        ))
      } else {
        HTML("<p>No strong correlations (|r| ≥ 0.7) found.</p>")
      }
    })
  })
  
  # ============================================================================
  # REGRESSION ANALYSIS
  # ============================================================================
  
  observeEvent(input$run_regression, {
    
    req(input$reg_dependent)
    req(input$reg_independent)
    req(length(input$reg_independent) >= 1)
    
    df <- data()
    
    # Prepare data
    reg_vars <- c(input$reg_dependent, input$reg_independent)
    reg_data <- df %>%
      select(all_of(reg_vars)) %>%
      drop_na()
    
    if (nrow(reg_data) < 30) {
      output$reg_summary <- renderPrint({
        cat("Insufficient data for regression analysis.\n")
        cat("Need at least 30 complete observations.\n")
        cat("Available:", nrow(reg_data), "observations")
      })
      return()
    }
    
    # Build formula
    formula_str <- paste(input$reg_dependent, "~", 
                         paste(input$reg_independent, collapse = " + "))
    formula_obj <- as.formula(formula_str)
    
    # Fit model
    model <- lm(formula_obj, data = reg_data)
    
    # -------------------------
    # REGRESSION SUMMARY
    # -------------------------
    output$reg_summary <- renderPrint({
      cat("REGRESSION MODEL\n")
      cat("================\n\n")
      cat("Formula:", formula_str, "\n\n")
      cat("Sample size:", nrow(reg_data), "observations\n\n")
      
      summary(model)
      
      cat("\n\n")
      cat("MODEL DIAGNOSTICS\n")
      cat("=================\n\n")
      
      # Check for multicollinearity (if multiple predictors)
      if (length(input$reg_independent) > 1) {
        vif_vals <- car::vif(model)
        cat("Variance Inflation Factors (VIF):\n")
        print(round(vif_vals, 2))
        cat("\nNote: VIF > 10 indicates multicollinearity concerns\n")
      }
    })
    
    # -------------------------
    # RESIDUAL PLOTS
    # -------------------------
    output$reg_diagnostics <- renderPlot({
      
      par(mfrow = c(2, 2))
      plot(model)
      par(mfrow = c(1, 1))
      
    }, height = 600)
    
    # -------------------------
    # PREDICTIONS PLOT
    # -------------------------
    output$reg_predictions <- renderPlot({
      
      # Get predictions
      reg_data$predicted <- predict(model)
      reg_data$residuals <- residuals(model)
      
      # Actual vs Predicted
      ggplot(reg_data, aes(x = predicted, y = .data[[input$reg_dependent]])) +
        geom_point(alpha = 0.3) +
        geom_abline(slope = 1, intercept = 0, color = "red", linetype = "dashed") +
        labs(
          title = "Actual vs. Predicted Values",
          x = "Predicted",
          y = "Actual"
        )
    })
    
    # -------------------------
    # COEFFICIENT PLOT
    # -------------------------
    output$reg_coefficients <- renderPlot({
      
      # Extract coefficients
      coef_df <- broom::tidy(model, conf.int = TRUE) %>%
        filter(term != "(Intercept)")
      
      if (nrow(coef_df) == 0) return()
      
      ggplot(coef_df, aes(x = reorder(term, estimate), y = estimate)) +
        geom_point(size = 3) +
        geom_errorbar(aes(ymin = conf.low, ymax = conf.high), width = 0.2) +
        geom_hline(yintercept = 0, linetype = "dashed", color = "red") +
        coord_flip() +
        labs(
          title = "Regression Coefficients (95% CI)",
          x = "Variable",
          y = "Coefficient Estimate"
        )
    })
  })
  
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
    if (input$group_var == "Census Region") {
      df$grp <- df$census_region
    }
    
    if (input$group_var == "Census Division") {
      df$grp <- df$census_division
    }
    
    if (input$group_var == "Rural/Urban") {
      df$grp <- df$urban_rural
    }
    
    if (input$group_var == "Poverty Category") {
      df$grp <- df$poverty_category
    }
    
    if (input$group_var == "Income Category") {
      df$grp <- df$income_category
    }
    
    if (input$group_var == "FI Category") {
      df$grp <- df$fi_category
    }
    
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
        pivot_longer(
          cols = c(black, hispanic, white),
          names_to = "grp",
          values_to = "value"
        ) %>%
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
    # BOXPLOT
    # -------------------------
    output$group_comp_plot <- renderPlot({
      
      ggplot(df, aes(x = grp, y = .data[[target_var]], fill = grp)) +
        geom_boxplot(alpha = 0.7, outlier.alpha = 0.3) +
        stat_summary(fun = mean, geom = "point", shape = 23, size = 3, 
                     fill = "white", color = "black") +
        labs(
          title = paste("Group Comparison:", input$group_var),
          x = input$group_var,
          y = target_var,
          caption = "Diamond = mean, Box = median ± IQR"
        ) +
        theme(
          legend.position = "none",
          axis.text.x = element_text(angle = 45, hjust = 1)
        )
    })
    
    # -------------------------
    # STATISTICAL TEST
    # -------------------------
    output$group_stats <- renderPrint({
      
      grp_count <- n_distinct(df$grp)
      
      cat("GROUP COMPARISON ANALYSIS\n")
      cat("=========================\n\n")
      
      # Summary statistics by group
      summary_stats <- df %>%
        group_by(grp) %>%
        summarise(
          n = n(),
          mean = mean(.data[[target_var]], na.rm = TRUE),
          sd = sd(.data[[target_var]], na.rm = TRUE),
          median = median(.data[[target_var]], na.rm = TRUE),
          .groups = "drop"
        )
      
      cat("Summary Statistics:\n")
      print(summary_stats)
      cat("\n\n")
      
      # Statistical test
      if (grp_count == 2) {
        cat("TWO-GROUP COMPARISON: Independent t-test\n")
        cat("=========================================\n\n")
        
        test_result <- t.test(df[[target_var]] ~ df$grp)
        print(test_result)
        
        # Effect size (Cohen's d)
        group1 <- df %>% filter(grp == unique(df$grp)[1]) %>% pull(!!target_var)
        group2 <- df %>% filter(grp == unique(df$grp)[2]) %>% pull(!!target_var)
        
        cohens_d <- (mean(group1, na.rm = TRUE) - mean(group2, na.rm = TRUE)) / 
          sqrt((sd(group1, na.rm = TRUE)^2 + sd(group2, na.rm = TRUE)^2) / 2)
        
        cat("\n\nEffect Size (Cohen's d):", round(cohens_d, 3))
        cat("\nInterpretation:", 
            ifelse(abs(cohens_d) < 0.2, "Negligible",
            ifelse(abs(cohens_d) < 0.5, "Small",
            ifelse(abs(cohens_d) < 0.8, "Medium", "Large"))))
        
      } else {
        cat("MULTIPLE-GROUP COMPARISON: One-way ANOVA\n")
        cat("========================================\n\n")
        
        anova_result <- aov(df[[target_var]] ~ df$grp)
        print(summary(anova_result))
        
        # Post-hoc test if significant
        anova_p <- summary(anova_result)[[1]]$`Pr(>F)`[1]
        
        if (anova_p < 0.05) {
          cat("\n\nPost-hoc Tukey HSD Test (pairwise comparisons):\n")
          cat("===============================================\n\n")
          print(TukeyHSD(anova_result))
        }
      }
    })
  })
}
