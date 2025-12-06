# R/ui_overview.R

ui_overview <- fluidPage(

  # ROW 1 — TOP 4 EXECUTIVE KPIs
  fluidRow(
    column(
      3,
      div(class = "kpi-card kpi-blue",
          div(class = "kpi-title", "National FI Rate"),
          div(class = "kpi-value", textOutput("kpi_fi_rate"))
      )
    ),
    column(
      3,
      div(class = "kpi-card kpi-green",
          div(class = "kpi-title", "Food Insecure Persons"),
          div(class = "kpi-value", textOutput("kpi_fi_persons"))
      )
    ),
    column(
      3,
      div(class = "kpi-card kpi-orange",
          div(class = "kpi-title", "Child FI Rate"),
          div(class = "kpi-value", textOutput("kpi_child_fi_rate"))
      )
    ),
    column(
      3,
      div(class = "kpi-card kpi-purple",
          div(class = "kpi-title", "Avg. Cost per Meal"),
          div(class = "kpi-value", textOutput("kpi_cost_per_meal"))
      )
    )
  ),

  br(),

  # ROW 2 — DISPARITIES + SHORTFALLS
  fluidRow(
    column(
      3,
      div(class = "kpi-card kpi-red",
          div(class = "kpi-title", "FI Gap: Black vs White"),
          div(class = "kpi-value", textOutput("kpi_gap_black"))
      )
    ),
    column(
      3,
      div(class = "kpi-card kpi-orange",
          div(class = "kpi-title", "FI Gap: Hispanic vs White"),
          div(class = "kpi-value", textOutput("kpi_gap_hisp"))
      )
    ),
    column(
      3,
      div(class = "kpi-card kpi-blue",
          div(class = "kpi-title", "Annual Budget Shortfall"),
          div(class = "kpi-value", textOutput("kpi_shortfall"))
      )
    ),
    column(
      3,
      div(class = "kpi-card kpi-green",
          div(class = "kpi-title", "Rural–Metro FI Gap"),
          div(class = "kpi-value", textOutput("kpi_rural_gap"))
      )
    )
  ),

  br(), br(),

  # INSIGHTS + TREND CHART
  fluidRow(
    column(
      4,
      div(
        class = "card insights-card fade-in",
        h5("Key Insights", class = "fw-bold mb-3"),
        tags$ul(
          tags$li("Food insecurity remains most concentrated in the South."),
          tags$li("Rural communities face consistently higher FI rates."),
          tags$li("Racial FI gaps persist across most states."),
          tags$li("Cost burden continues to rise in high-poverty counties.")
        )
      )
    ),

    column(
      8,
      div(
        class = "card trend-card fade-in",
        h5("National Food Insecurity Trend", class = "fw-bold mb-3"),
        plotly::plotlyOutput("national_trend_plot", height = "330px")
      )
    )
  )
)
