# ==============================================================================
# GLOBAL CONTROLS COMPONENT
# ==============================================================================
# PURPOSE: Persistent controls across all tabs (except landing)
# TEAM: Conrad, Sharon, Ryann, Alex
# ==============================================================================

global_controls_ui <- function() {
  div(
    id = "global-controls",
    style = "background: white; 
             padding: 15px 20px; 
             border-bottom: 2px solid #e9ecef;
             box-shadow: 0 2px 4px rgba(0,0,0,0.05);
             margin-bottom: 30px;",
    
    fluidRow(
      column(
        3,
        selectInput(
          "global_year",
          "Year",
          choices = 2009:2023,
          selected = 2023,
          width = "100%"
        )
      ),
      column(
        4,
        selectInput(
          "global_geography",
          "Geography Level",
          choices = c("National", "State", "County"),
          selected = "National",
          width = "100%"
        )
      ),
      column(
        3,
        selectInput(
          "global_region",
          "Region/State",
          choices = c("All Regions", "Northeast", "South", "Midwest", "West"),
          selected = "All Regions",
          width = "100%"
        )
      ),
      column(
        2,
        actionButton(
          "reset_filters",
          "Reset Filters",
#           icon removed for debugging
          style = "width: 100%; margin-top: 25px;
                   background-color: #6c757d; color: white; border: none;"
        )
      )
    )
  )
}
