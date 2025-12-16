# ==============================================================================
# SERVER MODULE: CORRELATION ANALYSIS (DEBUGGED VERSION)
# ==============================================================================
# PURPOSE: Bivariate correlation analysis with better error handling
# ==============================================================================

server_correlation_analysis <- function(input, output, session, data) {
  
  cat("\n========================================\n")
  cat("CORRELATION ANALYSIS MODULE LOADED\n")
  cat("========================================\n")
  
  # ==========================================================================
  # REACTIVE: FILTERED DATA WITH DEBUGGING
  # ==========================================================================
  
  corr_data <- reactive({
    req(data())
    
    cat("\n--- Filtering Data ---\n")
    cat("Selected year:", input$corr_year, "\n")
    
    df <- data()
    
    # Show what we have
    cat("Total rows:", nrow(df), "\n")
    cat("Available columns:", paste(names(df), collapse = ", "), "\n")
    
    # Filter by year
    filtered <- df %>%
      filter(year == input$corr_year)
    
    cat("Rows after year filter:", nrow(filtered), "\n")
    
    # Apply geography filter
    if (input$corr_geography == "State" && !is.null(input$corr_state) && input$corr_state != "all") {
      filtered <- filtered %>% filter(state == input$corr_state)
      cat("Rows after state filter:", nrow(filtered), "\n")
    }
    
    filtered
  })
  
  # ==========================================================================
  # REACTIVE: CORRELATION RESULTS WITH ERROR HANDLING
  # ==========================================================================
  
  corr_results <- eventReactive(input$run_correlation, {
    cat("\n========================================\n")
    cat("RUN CORRELATION BUTTON CLICKED\n")
    cat("========================================\n")
    
    req(corr_data(), input$corr_var_x, input$corr_var_y)
    
    df <- corr_data()
    cat("Working with", nrow(df), "rows\n")
    
    # Check if variables exist
    cat("X variable requested:", input$corr_var_x, "\n")
    cat("Y variable requested:", input$corr_var_y, "\n")
    
    if (!input$corr_var_x %in% names(df)) {
      cat("❌ ERROR: X variable not found in data!\n")
      cat("Available columns:", paste(names(df), collapse = ", "), "\n")
      return(list(error = paste("Variable not found:", input$corr_var_x)))
    }
    
    if (!input$corr_var_y %in% names(df)) {
      cat("❌ ERROR: Y variable not found in data!\n")
      return(list(error = paste("Variable not found:", input$corr_var_y)))
    }
    
    # Get variables
    x <- df[[input$corr_var_x]]
    y <- df[[input$corr_var_y]]
    
    cat("X variable: length =", length(x), "NAs =", sum(is.na(x)), "\n")
    cat("Y variable: length =", length(y), "NAs =", sum(is.na(y)), "\n")
    
    # Remove missing values
    complete_cases <- complete.cases(x, y)
    x_clean <- x[complete_cases]
    y_clean <- y[complete_cases]
    
    cat("Complete cases:", length(x_clean), "\n")
    
    # Check if we have enough data
    if (length(x_clean) < 3) {
      cat("❌ ERROR: Insufficient data (<3 observations)\n")
      return(list(
        r = NA,
        r2 = NA,
        p_value = NA,
        n = length(x_clean),
        method = input$corr_method,
        error = "Insufficient data for analysis"
      ))
    }
    
    # Calculate correlation
    cat("Calculating", input$corr_method, "correlation...\n")
    
    tryCatch({
      cor_test <- cor.test(x_clean, y_clean, method = input$corr_method)
      
      cat("✓ Correlation calculated successfully\n")
      cat("  r =", cor_test$estimate[[1]], "\n")
      cat("  p =", cor_test$p.value, "\n")
      
      list(
        r = cor_test$estimate[[1]],
        r2 = cor_test$estimate[[1]]^2,
        p_value = cor_test$p.value,
        n = length(x_clean),
        method = input$corr_method,
        x_clean = x_clean,
        y_clean = y_clean,
        error = NULL
      )
    }, error = function(e) {
      cat("❌ ERROR in correlation calculation:\n")
      cat("  ", e$message, "\n")
      list(
        r = NA,
        r2 = NA,
        p_value = NA,
        n = length(x_clean),
        method = input$corr_method,
        error = e$message
      )
    })
  })
  
  # ==========================================================================
  # OUTPUT: SCATTER PLOT WITH ERROR HANDLING
  # ==========================================================================
  
  output$correlation_scatter <- renderPlot({
    cat("\n--- Rendering Scatter Plot ---\n")
    
    req(corr_results())
    results <- corr_results()
    
    # Check for errors
    if (!is.null(results$error)) {
      cat("Error in results:", results$error, "\n")
      plot.new()
      text(0.5, 0.5, paste("Error:", results$error), cex = 1.2, col = "red")
      return()
    }
    
    if (is.na(results$r)) {
      cat("No valid correlation result\n")
      plot.new()
      text(0.5, 0.5, "Insufficient data for analysis", cex = 1.5)
      return()
    }
    
    cat("Creating plot with", results$n, "points\n")
    
    # Create data frame for plotting
    plot_df <- data.frame(
      x = results$x_clean,
      y = results$y_clean
    )
    
    # Get variable labels
    x_label <- switch(
      input$corr_var_x,
      "overall_food_insecurity_rate" = "Food Insecurity Rate (%)",
      "child_food_insecurity_rate" = "Child Food Insecurity Rate (%)",
      "poverty_rate" = "Poverty Rate (%)",
      "median_income" = "Median Income ($)",
      "unemployment_rate" = "Unemployment Rate (%)",
      "cost_per_meal" = "Cost per Meal ($)",
      input$corr_var_x
    )
    
    y_label <- switch(
      input$corr_var_y,
      "overall_food_insecurity_rate" = "Food Insecurity Rate (%)",
      "child_food_insecurity_rate" = "Child Food Insecurity Rate (%)",
      "poverty_rate" = "Poverty Rate (%)",
      "median_income" = "Median Income ($)",
      "unemployment_rate" = "Unemployment Rate (%)",
      "cost_per_meal" = "Cost per Meal ($)",
      input$corr_var_y
    )
    
    # Convert to percentages if needed
    if (grepl("rate", input$corr_var_x, ignore.case = TRUE)) {
      # Check if already in percentage (>1)
      if (max(plot_df$x, na.rm = TRUE) <= 1) {
        plot_df$x <- plot_df$x * 100
      }
    }
    if (grepl("rate", input$corr_var_y, ignore.case = TRUE)) {
      if (max(plot_df$y, na.rm = TRUE) <= 1) {
        plot_df$y <- plot_df$y * 100
      }
    }
    
    cat("Plot data prepared, creating ggplot...\n")
    
    # Create plot
    tryCatch({
      p <- ggplot(plot_df, aes(x = x, y = y)) +
        geom_point(
          alpha = 0.5,
          size = 3,
          color = "#0033A0"
        ) +
        geom_smooth(
          method = "lm",
          se = TRUE,
          color = "#E63946",
          fill = "#E63946",
          alpha = 0.2,
          linewidth = 1.5
        ) +
        labs(
          title = paste0("Correlation: ", x_label, " vs. ", y_label),
          subtitle = sprintf(
            "%s correlation: r = %.3f, p %s 0.001, n = %s",
            tools::toTitleCase(input$corr_method),
            results$r,
            ifelse(results$p_value < 0.001, "<", "="),
            format(results$n, big.mark = ",")
          ),
          x = x_label,
          y = y_label
        )
      cat("✓ Plot created successfully\n")
      print(p)
    }, error = function(e) {
      cat("❌ ERROR creating plot:\n")
      cat("  ", e$message, "\n")
      plot.new()
      text(0.5, 0.5, paste("Error creating plot:", e$message), cex = 1, col = "red")
    })
  }, res = 96)
  
  # ==========================================================================
  # OUTPUT: STATISTICS CARDS
  # ==========================================================================
  
  output$bivariate_r <- renderText({
    req(corr_results())
    results <- corr_results()
    
    if (!is.null(results$error) || is.na(results$r)) {
      return("--")
    }
    
    sprintf("%.3f", results$r)
  })
  
  output$bivariate_r2 <- renderText({
    req(corr_results())
    results <- corr_results()
    
    if (!is.null(results$error) || is.na(results$r2)) {
      return("--")
    }
    
    sprintf("%.1f%%", results$r2 * 100)
  })
  
  output$bivariate_p <- renderText({
    req(corr_results())
    results <- corr_results()
    
    if (!is.null(results$error) || is.na(results$p_value)) {
      return("--")
    }
    
    if (results$p_value < 0.001) {
      return("< 0.001")
    } else {
      return(sprintf("%.3f", results$p_value))
    }
  })
  
  output$sample_size <- renderText({
    req(corr_results())
    results <- corr_results()
    
    format(results$n, big.mark = ",")
  })
  
  # ==========================================================================
  # OUTPUT: INTERPRETATION CARDS
  # ==========================================================================
  
  output$correlation_strength <- renderUI({
    req(corr_results())
    results <- corr_results()
    
    if (!is.null(results$error) || is.na(results$r)) {
      return(HTML("<p style='color: #6c757d;'>Run analysis to see interpretation</p>"))
    }
    
    r_abs <- abs(results$r)
    
    strength <- if (r_abs >= 0.8) {
      list(label = "Very Strong", color = "#28a745")
    } else if (r_abs >= 0.6) {
      list(label = "Strong", color = "#0033A0")
    } else if (r_abs >= 0.4) {
      list(label = "Moderate", color = "#ffc107")
    } else if (r_abs >= 0.2) {
      list(label = "Weak", color = "#fd7e14")
    } else {
      list(label = "Very Weak", color = "#dc3545")
    }
    
    direction <- if (results$r > 0) "positive" else "negative"
    
    HTML(paste0(
      "<p style='margin: 0; font-size: 16px;'>",
      "<strong style='color: ", strength$color, ";'>", strength$label, "</strong> ",
      direction, " correlation",
      "</p>",
      "<p style='margin-top: 10px; color: #6c757d; font-size: 14px;'>",
      "As one variable increases, the other tends to ",
      ifelse(results$r > 0, "increase", "decrease"), ".",
      "</p>"
    ))
  })
  
  output$variance_explained <- renderUI({
    req(corr_results())
    results <- corr_results()
    
    if (!is.null(results$error) || is.na(results$r2)) {
      return(HTML("<p style='color: #6c757d;'>Run analysis to see interpretation</p>"))
    }
    
    pct <- results$r2 * 100
    
    HTML(paste0(
      "<p style='margin: 0; font-size: 16px;'>",
      "<strong style='color: #28a745;'>", sprintf("%.1f%%", pct), "</strong> ",
      "of variance explained",
      "</p>",
      "<p style='margin-top: 10px; color: #6c757d; font-size: 14px;'>",
      "The X variable explains ", sprintf("%.1f%%", pct), " of the variation in the Y variable.",
      "</p>"
    ))
  })
  
  output$significance_label <- renderUI({
    req(corr_results())
    results <- corr_results()
    
    if (!is.null(results$error) || is.na(results$p_value)) {
      return(HTML("<p style='color: #6c757d;'>Run analysis to see interpretation</p>"))
    }
    
    if (results$p_value < 0.001) {
      sig_label <- "Highly Significant"
      sig_color <- "#28a745"
      sig_text <- "p < 0.001 - Extremely strong evidence"
    } else if (results$p_value < 0.01) {
      sig_label <- "Very Significant"
      sig_color <- "#0033A0"
      sig_text <- "p < 0.01 - Very strong evidence"
    } else if (results$p_value < 0.05) {
      sig_label <- "Significant"
      sig_color <- "#ffc107"
      sig_text <- "p < 0.05 - Statistically significant"
    } else {
      sig_label <- "Not Significant"
      sig_color <- "#dc3545"
      sig_text <- "p ≥ 0.05 - Could be random chance"
    }
    
    HTML(paste0(
      "<p style='margin: 0; font-size: 16px;'>",
      "<strong style='color: ", sig_color, ";'>", sig_label, "</strong>",
      "</p>",
      "<p style='margin-top: 10px; color: #6c757d; font-size: 14px;'>",
      sig_text,
      "</p>"
    ))
  })
  
  # ==========================================================================
  # OUTPUT: CORRELATION MATRIX HEATMAP
  # ==========================================================================
  
  output$correlation_matrix <- renderPlot({
    cat("\n--- Rendering Correlation Matrix ---\n")
    
    req(corr_data())
    
    tryCatch({
      # Select numeric variables for correlation matrix
      df <- corr_data()
      
      # Try to find the columns (with common alternatives)
      col_map <- list(
        "overall_food_insecurity_rate" = c("overall_food_insecurity_rate", "food_insecurity_rate", "fi_rate"),
        "child_food_insecurity_rate" = c("child_food_insecurity_rate", "child_fi_rate"),
        "poverty_rate" = c("poverty_rate", "poverty"),
        "median_income" = c("median_income", "income"),
        "unemployment_rate" = c("unemployment_rate", "unemployment"),
        "cost_per_meal" = c("cost_per_meal", "cost_meal")
      )
      
      selected_cols <- c()
      for (target_col in names(col_map)) {
        for (alt_col in col_map[[target_col]]) {
          if (alt_col %in% names(df)) {
            selected_cols <- c(selected_cols, alt_col)
            break
          }
        }
      }
      
      cat("Found columns for matrix:", paste(selected_cols, collapse = ", "), "\n")
      
      if (length(selected_cols) < 2) {
        plot.new()
        text(0.5, 0.5, "Not enough variables found for correlation matrix", cex = 1.2)
        return()
      }
      
      matrix_vars <- df %>%
        select(all_of(selected_cols)) %>%
        na.omit()
      
      cat("Matrix data:", nrow(matrix_vars), "rows,", ncol(matrix_vars), "cols\n")
      
      # Calculate correlation matrix
      cor_matrix <- cor(matrix_vars, method = input$corr_method)
      
      # Convert to long format
      cor_long <- as.data.frame(cor_matrix) %>%
        tibble::rownames_to_column("Var1") %>%
        pivot_longer(-Var1, names_to = "Var2", values_to = "Correlation")
      
      # Create heatmap
      ggplot(cor_long, aes(x = Var1, y = Var2, fill = Correlation)) +
        geom_tile(color = "white", size = 1) +
        geom_text(
          aes(label = sprintf("%.2f", Correlation)),
          color = "white",
          fontface = "bold",
          size = 5
        ) +
        scale_fill_gradient2(
          low = "#dc3545",
          mid = "white",
          high = "#0033A0",
          midpoint = 0,
          limits = c(-1, 1),
          name = "Correlation"
        ) +
        labs(
          title = paste0("Correlation Matrix (", input$corr_year, ")"),
          subtitle = paste0(tools::toTitleCase(input$corr_method), " correlation coefficients"),
          x = NULL,
          y = NULL
        )
    }, error = function(e) {
      cat("❌ ERROR creating matrix:\n")
      cat("  ", e$message, "\n")
      plot.new()
      text(0.5, 0.5, paste("Error creating matrix:", e$message), cex = 1, col = "red")
    })
  }, res = 96)
  
  # ==========================================================================
  # AI INTERPRETATION (Placeholder for now)
  # ==========================================================================
  
  correlation_ai_text <- reactiveVal(NULL)
  
  output$correlation_ai_interpretation <- renderUI({
    if (is.null(correlation_ai_text())) {
      HTML(paste0(
        "<div style='text-align: center; padding: 40px; color: white; opacity: 0.9;'>",
        "<p style='font-size: 16px; margin: 0;'>",
        "Click <strong>'Generate AI Interpretation'</strong> to get insights.",
        "</p>",
        "</div>"
      ))
    } else {
      HTML(correlation_ai_text())
    }
  })
  
  observeEvent(input$generate_correlation_interpretation, {
    correlation_ai_text(paste0(
      "<div style='text-align: center; padding: 20px;'>",
      "<p style='color: white;'>AI interpretation feature coming soon!</p>",
      "</div>"
    ))
  })
  
  cat("✓ Correlation Analysis module initialized\n")
}