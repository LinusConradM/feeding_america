# R/ui_analysis.R

ui_analysis <- tabPanel(
  "Analysis",

  sidebarLayout(

    # ===========================
    # LEFT SIDEBAR
    # ===========================
    sidebarPanel(

      # -------------------------------
      # MODEL TYPE SELECTION
      # -------------------------------
      selectInput(
        "model_type",
        "Select Analysis Type:",
        choices = c(
          "Correlation",
          "Regression",
          "Classification",
          "Random Forest",
          "Decision Tree",
          "Group Comparison"
        )
      ),

      # -------------------------------
      # GROUP COMPARISON CONTROLS
      # -------------------------------
      conditionalPanel(
        condition = "input.model_type == 'Group Comparison'",

        selectInput(
          "group_var",
          "Group Variable:",
          choices = c(
            "Census Region",
            "Census Division",
            "Rural/Urban",
            "Income Category (≤185% vs >185%)",
            "Race"
          )
        ),

        selectInput(
          "group_target",
          "Outcome Variable:",
          choices = NULL    # updated dynamically in server
        )
      ),

      # -------------------------------
      # REGRESSION, CLASSIFICATION, ML
      # -------------------------------
      conditionalPanel(
        condition = "input.model_type != 'Correlation' &&
                     input.model_type != 'Group Comparison'",

        # Target variable
        selectInput(
          "dep_var",
          "Target Variable:",
          choices = NULL
        ),

        # Predictor variables
        selectInput(
          "indep_vars",
          "Predictors:",
          choices = NULL,
          multiple = TRUE
        ),

        # Train/test split
        sliderInput(
          "train_split",
          "Train/Test Split (% for Training):",
          min = 50, max = 90,
          value = 70, step = 1
        )
      ),

      # -------------------------------
      # RUN BUTTON
      # -------------------------------
      actionButton(
        "run_model",
        "Run Analysis",
        class = "btn btn-primary btn-block"
      )
    ),

    # ===========================
    # RIGHT MAIN CONTENT AREA
    # ===========================
    mainPanel(
      tabsetPanel(
        id = "analysis_tabs",

        # -------------------------------
        # CORRELATION TAB
        # -------------------------------
        tabPanel(
          "Correlation",
          plotly::plotlyOutput("corr_plot")
        ),

        # -------------------------------
        # REGRESSION TAB
        # -------------------------------
        tabPanel(
          "Regression",
          verbatimTextOutput("reg_summary"),
          plotOutput("reg_plot"),
          tableOutput("reg_metrics")
        ),

        # -------------------------------
        # CLASSIFICATION TAB
        # -------------------------------
        tabPanel(
          "Classification",
          verbatimTextOutput("class_summary"),
          tableOutput("class_metrics"),
          plotOutput("roc_plot")
        ),

        # -------------------------------
        # RANDOM FOREST TAB
        # -------------------------------
        tabPanel(
          "Random Forest",
          verbatimTextOutput("rf_summary"),
          plotOutput("rf_importance")
        ),

        # -------------------------------
        # DECISION TREE TAB
        # -------------------------------
        tabPanel(
          "Decision Tree",
          plotOutput("tree_plot"),
          verbatimTextOutput("tree_summary")
        ),

        # -------------------------------
        # GROUP COMPARISON TAB
        # -------------------------------
        tabPanel(
          "Group Comparison",
          plotly::plotlyOutput("group_comp_plot"),
          verbatimTextOutput("group_stats")
        )
      )
    )
  )
)
