# Load required packages
library(shiny)
library(plotly)
library(tidyverse)
library(leaflet)
library(DT)
library(bslib)
library(readxl)
library(dplyr)
library(janitor)
library(tidyverse)

# File Path setup
data_path <- "data/MMG2019-2023_Data_sets.xlsx"

# Reference dataset from sheet 2 ("County")
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
