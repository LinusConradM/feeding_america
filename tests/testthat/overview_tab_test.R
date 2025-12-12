library(shinytest2)

test_that("{shinytest2} recording: gp-food-basket", {
  app <- AppDriver$new(variant = platform_variant(), name = "gp-food-basket", height = 1120, 
      width = 1699)
  app$set_inputs(navbar = "overview")
  app$set_inputs(bottom_10_states_rows_current = c(1, 2, 3, 4, 5, 6, 7, 8, 9, 10), 
      allow_no_input_binding_ = TRUE)
  app$set_inputs(bottom_10_states_rows_all = c(1, 2, 3, 4, 5, 6, 7, 8, 9, 10), allow_no_input_binding_ = TRUE)
  app$set_inputs(bottom_10_states_state = c(1765551569429, 0, 10, "", TRUE, FALSE, 
      TRUE, c(TRUE, "", TRUE, FALSE, TRUE), c(TRUE, "", TRUE, FALSE, TRUE), c(TRUE, 
          "", TRUE, FALSE, TRUE), c(TRUE, "", TRUE, FALSE, TRUE)), allow_no_input_binding_ = TRUE)
  app$set_inputs(top_10_states_rows_current = c(1, 2, 3, 4, 5, 6, 7, 8, 9, 10), allow_no_input_binding_ = TRUE)
  app$set_inputs(top_10_states_rows_all = c(1, 2, 3, 4, 5, 6, 7, 8, 9, 10), allow_no_input_binding_ = TRUE)
  app$set_inputs(top_10_states_state = c(1765551569485, 0, 10, "", TRUE, FALSE, TRUE, 
      c(TRUE, "", TRUE, FALSE, TRUE), c(TRUE, "", TRUE, FALSE, TRUE), c(TRUE, "", 
          TRUE, FALSE, TRUE), c(TRUE, "", TRUE, FALSE, TRUE)), allow_no_input_binding_ = TRUE)
  app$set_inputs(overview_year_selector = "2020")
  app$set_inputs(bottom_10_states_rows_current = c(1, 2, 3, 4, 5, 6, 7, 8, 9, 10), 
      allow_no_input_binding_ = TRUE)
  app$set_inputs(bottom_10_states_rows_all = c(1, 2, 3, 4, 5, 6, 7, 8, 9, 10), allow_no_input_binding_ = TRUE)
  app$set_inputs(bottom_10_states_state = c(1765551643153, 0, 10, "", TRUE, FALSE, 
      TRUE, c(TRUE, "", TRUE, FALSE, TRUE), c(TRUE, "", TRUE, FALSE, TRUE), c(TRUE, 
          "", TRUE, FALSE, TRUE), c(TRUE, "", TRUE, FALSE, TRUE)), allow_no_input_binding_ = TRUE)
  app$set_inputs(top_10_states_rows_current = c(1, 2, 3, 4, 5, 6, 7, 8, 9, 10), allow_no_input_binding_ = TRUE)
  app$set_inputs(top_10_states_rows_all = c(1, 2, 3, 4, 5, 6, 7, 8, 9, 10), allow_no_input_binding_ = TRUE)
  app$set_inputs(top_10_states_state = c(1765551643167, 0, 10, "", TRUE, FALSE, TRUE, 
      c(TRUE, "", TRUE, FALSE, TRUE), c(TRUE, "", TRUE, FALSE, TRUE), c(TRUE, "", 
          TRUE, FALSE, TRUE), c(TRUE, "", TRUE, FALSE, TRUE)), allow_no_input_binding_ = TRUE)
  app$expect_screenshot()
  app$set_inputs(overview_year_selector = "2021")
  app$set_inputs(bottom_10_states_rows_current = c(1, 2, 3, 4, 5, 6, 7, 8, 9, 10), 
      allow_no_input_binding_ = TRUE)
  app$set_inputs(bottom_10_states_rows_all = c(1, 2, 3, 4, 5, 6, 7, 8, 9, 10), allow_no_input_binding_ = TRUE)
  app$set_inputs(bottom_10_states_state = c(1765551690473, 0, 10, "", TRUE, FALSE, 
      TRUE, c(TRUE, "", TRUE, FALSE, TRUE), c(TRUE, "", TRUE, FALSE, TRUE), c(TRUE, 
          "", TRUE, FALSE, TRUE), c(TRUE, "", TRUE, FALSE, TRUE)), allow_no_input_binding_ = TRUE)
  app$set_inputs(top_10_states_rows_current = c(1, 2, 3, 4, 5, 6, 7, 8, 9, 10), allow_no_input_binding_ = TRUE)
  app$set_inputs(top_10_states_rows_all = c(1, 2, 3, 4, 5, 6, 7, 8, 9, 10), allow_no_input_binding_ = TRUE)
  app$set_inputs(top_10_states_state = c(1765551690480, 0, 10, "", TRUE, FALSE, TRUE, 
      c(TRUE, "", TRUE, FALSE, TRUE), c(TRUE, "", TRUE, FALSE, TRUE), c(TRUE, "", 
          TRUE, FALSE, TRUE), c(TRUE, "", TRUE, FALSE, TRUE)), allow_no_input_binding_ = TRUE)
})
