"""
Data loading and cleaning pipeline.
Replicates the global.R data processing for the Food Insecurity Dashboard.
"""

import pandas as pd
import numpy as np
import streamlit as st
from pathlib import Path

# State FIPS lookup
STATE_FIPS = {
    1: "AL", 2: "AK", 4: "AZ", 5: "AR", 6: "CA", 8: "CO", 9: "CT",
    10: "DE", 11: "DC", 12: "FL", 13: "GA", 15: "HI", 16: "ID", 17: "IL",
    18: "IN", 19: "IA", 20: "KS", 21: "KY", 22: "LA", 23: "ME", 24: "MD",
    25: "MA", 26: "MI", 27: "MN", 28: "MS", 29: "MO", 30: "MT", 31: "NE",
    32: "NV", 33: "NH", 34: "NJ", 35: "NM", 36: "NY", 37: "NC", 38: "ND",
    39: "OH", 40: "OK", 41: "OR", 42: "PA", 44: "RI", 45: "SC", 46: "SD",
    47: "TN", 48: "TX", 49: "UT", 50: "VT", 51: "VA", 53: "WA", 54: "WV",
    55: "WI", 56: "WY",
}

STATE_NAMES = {
    "AL": "Alabama", "AK": "Alaska", "AZ": "Arizona", "AR": "Arkansas",
    "CA": "California", "CO": "Colorado", "CT": "Connecticut", "DE": "Delaware",
    "DC": "District of Columbia", "FL": "Florida", "GA": "Georgia", "HI": "Hawaii",
    "ID": "Idaho", "IL": "Illinois", "IN": "Indiana", "IA": "Iowa",
    "KS": "Kansas", "KY": "Kentucky", "LA": "Louisiana", "ME": "Maine",
    "MD": "Maryland", "MA": "Massachusetts", "MI": "Michigan", "MN": "Minnesota",
    "MS": "Mississippi", "MO": "Missouri", "MT": "Montana", "NE": "Nebraska",
    "NV": "Nevada", "NH": "New Hampshire", "NJ": "New Jersey", "NM": "New Mexico",
    "NY": "New York", "NC": "North Carolina", "ND": "North Dakota", "OH": "Ohio",
    "OK": "Oklahoma", "OR": "Oregon", "PA": "Pennsylvania", "RI": "Rhode Island",
    "SC": "South Carolina", "SD": "South Dakota", "TN": "Tennessee", "TX": "Texas",
    "UT": "Utah", "VT": "Vermont", "VA": "Virginia", "WA": "Washington",
    "WV": "West Virginia", "WI": "Wisconsin", "WY": "Wyoming",
}

STATE_CENTERS = {
    "AL": (-86.9, 32.8), "AK": (-152.0, 64.0), "AZ": (-111.9, 34.0),
    "AR": (-92.4, 35.0), "CA": (-119.4, 37.0), "CO": (-105.5, 39.0),
    "CT": (-72.7, 41.6), "DE": (-75.5, 39.0), "DC": (-77.0, 38.9),
    "FL": (-81.5, 28.0), "GA": (-83.5, 33.0), "HI": (-157.5, 20.0),
    "ID": (-114.7, 44.0), "IL": (-89.4, 40.0), "IN": (-86.3, 40.0),
    "IA": (-93.1, 42.0), "KS": (-98.0, 38.5), "KY": (-84.9, 37.8),
    "LA": (-92.0, 31.0), "ME": (-69.4, 45.0), "MD": (-76.6, 39.0),
    "MA": (-71.4, 42.3), "MI": (-84.5, 43.0), "MN": (-94.6, 46.0),
    "MS": (-89.7, 32.0), "MO": (-92.3, 38.6), "MT": (-109.5, 47.0),
    "NE": (-100.0, 41.5), "NV": (-117.0, 39.0), "NH": (-71.5, 43.2),
    "NJ": (-74.4, 40.0), "NM": (-106.0, 34.5), "NY": (-74.0, 43.0),
    "NC": (-79.0, 35.5), "ND": (-100.0, 47.5), "OH": (-82.9, 40.4),
    "OK": (-97.5, 35.5), "OR": (-120.5, 44.5), "PA": (-77.0, 41.0),
    "RI": (-71.5, 41.7), "SC": (-80.5, 34.0), "SD": (-99.9, 44.5),
    "TN": (-86.5, 35.5), "TX": (-100.0, 31.0), "UT": (-111.5, 39.3),
    "VT": (-72.6, 44.0), "VA": (-78.6, 37.5), "WA": (-120.5, 47.5),
    "WV": (-80.5, 39.0), "WI": (-89.5, 43.0), "WY": (-107.5, 43.0),
}

