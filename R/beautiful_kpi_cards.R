# ==============================================================================
# BEAUTIFUL KPI CARDS - GRADIENT DESIGN
# ==============================================================================
# Creates stunning gradient KPI cards with icons and animations
# Matches server_overview.R output names
# ==============================================================================

# Beautiful KPI cards layout
beautiful_kpi_cards <- tagList(
  # Row 1: Primary Metrics
  fluidRow(
    # National FI Rate - Coral Gradient
    column(
      width = 3,
      div(
        class = "beautiful-kpi-card gradient-coral",
        div(
          class = "kpi-icon-wrapper",
          icon("chart-line", class = "kpi-icon")
        ),
        div(
          class = "kpi-content",
          h4("NATIONAL FI RATE", class = "kpi-title"),
          h1(textOutput("kpi_national_fi_rate"), class = "kpi-value"),
          div(uiOutput("kpi_fi_rate_change"), class = "kpi-change")
        ),
        div(class = "kpi-decoration")
      )
    ),
    
    # Total Food Insecure - Navy Gradient
    column(
      width = 3,
      div(
        class = "beautiful-kpi-card gradient-navy",
        div(
          class = "kpi-icon-wrapper",
          icon("users", class = "kpi-icon")
        ),
        div(
          class = "kpi-content",
          h4("FOOD INSECURE PERSONS", class = "kpi-title"),
          h1(textOutput("kpi_total_food_insecure"), class = "kpi-value"),
          div(uiOutput("kpi_fi_persons_change"), class = "kpi-change")
        ),
        div(class = "kpi-decoration")
      )
    ),
    
    # Child FI Rate - Plum Gradient
    column(
      width = 3,
      div(
        class = "beautiful-kpi-card gradient-plum",
        div(
          class = "kpi-icon-wrapper",
          icon("child", class = "kpi-icon")
        ),
        div(
          class = "kpi-content",
          h4("CHILD FI RATE", class = "kpi-title"),
          h1(textOutput("kpi_child_fi_rate"), class = "kpi-value"),
          div(uiOutput("kpi_child_fi_change"), class = "kpi-change")
        ),
        div(class = "kpi-decoration")
      )
    ),
    
    # Cost Per Meal - Amber Gradient
    column(
      width = 3,
      div(
        class = "beautiful-kpi-card gradient-amber",
        div(
          class = "kpi-icon-wrapper",
          icon("dollar-sign", class = "kpi-icon")
        ),
        div(
          class = "kpi-content",
          h4("AVG COST PER MEAL", class = "kpi-title"),
          h1(textOutput("kpi_avg_cost_per_meal"), class = "kpi-value"),
          div(uiOutput("kpi_cost_change"), class = "kpi-change")
        ),
        div(class = "kpi-decoration")
      )
    )
  ),
  
  # Row 2: Secondary Metrics
  fluidRow(
    # Poverty Rate - Blue Gradient
    column(
      width = 3,
      div(
        class = "beautiful-kpi-card gradient-blue",
        div(
          class = "kpi-icon-wrapper",
          icon("hand-holding-usd", class = "kpi-icon")
        ),
        div(
          class = "kpi-content",
          h4("POVERTY RATE", class = "kpi-title"),
          h1(textOutput("kpi_poverty_rate"), class = "kpi-value"),
          div(uiOutput("kpi_poverty_change"), class = "kpi-change")
        ),
        div(class = "kpi-decoration")
      )
    ),
    
    # Median Income - Success Green Gradient
    column(
      width = 3,
      div(
        class = "beautiful-kpi-card gradient-success",
        div(
          class = "kpi-icon-wrapper",
          icon("coins", class = "kpi-icon")
        ),
        div(
          class = "kpi-content",
          h4("MEDIAN INCOME", class = "kpi-title"),
          h1(textOutput("kpi_median_income"), class = "kpi-value"),
          div(uiOutput("kpi_income_change"), class = "kpi-change")
        ),
        div(class = "kpi-decoration")
      )
    ),
    
    # Unemployment - Coral Gradient
    column(
      width = 3,
      div(
        class = "beautiful-kpi-card gradient-coral",
        div(
          class = "kpi-icon-wrapper",
          icon("briefcase", class = "kpi-icon")
        ),
        div(
          class = "kpi-content",
          h4("UNEMPLOYMENT RATE", class = "kpi-title"),
          h1(textOutput("kpi_unemployment_rate"), class = "kpi-value"),
          div(uiOutput("kpi_unemployment_change"), class = "kpi-change")
        ),
        div(class = "kpi-decoration")
      )
    ),
    
    # Budget Shortfall - Navy Gradient
    column(
      width = 3,
      div(
        class = "beautiful-kpi-card gradient-navy",
        div(
          class = "kpi-icon-wrapper",
          icon("piggy-bank", class = "kpi-icon")
        ),
        div(
          class = "kpi-content",
          h4("BUDGET SHORTFALL", class = "kpi-title"),
          h1(textOutput("kpi_budget_shortfall"), class = "kpi-value"),
          div(uiOutput("kpi_shortfall_change"), class = "kpi-change")
        ),
        div(class = "kpi-decoration")
      )
    )
  )
)

# ==============================================================================
# HELPER FUNCTION (Optional - for manual card creation)
# ==============================================================================

create_kpi_card <- function(id_value, id_change, title, icon_name, gradient_class = "gradient-coral") {
  div(
    class = paste("beautiful-kpi-card", gradient_class),
    div(
      class = "kpi-icon-wrapper",
      icon(icon_name, class = "kpi-icon")
    ),
    div(
      class = "kpi-content",
      h4(title, class = "kpi-title"),
      h1(textOutput(id_value), class = "kpi-value"),
      div(uiOutput(id_change), class = "kpi-change")
    ),
    div(class = "kpi-decoration")
  )
}

cat("✓ Beautiful KPI cards functions loaded\n")
cat("  Available gradients: coral, navy, plum, amber, blue, success\n")
cat("  Use: beautiful_kpi_cards in your UI\n")
