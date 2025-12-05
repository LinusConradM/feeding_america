# ================================================================
# GLOBAL.R — Loads data + sets global ggplot theme
# ================================================================

# Load required packages
library(shiny)
library(plotly)
library(tidyverse)
library(leaflet)
library(DT)
library(bslib)
library(readxl)
library(janitor)
library(dplyr)
library(tidyr)
library(ggplot2)

# ================================================================
# DATA LOADING
# ================================================================
data_path <- "data/MMG2019-2023_Data_sets.xlsx"

fd_basket <- read_excel(
  path = data_path,
  sheet = "County"
) %>%
  clean_names() %>%
  mutate(across(where(is.character), trimws)) %>%
  mutate(
    fips = as.character(fips),
    county_state = county_state
  )

colnames(fd_basket)
# ================================================================
# GLOBAL GGPLOT THEME (Auto-applied to ALL ggplots)
# ================================================================

my_theme <- theme(
    text = element_text(family = "Arial", size = 14, color = "black"),
    plot.title = element_text(
      hjust = 0.5, 
      size = 20, 
      face = "bold",
      color = "black"
    ),
    axis.title = element_text(
      size = 16,
      color = "black",
      face = "bold"
    ),
    axis.text = element_text(
      size = 14,
      color = "#000000",   # <-- force dark labels
      face = "bold"        # <-- optional but increases contrast
    ),
    legend.title = element_text(
      size = 14,
      face = "bold",
      color = "black"
    ),
    legend.text = element_text(
      size = 12,
      color = "black"
    ),
    
    strip.text = element_text(
      size = 14,
      face = "bold",
      color = "black"
    ),
    panel.grid.major = element_line(color = "grey85"),
    panel.grid.minor = element_blank()
  )
theme_set(my_theme)

# ================================================================
# END GLOBAL.R
# ================================================================
