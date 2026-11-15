"""Every public source the pipeline downloads.

Map the Meal Gap is not listed here: Feeding America releases it only through a
request form, so its files come from the private data repo (see mmg.py) and the
pipeline watches the Feeding America site for new editions instead.
"""

ERS = "https://www.ers.usda.gov/media"
ERR358_PAGE = "https://www.ers.usda.gov/publications/pub-details?pubid=113622"
ERS_KEY_STATS = "https://www.ers.usda.gov/topics/food-nutrition-assistance/food-security-in-the-us/key-statistics-graphics"

# USDA ERS, Household Food Security in the United States in 2024 (ERR-358).
# The chart data files on the key statistics page.
USDA_FILES = {
    "usda-trends": f"{ERS}/6990/trends.xlsx",
    "usda-mapdata": f"{ERS}/6988/mapdata.xlsx",
    "usda-insecurity": f"{ERS}/6987/insecurity.xlsx",
    "usda-verylow": f"{ERS}/6991/verylow.xlsx",
    "usda-householdpie": f"{ERS}/6986/householdpie.xlsx",
    "usda-foodsecurepie": f"{ERS}/6985/foodsecurepie.xlsx",
    "usda-interactive": f"{ERS}/649/data-file-for-interactive-charts.xlsx",
    "usda-err358-pdf": f"{ERS}/9161/err-358.pdf",
}

# Census ACS 5-year detailed tables, with margins of error.
# B22003: households receiving SNAP in the past 12 months.
# B17001: people by poverty status in the past 12 months.
ACS_VARS = [
    "NAME",
    "B22003_001E", "B22003_001M", "B22003_002E", "B22003_002M",
    "B17001_001E", "B17001_001M", "B17001_002E", "B17001_002M",
]
ACS_FIRST_VINTAGE = 2024
ACS_API = "https://api.census.gov/data/{vintage}/acs/acs5"

# Census cartographic boundary files, 1:20,000,000.
GEO_URL = "https://www2.census.gov/geo/tiger/GENZ{year}/shp/cb_{year}_us_{layer}_20m.zip"

MMG_PAGES = [
    "https://www.feedingamerica.org/research/map-the-meal-gap/by-county",
    "https://www.feedingamerica.org/research/map-the-meal-gap/how-we-got-the-map-data",
]
