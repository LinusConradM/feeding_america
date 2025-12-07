# ==============================================================================
# UI: ANALYSIS MODULE
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
            "Correlation Analysis"        = "correlation",
            "Regression Analysis"         = "regression",
            "Logistic Regression"         = "logistic",
            "Decision Tree"               = "decision_tree",
            "Principal Component Analysis"= "pca",
            "K-Means Clustering"          = "kmeans",
            "Group Comparison"            = "group_comparison"
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
          selectInput("corr_vars","Select Variables (2 or more):",choices=NULL,multiple=TRUE),
          actionButton("run_correlation","Run Correlation Analysis",class="btn-primary btn-block")
        ),
        
        # ==================================================================
        # LINEAR REGRESSION INPUTS
        # ==================================================================
        conditionalPanel(
          condition = "input.analysis_type == 'regression'",
          h4("Regression Analysis"),
          selectInput("reg_dependent","Dependent Variable (Y):",choices=NULL),
          selectInput("reg_independent","Independent Variables (X):",choices=NULL,multiple=TRUE),
          actionButton("run_regression","Run Regression Analysis",class="btn-primary btn-block")
        ),
        
        # ==================================================================
        # LOGISTIC REGRESSION INPUTS
        # ==================================================================
        conditionalPanel(
          condition = "input.analysis_type == 'logistic'",
          h4("Logistic Regression"),
          selectInput("logit_dependent","Binary Outcome Variable:",choices=NULL),
          selectInput("logit_independent","Independent Variables (X):",choices=NULL,multiple=TRUE),
          actionButton("run_logistic","Run Logistic Regression",class="btn-primary btn-block")
        ),
        
        # ==================================================================
        # DECISION TREE INPUTS
        # ==================================================================
        conditionalPanel(
          condition = "input.analysis_type == 'decision_tree'",
          h4("Decision Tree"),
          selectInput("tree_target","Target Variable:",choices=NULL),
          selectInput("tree_predictors","Predictor Variables:",choices=NULL,multiple=TRUE),
          actionButton("run_tree","Run Decision Tree",class="btn-primary btn-block")
        ),
        
        # ==================================================================
        # PCA INPUTS
        # ==================================================================
        conditionalPanel(
          condition = "input.analysis_type == 'pca'",
          h4("Principal Component Analysis"),
          selectInput("pca_vars","Variables for PCA:",choices=NULL,multiple=TRUE),
          checkboxInput("pca_scale","Scale variables",TRUE),
          actionButton("run_pca","Run PCA",class="btn-primary btn-block")
        ),
        
        # ==================================================================
        # K-MEANS INPUTS
        # ==================================================================
        conditionalPanel(
          condition = "input.analysis_type == 'kmeans'",
          h4("K-Means Clustering"),
          selectInput("kmeans_vars","Variables for Clustering:",choices=NULL,multiple=TRUE),
          numericInput("k_clusters","Number of Clusters (k):",4,min=2),
          actionButton("run_kmeans","Run K-Means",class="btn-primary btn-block")
        ),
        
        # ==================================================================
        # ENHANCED GROUP COMPARISON INPUTS ✅
        # ==================================================================
        conditionalPanel(
          condition = "input.analysis_type == 'group_comparison'",
          
          h4("Group Comparison"),
          
          selectInput("group_var","Grouping Variable:",
                      choices=c("Census Region","Census Division","Rural/Urban",
                                "Poverty Category","Income Category","FI Category","Race")),
          
          selectInput("group_target","Outcome Variable:",choices=NULL),
          
          selectInput(
            "group_test",
            "Statistical Test:",
            choices = c(
              "Auto (Recommended)" = "auto",
              "t-test (2 groups)"  = "ttest",
              "ANOVA (3+ groups)"  = "anova",
              "Nonparametric"      = "nonparametric"
            ),
            selected = "auto"
          ),
          
          sliderInput(
            "group_conf_level",
            "Confidence Level:",
            min = 0.90,
            max = 0.99,
            value = 0.95,
            step = 0.01
          ),
          
          actionButton(
            "run_group_comparison",
            "Run Group Comparison",
            class="btn-primary btn-block"
          )
        )
      ),
      
      ############################
      # MAIN PANEL
      ############################
      mainPanel(
        width = 9,
        
        conditionalPanel(
          condition="input.analysis_type=='group_comparison'",
          
          h3("Group Comparison Results"),
          
          tabsetPanel(
            
            tabPanel(
              "Visualization",
              plotOutput("group_comp_plot",height="600px")
            ),
            
            tabPanel(
              "Summary Statistics",
              DT::DTOutput("group_summary")
            ),
            
            tabPanel(
              "Statistical Test",
              verbatimTextOutput("group_stats")
            ),
            
            tabPanel(
              "Effect Size",
              verbatimTextOutput("group_effect_size")
            ),
            
            tabPanel(
              "Interpretation",
              uiOutput("group_interpretation")
            )
          )
        )
      )
    )
  )
)
