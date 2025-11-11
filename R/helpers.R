# Shared helper functions

filter_state_data <- function(df, state) {
  df %>% filter(State == state)
}