CHARACTER_COLS = [
    "state", "fa_state", "county_state", "county", "fips",
    "census_region", "census_division", "fns_region",
    "low_threshold_type", "high_threshold_type", "year_group",
]


def _clean_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """Replicate janitor::clean_names() - snake_case column names."""
    import re
    new_cols = {}
    for col in df.columns:
        clean = col.strip()
        clean = re.sub(r"[^\w\s]", "_", clean)
        clean = re.sub(r"\s+", "_", clean)
        clean = re.sub(r"_+", "_", clean)
        clean = clean.strip("_").lower()
        new_cols[col] = clean
    return df.rename(columns=new_cols)


def _clean_na_strings(df: pd.DataFrame) -> pd.DataFrame:
    """Replace string 'NA' and 'n/a' with actual NaN."""
    str_cols = df.select_dtypes(include="object").columns
    for col in str_cols:
        df[col] = df[col].str.strip()
        df.loc[df[col].isin(["NA", "n/a"]), col] = np.nan
    return df


def _convert_types(df: pd.DataFrame) -> pd.DataFrame:
    """Convert columns to appropriate types."""
    # Handle duplicate columns first
    df = df.loc[:, ~df.columns.duplicated()].copy()

    obj_cols = df.select_dtypes(include="object").columns
    for col in obj_cols:
        if col in CHARACTER_COLS or col == "year":
            continue
        try:
            df[col] = pd.to_numeric(df[col], errors="coerce")
        except (ValueError, TypeError):
            pass
    if "year" in df.columns:
        df["year"] = pd.to_numeric(df["year"], errors="coerce").astype("Int64")
    return df


@st.cache_data(show_spinner="Loading food insecurity data...")
def load_data() -> pd.DataFrame:
    """Load and process the food insecurity dataset (replicates global.R)."""
    base = Path(__file__).resolve().parent.parent / "data"

    # Load Excel files
    fa_pre = pd.read_excel(base / "feeding_america(2009-2018).xlsx")
    fa_post = pd.read_excel(base / "feeding_america(2019-2023).xlsx")

    # Clean column names
    fa_pre = _clean_column_names(fa_pre)
    fa_post = _clean_column_names(fa_post)

    # Clean NA strings
    fa_pre = _clean_na_strings(fa_pre)
    fa_post = _clean_na_strings(fa_post)

    # Convert state FIPS to abbreviation for post-2019 data
    if "state" in fa_post.columns:
        state_numeric = pd.to_numeric(fa_post["state"], errors="coerce")
        if state_numeric.notna().any():
            fa_post["state"] = state_numeric.map(STATE_FIPS).fillna(fa_post["state"])

    # Add year group
    fa_pre["year_group"] = "2009-2018"
    fa_post["year_group"] = "2019-2023"

    # Convert types
    fa_pre = _convert_types(fa_pre)
    fa_post = _convert_types(fa_post)

    # Ensure character columns are strings
    for col in CHARACTER_COLS:
        if col in fa_pre.columns:
            fa_pre[col] = fa_pre[col].astype(str).replace("nan", np.nan)
        if col in fa_post.columns:
            fa_post[col] = fa_post[col].astype(str).replace("nan", np.nan)

    # Combine datasets
    food_data = pd.concat([fa_pre, fa_post], ignore_index=True)

    # Remove duplicates
    food_data = food_data.drop_duplicates(subset=["fips", "year"], keep="first")
    food_data = food_data.sort_values(["fips", "year"]).reset_index(drop=True)

    # Extract county name
    if "county_state" in food_data.columns:
        food_data["county"] = food_data["county_state"].str.replace(r",.*$", "", regex=True)

    # Derived variables
    food_data["urban_rural"] = pd.cut(
        food_data["population"],
        bins=[-np.inf, 20000, 100000, np.inf],
        labels=["Rural", "Non-metro", "Metro"],
    )

    food_data["fi_category"] = pd.cut(
        food_data["overall_food_insecurity_rate"],
        bins=[-np.inf, 0.10, 0.15, 0.20, np.inf],
        labels=["Low", "Moderate", "High", "Very High"],
    )

    food_data["poverty_category"] = pd.cut(
        food_data["poverty_rate"],
        bins=[-np.inf, 0.10, 0.15, 0.20, np.inf],
        labels=["Low", "Medium", "High", "Very High"],
    )

    food_data["income_category"] = pd.cut(
        food_data["median_income"],
        bins=[-np.inf, 40000, 60000, np.inf],
        labels=["Low", "Medium", "High"],
    )

    food_data["education_category"] = pd.cut(
        food_data["hs_or_less"],
        bins=[-np.inf, 0.15, 0.25, np.inf],
        labels=["High Education", "Medium Education", "Low Education"],
    )

    # Add state full name
    food_data["state_name"] = food_data["state"].map(STATE_NAMES)

    # Add geographic coordinates (state centers as fallback)
    food_data["lat"] = food_data["state"].map(
        lambda s: STATE_CENTERS.get(s, (0, 0))[1] if pd.notna(s) else np.nan
    )
    food_data["lon"] = food_data["state"].map(
        lambda s: STATE_CENTERS.get(s, (0, 0))[0] if pd.notna(s) else np.nan
    )

    return food_data


