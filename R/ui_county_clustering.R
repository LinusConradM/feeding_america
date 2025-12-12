# ==============================================================================
# UI MODULE: COUNTY CLUSTERING & TYPOLOGY
# ==============================================================================
# PURPOSE: Segment counties into groups for targeted interventions
# CAPABILITIES: K-means, hierarchical clustering, radar charts, cluster maps
# TEAM: Conrad, Sharon, Ryann, Alex
# ==============================================================================

ui_county_clustering <- tabPanel(
  "County Clustering",
  value = "clustering",
  
  fluidPage(
    # Global Controls
    # global_controls_ui(),  # Removed to prevent duplicate IDs
    
    # Page Header
    fluidRow(
      column(
        12,
        h2(
          icon("object-group"), " County Clustering & Typology Tool",
          style = "color: #2c3e50; font-weight: 600; margin-bottom: 10px;"
        ),
        p(
          "Segment counties into similar groups for targeted policy interventions",
          style = "color: #6c757d; font-size: 16px; margin-bottom: 30px;"
        )
      )
    ),
    
    # ========================================================================
    # CLUSTERING CONFIGURATION
    # ========================================================================
    fluidRow(
      column(
        3,
        div(
          style = "background: white; padding: 25px; border-radius: 10px;
                   box-shadow: 0 2px 8px rgba(0,0,0,0.08);",
          h4("Clustering Setup", style = "margin-top: 0; color: #2c3e50;"),
          hr(),
          
          # Algorithm selection
          selectInput(
            "cluster_algorithm",
            "Algorithm:",
            choices = c(
              "K-Means" = "kmeans",
              "Hierarchical" = "hierarchical",
              "PAM (Medoids)" = "pam"
            ),
            selected = "kmeans"
          ),
          
          # Number of clusters
          sliderInput(
            "n_clusters",
            "Number of Clusters:",
            min = 2,
            max = 8,
            value = 4,
            step = 1
          ),
          
          hr(),
          
          # Feature selection
          checkboxGroupInput(
            "cluster_features",
            "Clustering Features:",
            choices = c(
              "Food Insecurity Rate" = "fi_rate",
              "Poverty Rate" = "poverty",
              "Median Income" = "income",
              "Unemployment Rate" = "unemployment",
              "Uninsured Rate" = "uninsured",
              "Education (College+)" = "education",
              "SNAP Participation" = "snap",
              "Rural Status" = "rural"
            ),
            selected = c("fi_rate", "poverty", "income", "unemployment")
          ),
          
          hr(),
          
          checkboxInput("standardize_vars", "Standardize Variables", TRUE),
          
          actionButton(
            "run_clustering",
            "Run Clustering",
#             icon removed for debugging
            style = "width: 100%; background: #0033A0; color: white; 
                     border: none; padding: 12px; font-weight: 600;"
          )
        )
      ),
      
      # ========================================================================
      # CLUSTER VISUALIZATION
      # ========================================================================
      column(
        9,
        div(
          style = "background: white; padding: 25px; border-radius: 10px;
                   box-shadow: 0 2px 8px rgba(0,0,0,0.08);",
          h4(
            icon("project-diagram"), " Cluster Visualization",
            style = "margin-top: 0; color: #2c3e50;"
          ),
          hr(),
          
          # Cluster map placeholder
          div(
            style = "height: 500px; display: flex; align-items: center; 
                     justify-content: center; background: #f8f9fa; 
                     border-radius: 8px; border: 2px dashed #dee2e6;",
            div(
              style = "text-align: center;",
              icon("map-marked-alt", style = "font-size: 60px; color: #0033A0; margin-bottom: 20px;"),
              h4("Geographic Cluster Map", 
                 style = "color: #495057; margin-bottom: 10px;"),
              p("Counties color-coded by cluster assignment",
                style = "color: #6c757d; margin-bottom: 20px;"),
              tags$div(
                tags$strong("Features:", style = "color: #0033A0;"),
                tags$ul(
                  style = "text-align: left; display: inline-block; color: #6c757d;",
                  tags$li("Each cluster shown in distinct color"),
                  tags$li("Click county to see cluster profile"),
                  tags$li("Hover for cluster membership info"),
                  tags$li("Export cluster assignments as CSV")
                )
              )
            )
          )
        )
      )
    ),
    
    # ========================================================================
    # CLUSTER PROFILES (RADAR CHARTS)
    # ========================================================================
    fluidRow(
      style = "margin-top: 30px;",
      column(
        12,
        div(
          style = "background: white; padding: 25px; border-radius: 10px;
                   box-shadow: 0 2px 8px rgba(0,0,0,0.08);",
          h4(
            icon("chart-area"), " Cluster Profiles (Radar Charts)",
            style = "margin-top: 0; color: #2c3e50;"
          ),
          p("Compare cluster characteristics across all features",
            style = "color: #6c757d; margin-bottom: 20px;"),
          hr(),
          
          # Radar charts placeholder
          div(
            style = "height: 400px; display: flex; align-items: center; 
                     justify-content: center; background: #f8f9fa; 
                     border-radius: 8px; border: 2px dashed #dee2e6;",
            div(
              style = "text-align: center;",
              icon("dot-circle", style = "font-size: 60px; color: #C41E3A; margin-bottom: 20px;"),
              h4("Multi-Dimensional Radar Charts", 
                 style = "color: #495057; margin-bottom: 10px;"),
              p("One radar chart per cluster showing mean values on all features",
                style = "color: #6c757d;")
            )
          )
        )
      )
    ),
    
    # ========================================================================
    # CLUSTER STATISTICS
    # ========================================================================
    fluidRow(
      style = "margin-top: 30px;",
      
      column(
        4,
        div(
          style = "background: linear-gradient(135deg, #0033A0 0%, #003D82 100%);
                   padding: 25px; border-radius: 10px; color: white;
                   box-shadow: 0 4px 15px rgba(0, 51, 160, 0.3);",
          div(icon("layer-group", style = "font-size: 2.5em; margin-bottom: 10px;")),
          h5("Total Clusters", style = "margin: 10px 0 5px 0;"),
          h3(textOutput("total_clusters"), style = "margin: 0; font-size: 48px;"),
          p("Groups identified", 
            style = "margin-top: 15px; font-size: 14px; opacity: 0.9;")
        )
      ),
      
      column(
        4,
        div(
          style = "background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
                   padding: 25px; border-radius: 10px; color: white;
                   box-shadow: 0 4px 15px rgba(40, 167, 69, 0.3);",
          div(icon("chart-bar", style = "font-size: 2.5em; margin-bottom: 10px;")),
          h5("Within-Cluster SS", style = "margin: 10px 0 5px 0;"),
          h3(textOutput("cluster_ss"), style = "margin: 0; font-size: 48px;"),
          p("Lower = tighter clusters", 
            style = "margin-top: 15px; font-size: 14px; opacity: 0.9;")
        )
      ),
      
      column(
        4,
        div(
          style = "background: linear-gradient(135deg, #ffc107 0%, #ff9800 100%);
                   padding: 25px; border-radius: 10px; color: white;
                   box-shadow: 0 4px 15px rgba(255, 193, 7, 0.3);",
          div(icon("percent", style = "font-size: 2.5em; margin-bottom: 10px;")),
          h5("Variance Explained", style = "margin: 10px 0 5px 0;"),
          h3(textOutput("cluster_variance"), style = "margin: 0; font-size: 48px;"),
          p("Between-cluster variance", 
            style = "margin-top: 15px; font-size: 14px; opacity: 0.9;")
        )
      )
    ),
    
    # ========================================================================
    # CLUSTER NAMING & INTERPRETATION
    # ========================================================================
    fluidRow(
      style = "margin-top: 30px;",
      column(
        12,
        div(
          style = "background: white; padding: 25px; border-radius: 10px;
                   box-shadow: 0 2px 8px rgba(0,0,0,0.08);",
          h4(
            icon("tag"), " Cluster Labels & Policy Profiles",
            style = "margin-top: 0; color: #2c3e50;"
          ),
          p("Use-case driven labels for each cluster based on characteristics",
            style = "color: #6c757d; margin-bottom: 20px;"),
          hr(),
          
          htmlOutput("cluster_interpretations")
        )
      )
    ),
    
    # ========================================================================
    # ELBOW PLOT (OPTIMAL K)
    # ========================================================================
    fluidRow(
      style = "margin-top: 30px;",
      column(
        6,
        div(
          style = "background: white; padding: 25px; border-radius: 10px;
                   box-shadow: 0 2px 8px rgba(0,0,0,0.08);",
          h4(
            icon("chart-line"), " Elbow Plot (Optimal K)",
            style = "margin-top: 0; color: #2c3e50;"
          ),
          hr(),
          
          # Elbow plot placeholder
          div(
            style = "height: 300px; display: flex; align-items: center; 
                     justify-content: center; background: #f8f9fa; 
                     border-radius: 8px; border: 2px dashed #dee2e6;",
            div(
              style = "text-align: center;",
              icon("chart-line", style = "font-size: 50px; color: #6f42c1; margin-bottom: 15px;"),
              h5("Within-Cluster SS by K", style = "color: #495057;"),
              p("Find the 'elbow' to choose optimal cluster count", 
                style = "color: #6c757d; font-size: 13px;")
            )
          )
        )
      ),
      
      column(
        6,
        div(
          style = "background: white; padding: 25px; border-radius: 10px;
                   box-shadow: 0 2px 8px rgba(0,0,0,0.08);",
          h4(
            icon("sitemap"), " Dendrogram (Hierarchical)",
            style = "margin-top: 0; color: #2c3e50;"
          ),
          hr(),
          
          # Dendrogram placeholder
          div(
            style = "height: 300px; display: flex; align-items: center; 
                     justify-content: center; background: #f8f9fa; 
                     border-radius: 8px; border: 2px dashed #dee2e6;",
            div(
              style = "text-align: center;",
              icon("project-diagram", style = "font-size: 50px; color: #17a2b8; margin-bottom: 15px;"),
              h5("Hierarchical Clustering Tree", style = "color: #495057;"),
              p("Shows how counties group together at different levels", 
                style = "color: #6c757d; font-size: 13px;")
            )
          )
        )
      )
    )
  )
)
