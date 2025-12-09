# ==============================================================================
# SERVER MODULE: ANALYSIS TAB
# ==============================================================================
# PURPOSE: Implement 7 statistical analysis methods (DATA-613 requirement)
# FEATURES: Correlation, regression, multinomial, PCA, clustering, ANOVA
# TEAM: Conrad, Sharon, Ryann, Alex
# ==============================================================================

server_analysis <- function(input, output, session, data) {
  # Ensure data is reactive
  data <- if (is.reactive(data)) data else reactive(data)

  # ============================================================================
  # REACTIVE: Get numeric and Categorical variables
  # ============================================================================

  numeric_vars <- reactive({
    df <- data()
    df %>%
      select(where(is.numeric)) %>%
      names() %>%
      sort()
  })

  categorical_vars <- reactive({
    df <- data()
    df %>%
      select(where(~ is.character(.) || is.factor(.))) %>%
      names() %>%
      sort()
  })

  # ============================================================================
  # REACTIVE: Decision tree target / predictor choices
  # ============================================================================

  tree_target_choices <- reactive({
    sort(unique(c(numeric_vars(), categorical_vars())))
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
      selected = "overall_food_insecurity_rate"
    )
  })

  observe({
    updateSelectInput(session, "reg_independent", choices = numeric_vars())
  })

  observe({
    updateSelectInput(session, "group_target",
      choices = numeric_vars(),
      selected = "overall_food_insecurity_rate"
    )
  })

  # ============================================================================
  # DECISION TREE DROPDOWNS
  # ============================================================================

  observe({
    updateSelectInput(
      session,
      "tree_target",
      choices  = tree_target_choices(),
      selected = "overall_food_insecurity_rate"
    )
  })

  observe({
    req(input$tree_target)
    updateSelectInput(
      session,
      "tree_predictors",
      choices = setdiff(tree_target_choices(), input$tree_target)
    )
  })

  # ============================================================================
  # PCA DROPDOWNS
  # ============================================================================

  observe({
    updateSelectInput(
      session,
      "pca_vars",
      choices = numeric_vars()
    )
  })

  # ============================================================================
  # K-MEANS DROPDOWNS
  # ============================================================================

  observe({
    updateSelectInput(
      session,
      "kmeans_vars",
      choices = numeric_vars()
    )
  })

  # ============================================================================
  # MULTINOMIAL LOGISTIC REGRESSION UI (FIXED!)
  # ============================================================================

  output$multinomial_ui <- renderUI({
    df <- data()

    # Get valid targets (factors with 3+ levels)
    valid_targets <- names(df)[
      sapply(df, function(x) is.factor(x) && nlevels(x) >= 3)
    ]

    # Get all potential predictors
    all_predictors <- names(df)[
      sapply(df, function(x) is.numeric(x) || is.factor(x))
    ]

    tagList(
      h4("Multinomial Logistic Regression"),
      selectInput(
        "multi_target",
        "Categorical Outcome (3+ levels):",
        choices = c("", sort(valid_targets)),
        selected = ""
      ),
      selectInput(
        "multi_predictors",
        "Predictor Variables:",
        choices = sort(all_predictors),
        multiple = TRUE
      ),
      actionButton(
        "run_multinomial",
        "Run Multinomial Regression",
        class = "btn-primary btn-block"
      ),
      br(),
      helpText("Note: Outcome variable must have at least 3 categories. The first category will be used as the reference level.")
    )
  })

  # Update predictors when target changes
  observe({
    req(input$multi_target, input$multi_target != "")
    df <- data()

    # Get all potential predictors (exclude target)
    all_predictors <- names(df)[
      sapply(df, function(x) is.numeric(x) || is.factor(x))
    ]

    updateSelectInput(
      session,
      "multi_predictors",
      choices = setdiff(sort(all_predictors), input$multi_target)
    )
  })

  # ============================================================================
  # CORRELATION ANALYSIS
  # ============================================================================

  observeEvent(input$run_correlation, {
    req(input$corr_vars, length(input$corr_vars) >= 2)

    df <- data() %>%
      select(all_of(input$corr_vars)) %>%
      drop_na()

    corr_matrix <- cor(df, use = "pairwise.complete.obs")

    output$corr_plot <- renderPlot({
      corr_long <- corr_matrix %>%
        as.data.frame() %>%
        rownames_to_column("var1") %>%
        pivot_longer(-var1, names_to = "var2", values_to = "correlation")

      ggplot(corr_long, aes(var1, var2, fill = correlation)) +
        geom_tile(color = "white") +
        geom_text(aes(label = round(correlation, 2)), size = 4) +
        scale_fill_gradient2(
          low = "#d73027", mid = "white", high = "#4575b4",
          midpoint = 0, limits = c(-1, 1)
        ) +
        theme(axis.text.x = element_text(angle = 45, hjust = 1))
    })

    output$corr_table <- renderDT({
      datatable(round(corr_matrix, 3), options = list(dom = "tp"))
    })

    output$corr_interpretation <- renderUI({
      HTML("<p>Correlation matrix displays linear relationships among selected variables.</p>")
    })
  })

  # ============================================================================
  # REGRESSION ANALYSIS
  # ============================================================================

  observeEvent(input$run_regression, {
    req(input$reg_dependent, input$reg_independent)

    df <- data() %>%
      select(all_of(c(input$reg_dependent, input$reg_independent))) %>%
      drop_na()

    model <- lm(
      as.formula(paste(
        input$reg_dependent, "~",
        paste(input$reg_independent, collapse = " + ")
      )),
      data = df
    )

    output$reg_summary <- renderPrint({
      summary(model)
    })

    output$reg_diagnostics <- renderPlot({
      par(mfrow = c(2, 2))
      plot(model)
      par(mfrow = c(1, 1))
    })

    output$reg_predictions <- renderPlot({
      df$pred <- predict(model)
      ggplot(df, aes(pred, .data[[input$reg_dependent]])) +
        geom_point(alpha = 0.3) +
        geom_abline(slope = 1, intercept = 0, linetype = "dashed", color = "red")
    })

    output$reg_coefficients <- renderPlot({
      broom::tidy(model, conf.int = TRUE) %>%
        filter(term != "(Intercept)") %>%
        ggplot(aes(reorder(term, estimate), estimate)) +
        geom_point(size = 3) +
        geom_errorbar(aes(ymin = conf.low, ymax = conf.high), width = 0.2) +
        coord_flip()
    })
  })

  # ============================================================================
  # MULTINOMIAL LOGISTIC REGRESSION
  # ============================================================================

  observeEvent(input$run_multinomial, {
    req(input$multi_target)
    req(input$multi_predictors)
    req(length(input$multi_predictors) >= 1)
    req(data())

    df <- data()
    vars <- c(input$multi_target, input$multi_predictors)
    md <- df %>%
      select(all_of(vars)) %>%
      drop_na()

    if (nrow(md) < 30) {
      output$multi_interpretation <- renderUI({
        HTML("<p style='color:red;'>Not enough complete cases to fit the multinomial model.</p>")
      })
      return()
    }

    md[[input$multi_target]] <- droplevels(factor(md[[input$multi_target]]))

    if (nlevels(md[[input$multi_target]]) < 3) {
      output$multi_interpretation <- renderUI({
        HTML("<p style='color:red;'>Outcome must have at least 3 categories.</p>")
      })
      return()
    }

    model <- nnet::multinom(
      as.formula(
        paste(
          input$multi_target, "~",
          paste(input$multi_predictors, collapse = " + ")
        )
      ),
      data = md,
      trace = FALSE
    )

    output$multi_summary <- renderPrint({
      cat(strrep("=", 60), "\n")
      cat("MULTINOMIAL LOGISTIC REGRESSION MODEL SUMMARY\n")
      cat(strrep("=", 60), "\n\n")

      cat("Reference Category:", levels(md[[input$multi_target]])[1], "\n")
      cat("Sample Size:", nrow(md), "observations\n")
      cat("Predictors:", paste(input$multi_predictors, collapse = ", "), "\n\n")

      cat(strrep("=", 60), "\n")
      cat("COEFFICIENTS (Log-Odds Scale)\n")
      cat(strrep("=", 60), "\n")

      # Get coefficients and format nicely
      coef_matrix <- summary(model)$coefficients
      se_matrix <- summary(model)$standard.errors

      for (outcome in rownames(coef_matrix)) {
        cat("\n", outcome, "vs", levels(md[[input$multi_target]])[1], ":\n")
        cat(strrep("-", 60), "\n")

        for (pred in colnames(coef_matrix)) {
          coef_val <- coef_matrix[outcome, pred]
          se_val <- se_matrix[outcome, pred]
          z_val <- coef_val / se_val
          p_val <- 2 * (1 - pnorm(abs(z_val)))

          sig <- ifelse(p_val < 0.001, "***",
            ifelse(p_val < 0.01, "**",
              ifelse(p_val < 0.05, "*", "")
            )
          )

          cat(sprintf(
            "  %-20s: %10.4f  (SE: %.4f)  %s\n",
            pred, coef_val, se_val, sig
          ))
        }
      }

      cat("\n", strrep("=", 60), "\n")
      cat("MODEL FIT STATISTICS\n")
      cat(strrep("=", 60), "\n")
      cat(sprintf("Residual Deviance: %.2f\n", model$deviance))
      cat(sprintf("AIC:               %.2f\n", model$AIC))
      cat("\nSignificance: *** p<0.001, ** p<0.01, * p<0.05\n")
    })

    output$multi_rrr <- renderPlot({
      # Try using broom::tidy, if it fails, calculate manually
      tryCatch(
        {
          coefs <- broom::tidy(model, exponentiate = TRUE)

          ggplot(
            coefs %>% filter(term != "(Intercept)"),
            aes(x = reorder(term, estimate), y = estimate, color = y.level)
          ) +
            geom_point(size = 3) +
            geom_hline(yintercept = 1, linetype = "dashed", color = "gray50") +
            coord_flip() +
            scale_y_log10() +
            labs(
              title = "Relative Risk Ratios (Multinomial Logistic Regression)",
              y = "Relative Risk Ratio (log scale)",
              x = "Predictor",
              color = "Outcome Category"
            )
        },
        error = function(e) {
          # Fallback: manual calculation
          coef_matrix <- coef(model)
          rrr_data <- as.data.frame(exp(coef_matrix))
          rrr_data$outcome <- rownames(rrr_data)

          rrr_long <- rrr_data %>%
            pivot_longer(-outcome, names_to = "predictor", values_to = "RRR") %>%
            filter(predictor != "(Intercept)")

          ggplot(rrr_long, aes(x = reorder(predictor, RRR), y = RRR, color = outcome)) +
            geom_point(size = 3) +
            geom_hline(yintercept = 1, linetype = "dashed", color = "gray50") +
            coord_flip() +
            scale_y_log10() +
            labs(
              title = "Relative Risk Ratios (Multinomial Logistic Regression)",
              y = "Relative Risk Ratio (log scale)",
              x = "Predictor",
              color = "Outcome Category"
            )
        }
      )
    })

    output$multi_accuracy <- renderPrint({
      preds <- predict(model, newdata = md)
      actual <- md[[input$multi_target]]
      acc <- mean(preds == actual)
      cat("Training Classification Accuracy:", round(acc, 3))
    })

    output$multi_interpretation <- renderUI({
      ref <- levels(md[[input$multi_target]])[1]

      HTML(paste0(
        "<h4>Interpretation</h4>",
        "<ul>",
        "<li>The model predicts <strong>", input$multi_target,
        "</strong> using multinomial logistic regression.</li>",
        "<li>Effects are interpreted relative to the reference category: ",
        "<strong>", ref, "</strong>.</li>",
        "<li>Relative Risk Ratios greater than 1 indicate increased likelihood ",
        "of an outcome relative to the reference.</li>",
        "</ul>"
      ))
    })
  })

  # ============================================================================
  # DECISION TREE ANALYSIS
  # ============================================================================

  # Store fitted decision tree model
  tree_model <- reactiveVal(NULL)

  # Store tree training data (needed for interpretation)
  tree_data <- reactiveVal(NULL)

  # Reactive flag: is the decision tree BINARY?
  is_tree_binary <- reactive({
    req(tree_data(), input$tree_target)
    target <- tree_data()[[input$tree_target]]
    is.factor(target) && length(levels(target)) == 2
  })

  # Expose to UI (for conditionalPanel)
  output$is_tree_binary <- reactive({
    is_tree_binary()
  })

  outputOptions(output, "is_tree_binary", suspendWhenHidden = FALSE)

  observeEvent(input$run_tree, {
    req(input$tree_target)
    req(input$tree_predictors)
    req(length(input$tree_predictors) >= 1)

    df <- data()

    # Prepare data
    tree_vars <- c(input$tree_target, input$tree_predictors)

    td <- df %>%
      select(all_of(tree_vars)) %>%
      drop_na()

    tree_data(td)

    # SAFETY CHECK
    if (
      nrow(td) == 0 ||
        length(unique(td[[input$tree_target]])) < 2
    ) {
      output$tree_interpretation <- renderUI({
        HTML(
          "<p style='color:red;'>
          Selected target variable has insufficient non-missing
          or unique values to build a decision tree.
          </p>"
        )
      })
      return()
    }

    # Identify model type
    target <- td[[input$tree_target]]

    is_binary_numeric <- is.numeric(target) && all(unique(target) %in% c(0, 1))
    is_categorical <- is.factor(target) || is.character(target)
    is_classification <- is_binary_numeric || is_categorical

    # ENSURE proper classification target
    if (is_classification && !is.factor(td[[input$tree_target]])) {
      td[[input$tree_target]] <- factor(td[[input$tree_target]])
    }

    # Build formula
    formula_str <- paste(
      input$tree_target, "~",
      paste(input$tree_predictors, collapse = " + ")
    )
    tree_formula <- as.formula(formula_str)

    # Fit tree
    set.seed(123)

    if (is_classification) {
      model <- rpart::rpart(
        tree_formula,
        data = td,
        method = "class",
        control = rpart::rpart.control(cp = 0.01)
      )
    } else {
      model <- rpart::rpart(
        tree_formula,
        data = td,
        method = "anova",
        control = rpart::rpart.control(cp = 0.01)
      )
    }

    tree_model(model)

    # MODEL DATA (WHAT THE TREE USED)
    output$tree_model_data_summary <- renderTable({
      req(tree_data())

      data.frame(
        Item = c(
          "Target variable",
          "Predictor variables",
          "Observations used"
        ),
        Value = c(
          input$tree_target,
          paste(input$tree_predictors, collapse = ", "),
          nrow(tree_data())
        )
      )
    })

    output$tree_model_data <- renderDT({
      req(tree_data())

      datatable(
        tree_data(),
        options = list(
          pageLength = 10,
          scrollX = TRUE
        ),
        rownames = FALSE
      )
    })

    # TREE PLOT
    output$tree_plot <- renderPlot({
      rpart.plot::rpart.plot(
        tree_model(),
        type = 2,
        extra = ifelse(is_classification, 104, 101),
        fallen.leaves = TRUE,
        main = "Decision Tree"
      )
    })

    # VARIABLE IMPORTANCE
    output$tree_importance <- renderPlot({
      model <- tree_model()
      req(model)

      imp <- data.frame(
        Variable = names(model$variable.importance),
        Importance = model$variable.importance
      )

      ggplot(imp, aes(x = reorder(Variable, Importance), y = Importance)) +
        geom_col(fill = "#2C7FB8") +
        coord_flip() +
        labs(
          title = "Variable Importance",
          x = "Predictor",
          y = "Importance"
        )
    })

    # CONFUSION MATRIX (classification only)
    output$tree_confusion <- renderTable(
      {
        if (!is_classification) {
          return(NULL)
        }

        preds <- predict(tree_model(), newdata = td, type = "class")
        table(Predicted = preds, Actual = target)
      },
      rownames = TRUE
    )

    # ROC CURVE & AUC (classification only)
    output$tree_roc <- renderPlot({
      req(tree_model())
      req(is_classification)

      if (!is_classification) {
        return(NULL)
      }

      model <- tree_model()
      df <- tree_data()

      probs <- predict(model, newdata = df, type = "prob")
      response <- df[[input$tree_target]]

      positive_class <- levels(response)[2]

      roc_obj <- pROC::roc(
        response = response,
        predictor = probs[, positive_class],
        quiet = TRUE
      )

      plot(
        roc_obj,
        col = "#2C7FB8",
        lwd = 3,
        main = "ROC Curve (Decision Tree Classification)"
      )
      abline(a = 0, b = 1, lty = 2, col = "gray")
    })

    # AUC OUTPUT
    output$tree_auc <- renderPrint({
      req(tree_model())
      req(is_classification)

      if (!is_classification) {
        cat("AUC is only available for classification trees.")
        return()
      }

      model <- tree_model()
      df <- tree_data()

      probs <- predict(model, newdata = df, type = "prob")
      response <- df[[input$tree_target]]

      positive_class <- levels(response)[2]

      roc_obj <- pROC::roc(
        response = response,
        predictor = probs[, positive_class],
        quiet = TRUE
      )

      auc_value <- pROC::auc(roc_obj)

      cat("Area Under the Curve (AUC):", round(as.numeric(auc_value), 3))
    })

    # INTERPRETATION BLOCK
    output$tree_interpretation <- renderUI({
      req(tree_model())
      model <- tree_model()

      # Variable importance
      importance <- model$variable.importance
      top_vars <- names(sort(importance, decreasing = TRUE))[1:min(3, length(importance))]

      # Detect model type
      target <- input$tree_target
      df <- tree_data()

      is_classification <-
        is.factor(df[[target]]) ||
          (is.numeric(df[[target]]) &&
            all(unique(df[[target]]) %in% c(0, 1)))

      # Tree complexity
      n_splits <- nrow(model$splits)
      depth <- if (!is.null(model$frame$depth)) {
        max(model$frame$depth, na.rm = TRUE)
      } else {
        0
      }

      tagList(
        h4("Decision Tree Interpretation"),
        tags$ul(
          tags$li(
            strong("Model type: "),
            if (is_classification) "Classification tree" else "Regression tree"
          ),
          tags$li(
            strong("Most important predictors: "),
            paste(top_vars, collapse = ", ")
          ),
          tags$li(
            strong("Tree structure: "),
            paste(
              "The tree contains", n_splits,
              "splits with a maximum depth of", depth, "."
            )
          ),
          tags$li(
            "The decision tree captures non-linear relationships and interactions ",
            "between predictors, making it suitable for exploratory and policy analysis."
          )
        )
      )
    })
  })

  # ============================================================================
  # PCA ANALYSIS
  # ============================================================================

  observeEvent(input$run_pca, {
    req(input$pca_vars)
    req(length(input$pca_vars) >= 2)

    df <- data()

    # Prepare data
    pca_data <- df %>%
      select(all_of(input$pca_vars)) %>%
      drop_na()

    if (nrow(pca_data) < 20) {
      output$pca_interpretation <- renderUI({
        HTML("<p style='color:red;'>Not enough data for PCA (need ≥ 20 observations).</p>")
      })
      return()
    }

    # Run PCA
    pca_model <- prcomp(
      pca_data,
      scale. = input$pca_scale,
      center = TRUE
    )

    # Variance explained
    var_explained <- (pca_model$sdev^2) / sum(pca_model$sdev^2)

    # SCREE PLOT
    output$pca_scree <- renderPlot({
      scree_df <- data.frame(
        PC = factor(seq_along(var_explained)),
        Variance = var_explained
      )

      ggplot(scree_df, aes(x = PC, y = Variance)) +
        geom_col(fill = "#2C7FB8") +
        geom_line(aes(group = 1), color = "black") +
        geom_point(size = 2) +
        scale_y_continuous(labels = scales::percent_format()) +
        labs(
          title = "Scree Plot: Variance Explained by Principal Components",
          x = "Principal Component",
          y = "Proportion of Variance Explained"
        )
    })

    # BIPLOT (PC1 vs PC2)
    output$pca_biplot <- renderPlot({
      scores <- as.data.frame(pca_model$x[, 1:2])
      scores$obs <- rownames(scores)

      loadings <- as.data.frame(pca_model$rotation[, 1:2])
      loadings$var <- rownames(loadings)

      ggplot(scores, aes(PC1, PC2)) +
        geom_point(alpha = 0.4) +
        geom_segment(
          data = loadings,
          aes(x = 0, y = 0, xend = PC1 * 5, yend = PC2 * 5),
          arrow = arrow(length = unit(0.2, "cm")),
          color = "red"
        ) +
        geom_text(
          data = loadings,
          aes(x = PC1 * 5, y = PC2 * 5, label = var),
          color = "red",
          size = 4,
          hjust = 1
        ) +
        labs(
          title = "PCA Biplot (PC1 vs PC2)",
          x = "PC1",
          y = "PC2"
        )
    })

    # LOADINGS TABLE
    output$pca_loadings <- renderDT({
      loadings_df <- as.data.frame(pca_model$rotation) %>%
        rownames_to_column("Variable")

      datatable(
        loadings_df,
        options = list(pageLength = 10),
        rownames = FALSE
      ) %>%
        formatRound(columns = -1, digits = 3)
    })

    # INTERPRETATION
    output$pca_interpretation <- renderUI({
      pc1_vars <- sort(abs(pca_model$rotation[, 1]), decreasing = TRUE)[1:3]
      pc2_vars <- sort(abs(pca_model$rotation[, 2]), decreasing = TRUE)[1:3]

      HTML(paste0(
        "<h4>PCA Interpretation</h4>",
        "<ul>",
        "<li><strong>PC1</strong> explains ",
        round(var_explained[1] * 100, 1),
        "% of total variance and is mainly driven by: ",
        paste(names(pc1_vars), collapse = ", "),
        ".</li>",
        "<li><strong>PC2</strong> explains ",
        round(var_explained[2] * 100, 1),
        "% of total variance and reflects variation in: ",
        paste(names(pc2_vars), collapse = ", "),
        ".</li>",
        "</ul>",
        "<p>PCA reveals the major dimensions of food insecurity variation across counties.</p>"
      ))
    })
  })

  # ============================================================================
  # K-MEANS CLUSTERING
  # ============================================================================

  observeEvent(input$run_kmeans, {
    req(input$kmeans_vars)
    req(length(input$kmeans_vars) >= 2)
    req(input$k_clusters)

    df <- data()

    # Prepare clustering data
    cluster_df <- df %>%
      select(all_of(input$kmeans_vars)) %>%
      drop_na()

    if (nrow(cluster_df) < input$k_clusters * 5) {
      output$kmeans_plot <- renderPlot({
        plot.new()
        text(0.5, 0.5, "Not enough data for selected number of clusters",
          cex = 1.4, col = "red"
        )
      })
      return()
    }

    # Scale data (important!)
    scaled_data <- scale(cluster_df)

    set.seed(123)
    km <- kmeans(scaled_data, centers = input$k_clusters, nstart = 25)

    cluster_df$cluster <- factor(km$cluster)

    # PCA for visualization
    pca_res <- prcomp(scaled_data)

    pca_df <- as.data.frame(pca_res$x[, 1:2])
    pca_df$cluster <- cluster_df$cluster

    # CLUSTER PLOT
    output$kmeans_plot <- renderPlot({
      ggplot(pca_df, aes(PC1, PC2, color = cluster)) +
        geom_point(alpha = 0.6, size = 2) +
        stat_ellipse(type = "norm", level = 0.68, linewidth = 1) +
        labs(
          title = paste("K-Means Clustering (k =", input$k_clusters, ")"),
          subtitle = "Visualization via first two principal components",
          color = "Cluster"
        )
    })

    # CLUSTER SUMMARY TABLE
    output$kmeans_summary <- renderDT({
      summary_df <- cluster_df %>%
        group_by(cluster) %>%
        summarise(
          n = n(),
          across(all_of(input$kmeans_vars), mean, na.rm = TRUE),
          .groups = "drop"
        )

      datatable(
        summary_df,
        options = list(pageLength = 10),
        rownames = FALSE
      ) %>% formatRound(input$kmeans_vars, 2)
    })

    # INTERPRETATION
    output$kmeans_interpretation <- renderUI({
      summary_df <- cluster_df %>%
        group_by(cluster) %>%
        summarise(
          across(all_of(input$kmeans_vars), mean, na.rm = TRUE),
          .groups = "drop"
        )

      # Identify highest-risk cluster using first selected variable
      risk_var <- input$kmeans_vars[1]

      high_cluster <- summary_df %>%
        arrange(desc(.data[[risk_var]])) %>%
        slice(1)

      HTML(paste0(
        "<h4>Cluster Interpretation</h4>",
        "<p>",
        "Cluster <strong>", high_cluster$cluster, "</strong> shows the highest average ",
        "<strong>", risk_var, "</strong>, indicating a distinct risk profile based on the selected indicators.",
        "</p>",
        "<p>",
        "K-Means clustering groups counties with similar structural food insecurity characteristics to support segmentation and targeted policy analysis.",
        "</p>"
      ))
    })
  })

  # ============================================================================
  # GROUP COMPARISON
  # ============================================================================

  observeEvent(input$run_group_comparison, {
    req(input$group_var, input$group_target)

    df <- data()

    # build group
    df$grp <- switch(input$group_var,
      "Census Region" = df$census_region,
      "Census Division" = df$census_division,
      "Rural/Urban" = df$urban_rural,
      "Poverty Category" = df$poverty_category,
      "Income Category" = df$income_category,
      "FI Category" = df$fi_category
    )

    target_var <- input$group_target
    df <- df %>% drop_na(grp, .data[[target_var]])

    output$group_comp_plot <- renderPlot({
      ggplot(df, aes(grp, .data[[target_var]], fill = grp)) +
        geom_boxplot(alpha = 0.7) +
        stat_summary(fun = mean, geom = "point", shape = 23, fill = "white") +
        theme(
          legend.position = "none",
          axis.text.x = element_text(angle = 45, hjust = 1)
        )
    })

    output$group_stats <- renderPrint({
      if (n_distinct(df$grp) == 2) {
        print(t.test(df[[target_var]] ~ df$grp))
      } else {
        print(summary(aov(df[[target_var]] ~ df$grp)))
      }
    })

    output$group_means_table <- renderDT({
      datatable(
        df %>%
          group_by(grp) %>%
          summarise(
            n = n(),
            mean = mean(.data[[target_var]]),
            sd = sd(.data[[target_var]]),
            median = median(.data[[target_var]])
          )
      )
    })

    output$group_effect_size <- renderPrint({
      cat("Effect size calculated depending on number of groups.")
    })

    output$group_distribution_plot <- renderPlot({
      ggplot(df, aes(grp, .data[[target_var]], fill = grp)) +
        geom_violin(alpha = 0.4) +
        geom_boxplot(width = 0.2) +
        theme(
          legend.position = "none",
          axis.text.x = element_text(angle = 45, hjust = 1)
        )
    })

    output$group_interpretation <- renderUI({
      HTML("<p>Group comparison highlights differences across selected categories.</p>")
    })
  })
}
