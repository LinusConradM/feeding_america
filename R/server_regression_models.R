# ==============================================================================
# SERVER MODULE: REGRESSION MODELS (CARD-BASED UI COMPATIBLE)
# ==============================================================================
# FEATURES:
# - Works with card-based model selection
# - Dynamic variable population (27+ predictors)
# - Variable scaling option
# - Multicollinearity diagnostics (Condition Index, VIF)
# - Proper NA handling before model building
# - Full AI interpretation integration
# - Placeholder handlers for all 17 model types
# ==============================================================================

server_regression_models <- function(input, output, session, data) {
  
  cat("\n========================================\n")
  cat("REGRESSION MODELS MODULE LOADED\n")
  cat("========================================\n")
  
  # ==========================================================================
  # OUTPUT: CURRENT MODEL TYPE DISPLAY
  # ==========================================================================
  
  output$current_model_display <- renderUI({
    req(input$reg_model_type)
    
    model_name <- switch(
      input$reg_model_type,
      "linear" = "Linear Regression",
      "poly2" = "Polynomial Regression (Degree 2)",
      "poly3" = "Polynomial Regression (Degree 3)",
      "ridge" = "Ridge Regression (L2 Regularization)",
      "lasso" = "LASSO Regression (L1 Regularization)",
      "elasticnet" = "Elastic Net (L1 + L2 Regularization)",
      "fixed_effects" = "Fixed Effects Panel Model",
      "quantile_50" = "Quantile Regression (50th Percentile)",
      "quantile_75" = "Quantile Regression (75th Percentile)",
      "random_forest_reg" = "Random Forest Regression",
      "xgboost_reg" = "XGBoost Regression",
      "gam" = "Generalized Additive Model (GAM)",
      "interaction" = "Interaction Effects Model",
      "logistic_binary" = "Logistic Regression (Binary Classification)",
      "logistic_multi" = "Multinomial Logistic Regression",
      "random_forest_class" = "Random Forest Classification",
      "xgboost_class" = "XGBoost Classification",
      "lda" = "Linear Discriminant Analysis",
      "Unknown Model"
    )
    
    model_color <- switch(
      input$reg_model_type,
      "linear" = "#0033A0",
      "poly2" = "#28a745",
      "poly3" = "#ffc107",
      "ridge" = "#6f42c1",
      "lasso" = "#dc3545",
      "elasticnet" = "#fd7e14",
      "#17a2b8"  # default
    )
    
    div(
      style = paste0("background: ", model_color, "; color: white; padding: 15px; ",
                    "border-radius: 8px; margin-bottom: 15px; text-align: center;"),
      h5(icon("check-circle"), " Currently Selected Model:", style = "margin: 0 0 5px 0; font-weight: 400; opacity: 0.9;"),
      h4(model_name, style = "margin: 0; font-weight: 600;")
    )
  })
  
  # ==========================================================================
  # POPULATE INDEPENDENT VARIABLE CHOICES
  # ==========================================================================
  
  observe({
    req(data())
    
    # Get ALL variables that could be numeric predictors
    all_vars <- names(data())
    
    # Exclude only: IDs, geographic codes, categorical variables, and dependent variables
    exclude_vars <- c(
      # IDs and codes
      "state", "county_state", "state_id", "county_id", "fips", "fa_state", "county",
      "year",  # Time variable
      "lat", "lon",  # Geographic coordinates
      
      # Dependent variables (outcome options)
      "overall_food_insecurity_rate",
      "child_food_insecurity_rate",
      
      # Categorical variables (factors)
      "census_region", "census_division", "fns_region", "year_group",
      "low_threshold_type", "high_threshold_type",
      "urban_rural", "fi_category", "poverty_category", 
      "income_category", "education_category"
    )
    
    # Get potential predictors
    potential_vars <- setdiff(all_vars, exclude_vars)
    
    # Filter to only numeric variables
    numeric_vars <- potential_vars[sapply(potential_vars, function(var) {
      is.numeric(data()[[var]])
    })]
    
    # Sort alphabetically
    numeric_vars <- sort(numeric_vars)
    
    cat("Found", length(numeric_vars), "numeric predictor variables\n")
    
    # Create nice labels with enhanced formatting
    var_labels <- sapply(numeric_vars, function(var) {
      label <- switch(
        var,
        # Main socioeconomic indicators
        "poverty_rate" = "Poverty Rate (%)",
        "median_income" = "Median Income ($)",
        "unemployment_rate" = "Unemployment Rate (%)",
        "snap_rate" = "SNAP Rate (%)",
        "rent_burden" = "Rent Burden (%)",
        
        # Demographic composition
        "female_headed" = "Female Headed Household (%)",
        "no_vehicle" = "No Vehicle (%)",
        "hs_or_less" = "High School or Less (%)",
        "black_pct" = "Black Population (%)",
        "hispanic_pct" = "Hispanic Population (%)",
        
        # Economic measures
        "gini" = "Gini Coefficient",
        "population" = "Population",
        "cost_per_meal" = "Cost per Meal ($)",
        "weighted_annual_food_budget_shortfall" = "Annual Food Budget Shortfall ($)",
        "weighted_weekly_needed_by_fi" = "Weekly Food Budget Needed ($)",
        
        # Food insecurity counts
        "no_of_food_insecure_persons_overall" = "Number of Food Insecure Persons",
        "no_of_food_insecure_children" = "Number of Food Insecure Children",
        
        # Thresholds
        "low_threshold_in_state" = "Low Threshold in State",
        "high_threshold_in_state" = "High Threshold in State",
        "snap_threshold" = "SNAP Threshold",
        
        # SNAP-related percentages
        "percent_fi_snap_threshold" = "% Food Insecure at SNAP Threshold",
        "percent_fi_snap_threshold_2" = "% Food Insecure at SNAP Threshold 2",
        
        # Child food insecurity by income
        "percent_food_insecure_children_in_hh_w_hh_incomes_below_185_fpl" = 
          "% Food Insecure Children (HH Income < 185% FPL)",
        "percent_food_insecure_children_in_hh_w_hh_incomes_above_185_fpl" = 
          "% Food Insecure Children (HH Income > 185% FPL)",
        
        # Racial/ethnic food insecurity rates
        "food_insecurity_rate_among_black_persons_all_ethnicities" = 
          "Food Insecurity Rate - Black Persons",
        "food_insecurity_rate_among_hispanic_persons_any_race" = 
          "Food Insecurity Rate - Hispanic Persons",
        "food_insecurity_rate_among_white_non_hispanic_persons" = 
          "Food Insecurity Rate - White Non-Hispanic",
        
        # Default: auto-format
        tools::toTitleCase(gsub("_", " ", var))
      )
      label
    })
    
    # Update dropdown choices
    updateSelectInput(
      session,
      "reg_independent",
      choices = setNames(numeric_vars, var_labels),
      selected = c("poverty_rate", "median_income")  # Default selections
    )
    
    cat("Dropdown options updated with", length(numeric_vars), "variables\n")
  })
  
  # ==========================================================================
  # MONITOR SELECTED MODEL TYPE (for debugging)
  # ==========================================================================
  
  observe({
    req(input$reg_model_type)
    cat("Model type selected:", input$reg_model_type, "\n")
  })
  
  # ==========================================================================
  # REACTIVE: FILTERED DATA
  # ==========================================================================
  
  reg_data <- reactive({
    req(data())
    req(input$reg_year)
    
    data() %>%
      filter(year == input$reg_year)
  })
  
  # ==========================================================================
  # REACTIVE: BUILD MODEL
  # ==========================================================================
  
  model_results <- eventReactive(input$build_model, {
    cat("\n========================================\n")
    cat("BUILD MODEL BUTTON CLICKED\n")
    cat("========================================\n")
    
    cat("Step 1: Checking inputs...\n")
    cat("  reg_data() exists:", !is.null(reg_data()), "\n")
    cat("  input$reg_dependent:", input$reg_dependent, "\n")
    cat("  input$reg_model_type:", input$reg_model_type, "\n")
    cat("  input$reg_scale:", input$reg_scale, "\n")
    cat("  input$reg_independent:", paste(input$reg_independent, collapse=", "), "\n")
    
    # CRITICAL: Check all inputs exist FIRST
    # Don't check reg_scale or reg_independent - they can be FALSE or empty!
    req(reg_data(), input$reg_dependent, input$reg_model_type)
    
    cat("Step 2: Passed req() checks\n")
    
    df <- reg_data()
    
    cat("Step 3: Got data, rows:", nrow(df), "\n")
    
    # Check we have independent variables selected (with helpful error message)
    if (is.null(input$reg_independent) || length(input$reg_independent) == 0) {
      cat("❌ ERROR: No independent variables selected\n")
      return(list(error = "Please select at least one independent variable from the dropdown above"))
    }
    
    cat("Step 4: Independent variables selected:", length(input$reg_independent), "\n")
    
    cat("Dependent variable:", input$reg_dependent, "\n")
    cat("Independent variables:", paste(input$reg_independent, collapse = ", "), "\n")
    cat("Model type:", input$reg_model_type, "\n")
    cat("Scaling:", input$reg_scale, "\n")
    cat("Working with", nrow(df), "rows\n")
    
    # Select only needed columns
    model_vars <- c(input$reg_dependent, input$reg_independent)
    df <- df %>%
      select(all_of(model_vars))
    
    cat("Working with", nrow(df), "rows and", ncol(df), "variables\n")
    
    # Check for missing data BEFORE dropping
    missing_counts <- sapply(df, function(x) sum(is.na(x)))
    vars_with_missing <- missing_counts[missing_counts > 0]
    
    if (length(vars_with_missing) > 0) {
      cat("\n⚠️  MISSING DATA DETECTED:\n")
      for (var in names(vars_with_missing)) {
        pct_missing <- round(100 * vars_with_missing[var] / nrow(df), 1)
        cat("  ", var, ":", vars_with_missing[var], "missing (", pct_missing, "%)\n", sep="")
      }
      cat("\n")
    }
    
    # Now remove rows with ANY missing values
    df_complete <- df %>% drop_na()
    
    cat("After removing rows with missing values:", nrow(df_complete), "complete observations\n")
    
    # Check if we have enough data
    if (nrow(df_complete) < 10) {
      error_msg <- paste0(
        "Insufficient complete data! Started with ", nrow(df), " rows, ",
        "but only ", nrow(df_complete), " have complete data across all ", length(model_vars), " variables.\n\n",
        "SUGGESTIONS:\n",
        "1. Select fewer independent variables (you have ", length(input$reg_independent), " selected)\n",
        "2. Remove variables with high missing data:\n"
      )
      
      # List top problematic variables
      if (length(vars_with_missing) > 0) {
        top_missing <- sort(vars_with_missing, decreasing = TRUE)[1:min(5, length(vars_with_missing))]
        for (var in names(top_missing)) {
          pct <- round(100 * top_missing[var] / nrow(df), 1)
          error_msg <- paste0(error_msg, "   • ", var, " (", pct, "% missing)\n")
        }
      }
      
      cat("❌ ERROR:", error_msg, "\n")
      return(list(error = error_msg))
    }
    
    # Use complete data for modeling
    df <- df_complete
    
    cat("✅ Proceeding with", nrow(df), "complete observations\n")
    
    # Scale variables if requested
    if (input$reg_scale) {
      cat("Scaling all variables to z-scores\n")
      df <- df %>%
        mutate(across(everything(), ~as.numeric(scale(.))))
    }
    
    # ==========================================================================
    # MODEL TYPE SELECTION
    # ==========================================================================
    
    # Prepare formula based on model type
    model_type <- input$reg_model_type
    
    if (model_type == "linear") {
      # ===== LINEAR REGRESSION =====
      cat("Building: Linear Regression\n")
      formula_str <- paste(input$reg_dependent, "~", paste(input$reg_independent, collapse = " + "))
      
    } else if (model_type == "poly2") {
      # ===== POLYNOMIAL DEGREE 2 =====
      cat("Building: Polynomial Regression (degree 2)\n")
      formula_str <- paste(input$reg_dependent, "~", 
                          paste0("poly(", input$reg_independent, ", 2)", collapse = " + "))
      
    } else if (model_type == "poly3") {
      # ===== POLYNOMIAL DEGREE 3 =====
      cat("Building: Polynomial Regression (degree 3)\n")
      formula_str <- paste(input$reg_dependent, "~", 
                          paste0("poly(", input$reg_independent, ", 3)", collapse = " + "))
      
    } else if (model_type == "ridge") {
      # ===== RIDGE REGRESSION (L2 REGULARIZATION) =====
      cat("Building: Ridge Regression (L2 Regularization)\n")
      
      # Prepare data for glmnet
      X <- as.matrix(df[, input$reg_independent, drop = FALSE])
      y <- df[[input$reg_dependent]]
      
      cat("  Using glmnet with alpha = 0 (Ridge)\n")
      cat("  Running 10-fold cross-validation to find optimal lambda\n")
      
      # Cross-validation to find optimal lambda
      set.seed(123)  # For reproducibility
      cv_model <- glmnet::cv.glmnet(
        x = X,
        y = y,
        alpha = 0,  # Ridge regression (alpha=0)
        nfolds = 10,
        standardize = !input$reg_scale  # Don't re-standardize if already scaled
      )
      
      # Get optimal lambdas
      lambda_min <- cv_model$lambda.min
      lambda_1se <- cv_model$lambda.1se
      
      cat("  Optimal lambda (min CV error):", sprintf("%.6f", lambda_min), "\n")
      cat("  Lambda 1-SE (within 1 SE):", sprintf("%.6f", lambda_1se), "\n")
      
      # Fit final model with optimal lambda (lambda.min)
      model <- glmnet::glmnet(
        x = X,
        y = y,
        alpha = 0,
        lambda = lambda_min,
        standardize = !input$reg_scale
      )
      
      # Also fit model with full lambda sequence for plotting
      model_full <- glmnet::glmnet(
        x = X,
        y = y,
        alpha = 0,
        standardize = !input$reg_scale
      )
      
      # Make predictions with lambda.min
      y_pred <- predict(model, newx = X, s = lambda_min)[,1]
      
      # Calculate metrics
      residuals_vec <- y - y_pred
      train_rmse <- sqrt(mean(residuals_vec^2))
      train_mae <- mean(abs(residuals_vec))
      
      if (all(y != 0)) {
        mape <- mean(abs(residuals_vec / y)) * 100
      } else {
        mape <- NA
      }
      
      # Training R-squared
      ss_res <- sum(residuals_vec^2)
      ss_tot <- sum((y - mean(y))^2)
      r_squared <- 1 - (ss_res / ss_tot)
      
      # Cross-validated metrics
      cv_rmse <- sqrt(min(cv_model$cvm))  # Min cross-validated MSE
      cv_r_squared <- 1 - (min(cv_model$cvm) / var(y))
      
      # Deviance Ratio (proportion of null deviance explained)
      # For Ridge, this is essentially the same as R²
      null_deviance <- sum((y - mean(y))^2)
      model_deviance <- ss_res
      deviance_ratio <- 1 - (model_deviance / null_deviance)
      
      # Get coefficients (excluding intercept for L2 norm)
      coefs <- as.numeric(coef(model, s = lambda_min))
      coef_names <- rownames(coef(model, s = lambda_min))
      
      # Calculate L2 Norm (sqrt of sum of squared coefficients, excluding intercept)
      l2_norm <- sqrt(sum(coefs[-1]^2))
      
      # Count non-zero coefficients (excluding intercept)
      # For Ridge, this is always all of them (they shrink but don't become 0)
      nonzero_count <- sum(abs(coefs[-1]) > 1e-10)  # Use small threshold for numerical precision
      
      # Prepare data frame with predictions
      df <- df %>%
        mutate(
          fitted = y_pred,
          residuals = residuals_vec
        )
      
      cat("✓ Ridge model built successfully\n")
      cat("  Training R²:", round(r_squared, 4), "\n")
      cat("  CV R²:", round(cv_r_squared, 4), "\n")
      cat("  Deviance Ratio:", round(deviance_ratio, 4), "\n")
      cat("  Optimal lambda:", sprintf("%.6f", lambda_min), "\n")
      cat("  Lambda 1-SE:", sprintf("%.6f", lambda_1se), "\n")
      cat("  L2 Norm:", round(l2_norm, 4), "\n")
      cat("  Non-zero coefficients:", nonzero_count, "of", length(coefs)-1, "\n")
      cat("  Training RMSE:", round(train_rmse, 4), "\n")
      cat("  CV RMSE:", round(cv_rmse, 4), "\n")
      cat("  Training MAE:", round(train_mae, 4), "\n")
      
      # Create summary object compatible with downstream code
      ridge_summary <- list(
        coefficients = cbind(
          Estimate = coefs,
          `Std. Error` = rep(NA, length(coefs)),
          `t value` = rep(NA, length(coefs)),
          `Pr(>|t|)` = rep(NA, length(coefs))
        ),
        r.squared = r_squared,
        adj.r.squared = NA,  # Not applicable for Ridge
        fstatistic = c(NA, NA, NA)
      )
      rownames(ridge_summary$coefficients) <- coef_names
      
      cat("\n✅ RIDGE MODEL BUILD COMPLETE\n")
      cat("Returning results with:\n")
      cat("  - Model type: Ridge Regression\n")
      cat("  - Training R²:", round(r_squared, 4), "\n")
      cat("  - CV R²:", round(cv_r_squared, 4), "\n")
      cat("  - Deviance Ratio:", round(deviance_ratio, 4), "\n")
      cat("  - Lambda (min):", sprintf("%.6f", lambda_min), "\n")
      cat("  - Lambda (1-SE):", sprintf("%.6f", lambda_1se), "\n")
      cat("  - L2 Norm:", round(l2_norm, 4), "\n")
      cat("  - RMSE:", round(train_rmse, 4), "\n")
      cat("========================================\n\n")
      
      return(list(
        model = model,
        model_full = model_full,  # Full lambda sequence for plotting
        cv_model = cv_model,
        summary = ridge_summary,
        data = df,
        formula = paste(input$reg_dependent, "~", paste(input$reg_independent, collapse = " + "), "(Ridge, L2)"),
        model_type = "ridge",
        lambda_min = lambda_min,
        lambda_1se = lambda_1se,
        l2_norm = l2_norm,
        r_squared = r_squared,
        cv_r_squared = cv_r_squared,
        deviance_ratio = deviance_ratio,
        nonzero_coefs = nonzero_count,
        total_coefs = length(coefs) - 1,
        train_rmse = train_rmse,
        train_mae = train_mae,
        rmse = train_rmse,  # For compatibility
        mae = train_mae,    # For compatibility
        mape = mape,
        cv_rmse = cv_rmse,
        cv_mae = NA,  # Could calculate if needed
        cv_folds = 10,
        condition_index = NA,  # Not applicable for regularized models
        max_vif = NA,
        error = NULL
      ))
      
    } else if (model_type == "lasso") {
      # ===== LASSO REGRESSION (PLACEHOLDER) =====
      return(list(error = "LASSO Regression is not yet implemented. Coming soon! For now, please use Linear, Polynomial (2), or Polynomial (3)."))
      
    } else if (model_type == "elasticnet") {
      # ===== ELASTIC NET (PLACEHOLDER) =====
      return(list(error = "Elastic Net is not yet implemented. Coming soon! For now, please use Linear, Polynomial (2), or Polynomial (3)."))
      
    } else if (model_type == "fixed_effects") {
      # ===== FIXED EFFECTS PANEL (PLACEHOLDER) =====
      return(list(error = "Fixed Effects Panel model is not yet implemented. Coming soon! For now, please use Linear, Polynomial (2), or Polynomial (3)."))
      
    } else if (model_type %in% c("quantile_50", "quantile_75")) {
      # ===== QUANTILE REGRESSION (PLACEHOLDER) =====
      return(list(error = "Quantile Regression is not yet implemented. Coming soon! For now, please use Linear, Polynomial (2), or Polynomial (3)."))
      
    } else if (model_type %in% c("random_forest_reg", "xgboost_reg")) {
      # ===== ENSEMBLE METHODS (PLACEHOLDER) =====
      return(list(error = paste(toupper(gsub("_", " ", model_type)), "is not yet implemented. Coming soon! For now, please use Linear, Polynomial (2), or Polynomial (3).")))
      
    } else if (model_type == "gam") {
      # ===== GAM (PLACEHOLDER) =====
      return(list(error = "GAM (Generalized Additive Models) is not yet implemented. Coming soon! For now, please use Linear, Polynomial (2), or Polynomial (3)."))
      
    } else if (model_type == "interaction") {
      # ===== INTERACTION MODELS (PLACEHOLDER) =====
      return(list(error = "Interaction Models are not yet implemented. Coming soon! For now, please use Linear, Polynomial (2), or Polynomial (3)."))
      
    } else if (model_type %in% c("logistic_binary", "logistic_multi", "random_forest_class", "xgboost_class", "lda")) {
      # ===== CLASSIFICATION MODELS (PLACEHOLDER) =====
      return(list(error = "Classification models are not yet implemented. Coming soon! For now, please use Linear, Polynomial (2), or Polynomial (3)."))
      
    } else {
      # ===== UNKNOWN MODEL TYPE =====
      return(list(error = paste("Unknown model type:", model_type, ". Please select Linear, Polynomial (2), or Polynomial (3).")))
    }
    
    cat("Formula:", formula_str, "\n")
    
    # ==========================================================================
    # BUILD MODEL
    # ==========================================================================
    
    tryCatch({
      model <- lm(as.formula(formula_str), data = df)
      
      cat("✓ Model built successfully\n")
      cat("  R² =", summary(model)$r.squared, "\n")
      cat("  Adj. R² =", summary(model)$adj.r.squared, "\n")
      
      # Calculate multicollinearity diagnostics
      # Condition Index
      X <- model.matrix(model)[, -1, drop = FALSE]  # Design matrix without intercept
      
      if (ncol(X) > 0) {
        eigenvalues <- eigen(t(X) %*% X)$values
        condition_index <- sqrt(max(eigenvalues) / min(eigenvalues))
      } else {
        condition_index <- NA
      }
      
      # VIF (Variance Inflation Factor)
      if (ncol(X) > 1 && length(input$reg_independent) > 1) {
        tryCatch({
          vif_values <- car::vif(model)
          max_vif <- if (is.matrix(vif_values)) max(vif_values[, "GVIF"]) else max(vif_values)
        }, error = function(e) {
          cat("  Warning: Could not calculate VIF:", e$message, "\n")
          max_vif <<- NA
        })
      } else {
        max_vif <- NA  # VIF not applicable with single predictor
      }
      
      cat("  Condition Index =", round(condition_index, 2), "\n")
      if (!is.na(max_vif)) {
        cat("  Max VIF =", round(max_vif, 2), "\n")
      }
      
      # Now fitted values will match df exactly
      df <- df %>%
        mutate(
          fitted = fitted(model),
          residuals = residuals(model)
        )
      
      # Calculate additional error metrics
      rmse <- sqrt(mean((df$residuals)^2))
      mae <- mean(abs(df$residuals))
      
      # MAPE (Mean Absolute Percentage Error) - only if no zeros in actual values
      actual_vals <- df[[input$reg_dependent]]
      if (all(actual_vals != 0)) {
        mape <- mean(abs(df$residuals / actual_vals)) * 100
      } else {
        mape <- NA
      }
      
      cat("\n✅ MODEL BUILD COMPLETE\n")
      cat("Returning results with:\n")
      cat("  - Model object: ", class(model)[1], "\n")
      cat("  - R²: ", round(summary(model)$r.squared, 4), "\n")
      cat("  - RMSE: ", round(rmse, 4), "\n")
      cat("  - MAE: ", round(mae, 4), "\n")
      if (!is.na(mape)) cat("  - MAPE: ", round(mape, 2), "%\n")
      cat("  - Data rows: ", nrow(df), "\n")
      cat("  - Error: NULL\n")
      cat("========================================\n\n")
      
      list(
        model = model,
        summary = summary(model),
        data = df,
        formula = formula_str,
        model_type = model_type,
        condition_index = condition_index,
        max_vif = max_vif,
        rmse = rmse,
        mae = mae,
        mape = mape,
        error = NULL
      )
      
    }, error = function(e) {
      cat("❌ ERROR building model:\n")
      cat("  ", e$message, "\n")
      cat("  Formula:", formula_str, "\n")
      cat("  Data rows:", nrow(df), "\n")
      cat("  Scaling:", input$reg_scale, "\n")
      list(error = paste("Model building failed:", e$message))
    })
  })
  
  # Log when outputs are being rendered
  observe({
    req(model_results())
    cat("\n✓ Model results available - outputs should render now\n")
    if (!is.null(model_results()$error)) {
      cat("  But there's an error:", model_results()$error, "\n")
    }
  })
  
  # ==========================================================================
  # OUTPUT: MODEL EQUATION
  # ==========================================================================
  
  output$model_equation <- renderUI({
    cat(">>> model_equation output called\n")
    req(model_results())
    cat(">>> model_results() exists\n")
    results <- model_results()
    cat(">>> Got results, checking for error\n")
    
    if (!is.null(results$error)) {
      cat(">>> Error found:", results$error, "\n")
      return(HTML(paste0(
        "<div style='padding: 20px; background: #fff3cd; border-left: 4px solid #ffc107; ",
        "border-radius: 4px;'>",
        "<strong>⚠️ ", results$error, "</strong>",
        "</div>"
      )))
    }
    
    cat(">>> No error, formatting equation\n")
    
    # Get coefficients based on model type
    if (results$model_type %in% c("ridge", "lasso", "elasticnet")) {
      # For regularized models, get coefficients from summary
      coefs <- results$summary$coefficients[, "Estimate"]
    } else {
      # For regular regression models
      coefs <- coef(results$model)
    }
    
    # Dependent variable label
    dep_label <- switch(
      input$reg_dependent,
      "overall_food_insecurity_rate" = "Food Insecurity Rate",
      "child_food_insecurity_rate" = "Child Food Insecurity Rate",
      input$reg_dependent
    )
    
    # Add scaling note if applicable
    if (input$reg_scale) {
      dep_label <- paste0(dep_label, " (standardized)")
    }
    
    # Build equation string
    eq_parts <- paste0(
      "<strong>", dep_label, "</strong> = ",
      sprintf("%.4f", coefs[1])
    )
    
    for (i in 2:length(coefs)) {
      coef_val <- coefs[i]
      sign <- ifelse(coef_val >= 0, " + ", " − ")
      eq_parts <- paste0(eq_parts, sign, sprintf("%.4f", abs(coef_val)), " × ", names(coefs)[i])
    }
    
    # Add model type badge
    model_badge <- switch(
      results$model_type,
      "linear" = "<span style='background: #0033A0; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px; margin-left: 10px;'>LINEAR</span>",
      "poly2" = "<span style='background: #28a745; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px; margin-left: 10px;'>POLYNOMIAL (2)</span>",
      "poly3" = "<span style='background: #ffc107; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px; margin-left: 10px;'>POLYNOMIAL (3)</span>",
      "ridge" = "<span style='background: #6f42c1; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px; margin-left: 10px;'>RIDGE (L2)</span>",
      "lasso" = "<span style='background: #dc3545; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px; margin-left: 10px;'>LASSO (L1)</span>",
      "elasticnet" = "<span style='background: #fd7e14; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px; margin-left: 10px;'>ELASTIC NET</span>",
      ""
    )
    
    HTML(paste0(
      "<div style='background: #f8f9fa; padding: 15px; border-radius: 8px; ",
      "font-family: monospace; font-size: 14px;'>",
      eq_parts, model_badge,
      "</div>"
    ))
  })
  
  # ==========================================================================
  # OUTPUT: FITTED VS ACTUAL PLOT
  # ==========================================================================
  
  output$fitted_vs_actual <- renderPlot({
    req(model_results())
    results <- model_results()
    
    if (!is.null(results$error)) {
      plot.new()
      text(0.5, 0.5, "Select a model and click 'Build Model'", cex = 1.2, col = "#6c757d")
      return()
    }
    
    df <- results$data
    
    # Get variable label
    y_label <- switch(
      input$reg_dependent,
      "overall_food_insecurity_rate" = "Food Insecurity Rate (%)",
      "child_food_insecurity_rate" = "Child Food Insecurity Rate (%)",
      input$reg_dependent
    )
    
    # Convert to percentage if needed (only if NOT scaled)
    if (!input$reg_scale && grepl("rate", input$reg_dependent, ignore.case = TRUE)) {
      if (max(df[[input$reg_dependent]], na.rm = TRUE) <= 1) {
        df[[input$reg_dependent]] <- df[[input$reg_dependent]] * 100
        df$fitted <- df$fitted * 100
      }
    }
    
    # Add scaling note
    if (input$reg_scale) {
      y_label <- paste0(y_label, " (z-score)")
    }
    
    # Create plot
    ggplot(df, aes(x = .data[[input$reg_dependent]], y = fitted)) +
      geom_point(alpha = 0.5, size = 2.5, color = "#0033A0") +
      geom_abline(intercept = 0, slope = 1, color = "#E63946", 
                  linetype = "dashed", linewidth = 1.2) +
      labs(
        title = "Model Predictions vs. Actual Values",
        subtitle = sprintf("R² = %.3f | Perfect prediction shown as red dashed line",
                          results$summary$r.squared),
        x = paste("Actual", y_label),
        y = paste("Predicted", y_label)
      ) +
      theme_minimal()
      # Global theme automatically applied!
    
  }, res = 96)
  
  # ==========================================================================
  # OUTPUT: MODEL METRICS
  # ==========================================================================
  
  output$model_r2 <- renderText({
    req(model_results())
    results <- model_results()
    
    if (!is.null(results$error)) {
      return("--")
    }
    
    sprintf("%.3f", results$summary$r.squared)
  })
  
  output$model_adj_r2 <- renderText({
    req(model_results())
    results <- model_results()
    
    if (!is.null(results$error)) {
      return("--")
    }
    
    sprintf("%.3f", results$summary$adj.r.squared)
  })
  
  output$model_fstat <- renderText({
    req(model_results())
    results <- model_results()
    
    if (!is.null(results$error)) {
      return("--")
    }
    
    fstat <- results$summary$fstatistic[1]
    sprintf("%.2f", fstat)
  })
  
  output$model_n <- renderText({
    req(model_results())
    results <- model_results()
    
    if (!is.null(results$error)) {
      return("--")
    }
    
    format(nobs(results$model), big.mark = ",")
  })
  
  # ==========================================================================
  # OUTPUT: ERROR METRICS (RMSE, MAE, MAPE)
  # ==========================================================================
  
  output$model_rmse <- renderText({
    req(model_results())
    results <- model_results()
    
    if (!is.null(results$error)) {
      return("--")
    }
    
    sprintf("%.4f", results$rmse)
  })
  
  output$model_mae <- renderText({
    req(model_results())
    results <- model_results()
    
    if (!is.null(results$error)) {
      return("--")
    }
    
    sprintf("%.4f", results$mae)
  })
  
  output$model_mape <- renderText({
    req(model_results())
    results <- model_results()
    
    if (!is.null(results$error)) {
      return("--")
    }
    
    if (is.na(results$mape)) {
      return("N/A")
    }
    
    sprintf("%.2f%%", results$mape)
  })
  
  # ==========================================================================
  # OUTPUT: REGULARIZED MODEL METRICS (Ridge, LASSO, Elastic Net)
  # ==========================================================================
  
  output$reg_r2 <- renderText({
    req(model_results())
    results <- model_results()
    
    if (!is.null(results$error)) {
      return("--")
    }
    
    if (results$model_type %in% c("ridge", "lasso", "elasticnet")) {
      sprintf("%.3f", results$r_squared)
    } else {
      "--"
    }
  })
  
  output$reg_cv_r2 <- renderText({
    req(model_results())
    results <- model_results()
    
    if (!is.null(results$error)) {
      return("--")
    }
    
    if (results$model_type %in% c("ridge", "lasso", "elasticnet")) {
      sprintf("%.3f", results$cv_r_squared)
    } else {
      "--"
    }
  })
  
  output$reg_deviance_ratio <- renderText({
    req(model_results())
    results <- model_results()
    
    if (!is.null(results$error)) {
      return("--")
    }
    
    if (results$model_type %in% c("ridge", "lasso", "elasticnet")) {
      sprintf("%.3f", results$deviance_ratio)
    } else {
      "--"
    }
  })
  
  output$reg_n_obs <- renderText({
    req(model_results())
    results <- model_results()
    
    if (!is.null(results$error)) {
      return("--")
    }
    
    if (results$model_type %in% c("ridge", "lasso", "elasticnet")) {
      format(nrow(results$data), big.mark = ",")
    } else {
      "--"
    }
  })
  
  output$reg_lambda <- renderText({
    req(model_results())
    results <- model_results()
    
    if (!is.null(results$error)) {
      return("--")
    }
    
    if (results$model_type %in% c("ridge", "lasso", "elasticnet")) {
      sprintf("%.6f", results$lambda_min)
    } else {
      "--"
    }
  })
  
  output$reg_lambda_1se <- renderText({
    req(model_results())
    results <- model_results()
    
    if (!is.null(results$error)) {
      return("--")
    }
    
    if (results$model_type %in% c("ridge", "lasso", "elasticnet")) {
      sprintf("%.6f", results$lambda_1se)
    } else {
      "--"
    }
  })
  
  output$reg_l2_norm <- renderText({
    req(model_results())
    results <- model_results()
    
    if (!is.null(results$error)) {
      return("--")
    }
    
    if (results$model_type %in% c("ridge", "lasso", "elasticnet")) {
      sprintf("%.2f", results$l2_norm)
    } else {
      "--"
    }
  })
  
  output$reg_nonzero <- renderText({
    req(model_results())
    results <- model_results()
    
    if (!is.null(results$error)) {
      return("--")
    }
    
    if (results$model_type %in% c("ridge", "lasso", "elasticnet")) {
      paste0(results$nonzero_coefs, " / ", results$total_coefs)
    } else {
      "--"
    }
  })
  
  output$reg_train_rmse <- renderText({
    req(model_results())
    results <- model_results()
    
    if (!is.null(results$error)) {
      return("--")
    }
    
    if (results$model_type %in% c("ridge", "lasso", "elasticnet")) {
      sprintf("%.4f", results$train_rmse)
    } else {
      "--"
    }
  })
  
  output$reg_cv_rmse <- renderText({
    req(model_results())
    results <- model_results()
    
    if (!is.null(results$error)) {
      return("--")
    }
    
    if (results$model_type %in% c("ridge", "lasso", "elasticnet")) {
      sprintf("%.4f", results$cv_rmse)
    } else {
      "--"
    }
  })
  
  output$reg_train_mae <- renderText({
    req(model_results())
    results <- model_results()
    
    if (!is.null(results$error)) {
      return("--")
    }
    
    if (results$model_type %in% c("ridge", "lasso", "elasticnet")) {
      sprintf("%.4f", results$train_mae)
    } else {
      "--"
    }
  })
  
  output$reg_cv_mae <- renderText({
    req(model_results())
    results <- model_results()
    
    if (!is.null(results$error)) {
      return("--")
    }
    
    if (results$model_type %in% c("ridge", "lasso", "elasticnet") && !is.na(results$cv_mae)) {
      sprintf("%.4f", results$cv_mae)
    } else {
      "--"
    }
  })
  
  output$reg_cv_folds <- renderText({
    req(model_results())
    results <- model_results()
    
    if (!is.null(results$error)) {
      return("--")
    }
    
    if (results$model_type %in% c("ridge", "lasso", "elasticnet")) {
      as.character(results$cv_folds)
    } else {
      "--"
    }
  })
  
  # ==========================================================================
  # OUTPUT: LAMBDA PATH PLOT (Ridge coefficient shrinkage)
  # ==========================================================================
  
  output$lambda_path_plot <- renderPlot({
    req(model_results())
    results <- model_results()
    
    if (!is.null(results$error) || !results$model_type %in% c("ridge", "lasso", "elasticnet")) {
      plot.new()
      text(0.5, 0.5, "Build a regularized model to see coefficient paths", 
           cex = 1.2, col = "#6c757d")
      return()
    }
    
    # Plot lambda path from the full model
    plot(results$model_full, 
         xvar = "lambda",
         label = TRUE,
         main = "",
         xlab = "Log(Lambda)",
         ylab = "Coefficients")
    
    # Add vertical line at optimal lambda
    abline(v = log(results$lambda_min), col = "#0033A0", lwd = 2, lty = 2)
    abline(v = log(results$lambda_1se), col = "#28a745", lwd = 2, lty = 2)
    
    # Add legend
    legend("topright", 
           legend = c("Lambda (min)", "Lambda (1-SE)"),
           col = c("#0033A0", "#28a745"),
           lty = 2, lwd = 2,
           cex = 0.8)
  }, res = 96)
  
  # ==========================================================================
  # OUTPUT: CV ERROR VS LAMBDA PLOT
  # ==========================================================================
  
  output$cv_lambda_plot <- renderPlot({
    req(model_results())
    results <- model_results()
    
    if (!is.null(results$error) || !results$model_type %in% c("ridge", "lasso", "elasticnet")) {
      plot.new()
      text(0.5, 0.5, "Build a regularized model to see CV error plot", 
           cex = 1.2, col = "#6c757d")
      return()
    }
    
    # Plot CV error from cv.glmnet
    plot(results$cv_model,
         main = "",
         xlab = "Log(Lambda)",
         ylab = "Mean-Squared Error (10-Fold CV)")
    
  }, res = 96)
  
  # ==========================================================================
  # OUTPUT: CLASSIFICATION METRICS (PLACEHOLDERS)
  # ==========================================================================
  
  output$class_accuracy <- renderText({ "--" })
  output$class_precision <- renderText({ "--" })
  output$class_recall <- renderText({ "--" })
  output$class_f1 <- renderText({ "--" })
  output$class_auc <- renderText({ "AUC: --" })
  
  output$confusion_matrix <- renderPlot({
    plot.new()
    text(0.5, 0.5, "Build a classification model to see confusion matrix", 
         cex = 1.2, col = "#6c757d")
  }, res = 96)
  
  output$roc_curve <- renderPlot({
    plot.new()
    text(0.5, 0.5, "Build a classification model to see ROC curve", 
         cex = 1.2, col = "#6c757d")
  }, res = 96)
  
  # ==========================================================================
  # OUTPUT: QUANTILE REGRESSION METRICS (PLACEHOLDERS)
  # ==========================================================================
  
  output$quant_tau <- renderText({ "--" })
  output$quant_pseudo_r2 <- renderText({ "--" })
  output$quant_mad <- renderText({ "--" })
  
  # ==========================================================================
  # OUTPUT: MULTICOLLINEARITY DIAGNOSTICS
  # ==========================================================================
  
  output$model_condition_index <- renderText({
    req(model_results())
    results <- model_results()
    
    if (!is.null(results$error)) {
      return("--")
    }
    
    if (is.na(results$condition_index)) {
      return("N/A")
    }
    
    sprintf("%.2f", results$condition_index)
  })
  
  output$model_max_vif <- renderText({
    req(model_results())
    results <- model_results()
    
    if (!is.null(results$error)) {
      return("--")
    }
    
    if (is.na(results$max_vif)) {
      return("N/A")
    }
    
    sprintf("%.2f", results$max_vif)
  })
  
  # ==========================================================================
  # OUTPUT: COEFFICIENT INTERPRETATION CARDS
  # ==========================================================================
  
  output$coefficient_cards <- renderUI({
    req(model_results())
    results <- model_results()
    
    if (!is.null(results$error)) {
      return(HTML("<p style='text-align: center; color: #6c757d;'>Build a model to see coefficient interpretations</p>"))
    }
    
    # Get coefficient summary
    coef_summary <- results$summary$coefficients
    
    # Check if we have p-values (regularized models don't)
    has_pvalues <- !all(is.na(coef_summary[, "Pr(>|t|)"]))
    
    # Create cards for each coefficient (skip intercept)
    cards <- lapply(2:nrow(coef_summary), function(i) {
      coef_name <- rownames(coef_summary)[i]
      coef_value <- coef_summary[i, "Estimate"]
      std_error <- coef_summary[i, "Std. Error"]
      t_value <- coef_summary[i, "t value"]
      p_value <- coef_summary[i, "Pr(>|t|)"]
      
      if (has_pvalues && !is.na(p_value)) {
        # Standard regression with p-values
        sig_stars <- if (p_value < 0.001) {
          "***"
        } else if (p_value < 0.01) {
          "**"
        } else if (p_value < 0.05) {
          "*"
        } else {
          ""
        }
        
        sig_color <- if (p_value < 0.001) {
          "#28a745"
        } else if (p_value < 0.01) {
          "#0033A0"
        } else if (p_value < 0.05) {
          "#ffc107"
        } else {
          "#dc3545"
        }
        
        sig_label <- if (p_value < 0.001) {
          "Highly Significant"
        } else if (p_value < 0.01) {
          "Very Significant"
        } else if (p_value < 0.05) {
          "Significant"
        } else {
          "Not Significant"
        }
      } else {
        # Regularized regression - show magnitude instead
        sig_stars <- ""
        abs_coef <- abs(coef_value)
        
        sig_color <- if (abs_coef > 0.1) {
          "#28a745"
        } else if (abs_coef > 0.05) {
          "#0033A0"
        } else if (abs_coef > 0.01) {
          "#ffc107"
        } else {
          "#dc3545"
        }
        
        sig_label <- if (abs_coef > 0.1) {
          "Strong Effect"
        } else if (abs_coef > 0.05) {
          "Moderate Effect"
        } else if (abs_coef > 0.01) {
          "Weak Effect"
        } else {
          "Very Weak"
        }
      }
      
      # Format coefficient name
      display_name <- gsub("_", " ", coef_name)
      display_name <- tools::toTitleCase(display_name)
      
      # Create interpretation text
      if (input$reg_scale) {
        interpretation_text <- sprintf(
          "Interpretation: A one standard deviation increase in %s is associated with a %.4f standard deviation change in %s.",
          tolower(display_name), coef_value, 
          switch(input$reg_dependent,
                 "overall_food_insecurity_rate" = "food insecurity rate",
                 "child_food_insecurity_rate" = "child food insecurity rate",
                 input$reg_dependent)
        )
      } else {
        interpretation_text <- sprintf(
          "Interpretation: A one-unit increase in %s is associated with a %.4f change in %s.",
          tolower(display_name), coef_value, 
          switch(input$reg_dependent,
                 "overall_food_insecurity_rate" = "food insecurity rate",
                 "child_food_insecurity_rate" = "child food insecurity rate",
                 input$reg_dependent)
        )
      }
      
      # Create card
      div(
        style = "border-left: 4px solid #0033A0; padding: 15px; margin-bottom: 15px;
                 background: #f8f9fa; border-radius: 4px;",
        div(
          style = "display: flex; justify-content: space-between; align-items: center;",
          h5(display_name, style = "margin: 0; color: #2c3e50;"),
          div(
            style = paste0("background: ", sig_color, "; color: white; padding: 5px 12px; ",
                          "border-radius: 20px; font-size: 12px; font-weight: 600;"),
            sig_label
          )
        ),
        hr(style = "margin: 10px 0; border-color: #dee2e6;"),
        div(
          style = "display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px;",
          div(
            p("Coefficient", style = "margin: 0; font-size: 11px; color: #6c757d;"),
            p(sprintf("%.4f %s", coef_value, sig_stars), 
              style = "margin: 5px 0 0 0; font-size: 16px; font-weight: 600; color: #2c3e50;")
          ),
          if (has_pvalues && !is.na(std_error)) {
            div(
              p("Std. Error", style = "margin: 0; font-size: 11px; color: #6c757d;"),
              p(sprintf("%.4f", std_error), 
                style = "margin: 5px 0 0 0; font-size: 16px; font-weight: 600; color: #2c3e50;")
            )
          } else {
            div(
              p("Abs. Value", style = "margin: 0; font-size: 11px; color: #6c757d;"),
              p(sprintf("%.4f", abs(coef_value)), 
                style = "margin: 5px 0 0 0; font-size: 16px; font-weight: 600; color: #2c3e50;")
            )
          },
          if (has_pvalues && !is.na(t_value)) {
            div(
              p("t-value", style = "margin: 0; font-size: 11px; color: #6c757d;"),
              p(sprintf("%.3f", t_value), 
                style = "margin: 5px 0 0 0; font-size: 16px; font-weight: 600; color: #2c3e50;")
            )
          } else {
            div(
              p("Direction", style = "margin: 0; font-size: 11px; color: #6c757d;"),
              p(if (coef_value > 0) "Positive ↑" else "Negative ↓", 
                style = "margin: 5px 0 0 0; font-size: 16px; font-weight: 600; color: #2c3e50;")
            )
          },
          if (has_pvalues && !is.na(p_value)) {
            div(
              p("p-value", style = "margin: 0; font-size: 11px; color: #6c757d;"),
              p(if (p_value < 0.001) "< 0.001" else sprintf("%.4f", p_value), 
                style = "margin: 5px 0 0 0; font-size: 16px; font-weight: 600; color: #2c3e50;")
            )
          } else {
            div(
              p("% of Max", style = "margin: 0; font-size: 11px; color: #6c757d;"),
              p(sprintf("%.1f%%", abs(coef_value) / max(abs(coef_summary[-1, "Estimate"])) * 100), 
                style = "margin: 5px 0 0 0; font-size: 16px; font-weight: 600; color: #2c3e50;")
            )
          }
        ),
        p(
          interpretation_text,
          style = "margin-top: 10px; font-size: 13px; color: #535c68; font-style: italic;"
        )
      )
    })
    
    do.call(tagList, cards)
  })
  
  # ==========================================================================
  # OUTPUT: RESIDUALS VS FITTED PLOT
  # ==========================================================================
  
  output$residuals_fitted <- renderPlot({
    req(model_results())
    results <- model_results()
    
    if (!is.null(results$error)) {
      plot.new()
      text(0.5, 0.5, "Build a model to see diagnostics", cex = 1.2, col = "#6c757d")
      return()
    }
    
    df <- results$data
    
    ggplot(df, aes(x = fitted, y = residuals)) +
      geom_point(alpha = 0.5, size = 2, color = "#0033A0") +
      geom_hline(yintercept = 0, color = "#E63946", linetype = "dashed", linewidth = 1) +
      geom_smooth(method = "loess", se = FALSE, color = "#28a745", linewidth = 1) +
      labs(
        title = "Residual Analysis",
        subtitle = "Points should be randomly scattered around zero line",
        x = "Fitted Values",
        y = "Residuals"
      )
      # Global theme applied!
    
  }, res = 96)
  
  # ==========================================================================
  # OUTPUT: Q-Q PLOT
  # ==========================================================================
  
  output$qq_plot <- renderPlot({
    req(model_results())
    results <- model_results()
    
    if (!is.null(results$error)) {
      plot.new()
      text(0.5, 0.5, "Build a model to see diagnostics", cex = 1.2, col = "#6c757d")
      return()
    }
    
    # Q-Q plot data
    residuals_std <- rstandard(results$model)
    qq_data <- data.frame(
      theoretical = qqnorm(residuals_std, plot.it = FALSE)$x,
      sample = qqnorm(residuals_std, plot.it = FALSE)$y
    )
    
    ggplot(qq_data, aes(x = theoretical, y = sample)) +
      geom_point(alpha = 0.5, size = 2, color = "#0033A0") +
      geom_abline(intercept = 0, slope = 1, color = "#E63946", 
                  linetype = "dashed", linewidth = 1) +
      labs(
        title = "Normal Q-Q Plot",
        subtitle = "Points should follow the diagonal line for normal residuals",
        x = "Theoretical Quantiles",
        y = "Sample Quantiles"
      )
      # Global theme applied!
    
  }, res = 96)
  
  # ==========================================================================
  # OUTPUT: MODEL SUMMARY
  # ==========================================================================
  
  output$model_summary <- renderPrint({
    req(model_results())
    results <- model_results()
    
    if (!is.null(results$error)) {
      cat("Error:", results$error, "\n\n")
      cat("Please select a different model type or check your data.\n")
      return()
    }
    
    summary(results$model)
  })
  
  # ==========================================================================
  # AI-POWERED INTERPRETATION (Full Claude API Integration)
  # ==========================================================================
  
  model_ai_text <- reactiveVal(NULL)
  
  output$model_ai_interpretation <- renderUI({
    if (is.null(model_ai_text())) {
      HTML(paste0(
        "<div style='text-align: center; padding: 40px; color: white; opacity: 0.9;'>",
        "<p style='font-size: 16px; margin: 0;'>",
        "Click <strong>'Generate AI Analysis'</strong> to get comprehensive model interpretation ",
        "from Claude AI.",
        "</p>",
        "</div>"
      ))
    } else {
      HTML(model_ai_text())
    }
  })
  
  observeEvent(input$generate_model_interpretation, {
    req(model_results())
    results <- model_results()
    
    if (!is.null(results$error)) {
      model_ai_text(paste0(
        "<div style='text-align: center; padding: 20px;'>",
        "<p style='color: white;'>Please build a model first.</p>",
        "</div>"
      ))
      return()
    }
    
    # Show loading
    model_ai_text(paste0(
      "<div style='text-align: center; padding: 40px;'>",
      "<i class='fa fa-spinner fa-spin' style='font-size: 48px; color: white;'></i>",
      "<p style='margin-top: 20px; color: white;'>Generating AI analysis...</p>",
      "</div>"
    ))
    
    # Check if AI module exists
    if (!exists("ask_claude")) {
      model_ai_text(paste0(
        "<div style='background: rgba(255,255,255,0.15); padding: 20px; border-radius: 8px;'>",
        "<p style='color: white; margin: 0;'>",
        "AI interpretation requires the AI module. Load it in global.R: ",
        "<code>source('R/ai_explanations.R')</code>",
        "</p>",
        "</div>"
      ))
      return()
    }
    
    # Get variable labels
    dep_label <- switch(
      input$reg_dependent,
      "overall_food_insecurity_rate" = "Food Insecurity Rate",
      "child_food_insecurity_rate" = "Child Food Insecurity Rate",
      input$reg_dependent
    )
    
    # Build coefficient summary
    coef_summary <- summary(results$model)$coefficients
    coef_text <- ""
    for (i in 2:nrow(coef_summary)) {
      var_name <- rownames(coef_summary)[i]
      coef_val <- coef_summary[i, "Estimate"]
      p_val <- coef_summary[i, "Pr(>|t|)"]
      sig <- if (p_val < 0.001) "***" else if (p_val < 0.01) "**" else if (p_val < 0.05) "*" else ""
      
      coef_text <- paste0(coef_text, 
        "• ", gsub("_", " ", var_name), ": β = ", sprintf("%.4f", coef_val), 
        sig, " (p ", ifelse(p_val < 0.001, "< 0.001", sprintf("= %.4f", p_val)), ")\n")
    }
    
    # Build multicollinearity summary
    multicoll_text <- ""
    if (!is.na(results$condition_index)) {
      multicoll_text <- paste0(
        "• Condition Index: ", sprintf("%.2f", results$condition_index),
        if (results$condition_index < 10) " (no multicollinearity)" else 
        if (results$condition_index < 30) " (moderate multicollinearity)" else 
        " (severe multicollinearity)", "\n"
      )
    }
    if (!is.na(results$max_vif)) {
      multicoll_text <- paste0(multicoll_text,
        "• Max VIF: ", sprintf("%.2f", results$max_vif),
        if (results$max_vif < 5) " (no multicollinearity)" else 
        if (results$max_vif < 10) " (moderate multicollinearity)" else 
        " (high multicollinearity)", "\n"
      )
    }
    
    # Build prompt
    prompt <- paste0(
      "You are a statistician analyzing food insecurity data. Provide a clear, policy-focused interpretation of this regression analysis:\n\n",
      "REGRESSION MODEL:\n",
      "• Dependent Variable: ", dep_label, "\n",
      "• Independent Variables: ", paste(input$reg_independent, collapse = ", "), "\n",
      "• Model Type: ", toupper(gsub("_", " ", results$model_type)), "\n",
      "• Scaled: ", if (input$reg_scale) "Yes (standardized)" else "No", "\n",
      "• Year: ", input$reg_year, "\n\n",
      "MODEL PERFORMANCE:\n",
      "• R-squared: ", sprintf("%.3f", results$summary$r.squared), " (", sprintf("%.1f%%", results$summary$r.squared * 100), " variance explained)\n",
      "• Adjusted R-squared: ", sprintf("%.3f", results$summary$adj.r.squared), "\n",
      "• F-statistic: ", sprintf("%.2f", results$summary$fstatistic[1]), " (p < 0.001)\n",
      "• Sample Size: ", format(nobs(results$model), big.mark = ","), " counties\n\n",
      "MULTICOLLINEARITY DIAGNOSTICS:\n",
      multicoll_text, "\n",
      "COEFFICIENTS", if (input$reg_scale) " (standardized)" else "", ":\n",
      coef_text, "\n",
      "Please provide:\n",
      "1. Overall model performance assessment\n",
      "2. Interpretation of each significant predictor in plain language\n",
      "3. Which predictor is strongest and what that means\n",
      if (multicoll_text != "") "4. Comment on multicollinearity and its implications\n",
      "5. Policy implications - what this tells us about addressing food insecurity\n",
      if (!input$reg_scale) "6. Practical example: If poverty increases by 5%, what happens to food insecurity?\n",
      "7. Important caveats (correlation vs causation, omitted variables, etc.)\n\n",
      "Write in 3-5 paragraphs using <p> tags. Be concise, clear, and policy-focused. Use specific numbers from the results."
    )
    
    # Call Claude API
    ai_response <- ask_claude(prompt, max_tokens = 2000)
    
    # Update output
    model_ai_text(ai_response)
  })
  
  cat("✓ Regression Models module initialized\n")
  cat("✓ Currently supporting: Linear, Polynomial (2), Polynomial (3), Ridge (L2)\n")
  cat("✓ Additional models (LASSO, Elastic Net, etc.) coming soon!\n")
}