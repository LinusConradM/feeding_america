# GLOBAL.R — Loads data + sets global ggplot theme

# ==============================================================================
# REQUIRED PACKAGES
# ==============================================================================

required_packages <- c(
  "shiny", "tidyverse", "readxl", "leaflet", "leaflet.extras",
  "plotly", "DT", "maps", "scales", "janitor"
)

# Install missing packages
missing_packages <- required_packages[!required_packages %in% installed.packages()[,"Package"]]

if(length(missing_packages) > 0) {
  cat("Installing missing packages:", paste(missing_packages, collapse = ", "), "\n")
  install.packages(missing_packages)
}

# Load packages
library(shiny)
library(tidyverse)
library(readxl)
library(leaflet)
library(plotly)
library(DT)
library(maps)
library(scales)
library(janitor)

cat("✓ All packages loaded\n")

cat("========================================\n")
cat("LOADING FOOD INSECURITY DATA\n")
cat("========================================\n\n")

## Load data and perform initial cleaning

# Load 2009 - 2018 data
path_pre  <- "data/feeding_america(2009-2018).xlsx"
path_post <- "data/feeding_america(2019-2023).xlsx"

cat("Loading Excel files...\n")
fa_pre_raw  <- read_excel(path_pre)
fa_post_raw <- read_excel(path_post)
cat("✓ Files loaded\n\n")

# Clean column names
cat("Cleaning column names...\n")
fa_pre  <- fa_pre_raw %>% clean_names()
fa_post <- fa_post_raw %>% clean_names()
cat("✓ Column names cleaned\n\n")

# Define columns that should remain character
character_cols <- c(
  "state", "fa_state", "county_state", "county", "fips",
  "census_region", "census_division", "fns_region",
  "low_threshold_type", "high_threshold_type", "year_group"
)

# Apply data cleaning and type fixing
cat("Applying data cleaning and type conversions...\n")

fa_pre <- fa_pre %>%
  mutate(
    # Clean character columns
    across(where(is.character), trimws),
    across(where(is.character), ~ na_if(.x, "NA")),
    across(where(is.character), ~ na_if(.x, "n/a"))
  ) %>%
  mutate(
    # Force geographic columns to character
    across(all_of(character_cols[character_cols %in% names(.)]), as.character),
    
    # Convert ALL non-character columns to numeric (except year)
    across(!any_of(c(character_cols, "year")) & !where(is.numeric), as.numeric),
    
    # Year as integer
    year = as.integer(year),
    
    # Add year group
    year_group = "2009–2018"
  )

fa_post <- fa_post %>%
  mutate(
    # Clean character columns
    across(where(is.character), trimws),
    across(where(is.character), ~ na_if(.x, "NA")),
    across(where(is.character), ~ na_if(.x, "n/a"))
  ) %>%
  mutate(
    # Force geographic columns to character
    across(all_of(character_cols[character_cols %in% names(.)]), as.character),
    
    # Convert ALL non-character columns to numeric (except year)
    across(!any_of(c(character_cols, "year")) & !where(is.numeric), as.numeric),
    
    # Year as integer
    year = as.integer(year),
    
    # Add year group
    year_group = "2019–2023"
  )

cat("✓ Data types fixed\n\n")

# Verify key columns
cat("Verifying data types:\n")
cat("  fa_pre$state:", class(fa_pre$state), "\n")
cat("  fa_post$state:", class(fa_post$state), "\n")
cat("  fa_pre$snap_rate:", class(fa_pre$snap_rate), "\n")
cat("  fa_post$snap_rate:", class(fa_post$snap_rate), "\n\n")

# Combine both time periods into one dataset
cat("Combining datasets...\n")

food_data <- bind_rows(fa_pre, fa_post) %>%
  arrange(fips, year) %>%
  # Create derived variables
  mutate(
    # Extract county name only
    county = str_remove(county_state, ", .*$"),
    
    # Urban/rural classification (using population since no RUCC column)
    urban_rural = case_when(
      population >= 100000 ~ "Metro",
      population >= 20000 ~ "Non-metro",
      TRUE ~ "Rural"
    ),
    
    # Food insecurity categories
    fi_category = case_when(
      overall_food_insecurity_rate < 0.10 ~ "Low",
      overall_food_insecurity_rate < 0.15 ~ "Moderate",
      overall_food_insecurity_rate < 0.20 ~ "High",
      TRUE ~ "Very High"
    ),
    
    # Poverty categories
    poverty_category = case_when(
      poverty_rate < 0.10 ~ "Low",
      poverty_rate < 0.15 ~ "Medium",
      poverty_rate < 0.20 ~ "High",
      TRUE ~ "Very High"
    ),
    
    # Income categories
    income_category = case_when(
      median_income < 40000 ~ "Low",
      median_income < 60000 ~ "Medium",
      TRUE ~ "High"
    ),
    
    # Education categories
    education_category = case_when(
      hs_or_less < 0.15 ~ "High Education",
      hs_or_less < 0.25 ~ "Medium Education",
      TRUE ~ "Low Education"
    )
  )

