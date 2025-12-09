# ==============================================================================
# UI MODULE: ANALYSIS TAB
# ==============================================================================
# PURPOSE: Interactive statistical modeling (required for DATA-613)
# FEATURES: 7 analysis types, dynamic variable selection, visual results
# TEAM: Conrad, Sharon, Ryann, Alex
# ==============================================================================
ui_analysis <- tabPanel(
  "Analysis",
  fluidPage(
    titlePanel("Statistical Analysis"),
    sidebarLayout(
      ############################
      # SIDEBAR
      ############################
      sidebarPanel(
        width = 3,
        radioButtons(
          "analysis_type",
          "Select Analysis Type:",
          choices = c(
            "Correlation Analysis" = "correlation",
            "Regression Analysis" = "regression",
            "Multinomial Logistic Regression" = "multinomial",
            "Decision Tree" = "decision_tree",
            "Principal Component Analysis" = "pca",
            "K-Means Clustering" = "kmeans",
            "Group Comparison" = "group_comparison"
          ),
          selected = "correlation"
        ),
        hr(),

        # ==================================================================
        # CORRELATION INPUTS
        # ==================================================================
        conditionalPanel(
          condition = "input.analysis_type == 'correlation'",
          h4("Correlation Analysis"),
          selectInput("corr_vars", "Select Variables (2 or more):", choices = NULL, multiple = TRUE),
          actionButton("run_correlation", "Run Correlation Analysis", class = "btn-primary btn-block")
        ),

        # ==================================================================
        # LINEAR REGRESSION INPUTS
        # ==================================================================
        conditionalPanel(
          condition = "input.analysis_type == 'regression'",
          h4("Regression Analysis"),
          selectInput("reg_dependent", "Dependent Variable (Y):", choices = NULL),
          selectInput("reg_independent", "Independent Variables (X):", choices = NULL, multiple = TRUE),
          actionButton("run_regression", "Run Regression Analysis", class = "btn-primary btn-block")
        ),

        # ==================================================================
        # MULTINOMIAL REGRESSION INPUTS
        # ==================================================================
        conditionalPanel(
          condition = "input.analysis_type == 'multinomial'",
          uiOutput("multinomial_ui")
        ),

        # ==================================================================
        # DECISION TREE INPUTS
        # ==================================================================
        conditionalPanel(
          condition = "input.analysis_type == 'decision_tree'",
          h4("Decision Tree"),
          selectInput("tree_target", "Target Variable:", choices = NULL),
          selectInput("tree_predictors", "Predictor Variables:", choices = NULL, multiple = TRUE),
          actionButton("run_tree", "Run Decision Tree", class = "btn-primary btn-block")
        ),

        # ==================================================================
        # PCA INPUTS
        # ==================================================================
        conditionalPanel(
          condition = "input.analysis_type == 'pca'",
          h4("Principal Component Analysis"),
          selectInput("pca_vars", "Variables for PCA:", choices = NULL, multiple = TRUE),
          checkboxInput("pca_scale", "Scale variables", TRUE),
          actionButton("run_pca", "Run PCA", class = "btn-primary btn-block")
        ),

        # ==================================================================
        # K-MEANS INPUTS
        # ==================================================================
        conditionalPanel(
          condition = "input.analysis_type == 'kmeans'",
          h4("K-Means Clustering"),
          selectInput("kmeans_vars", "Variables for Clustering:", choices = NULL, multiple = TRUE),
          numericInput("k_clusters", "Number of Clusters (k):", 4, min = 2),
          actionButton("run_kmeans", "Run K-Means", class = "btn-primary btn-block")
        ),

        # ==================================================================
        # GROUP COMPARISON INPUTS
        # ==================================================================
        conditionalPanel(
          condition = "input.analysis_type == 'group_comparison'",
          h4("Group Comparison"),
          selectInput(
            "group_var",
            "Grouping Variable:",
            choices = c(
              "Census Region" = "census_region",
              "Census Division" = "census_division",
              "Rural/Urban" = "urban_rural",
              "Poverty Category" = "poverty_category",
              "Income Category" = "income_category",
              "FI Category" = "fi_category"
            )
          ),
          selectInput("group_target", "Outcome Variable:", choices = NULL),
          actionButton("run_group_comparison", "Run Group Comparison", class = "btn-primary btn-block")
        )
      ),

      ############################
      # MAIN PANEL
      ############################
      mainPanel(
        width = 9,
        conditionalPanel(
          condition = "input.analysis_type=='correlation'",
          h3("Correlation Analysis Results"),
          tabsetPanel(
            tabPanel("Correlation Matrix", plotOutput("corr_plot", height = "600px")),
            tabPanel("Correlation Table", DT::DTOutput("corr_table")),
            tabPanel("Interpretation", uiOutput("corr_interpretation"))
          )
        ),
        conditionalPanel(
          condition = "input.analysis_type=='regression'",
          h3("Regression Analysis Results"),
          tabsetPanel(
            tabPanel("Model Summary", verbatimTextOutput("reg_summary")),
            tabPanel("Diagnostics", plotOutput("reg_diagnostics", height = "600px")),
            tabPanel("Predictions", plotOutput("reg_predictions", height = "500px")),
            tabPanel("Coefficients", plotOutput("reg_coefficients", height = "500px"))
          )
        ),
        conditionalPanel(
          condition = "input.analysis_type == 'multinomial'",
          h3("Multinomial Logistic Regression Results"),
          tabsetPanel(
            tabPanel("Model Summary", verbatimTextOutput("multi_summary")),
            tabPanel("Relative Risk Ratios", plotOutput("multi_rrr", height = "600px")),
            tabPanel("Classification Accuracy", verbatimTextOutput("multi_accuracy")),
            tabPanel("Interpretation", uiOutput("multi_interpretation"))
          )
        ),
        conditionalPanel(
          condition = "input.analysis_type=='decision_tree'",
          h3("Decision Tree Results"),
          tabsetPanel(
            tabPanel("Tree Plot", plotOutput("tree_plot", height = "600px")),
            tabPanel("Variable Importance", plotOutput("tree_importance", height = "500px")),

            # Binary classification tabs with conditional content
            tabPanel(
              "Confusion Matrix",
              conditionalPanel(
                condition = "output.is_tree_binary",
                tableOutput("tree_confusion")
              ),
              conditionalPanel(
                condition = "!output.is_tree_binary",
                div(
                  style = "padding: 20px; color: #666; font-style: italic;",
                  p("Confusion matrix is only available for binary classification trees.")
                )
              )
            ),
            tabPanel(
              "ROC Curve",
              conditionalPanel(
                condition = "output.is_tree_binary",
                plotOutput("tree_roc", height = "500px")
              ),
              conditionalPanel(
                condition = "!output.is_tree_binary",
                div(
                  style = "padding: 20px; color: #666; font-style: italic;",
                  p("ROC curve is only available for binary classification trees.")
                )
              )
            ),
            tabPanel(
              "AUC",
              conditionalPanel(
                condition = "output.is_tree_binary",
                verbatimTextOutput("tree_auc")
              ),
              conditionalPanel(
                condition = "!output.is_tree_binary",
                div(
                  style = "padding: 20px; color: #666; font-style: italic;",
                  p("AUC is only available for binary classification trees.")
                )
              )
            ),
            tabPanel("Interpretation", uiOutput("tree_interpretation")),
            tabPanel("Model Data", DT::DTOutput("tree_model_data"))
          )
        ),
        conditionalPanel(
          condition = "input.analysis_type=='pca'",
          h3("PCA Results"),
          tabsetPanel(
            tabPanel("Scree Plot", plotOutput("pca_scree")),
            tabPanel("Biplot", plotOutput("pca_biplot")),
            tabPanel("Loadings", DT::DTOutput("pca_loadings")),
            tabPanel("Interpretation", uiOutput("pca_interpretation"))
          )
        ),
        conditionalPanel(
          condition = "input.analysis_type=='kmeans'",
          h3("K-Means Results"),
          tabsetPanel(
            tabPanel("Cluster Plot", plotOutput("kmeans_plot", height = "600px")),
            tabPanel("Cluster Summary", DT::DTOutput("kmeans_summary")),
            tabPanel("Interpretation", uiOutput("kmeans_interpretation"))
          )
        ),
        conditionalPanel(
          condition = "input.analysis_type=='group_comparison'",
          h3("Group Comparison Results"),
          tabsetPanel(
            tabPanel("Visualization", plotOutput("group_comp_plot", height = "600px")),
            tabPanel("Statistical Test", verbatimTextOutput("group_stats")),
            tabPanel("Group Means", DT::DTOutput("group_means_table")),
            tabPanel("Effect Size", verbatimTextOutput("group_effect_size")),
            tabPanel("Distribution Plot", plotOutput("group_distribution_plot", height = "600px")),
            tabPanel("Interpretation", uiOutput("group_interpretation"))
          )
        )
      )
    )
  )
)
