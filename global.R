
# GLOBAL.R — Loads data + sets global ggplot theme

# Load required packages

#| label: loading packages
library(shiny)
library(plotly)
library(tidyverse)
library(leaflet)
library(DT)
library(bslib)
library(readxl)
library(dplyr)
library(tidyr)
library(ggplot2)
library(dplyr)
library(readr)
library(readxl)
library(janitor)
library(stringr)



## Load data and perform initial cleaning

#| label: loading data
#| warnings: false

# load 2009 - 2018 data
path_pre  <- "data/feeding_america(2009-2018).xlsx"
path_post <- "data/feeding_america(2019-2023).xlsx"

fa_pre_raw  <- read_excel(path_pre)
fa_post_raw <- read_excel(path_post)


#Create a function to clean data

#| label: cleaning data

clean_stage1 <- function(df) {
  df %>%
    clean_names() %>%
    mutate(across(where(is.character), trimws)) %>%
    mutate(across(where(is.character), ~ na_if(.x, "NA"))) %>%
    mutate(across(where(is.character), ~ na_if(.x, "n/a"))) %>%
    mutate(fips = as.character(fips))
}

#Apply cleaning function to datasets

#| label: applying cleaning function

fa_pre  <- clean_stage1(fa_pre_raw)
fa_post <- clean_stage1(fa_post_raw)


#Create a function to convert numeric columns

#| label: converting numeric columns

label_vars <- c(
  "state",
  "county_state",
  "census_region",
  "census_division",
  "fns_region",
  "low_threshold_type",
  "high_threshold_type"
)

convert_numeric <- function(df) {
  df %>%
    mutate(
      across(
        where(is.character) & !any_of(label_vars),
        readr::parse_number
      )
    )
}


# Apply numeric conversion function to datasets

#| label: applying numeric conversion
fa_pre  <- convert_numeric(fa_pre)
fa_post <- convert_numeric(fa_post)


# Add year group columns to datasets

#| label: adding year group columns
fa_pre  <- fa_pre  %>% mutate(year_group = "2009–2018")
fa_post <- fa_post %>% mutate(year_group = "2019–2023")



## Create global ggplot theme

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
  mutate(across(where(is.character), ~ trimws(.)))

# Inspect structure (optional)
#glimpse(fd_basket)
#unique(fd_basket$year)