cat("✓ Datasets combined successfully!\n\n")

# Summary
cat("========================================\n")
cat("DATA LOADING COMPLETE!\n")
cat("========================================\n")
cat("  Rows:", format(nrow(food_data), big.mark = ","), "\n")
cat("  Columns:", ncol(food_data), "\n")
cat("  Years:", paste(range(food_data$year, na.rm = TRUE), collapse = "-"), "\n")
cat("  Counties:", format(n_distinct(food_data$fips), big.mark = ","), "\n")
cat("========================================\n\n")

# Quick data quality check
cat("Key variable coverage:\n")
cat("  Food insecurity rate missing:", sum(is.na(food_data$overall_food_insecurity_rate)), "\n")
cat("  Poverty rate missing:", sum(is.na(food_data$poverty_rate)), "\n")
cat("  Median income missing:", sum(is.na(food_data$median_income)), "\n")
cat("  Cost per meal missing:", sum(is.na(food_data$cost_per_meal)), "\n\n")

# ==============================================================================
# ADD GEOGRAPHIC COORDINATES FOR MAPPING (SIMPLIFIED)
# ==============================================================================

cat("Adding geographic coordinates for mapping...\n")

# Get county FIPS codes (from maps package)
county_fips <- maps::county.fips %>%
  as_tibble() %>%
  mutate(
    fips = sprintf("%05d", fips),
    polyname = as.character(polyname)
  ) %>%
  separate(polyname, c("state_map", "county_map"), sep = ",", remove = FALSE)

# Get county centroids (using ggplot2::map_data, not maps::map_data)
county_coords <- ggplot2::map_data("county") %>%
  group_by(region, subregion) %>%
  summarise(
    lon = mean(long),
    lat = mean(lat),
    .groups = "drop"
  )

# Merge FIPS with coordinates
county_geo <- county_fips %>%
  left_join(
    county_coords,
    by = c("state_map" = "region", "county_map" = "subregion")
  ) %>%
  select(fips, lon, lat) %>%
  distinct(fips, .keep_all = TRUE)

# Add coordinates to food_data
food_data <- food_data %>%
  left_join(county_geo, by = "fips")

# Check success
coords_added <- sum(!is.na(food_data$lon))
cat("✓ Geographic coordinates added\n")
cat("  Counties with coordinates:", 
    format(coords_added, big.mark = ","), 
    "out of", 
    format(nrow(food_data), big.mark = ","),
    paste0(" (", round(coords_added/nrow(food_data)*100, 1), "%)\n\n"))

# For counties without coordinates, use state center
if (sum(is.na(food_data$lon)) > 0) {
  
  # State centers (approximate)
  state_centers <- tibble(
    state = state.abb,
    state_lon = c(-86.9, -152.0, -111.9, -92.4, -119.4, -105.5, -72.7, -75.5, -81.5, 
                  -83.5, -157.5, -114.7, -89.4, -86.3, -93.1, -98.0, -84.9, -92.0, 
                  -69.4, -76.6, -71.4, -84.5, -94.6, -89.7, -92.3, -109.5, -100.0, 
                  -117.0, -71.5, -74.4, -106.0, -74.0, -79.0, -100.0, -82.9, -97.5, 
                  -120.5, -77.0, -71.5, -80.5, -99.9, -111.5, -72.6, -78.6, -100.0, 
                  -79.5, -120.5, -80.5, -89.5, -107.5),
    state_lat = c(32.8, 64.0, 34.0, 35.0, 37.0, 39.0, 41.6, 39.0, 28.0, 
                  33.0, 20.0, 44.0, 40.0, 40.0, 42.0, 38.5, 37.8, 31.0, 
                  45.0, 39.0, 42.3, 43.0, 46.0, 32.0, 38.6, 47.0, 41.5, 
                  39.0, 43.2, 40.0, 34.5, 43.0, 35.5, 47.5, 40.4, 35.5, 
                  44.5, 41.0, 41.7, 34.0, 44.5, 39.3, 44.0, 37.5, 31.0, 
                  38.5, 47.5, 39.0, 43.0, 43.0)
  )
  
  food_data <- food_data %>%
    left_join(state_centers, by = "state") %>%
    mutate(
      lon = coalesce(lon, state_lon),
      lat = coalesce(lat, state_lat)
    ) %>%
    select(-state_lon, -state_lat)
  
  cat("✓ State centers used for remaining counties\n\n")
}

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
      color = "#000000",
      face = "bold"
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

cat("✓ ggplot theme set\n")
cat("✓ Ready to run Shiny app!\n\n")
