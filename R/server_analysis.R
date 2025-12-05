# R/server_analysis.R

server_analysis <- function(input, output, session, data) {

  # ------------------------------------------
  # 1. Populate numeric variables for outcome
  # ------------------------------------------
  observe({
    df <- data()

    numeric_vars <- df %>%
      select(where(is.numeric)) %>%
      names()

    updateSelectInput(
      session, "group_target",
      choices = numeric_vars,
      selected = "overall_food_insecurity_rate"
    )
  })

  # ------------------------------------------------
  # 2. Run GROUP COMPARISON when button is clicked
  # ------------------------------------------------
  observeEvent(input$run_model, {

    req(input$model_type == "Group Comparison")

    df <- data()

    # --------------------------
    # build grouping variable
    # --------------------------
    if (input$group_var == "Census Region") {
      df$grp <- df$census_region
    }

    if (input$group_var == "Census Division") {
      df$grp <- df$census_division
    }

    if (input$group_var == "Rural/Urban") {
      df$grp <- case_when(
        df$rural_urban_continuum_code_2013 <= 3 ~ "Metro",
        df$rural_urban_continuum_code_2013 <= 6 ~ "Non-Metro",
        TRUE ~ "Rural"
      )
    }

    if (input$group_var == "Income Category (≤185% vs >185%)") {
      df$grp <- case_when(
        df$percent_food_insecure_children_in_hh_w_hh_incomes_below_185_fpl >= 0.5 ~ "Low Income",
        TRUE ~ "Higher Income"
      )
    }

    # --------------------------
    # Special handling for Race
    # --------------------------
    if (input$group_var == "Race") {

      df <- df %>%
        select(
          county_state, year,
          black = food_insecurity_rate_among_black_persons_all_ethnicities,
          hispanic = food_insecurity_rate_among_hispanic_persons_any_race,
          white = food_insecurity_rate_among_white_non_hispanic_persons
        ) %>%
        pivot_longer(cols = c(black, hispanic, white),
                     names_to = "grp",
                     values_to = "value")

      target_var <- "value"

      updateSelectInput(
        session,
        "group_target",
        choices = "value",
        selected = "value"
      )

    } else {
      target_var <- input$group_target
    }

    req(target_var)

    # ======================================================
    # 3. PLOT: Boxplot by group
    # ======================================================
    output$group_comp_plot <- plotly::renderPlotly({

      plot_ly(
        df,
        x = ~grp,
        y = df[[target_var]],
        type = "box",
        color = ~grp,
        colors = "Set2"
      ) %>%
        layout(
          title = paste("Group Comparison:", input$group_var),
          xaxis = list(title = input$group_var),
          yaxis = list(title = target_var)
        )
    })

    # ======================================================
    # 4. STATISTICAL TEST (t-test or ANOVA)
    # ======================================================
    output$group_stats <- renderPrint({

      grp_count <- df %>% pull(grp) %>% unique() %>% length()

      if (grp_count == 2) {
        cat("Two-group comparison → t-test\n\n")
        print(t.test(df[[target_var]] ~ df$grp))
      } else {
        cat("Multiple-group comparison → ANOVA\n\n")
        print(summary(aov(df[[target_var]] ~ df$grp)))
      }
    })
  })
}
