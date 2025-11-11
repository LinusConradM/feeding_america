# R/server_analysis.R
server_analysis <- function(input, output, session, data) {
  observeEvent(input$run_model, {
    df <- data()

    if (input$model_type == "Correlation") {
      corr_matrix <- cor(select(df, -State))
      output$corr_plot <- plotly::renderPlotly({
        plotly::plot_ly(z = corr_matrix, type = "heatmap", colors = "RdBu") %>%
          plotly::layout(title = "Correlation Matrix (Placeholder)")
      })
    }

    if (input$model_type == "Regression") {
      formula <- as.formula(paste(input$dep_var, "~", paste(input$indep_vars, collapse = "+")))
      model <- lm(formula, data = df)
      output$reg_summary <- renderPrint({ summary(model) })
    }

    if (input$model_type == "Group Comparison") {
      output$group_plot <- plotly::renderPlotly({
        plotly::plot_ly(df, x = ~State, y = ~FoodInsecurity, type = "box", color = ~State)
      })
    }
  })
}
