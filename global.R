# ==============================================================================
# GLOBAL.R — Loads data + sets global ggplot theme
# ==============================================================================

# ==============================================================================
# REQUIRED PACKAGES
# ==============================================================================
library(shiny)
required_packages <- c(
  "shiny", "tidyverse", "readxl", "leaflet", "leaflet.extras",
  "DT", "maps", "scales", "janitor",
  "nnet", "rpart", "rpart.plot", "broom", "pROC"
)

# Install missing packages
missing_packages <- required_packages[!required_packages %in% installed.packages()[, "Package"]]

if (length(missing_packages) > 0) {
  cat("Installing missing packages:", paste(missing_packages, collapse = ", "), "\n")
  install.packages(missing_packages, dependencies = TRUE)
}

# Load packages (with suppressed startup messages for cleaner console)
suppressPackageStartupMessages({
  library(shiny)
  library(tidyverse)
  library(readxl)
  library(leaflet)
# library(plotly)  # Using ggplot2 instead
  library(DT)
  library(maps)
  library(scales)
  library(janitor)
  library(nnet)
  library(rpart)
  library(rpart.plot)
  library(broom)
  library(pROC)
})

cat("✓ All packages loaded\n\n")

# ==============================================================================
# LOAD DATA
# ==============================================================================

cat("========================================\n")
cat("LOADING FOOD INSECURITY DATA\n")
cat("========================================\n\n")

## Load data and perform initial cleaning

# Load 2009 - 2018 data
path_pre <- "data/feeding_america(2009-2018).xlsx"
path_post <- "data/feeding_america(2019-2023).xlsx"

cat("Loading Excel files...\n")
fa_pre_raw <- read_excel(path_pre)
fa_post_raw <- read_excel(path_post)
cat("  Pre-pandemic rows:", format(nrow(fa_pre_raw), big.mark = ","), "\n")
cat("  Post-pandemic rows:", format(nrow(fa_post_raw), big.mark = ","), "\n")
cat("✓ Files loaded\n\n")

# Clean column names
cat("Cleaning column names...\n")
fa_pre <- fa_pre_raw %>% clean_names()
fa_post <- fa_post_raw %>% clean_names()
cat("✓ Column names cleaned\n\n")

# ==============================================================================
# CREATE FIPS STATE CODE LOOKUP TABLE
# ==============================================================================

state_lookup <- tibble(
  state_fips = c(
    1, 2, 4, 5, 6, 8, 9, 10, 11, 12, 13, 15, 16, 17, 18, 19,
    20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33,
    34, 35, 36, 37, 38, 39, 40, 41, 42, 44, 45, 46, 47, 48,
    49, 50, 51, 53, 54, 55, 56
  ),
  state = c(
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "DC", "FL",
    "GA", "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME",
    "MD", "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH",
    "NJ", "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI",
    "SC", "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"
  )
)

# Define columns that should remain character
character_cols <- c(
  "state", "fa_state", "county_state", "county", "fips",
  "census_region", "census_division", "fns_region",
  "low_threshold_type", "high_threshold_type", "year_group"
)

# ==============================================================================
# APPLY DATA CLEANING AND TYPE CONVERSIONS
# ==============================================================================

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
    across(where(is.character), ~ na_if(.x, "n/a")),

    # Convert state from numeric to abbreviation
    state_fips = as.numeric(state)
  ) %>%
  left_join(state_lookup, by = "state_fips") %>%
  select(-state_fips, -state.x) %>%
  rename(state = state.y) %>%
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

# ==============================================================================
# COMBINE DATASETS AND CREATE DERIVED VARIABLES
# ==============================================================================

cat("Combining datasets...\n")

food_data <- bind_rows(fa_pre, fa_post) %>%
  distinct(fips, year, .keep_all = TRUE) %>% # Remove duplicates!
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

cat("✓ Datasets combined successfully!\n")
cat("  Total rows:", format(nrow(food_data), big.mark = ","), "\n")
cat("  Years:", paste(range(food_data$year, na.rm = TRUE), collapse = "–"), "\n")
cat("  Counties:", format(n_distinct(food_data$fips), big.mark = ","), "\n\n")

# ==============================================================================
# CONVERT CATEGORICAL VARIABLES TO FACTORS
# ==============================================================================

cat("Applying categorical → factor conversion for modeling...\n")

