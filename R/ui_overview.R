# R/ui_overview.R
ui_overview <- fluidPage(
  titlePanel("Overview: U.S. Food Insecurity"),
  fluidRow(
    column(
      4,
      wellPanel(
        h4("Key Indicators"),
        p("Placeholder summary for national-level metrics."),
        tags$ul(
          tags$li("Overall U.S. food insecurity rate"),
          tags$li("Top 5 most food insecure states"),
          tags$li("Change since last year")
        )
      )
    ),
    column(
      8,
      plotly::plotlyOutput("national_trend_plot", height = "400px")
    )
  )
)
