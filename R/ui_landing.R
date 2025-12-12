# ==============================================================================
# UI MODULE: LANDING PAGE
# ==============================================================================
# PURPOSE: Orient users in <10 seconds, provide context
# FEATURES: Hero section, key facts, primary CTA
# TEAM: Conrad, Sharon, Ryann, Alex
# ==============================================================================

ui_landing <- tabPanel(
  "Home",
  value = "landing",
  
  fluidPage(
    style = "min-height: 80vh; display: flex; align-items: center;",
    
    fluidRow(
      column(
        12,
        div(
          style = "text-align: center; max-width: 900px; margin: 0 auto;",
          
          # Hero Title
          h1(
            "U.S. Food Insecurity Patterns (2009-2023)",
            style = "font-size: 48px; 
                     font-weight: 700; 
                     color: #2c3e50; 
                     margin-bottom: 20px;
                     line-height: 1.2;"
          ),
          
          # Subtitle
          p(
            "County-level insights for policy and decision-making",
            style = "font-size: 20px; 
                     color: #6c757d; 
                     margin-bottom: 50px;
                     font-weight: 300;"
          ),
          
          # Three Supporting Facts
          fluidRow(
            style = "margin-bottom: 60px;",
            
            column(
              4,
              div(
                style = "padding: 30px; background: #f8f9fa; border-radius: 8px;",
                h2("44.2M", style = "color: #dc3545; font-size: 36px; margin: 0;"),
                p("Americans experienced food insecurity in 2023", 
                  style = "color: #495057; margin-top: 10px; font-size: 15px;")
              )
            ),
            
            column(
              4,
              div(
                style = "padding: 30px; background: #f8f9fa; border-radius: 8px;",
                h2("3,156", style = "color: #667eea; font-size: 36px; margin: 0;"),
                p("U.S. counties analyzed across 15 years", 
                  style = "color: #495057; margin-top: 10px; font-size: 15px;")
              )
            ),
            
            column(
              4,
              div(
                style = "padding: 30px; background: #f8f9fa; border-radius: 8px;",
                h2("2-3x", style = "color: #ffc107; font-size: 36px; margin: 0;"),
                p("Higher rates in rural and southern counties", 
                  style = "color: #495057; margin-top: 10px; font-size: 15px;")
              )
            )
          ),
          
          # Primary CTA
          actionButton(
            "start_exploring",
            "Start Exploring",
#             icon removed for debugging
            style = "font-size: 18px; 
                     padding: 15px 50px; 
                     background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                     color: white; 
                     border: none; 
                     border-radius: 50px;
                     box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
                     transition: all 0.3s;
                     font-weight: 600;"
          ),
          
          # Data Source Badge
          div(
            style = "margin-top: 50px;",
            p(
              icon("database"), " Data: Feeding America & U.S. Census Bureau",
              style = "color: #6c757d; font-size: 14px;"
            )
          )
        )
      )
    )
  )
)