def weighted_rate(df: pd.DataFrame, col: str, weight_col: str = "population") -> float:
    """Population-weighted mean for rate columns. Falls back to unweighted if weights unavailable."""
    if weight_col not in df.columns:
        return df[col].mean()
    valid = df[[col, weight_col]].dropna()
    if valid.empty or valid[weight_col].sum() == 0:
        return df[col].mean()
    return np.average(valid[col], weights=valid[weight_col])


def weighted_rate_by_group(df: pd.DataFrame, value_col: str, group_col: str, weight_col: str = "population") -> pd.Series:
    """Population-weighted mean grouped by a column (e.g., year or state)."""
    def _wm(group):
        if weight_col not in group.columns:
            return group[value_col].mean()
        valid = group[[value_col, weight_col]].dropna()
        if valid.empty or valid[weight_col].sum() == 0:
            return group[value_col].mean()
        return np.average(valid[value_col], weights=valid[weight_col])
    return df.groupby(group_col, observed=True).apply(_wm)


def get_numeric_columns(df: pd.DataFrame) -> list:
    """Get numeric columns suitable for analysis (excludes IDs, coordinates)."""
    exclude = {"fips", "lat", "lon", "year", "state_fips"}
    return [
        col for col in df.select_dtypes(include=[np.number]).columns
        if col not in exclude
    ]


def get_variable_label(col_name: str) -> str:
    """Convert column name to a nice display label."""
    labels = {
        "overall_food_insecurity_rate": "Food Insecurity Rate",
        "child_food_insecurity_rate": "Child Food Insecurity Rate",
        "poverty_rate": "Poverty Rate",
        "median_income": "Median Household Income",
        "unemployment_rate": "Unemployment Rate",
        "cost_per_meal": "Cost Per Meal",
        "population": "Population",
        "snap_rate": "SNAP Participation Rate",
        "weighted_annual_food_budget_shortfall": "Annual Food Budget Shortfall",
        "no_of_food_insecure_persons_overall": "Food Insecure Persons",
        "no_of_food_insecure_children": "Food Insecure Children",
        "hs_or_less": "High School or Less (%)",
        "black_pct": "Black Population (%)",
        "hispanic_pct": "Hispanic Population (%)",
        "female_headed": "Female-Headed Households (%)",
        "no_vehicle": "No Vehicle (%)",
        "gini": "Gini Coefficient",
    }
    if col_name in labels:
        return labels[col_name]
    return col_name.replace("_", " ").title()
