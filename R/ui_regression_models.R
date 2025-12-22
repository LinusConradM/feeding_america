# ==============================================================================
# UI MODULE: REGRESSION MODELS - DYNAMIC UI BY MODEL TYPE
# ==============================================================================
# Each model type shows its own appropriate metrics and visualizations
# ==============================================================================

ui_regression_models <- tabPanel(
  "Regression Models",
  value = "regression",
  
  fluidPage(
    # Page Header
    fluidRow(
      column(
        12,
        h2(
          icon("chart-line"), " Regression Models",
          style = "color: #2c3e50; font-weight: 600; margin-bottom: 10px;"
        ),
        p(
          "Build predictive models with dynamic metrics for each model type",
          style = "color: #6c757d; font-size: 16px; margin-bottom: 30px;"
        )
      )
    ),
    
    # ========================================================================
    # MODEL CONFIGURATION (ALWAYS VISIBLE)
    # ========================================================================
    fluidRow(
      column(
        12,
        div(
          style = "background: white; padding: 20px; border-radius: 10px; 
                   box-shadow: 0 2px 8px rgba(0,0,0,0.08);",
          h4("Model Configuration", style = "margin-top: 0; color: #0033A0;"),
          
          fluidRow(
            column(
              6,
              # Dependent Variable
              selectInput(
                "reg_dependent",
                label = tags$b("Dependent Variable (Y):"),
                choices = c(
                  "Food Insecurity Rate" = "overall_food_insecurity_rate",
                  "Child Food Insecurity Rate" = "child_food_insecurity_rate"
                ),
                selected = "overall_food_insecurity_rate"
              )
            ),
            
            column(
              6,
              # Year
              sliderInput(
                "reg_year",
                label = tags$b("Year:"),
                min = 2009,
                max = 2023,
                value = 2023,
                step = 1,
                sep = "",
                width = "100%"
              )
            )
          ),
          
          hr(style = "margin: 20px 0;"),
          
          # Hidden input for model type (set by JavaScript submenu)
          tags$input(
            id = "reg_model_type",
            type = "text",
            value = "linear",
            style = "display: none;"
          ),
          
          # Current model type display
          uiOutput("current_model_display"),
          
          # Independent Variables
          selectInput(
            "reg_independent",
            label = tags$b("Independent Variables (X):"),
            choices = NULL,
            selected = NULL,
            multiple = TRUE,
            selectize = TRUE,
            width = "100%"
          ),
          
          tags$p(
            "Select one or more predictors (type to search). Model type is selected from the Analysis menu.",
            style = "color: #6c757d; font-size: 13px; margin-top: -10px; margin-bottom: 15px;"
          ),
          
          # Scale Variables
          checkboxInput(
            "reg_scale",
            label = "Scale variables (standardize)",
            value = FALSE
          ),
          
          tags$p(
            icon("info-circle"), " Scaling converts all variables to z-scores (mean=0, SD=1)",
            style = "color: #6c757d; font-size: 11px; margin-top: -10px;"
          ),
          
          hr(style = "margin: 20px 0;"),
          
          # Build Model Button
          actionButton(
            "build_model",
            label = "Build Model",
            icon = icon("cogs"),
            style = "width: 100%; background: #0033A0; color: white; border: none; 
                     padding: 12px; font-weight: 600; border-radius: 8px;
                     font-size: 16px; margin-top: 10px;"
          )
        )
      )
    ),
    
    # ========================================================================
    # MODEL EQUATION & SUMMARY (ALWAYS VISIBLE)
    # ========================================================================
    fluidRow(
      style = "margin-top: 20px;",
      column(12,
        div(style = "background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); margin-bottom: 20px;",
          h4(icon("calculator"), " Model Equation", style = "margin-top: 0; color: #2c3e50;"),
          uiOutput("model_equation")
        ),
        div(style = "background: white; padding: 25px; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); margin-bottom: 20px;",
          h4(icon("table"), " Model Summary", style = "margin-top: 0; color: #2c3e50;"),
          verbatimTextOutput("model_summary")
        )
      )
    ),
    
    # ========================================================================
    # DYNAMIC METRICS SECTIONS (CONDITIONAL ON MODEL TYPE)
    # ========================================================================
    
    # BASIC REGRESSION METRICS (Linear, Polynomial)
    conditionalPanel(
      condition = "input.reg_model_type == 'linear' || input.reg_model_type == 'poly2' || input.reg_model_type == 'poly3'",
      
      h3("Basic Regression Metrics", style = "color: #2c3e50; margin-top: 30px; margin-bottom: 20px;"),
      
      # Core Metrics Row
      fluidRow(
        column(3, div(style = "background: linear-gradient(135deg, #0033A0 0%, #003D82 100%); padding: 25px; border-radius: 10px; color: white; box-shadow: 0 4px 15px rgba(0, 51, 160, 0.3);",
          div(icon("bullseye", style = "font-size: 2.5em; margin-bottom: 10px;")),
          h5("R²", style = "margin: 10px 0 5px 0;"),
          h3(textOutput("model_r2"), style = "margin: 0; font-size: 36px;"),
          p("Variance explained", style = "margin-top: 10px; font-size: 13px; opacity: 0.9;")
        )),
        column(3, div(style = "background: linear-gradient(135deg, #28a745 0%, #20c997 100%); padding: 25px; border-radius: 10px; color: white; box-shadow: 0 4px 15px rgba(40, 167, 69, 0.3);",
          div(icon("balance-scale", style = "font-size: 2.5em; margin-bottom: 10px;")),
          h5("Adj. R²", style = "margin: 10px 0 5px 0;"),
          h3(textOutput("model_adj_r2"), style = "margin: 0; font-size: 36px;"),
          p("Adjusted for predictors", style = "margin-top: 10px; font-size: 13px; opacity: 0.9;")
        )),
        column(3, div(style = "background: linear-gradient(135deg, #ffc107 0%, #ff9800 100%); padding: 25px; border-radius: 10px; color: white; box-shadow: 0 4px 15px rgba(255, 193, 7, 0.3);",
          div(icon("chart-bar", style = "font-size: 2.5em; margin-bottom: 10px;")),
          h5("F-Statistic", style = "margin: 10px 0 5px 0;"),
          h3(textOutput("model_fstat"), style = "margin: 0; font-size: 36px;"),
          p("Model significance", style = "margin-top: 10px; font-size: 13px; opacity: 0.9;")
        )),
        column(3, div(style = "background: linear-gradient(135deg, #6f42c1 0%, #563d7c 100%); padding: 25px; border-radius: 10px; color: white; box-shadow: 0 4px 15px rgba(111, 66, 193, 0.3);",
          div(icon("database", style = "font-size: 2.5em; margin-bottom: 10px;")),
          h5("Observations", style = "margin: 10px 0 5px 0;"),
          h3(textOutput("model_n"), style = "margin: 0; font-size: 36px;"),
          p("Sample size", style = "margin-top: 10px; font-size: 13px; opacity: 0.9;")
        ))
      ),
      
      # Error Metrics Row
      fluidRow(style = "margin-top: 20px;",
        column(4, div(style = "background: linear-gradient(135deg, #dc3545 0%, #c82333 100%); padding: 25px; border-radius: 10px; color: white; box-shadow: 0 4px 15px rgba(220, 53, 69, 0.3);",
          div(icon("exclamation-circle", style = "font-size: 2.5em; margin-bottom: 10px;")),
          h5("RMSE", style = "margin: 10px 0 5px 0;"),
          h3(textOutput("model_rmse"), style = "margin: 0; font-size: 36px;"),
          p("Root Mean Squared Error", style = "margin-top: 10px; font-size: 13px; opacity: 0.9;")
        )),
        column(4, div(style = "background: linear-gradient(135deg, #17a2b8 0%, #138496 100%); padding: 25px; border-radius: 10px; color: white; box-shadow: 0 4px 15px rgba(23, 162, 184, 0.3);",
          div(icon("ruler", style = "font-size: 2.5em; margin-bottom: 10px;")),
          h5("MAE", style = "margin: 10px 0 5px 0;"),
          h3(textOutput("model_mae"), style = "margin: 0; font-size: 36px;"),
          p("Mean Absolute Error", style = "margin-top: 10px; font-size: 13px; opacity: 0.9;")
        )),
        column(4, div(style = "background: linear-gradient(135deg, #fd7e14 0%, #e8590c 100%); padding: 25px; border-radius: 10px; color: white; box-shadow: 0 4px 15px rgba(253, 126, 20, 0.3);",
          div(icon("percentage", style = "font-size: 2.5em; margin-bottom: 10px;")),
          h5("MAPE", style = "margin: 10px 0 5px 0;"),
          h3(textOutput("model_mape"), style = "margin: 0; font-size: 36px;"),
          p("Mean Absolute % Error", style = "margin-top: 10px; font-size: 13px; opacity: 0.9;")
        ))
      ),
      
      # Multicollinearity Row
      fluidRow(style = "margin-top: 20px;",
        column(6, div(style = "background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%); padding: 25px; border-radius: 10px; color: white; box-shadow: 0 4px 15px rgba(231, 76, 60, 0.3);",
          div(icon("exclamation-triangle", style = "font-size: 2.5em; margin-bottom: 10px;")),
          h5("Condition Index", style = "margin: 10px 0 5px 0;"),
          h3(textOutput("model_condition_index"), style = "margin: 0; font-size: 36px;"),
          p("Multicollinearity indicator", style = "margin-top: 10px; font-size: 13px; opacity: 0.9;"),
          p(HTML("<small>< 10: Good | 10-30: Moderate | > 30: Severe</small>"), style = "margin-top: 5px; font-size: 11px; opacity: 0.8;")
        )),
        column(6, div(style = "background: linear-gradient(135deg, #9b59b6 0%, #8e44ad 100%); padding: 25px; border-radius: 10px; color: white; box-shadow: 0 4px 15px rgba(155, 89, 182, 0.3);",
          div(icon("code-branch", style = "font-size: 2.5em; margin-bottom: 10px;")),
          h5("Max VIF", style = "margin: 10px 0 5px 0;"),
          h3(textOutput("model_max_vif"), style = "margin: 0; font-size: 36px;"),
          p("Variance inflation factor", style = "margin-top: 10px; font-size: 13px; opacity: 0.9;"),
          p(HTML("<small>< 5: Good | 5-10: Moderate | > 10: High</small>"), style = "margin-top: 5px; font-size: 11px; opacity: 0.8;")
        ))
      )
    ),
    
    # REGULARIZED REGRESSION METRICS (Ridge, LASSO, Elastic Net)
    conditionalPanel(
      condition = "input.reg_model_type == 'ridge' || input.reg_model_type == 'lasso' || input.reg_model_type == 'elasticnet'",
      
      h3("Regularized Regression Metrics", style = "color: #2c3e50; margin-top: 30px; margin-bottom: 20px;"),
      
      # Row 1: R² Metrics
      fluidRow(
        column(3, div(style = "background: linear-gradient(135deg, #0033A0 0%, #003D82 100%); padding: 25px; border-radius: 10px; color: white; box-shadow: 0 4px 15px rgba(0, 51, 160, 0.3);",
          div(icon("bullseye", style = "font-size: 2.5em; margin-bottom: 10px;")),
          h5("Training R²", style = "margin: 10px 0 5px 0;"),
          h3(textOutput("reg_r2"), style = "margin: 0; font-size: 36px;"),
          p("Model fit on training data", style = "margin-top: 10px; font-size: 13px; opacity: 0.9;")
        )),
        column(3, div(style = "background: linear-gradient(135deg, #28a745 0%, #20c997 100%); padding: 25px; border-radius: 10px; color: white; box-shadow: 0 4px 15px rgba(40, 167, 69, 0.3);",
          div(icon("check-circle", style = "font-size: 2.5em; margin-bottom: 10px;")),
          h5("CV R²", style = "margin: 10px 0 5px 0;"),
          h3(textOutput("reg_cv_r2"), style = "margin: 0; font-size: 36px;"),
          p("10-Fold cross-validated R²", style = "margin-top: 10px; font-size: 13px; opacity: 0.9;")
        )),
        column(3, div(style = "background: linear-gradient(135deg, #17a2b8 0%, #138496 100%); padding: 25px; border-radius: 10px; color: white; box-shadow: 0 4px 15px rgba(23, 162, 184, 0.3);",
          div(icon("percentage", style = "font-size: 2.5em; margin-bottom: 10px;")),
          h5("Deviance Ratio", style = "margin: 10px 0 5px 0;"),
          h3(textOutput("reg_deviance_ratio"), style = "margin: 0; font-size: 36px;"),
          p("Proportion of null deviance explained", style = "margin-top: 10px; font-size: 13px; opacity: 0.9;")
        )),
        column(3, div(style = "background: linear-gradient(135deg, #6f42c1 0%, #563d7c 100%); padding: 25px; border-radius: 10px; color: white; box-shadow: 0 4px 15px rgba(111, 66, 193, 0.3);",
          div(icon("database", style = "font-size: 2.5em; margin-bottom: 10px;")),
          h5("Observations", style = "margin: 10px 0 5px 0;"),
          h3(textOutput("reg_n_obs"), style = "margin: 0; font-size: 36px;"),
          p("Sample size", style = "margin-top: 10px; font-size: 13px; opacity: 0.9;")
        ))
      ),
      
      # Row 2: Lambda Metrics
      fluidRow(style = "margin-top: 20px;",
        column(3, div(style = "background: linear-gradient(135deg, #ffc107 0%, #ff9800 100%); padding: 25px; border-radius: 10px; color: white; box-shadow: 0 4px 15px rgba(255, 193, 7, 0.3);",
          div(icon("sliders-h", style = "font-size: 2.5em; margin-bottom: 10px;")),
          h5("Lambda (Optimal)", style = "margin: 10px 0 5px 0;"),
          h3(textOutput("reg_lambda"), style = "margin: 0; font-size: 28px;"),
          p("Minimum CV error", style = "margin-top: 10px; font-size: 13px; opacity: 0.9;")
        )),
        column(3, div(style = "background: linear-gradient(135deg, #fd7e14 0%, #e8590c 100%); padding: 25px; border-radius: 10px; color: white; box-shadow: 0 4px 15px rgba(253, 126, 20, 0.3);",
          div(icon("plus-minus", style = "font-size: 2.5em; margin-bottom: 10px;")),
          h5("Lambda 1-SE", style = "margin: 10px 0 5px 0;"),
          h3(textOutput("reg_lambda_1se"), style = "margin: 0; font-size: 28px;"),
          p("Within 1 SE of minimum", style = "margin-top: 10px; font-size: 13px; opacity: 0.9;")
        )),
        column(3, div(style = "background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%); padding: 25px; border-radius: 10px; color: white; box-shadow: 0 4px 15px rgba(231, 76, 60, 0.3);",
          div(icon("compress-arrows-alt", style = "font-size: 2.5em; margin-bottom: 10px;")),
          h5("L2 Norm", style = "margin: 10px 0 5px 0;"),
          h3(textOutput("reg_l2_norm"), style = "margin: 0; font-size: 36px;"),
          p("√(Σ coefficients²)", style = "margin-top: 10px; font-size: 13px; opacity: 0.9;")
        )),
        column(3, div(style = "background: linear-gradient(135deg, #9b59b6 0%, #8e44ad 100%); padding: 25px; border-radius: 10px; color: white; box-shadow: 0 4px 15px rgba(155, 89, 182, 0.3);",
          div(icon("filter", style = "font-size: 2.5em; margin-bottom: 10px;")),
          h5("Coefficients", style = "margin: 10px 0 5px 0;"),
          h3(textOutput("reg_nonzero"), style = "margin: 0; font-size: 36px;"),
          p("Variables retained", style = "margin-top: 10px; font-size: 13px; opacity: 0.9;")
        ))
      ),
      
      # Row 3: Error Metrics
      fluidRow(style = "margin-top: 20px;",
        column(3, div(style = "background: linear-gradient(135deg, #dc3545 0%, #c82333 100%); padding: 25px; border-radius: 10px; color: white; box-shadow: 0 4px 15px rgba(220, 53, 69, 0.3);",
          div(icon("exclamation-circle", style = "font-size: 2.5em; margin-bottom: 10px;")),
          h5("Training RMSE", style = "margin: 10px 0 5px 0;"),
          h3(textOutput("reg_train_rmse"), style = "margin: 0; font-size: 36px;"),
          p("Training set error", style = "margin-top: 10px; font-size: 13px; opacity: 0.9;")
        )),
        column(3, div(style = "background: linear-gradient(135deg, #c0392b 0%, #a93226 100%); padding: 25px; border-radius: 10px; color: white; box-shadow: 0 4px 15px rgba(192, 57, 43, 0.3);",
          div(icon("chart-line", style = "font-size: 2.5em; margin-bottom: 10px;")),
          h5("CV RMSE", style = "margin: 10px 0 5px 0;"),
          h3(textOutput("reg_cv_rmse"), style = "margin: 0; font-size: 36px;"),
          p("10-Fold CV error", style = "margin-top: 10px; font-size: 13px; opacity: 0.9;")
        )),
        column(3, div(style = "background: linear-gradient(135deg, #34495e 0%, #2c3e50 100%); padding: 25px; border-radius: 10px; color: white; box-shadow: 0 4px 15px rgba(52, 73, 94, 0.3);",
          div(icon("ruler", style = "font-size: 2.5em; margin-bottom: 10px;")),
          h5("Training MAE", style = "margin: 10px 0 5px 0;"),
          h3(textOutput("reg_train_mae"), style = "margin: 0; font-size: 36px;"),
          p("Mean absolute error", style = "margin-top: 10px; font-size: 13px; opacity: 0.9;")
        )),
        column(3, div(style = "background: linear-gradient(135deg, #16a085 0%, #138d75 100%); padding: 25px; border-radius: 10px; color: white; box-shadow: 0 4px 15px rgba(22, 160, 133, 0.3);",
          div(icon("layer-group", style = "font-size: 2.5em; margin-bottom: 10px;")),
          h5("CV Folds", style = "margin: 10px 0 5px 0;"),
          h3(textOutput("reg_cv_folds"), style = "margin: 0; font-size: 36px;"),
          p("Cross-validation folds", style = "margin-top: 10px; font-size: 13px; opacity: 0.9;")
        ))
      ),
      
      # Ridge-specific visualizations
      fluidRow(style = "margin-top: 20px;",
        column(6, div(style = "background: white; padding: 25px; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.08);",
          h4(icon("chart-line"), " Lambda Path: Coefficient Shrinkage", style = "margin-top: 0; color: #2c3e50;"),
          p("How coefficients shrink as lambda increases", style = "color: #6c757d; margin-bottom: 15px; font-size: 13px;"),
          plotOutput("lambda_path_plot", height = "350px")
        )),
        column(6, div(style = "background: white; padding: 25px; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.08);",
          h4(icon("bullseye"), " Cross-Validation Error vs Lambda", style = "margin-top: 0; color: #2c3e50;"),
          p("Finding optimal lambda via 10-fold CV", style = "color: #6c757d; margin-bottom: 15px; font-size: 13px;"),
          plotOutput("cv_lambda_plot", height = "350px")
        ))
      )
    ),
    
    # CLASSIFICATION METRICS (Logistic, RF Class, XGB Class, LDA)
    conditionalPanel(
      condition = "input.reg_model_type == 'logistic_binary' || input.reg_model_type == 'logistic_multi' || input.reg_model_type == 'random_forest_class' || input.reg_model_type == 'xgboost_class' || input.reg_model_type == 'lda'",
      
      h3("Classification Metrics", style = "color: #2c3e50; margin-top: 30px; margin-bottom: 20px;"),
      
      fluidRow(
        column(3, div(style = "background: linear-gradient(135deg, #0033A0 0%, #003D82 100%); padding: 25px; border-radius: 10px; color: white; box-shadow: 0 4px 15px rgba(0, 51, 160, 0.3);",
          div(icon("check-circle", style = "font-size: 2.5em; margin-bottom: 10px;")),
          h5("Accuracy", style = "margin: 10px 0 5px 0;"),
          h3(textOutput("class_accuracy"), style = "margin: 0; font-size: 36px;"),
          p("Correct predictions", style = "margin-top: 10px; font-size: 13px; opacity: 0.9;")
        )),
        column(3, div(style = "background: linear-gradient(135deg, #28a745 0%, #20c997 100%); padding: 25px; border-radius: 10px; color: white; box-shadow: 0 4px 15px rgba(40, 167, 69, 0.3);",
          div(icon("crosshairs", style = "font-size: 2.5em; margin-bottom: 10px;")),
          h5("Precision", style = "margin: 10px 0 5px 0;"),
          h3(textOutput("class_precision"), style = "margin: 0; font-size: 36px;"),
          p("True positives rate", style = "margin-top: 10px; font-size: 13px; opacity: 0.9;")
        )),
        column(3, div(style = "background: linear-gradient(135deg, #ffc107 0%, #ff9800 100%); padding: 25px; border-radius: 10px; color: white; box-shadow: 0 4px 15px rgba(255, 193, 7, 0.3);",
          div(icon("search-plus", style = "font-size: 2.5em; margin-bottom: 10px;")),
          h5("Recall", style = "margin: 10px 0 5px 0;"),
          h3(textOutput("class_recall"), style = "margin: 0; font-size: 36px;"),
          p("Sensitivity", style = "margin-top: 10px; font-size: 13px; opacity: 0.9;")
        )),
        column(3, div(style = "background: linear-gradient(135deg, #6f42c1 0%, #563d7c 100%); padding: 25px; border-radius: 10px; color: white; box-shadow: 0 4px 15px rgba(111, 66, 193, 0.3);",
          div(icon("balance-scale", style = "font-size: 2.5em; margin-bottom: 10px;")),
          h5("F1 Score", style = "margin: 10px 0 5px 0;"),
          h3(textOutput("class_f1"), style = "margin: 0; font-size: 36px;"),
          p("Harmonic mean", style = "margin-top: 10px; font-size: 13px; opacity: 0.9;")
        ))
      ),
      
      fluidRow(style = "margin-top: 20px;",
        column(6, div(style = "background: white; padding: 25px; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.08);",
          h4(icon("table"), " Confusion Matrix", style = "margin-top: 0; color: #2c3e50;"),
          plotOutput("confusion_matrix", height = "300px")
        )),
        column(6, div(style = "background: white; padding: 25px; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.08);",
          h4(icon("chart-line"), " ROC Curve", style = "margin-top: 0; color: #2c3e50;"),
          plotOutput("roc_curve", height = "300px"),
          h5(textOutput("class_auc"), style = "text-align: center; color: #0033A0; margin-top: 10px;")
        ))
      )
    ),
    
    # QUANTILE REGRESSION METRICS
    conditionalPanel(
      condition = "input.reg_model_type == 'quantile_50' || input.reg_model_type == 'quantile_75'",
      
      h3("Quantile Regression Metrics", style = "color: #2c3e50; margin-top: 30px; margin-bottom: 20px;"),
      
      fluidRow(
        column(4, div(style = "background: linear-gradient(135deg, #0033A0 0%, #003D82 100%); padding: 25px; border-radius: 10px; color: white; box-shadow: 0 4px 15px rgba(0, 51, 160, 0.3);",
          div(icon("percentage", style = "font-size: 2.5em; margin-bottom: 10px;")),
          h5("Quantile", style = "margin: 10px 0 5px 0;"),
          h3(textOutput("quant_tau"), style = "margin: 0; font-size: 36px;"),
          p("Target quantile", style = "margin-top: 10px; font-size: 13px; opacity: 0.9;")
        )),
        column(4, div(style = "background: linear-gradient(135deg, #28a745 0%, #20c997 100%); padding: 25px; border-radius: 10px; color: white; box-shadow: 0 4px 15px rgba(40, 167, 69, 0.3);",
          div(icon("bullseye", style = "font-size: 2.5em; margin-bottom: 10px;")),
          h5("Pseudo R²", style = "margin: 10px 0 5px 0;"),
          h3(textOutput("quant_pseudo_r2"), style = "margin: 0; font-size: 36px;"),
          p("Goodness of fit", style = "margin-top: 10px; font-size: 13px; opacity: 0.9;")
        )),
        column(4, div(style = "background: linear-gradient(135deg, #ffc107 0%, #ff9800 100%); padding: 25px; border-radius: 10px; color: white; box-shadow: 0 4px 15px rgba(255, 193, 7, 0.3);",
          div(icon("ruler", style = "font-size: 2.5em; margin-bottom: 10px;")),
          h5("MAD", style = "margin: 10px 0 5px 0;"),
          h3(textOutput("quant_mad"), style = "margin: 0; font-size: 36px;"),
          p("Median Absolute Deviation", style = "margin-top: 10px; font-size: 13px; opacity: 0.9;")
        ))
      )
    ),
    
    # ========================================================================
    # VISUALIZATIONS (ALWAYS VISIBLE)
    # ========================================================================
    
    fluidRow(style = "margin-top: 20px;",
      column(12,
        div(style = "background: white; padding: 25px; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.08);",
          h4(icon("chart-area"), " Fitted vs. Actual Values", style = "margin-top: 0; color: #2c3e50;"),
          plotOutput("fitted_vs_actual", height = "400px")
        )
      )
    ),
    
    # Coefficients
    fluidRow(style = "margin-top: 20px;",
      column(12, div(style = "background: white; padding: 25px; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.08);",
        h4(icon("list-ol"), " Coefficient Interpretations", style = "margin-top: 0; color: #2c3e50; margin-bottom: 20px;"),
        uiOutput("coefficient_cards")
      ))
    ),
    
    # Diagnostics (only for regression models)
    conditionalPanel(
      condition = "input.reg_model_type == 'linear' || input.reg_model_type == 'poly2' || input.reg_model_type == 'poly3' || input.reg_model_type == 'ridge' || input.reg_model_type == 'lasso' || input.reg_model_type == 'elasticnet'",
      
      fluidRow(style = "margin-top: 20px;",
        column(6, div(style = "background: white; padding: 25px; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.08);",
          h4(icon("chart-area"), " Residuals vs. Fitted", style = "margin-top: 0; color: #2c3e50;"),
          p("Check for homoscedasticity (constant variance)", style = "color: #6c757d; margin-bottom: 15px; font-size: 13px;"),
          plotOutput("residuals_fitted", height = "350px")
        )),
        column(6, div(style = "background: white; padding: 25px; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.08);",
          h4(icon("chart-line"), " Normal Q-Q Plot", style = "margin-top: 0; color: #2c3e50;"),
          p("Check for normality of residuals", style = "color: #6c757d; margin-bottom: 15px; font-size: 13px;"),
          plotOutput("qq_plot", height = "350px")
        ))
      )
    ),
    
    # AI Interpretation
    fluidRow(style = "margin-top: 20px; margin-bottom: 30px;",
      column(12, div(style = "background: linear-gradient(135deg, #6c5ce7 0%, #a29bfe 100%); padding: 30px; border-radius: 10px; color: white; box-shadow: 0 4px 15px rgba(108, 92, 231, 0.3);",
        div(style = "display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; flex-wrap: wrap;",
          h3(icon("brain"), " AI Model Interpretation", style = "margin: 0; font-weight: 600;"),
          actionButton("generate_model_interpretation", label = "Generate AI Analysis", icon = icon("magic"),
            style = "background: rgba(255,255,255,0.2); color: white; border: 2px solid white; padding: 10px 20px; font-weight: 600; border-radius: 8px; margin-top: 10px;")
        ),
        htmlOutput("model_ai_interpretation")
      ))
    )
  )
)