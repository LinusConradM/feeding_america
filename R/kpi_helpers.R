# R/kpi_helpers.R
compute_kpis <- function(df) {

  df <- df %>%
    mutate(
      rural_group = case_when(
        rural_urban_continuum_code_2013 <= 3 ~ "Metro",
        rural_urban_continuum_code_2013 <= 6 ~ "Non-Metro",
        TRUE ~ "Rural"
      )
    )

  list(
    national_fi_rate = df %>% summarise(rate = mean(overall_food_insecurity_rate, na.rm=TRUE)) %>% pull(),

    fi_persons = df %>% summarise(total = sum(number_of_food_insecure_persons_overall, na.rm=TRUE)) %>% pull(),

    child_fi_rate = df %>% summarise(rate = mean(child_food_insecurity_rate, na.rm=TRUE)) %>% pull(),

    racial_gap_black = df %>% summarise(gap =
      mean(food_insecurity_rate_among_black_persons_all_ethnicities, na.rm=TRUE) -
      mean(food_insecurity_rate_among_white_non_hispanic_persons, na.rm=TRUE)
    ) %>% pull(),

    racial_gap_hisp = df %>% summarise(gap =
      mean(food_insecurity_rate_among_hispanic_persons_any_race, na.rm=TRUE) -
      mean(food_insecurity_rate_among_white_non_hispanic_persons, na.rm=TRUE)
    ) %>% pull(),

    cost_per_meal = df %>% summarise(cost = mean(cost_per_meal, na.rm=TRUE)) %>% pull(),

    budget_shortfall = df %>% summarise(total = sum(weighted_annual_food_budget_shortfall, na.rm=TRUE)) %>% pull(),

    rural_metro_gap = df %>% 
      group_by(rural_group) %>% 
      summarise(rate = mean(overall_food_insecurity_rate, na.rm=TRUE)) %>% 
      pivot_wider(names_from = rural_group, values_from = rate) %>% 
      mutate(gap = Rural - Metro) %>% 
      pull(gap)
  )
}