food_data <- food_data %>%
  mutate(
    census_region = factor(census_region),
    census_division = factor(census_division),
    fns_region = factor(fns_region),
    urban_rural = factor(urban_rural, levels = c("Rural", "Non-metro", "Metro")),
    fi_category = factor(fi_category, levels = c("Low", "Moderate", "High", "Very High")),
    poverty_category = factor(poverty_category, levels = c("Low", "Medium", "High", "Very High")),
    income_category = factor(income_category, levels = c("Low", "Medium", "High")),
    education_category = factor(education_category, levels = c("Low Education", "Medium Education", "High Education")),
    low_threshold_type = factor(low_threshold_type),
    high_threshold_type = factor(high_threshold_type),
    year_group = factor(year_group, levels = c("2009–2018", "2019–2023"))
  )

cat("✓ Categorical variables converted to factors (models enabled)\n\n")

# ==============================================================================
# DATA SUMMARY
# ==============================================================================

cat("========================================\n")
cat("DATA LOADING COMPLETE!\n")
cat("========================================\n")
cat("  Rows:", format(nrow(food_data), big.mark = ","), "\n")
cat("  Columns:", ncol(food_data), "\n")
cat("  Years:", paste(range(food_data$year, na.rm = TRUE), collapse = "–"), "\n")
cat("  Counties:", format(n_distinct(food_data$fips), big.mark = ","), "\n")
cat("========================================\n\n")

# Quick data quality check
cat("Key variable coverage:\n")
cat("  Food insecurity rate missing:", sum(is.na(food_data$overall_food_insecurity_rate)), "\n")
cat("  Poverty rate missing:", sum(is.na(food_data$poverty_rate)), "\n")
cat("  Median income missing:", sum(is.na(food_data$median_income)), "\n")
cat("  Cost per meal missing:", sum(is.na(food_data$cost_per_meal)), "\n\n")

# ==============================================================================
# DIAGNOSTIC: CHECK FACTOR VARIABLES FOR MULTINOMIAL REGRESSION
# ==============================================================================

cat("========================================\n")
cat("CHECKING FACTORS FOR MULTINOMIAL MODEL\n")
cat("========================================\n\n")

factor_vars <- names(food_data)[sapply(food_data, is.factor)]
cat("Factor variables found:", length(factor_vars), "\n")
cat("Names:", paste(factor_vars, collapse = ", "), "\n\n")

cat("Factor levels check:\n")

# Track which variables are suitable for multinomial
multinomial_suitable <- character(0)

for (var in factor_vars) {
  n_levels <- nlevels(food_data[[var]])
  cat(sprintf("  %-25s: %2d levels", var, n_levels))

  if (n_levels >= 3) {
    cat(" ✓ (suitable for multinomial)")
    multinomial_suitable <- c(multinomial_suitable, var)
  } else if (n_levels == 2) {
    cat(" (binary)")
  } else if (n_levels < 2) {
    cat(" ⚠ (insufficient levels)")
  }
  cat("\n")

  # Show the levels
  if (n_levels > 0) {
    cat(sprintf(
      "    Levels: %s",
      paste(levels(food_data[[var]])[1:min(5, n_levels)], collapse = ", ")
    ))
    if (n_levels > 5) cat(" ...")
    cat("\n")
  }
  cat("\n")
}

# Summary
cat("Summary:\n")
cat("  Total factor variables:", length(factor_vars), "\n")
cat("  Suitable for multinomial (3+ levels):", length(multinomial_suitable), "\n")
if (length(multinomial_suitable) > 0) {
  cat("    →", paste(multinomial_suitable, collapse = ", "), "\n")
}
cat("\n")

cat("========================================\n\n")

# ==============================================================================
# ADD GEOGRAPHIC COORDINATES FOR MAPPING
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

# Get county centroids (using ggplot2::map_data)
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
cat(
  "  Counties with coordinates:",
  format(coords_added, big.mark = ","),
  "out of",
  format(nrow(food_data), big.mark = ","),
  sprintf(" (%.1f%%)\n", coords_added / nrow(food_data) * 100)
)

