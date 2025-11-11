## 1. Business Logic Section 
## U.S. Food Insecurity Dashboard - Overview Module
# (Libraries, helper functions, and themes are already loaded from app.R)
# This module inherits global theme_modern and custom.css styling.


## 2. User Interface Section 
ui_overview <- fluidPage(

  # Section Header
  fluidRow(
    column(
      12,
      div(
        class = "section-header",
        h3("National Overview", class = "fw-bold mb-2"),
        p("Explore food insecurity rates, affected households, and emerging trends across the United States.",
          class = "text-muted mb-4")
      )
    )
  ),

  # Summary Metric Cards
  fluidRow(
    column(
      3,
      div(class = "metric-card primary",
          h5("National Rate", class = "text-muted"),
          h2(textOutput("national_rate"), class = "metric-value"),
          p(textOutput("rate_change"), class = "metric-change")
      )
    ),
    column(
      3,
      div(class = "metric-card success",
          h5("Households Affected", class = "text-muted"),
          h2(textOutput("households_affected"), class = "metric-value"),
          p(textOutput("households_change"), class = "metric-change")
      )
    ),
    column(
      3,
      div(class = "metric-card warning",
          h5("Children at Risk", class = "text-muted"),
          h2(textOutput("children_at_risk"), class = "metric-value"),
          p(textOutput("children_change"), class = "metric-change")
      )
    ),
    column(
      3,
      div(class = "metric-card info",
          h5("States Tracked", class = "text-muted"),
          h2(textOutput("states_tracked"), class = "metric-value"),
          p("✓ Complete", class = "metric-change")
      )
    )
  ),

  br(),

  # Insights + Trend Plot
  fluidRow(
    column(
      4,
      div(class = "card insights-card",
          h5("Key Insights", class = "fw-bold mb-3"),
          tags$ul(
            tags$li("Food insecurity remains highest in Southern states."),
            tags$li("Rural areas show 15% higher rates than urban."),
            tags$li("Child food insecurity decreased by 1.8%."),
            tags$li("Federal programs reached 42M households.")
          )
      )
    ),
    column(
      8,
      div(class = "card trend-card",
          h5("National Food Insecurity Trends (2000–2025)", class = "fw-bold mb-3"),
          plotOutput("national_trend_plot", height = "320px")
      )
    )
  ),

  br(),
  p(em("Source: USDA Economic Research Service, 2025"),
    class = "text-center text-muted small mt-4 mb-2")
)


## 3. Server Section 
server_overview <- function(input, output, session, data) {

  # Placeholder Values (to be replaced with dynamic data)
  output$national_rate        <- renderText("12.8%")
  output$rate_change          <- renderText("↓ 0.3% from 2024")
  output$households_affected  <- renderText("17.2M")
  output$households_change    <- renderText("↑ 2.1% increase")
  output$children_at_risk     <- renderText("13.5M")
  output$children_change      <- renderText("↓ 1.8% improvement")
  output$states_tracked       <- renderText("50")

  # National Trend Plot 
  output$national_trend_plot <- renderPlot({
    set.seed(123)
    df <- tibble(
      Year = 2000:2025,
      Rate = 12 + cumsum(rnorm(26, 0, 0.3))
    )

    ggplot(df, aes(Year, Rate)) +
      geom_line(color = "#220BED", linewidth = 1.4) +
      geom_point(color = "#00B884", size = 2) +
      labs(
        y = "Food Insecurity Rate (%)",
        x = NULL,
        subtitle = "National trend from 2000 to 2025"
      ) +
      my_theme
  })
}
