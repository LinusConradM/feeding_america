# ==============================================================================
# HELPER FUNCTIONS
# ==============================================================================
# PURPOSE: Utility functions used across multiple modules
# TEAM: Conrad, Sharon, Ryann, Alex
# ==============================================================================

library(dplyr)

# ------------------------------------------------------------------
# Generic state + county sanity filter (NO year filtering)
# ------------------------------------------------------------------
filter_state_county <- function(df) {
  df %>%
    filter(
      !is.na(state),
      !is.na(county),
      !is.na(year)
    )
}

# ------------------------------------------------------------------
# Optional: explicit state filter (correct column name)
# ------------------------------------------------------------------
# helpers.R
filter_state_data <- function(df, state_value) {
  df %>% filter(state == state_value)
}
