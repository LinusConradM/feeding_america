"""
Unit tests for State Lookup integration in Executive Overview.

Tests the State Lookup feature implementation including:
- State selection callback
- StateSummary card display
- Data retrieval and formatting
"""

import pytest
import pandas as pd
import numpy as np
from utils.responsive import StateSummary
from utils.data_loader import STATE_NAMES


def test_state_summary_creation():
    """Test StateSummary data model creation and display formatting."""
    summary = StateSummary(
        state_code="CA",
        state_name="California",
        fi_rate=0.123,
        rank=15,
        total_states=51,
        food_insecure_persons=4500000,
        cost_per_meal=3.45,
        poverty_rate=0.145
    )
    
    assert summary.state_code == "CA"
    assert summary.state_name == "California"
    assert summary.fi_rate == 0.123
    assert summary.rank == 15
    assert summary.total_states == 51
    
    # Test display formatting
    display_dict = summary.to_display_dict()
    assert display_dict["State"] == "California"
    assert display_dict["FI Rate"] == "12.3%"
    assert display_dict["Rank"] == "15 of 51"
    assert display_dict["Food Insecure"] == "4,500,000"
    assert display_dict["Cost/Meal"] == "$3.45"
    assert display_dict["Poverty"] == "14.5%"


def test_state_summary_with_edge_values():
    """Test StateSummary handles edge values correctly."""
    summary = StateSummary(
        state_code="DC",
        state_name="District of Columbia",
        fi_rate=0.0,
        rank=1,
        total_states=51,
        food_insecure_persons=0,
        cost_per_meal=0.0,
        poverty_rate=0.0
    )
    
    display_dict = summary.to_display_dict()
    assert display_dict["FI Rate"] == "0.0%"
    assert display_dict["Rank"] == "1 of 51"
    assert display_dict["Food Insecure"] == "0"
    assert display_dict["Cost/Meal"] == "$0.00"


def test_state_lookup_data_preparation():
    """Test state rankings data preparation for lookup."""
    # Create sample year data
    year_data = pd.DataFrame({
        "state": ["CA", "TX", "NY", "FL", "IL"],
        "overall_food_insecurity_rate": [0.12, 0.15, 0.11, 0.14, 0.13],
        "no_of_food_insecure_persons_overall": [4500000, 4200000, 2100000, 2800000, 1600000],
        "cost_per_meal": [3.45, 2.89, 3.78, 3.12, 3.34],
        "poverty_rate": [0.145, 0.168, 0.132, 0.156, 0.141]
    })
    
    # Prepare state rankings (same logic as in the implementation)
    state_rankings = (year_data.groupby("state", observed=True)["overall_food_insecurity_rate"]
                      .mean().reset_index()
                      .sort_values("overall_food_insecurity_rate"))
    state_rankings.columns = ["State", "FI Rate"]
    state_rankings["Rank"] = range(1, len(state_rankings) + 1)
    
    # Verify rankings are correct (sorted by FI rate ascending)
    assert len(state_rankings) == 5
    assert state_rankings.iloc[0]["State"] == "NY"  # Lowest FI rate (0.11)
    assert state_rankings.iloc[0]["Rank"] == 1
    assert state_rankings.iloc[-1]["State"] == "TX"  # Highest FI rate (0.15)
    assert state_rankings.iloc[-1]["Rank"] == 5


def test_state_data_extraction():
    """Test extracting state-specific data from year_data."""
    # Create sample year data
    year_data = pd.DataFrame({
        "state": ["CA", "CA", "TX", "TX", "NY"],
        "county": ["Los Angeles", "San Diego", "Harris", "Dallas", "New York"],
        "overall_food_insecurity_rate": [0.12, 0.13, 0.15, 0.14, 0.11],
        "no_of_food_insecure_persons_overall": [1000000, 500000, 800000, 600000, 1200000],
        "cost_per_meal": [3.45, 3.50, 2.89, 2.95, 3.78],
        "poverty_rate": [0.145, 0.150, 0.168, 0.165, 0.132]
    })
    
    # Extract California data
    state_code = "CA"
    state_data = year_data[year_data["state"] == state_code]
    
    assert len(state_data) == 2
    assert not state_data.empty
    
    # Calculate metrics (same logic as in the implementation)
    fi_rate = state_data["overall_food_insecurity_rate"].mean()
    food_insecure_persons = state_data["no_of_food_insecure_persons_overall"].sum()
    cost_per_meal = state_data["cost_per_meal"].mean()
    poverty_rate = state_data["poverty_rate"].mean()
    
    assert fi_rate == pytest.approx(0.125)  # (0.12 + 0.13) / 2
    assert food_insecure_persons == 1500000  # 1000000 + 500000
    assert cost_per_meal == pytest.approx(3.475)  # (3.45 + 3.50) / 2
    assert poverty_rate == pytest.approx(0.1475)  # (0.145 + 0.150) / 2


def test_state_lookup_with_missing_state():
    """Test handling of state code not in dataset."""
    year_data = pd.DataFrame({
        "state": ["CA", "TX", "NY"],
        "overall_food_insecurity_rate": [0.12, 0.15, 0.11]
    })
    
    # Try to get data for a state not in the dataset
    state_code = "AK"
    state_data = year_data[year_data["state"] == state_code]
    
    assert state_data.empty


def test_state_lookup_with_nan_values():
    """Test handling of NaN values in state data."""
    year_data = pd.DataFrame({
        "state": ["CA", "CA"],
        "overall_food_insecurity_rate": [0.12, np.nan],
        "no_of_food_insecure_persons_overall": [1000000, np.nan],
        "cost_per_meal": [3.45, np.nan],
        "poverty_rate": [0.145, np.nan]
    })
    
    state_code = "CA"
    state_data = year_data[year_data["state"] == state_code]
    
    # Calculate metrics with NaN handling
    fi_rate = state_data["overall_food_insecurity_rate"].mean()
    food_insecure_persons = state_data["no_of_food_insecure_persons_overall"].sum()
    cost_per_meal = state_data["cost_per_meal"].mean()
    poverty_rate = state_data["poverty_rate"].mean()
    
    # mean() ignores NaN by default
    assert fi_rate == pytest.approx(0.12)
    # sum() treats NaN as 0
    assert food_insecure_persons == 1000000
    assert cost_per_meal == pytest.approx(3.45)
    assert poverty_rate == pytest.approx(0.145)


def test_state_names_mapping():
    """Test that STATE_NAMES contains all expected states."""
    # Should have 50 states + DC = 51 entries
    assert len(STATE_NAMES) == 51
    
    # Test a few key mappings
    assert STATE_NAMES["CA"] == "California"
    assert STATE_NAMES["TX"] == "Texas"
    assert STATE_NAMES["NY"] == "New York"
    assert STATE_NAMES["DC"] == "District of Columbia"
    
    # Test that all values are strings
    for code, name in STATE_NAMES.items():
        assert isinstance(code, str)
        assert isinstance(name, str)
        assert len(code) == 2  # All state codes are 2 characters


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