# For counties without coordinates, use state centers
if (sum(is.na(food_data$lon)) > 0) {
  cat("  Adding state center coordinates for remaining counties...\n")

  # State centers (approximate)
  state_centers <- tibble(
    state = state.abb,
    state_lon = c(
      -86.9, -152.0, -111.9, -92.4, -119.4, -105.5, -72.7, -75.5, -81.5,
      -83.5, -157.5, -114.7, -89.4, -86.3, -93.1, -98.0, -84.9, -92.0,
      -69.4, -76.6, -71.4, -84.5, -94.6, -89.7, -92.3, -109.5, -100.0,
      -117.0, -71.5, -74.4, -106.0, -74.0, -79.0, -100.0, -82.9, -97.5,
      -120.5, -77.0, -71.5, -80.5, -99.9, -111.5, -72.6, -78.6, -100.0,
      -79.5, -120.5, -80.5, -89.5, -107.5
    ),
    state_lat = c(
      32.8, 64.0, 34.0, 35.0, 37.0, 39.0, 41.6, 39.0, 28.0,
      33.0, 20.0, 44.0, 40.0, 40.0, 42.0, 38.5, 37.8, 31.0,
      45.0, 39.0, 42.3, 43.0, 46.0, 32.0, 38.6, 47.0, 41.5,
      39.0, 43.2, 40.0, 34.5, 43.0, 35.5, 47.5, 40.4, 35.5,
      44.5, 41.0, 41.7, 34.0, 44.5, 39.3, 44.0, 37.5, 31.0,
      38.5, 47.5, 39.0, 43.0, 43.0
    )
  )

  food_data <- food_data %>%
    left_join(state_centers, by = "state") %>%
    mutate(
      lon = coalesce(lon, state_lon),
      lat = coalesce(lat, state_lat)
    ) %>%
    select(-state_lon, -state_lat)

  cat("  ✓ State centers used for remaining counties\n")
}
cat("\n")

# ==============================================================================
# SET GLOBAL GGPLOT THEME
# ==============================================================================

cat("Setting global ggplot theme...\n")

bs_theme <- theme(
  text = element_text(family = "Arial", size = 14, color = "black"),
  plot.title = element_text(
    hjust = 0.5,
    size = 20,
    face = "bold",
    color = "black"
  ),
  plot.subtitle = element_text(
    hjust = 0.5,
    size = 20,
    face = "bold"
  ),
  plot.caption = element_text(
    size = 16,
    color = "gray30",
    hjust = 1,
    face = "italic"
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

theme_set(bs_theme)

cat("✓ ggplot theme set\n\n")

# ==============================================================================
# FINAL STATUS
# ==============================================================================

cat("========================================\n")
cat("✓ READY TO RUN SHINY APP\n")
cat("========================================\n")
cat("Dataset: food_data\n")
cat("  Rows:", format(nrow(food_data), big.mark = ","), "\n")
cat("  Columns:", ncol(food_data), "\n")
cat("  Factor variables:", length(factor_vars), "\n")
if (length(multinomial_suitable) > 0) {
  cat("  Multinomial-ready variables:", length(multinomial_suitable), "\n")
  cat("    →", paste(multinomial_suitable, collapse = ", "), "\n")
}
cat("========================================\n\n")
cat("Loading beautiful KPI cards...\n")
source("R/beautiful_kpi_cards.R")
cat("✓ Beautiful KPI cards loaded\n\n")


cat("Creating state name lookup for maps...\n")

state_name_lookup <- tibble(
  state = c(
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "DC", "FL",
    "GA", "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME",
    "MD", "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH",
    "NJ", "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI",
    "SC", "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"
  ),
  state_name = c(
    "alabama", "alaska", "arizona", "arkansas", "california", "colorado",
    "connecticut", "delaware", "district of columbia", "florida",
    "georgia", "hawaii", "idaho", "illinois", "indiana", "iowa", "kansas",
    "kentucky", "louisiana", "maine",
    "maryland", "massachusetts", "michigan", "minnesota", "mississippi",
    "missouri", "montana", "nebraska", "nevada", "new hampshire",
    "new jersey", "new mexico", "new york", "north carolina", "north dakota",
    "ohio", "oklahoma", "oregon", "pennsylvania", "rhode island",
    "south carolina", "south dakota", "tennessee", "texas", "utah", "vermont",
    "virginia", "washington", "west virginia", "wisconsin", "wyoming"
  )
)

cat("✓ State name lookup created (", nrow(state_name_lookup), " states)\n\n")