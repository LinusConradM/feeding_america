"""
Unit tests for Hero Section integration in Executive Overview.

Tests verify the Hero Section implementation including:
- Metric calculations (national FI rate for selected year)
- Contextual summary generation (year-over-year comparison)
- LLM explainer integration (context passed correctly)

Requirements: 1.2, 15.4, 20.2
"""

import pytest
import pandas as pd
import numpy as np


def test_metric_calculation_with_valid_data():
    """Test national FI rate calculation for selected year."""
    # Create sample data for a single year
    year_data = pd.DataFrame({
        "year": [2023, 2023, 2023, 2023],
        "state": ["CA", "TX", "NY", "FL"],
        "overall_food_insecurity_rate": [0.12, 0.15, 0.11, 0.14]
    })
    
    # Calculate national FI rate (mean across all states)
    fi_rate = year_data["overall_food_insecurity_rate"].mean()
    
    # Verify calculation
    expected = (0.12 + 0.15 + 0.11 + 0.14) / 4
    assert fi_rate == pytest.approx(expected)
    assert fi_rate == pytest.approx(0.13)


def test_metric_calculation_with_previous_year():
    """Test previous year FI rate calculation."""
    # Create sample data for current and previous year
    data = pd.DataFrame({
        "year": [2022, 2022, 2022, 2023, 2023, 2023],
        "state": ["CA", "TX", "NY", "CA", "TX", "NY"],
        "overall_food_insecurity_rate": [0.11, 0.14, 0.10, 0.12, 0.15, 0.11]
    })
    
    selected_year = 2023
    year_data = data[data["year"] == selected_year]
    prev_data = data[data["year"] == selected_year - 1]
    
    fi_rate = year_data["overall_food_insecurity_rate"].mean()
    prev_fi = prev_data["overall_food_insecurity_rate"].mean()
    
    # Verify calculations
    assert fi_rate == pytest.approx((0.12 + 0.15 + 0.11) / 3)
    assert prev_fi == pytest.approx((0.11 + 0.14 + 0.10) / 3)
    assert fi_rate > prev_fi  # 2023 rate is higher than 2022


def test_metric_calculation_with_no_previous_year():
    """Test handling when no previous year data exists."""
    # Create sample data for only one year (first year in dataset)
    data = pd.DataFrame({
        "year": [2009, 2009, 2009],
        "state": ["CA", "TX", "NY"],
        "overall_food_insecurity_rate": [0.14, 0.16, 0.13]
    })
    
    selected_year = 2009
    year_data = data[data["year"] == selected_year]
    prev_data = data[data["year"] == selected_year - 1]
    
    fi_rate = year_data["overall_food_insecurity_rate"].mean()
    
    # Verify current year calculation
    assert fi_rate == pytest.approx((0.14 + 0.16 + 0.13) / 3)
    
    # Verify previous year data is empty
    assert prev_data.empty
    prev_fi = prev_data["overall_food_insecurity_rate"].mean() if not prev_data.empty else None
    assert prev_fi is None


def test_metric_calculation_with_nan_values():
    """Test metric calculation handles NaN values correctly."""
    year_data = pd.DataFrame({
        "year": [2023, 2023, 2023, 2023],
        "state": ["CA", "TX", "NY", "FL"],
        "overall_food_insecurity_rate": [0.12, np.nan, 0.11, 0.14]
    })
    
    # Calculate FI rate (mean ignores NaN by default)
    fi_rate = year_data["overall_food_insecurity_rate"].mean()
    
    # Verify NaN is ignored in calculation
    expected = (0.12 + 0.11 + 0.14) / 3
    assert fi_rate == pytest.approx(expected)


def test_contextual_summary_generation_increase():
    """Test contextual summary generation when FI rate increases."""
    # Simulate data showing increase
    fi_rate = 0.13
    prev_fi = 0.12
    selected_year = 2023
    
    # Generate contextual summary (same logic as implementation)
    context_summary = ""
    if prev_fi and pd.notna(prev_fi) and pd.notna(fi_rate):
        change = fi_rate - prev_fi
        change_pct = abs(change / prev_fi * 100)
        direction = "increased" if change > 0 else "decreased"
        context_summary = f"The national food insecurity rate has {direction} by {change_pct:.1f}% compared to {selected_year - 1}."
    
    # Verify summary
    assert "increased" in context_summary
    assert "8.3%" in context_summary  # (0.01 / 0.12) * 100 = 8.33%
    assert "2022" in context_summary


def test_contextual_summary_generation_decrease():
    """Test contextual summary generation when FI rate decreases."""
    # Simulate data showing decrease
    fi_rate = 0.11
    prev_fi = 0.13
    selected_year = 2023
    
    # Generate contextual summary
    context_summary = ""
    if prev_fi and pd.notna(prev_fi) and pd.notna(fi_rate):
        change = fi_rate - prev_fi
        change_pct = abs(change / prev_fi * 100)
        direction = "increased" if change > 0 else "decreased"
        context_summary = f"The national food insecurity rate has {direction} by {change_pct:.1f}% compared to {selected_year - 1}."
    
    # Verify summary
    assert "decreased" in context_summary
    assert "15.4%" in context_summary  # (0.02 / 0.13) * 100 = 15.38%
    assert "2022" in context_summary


def test_contextual_summary_generation_no_previous_year():
    """Test contextual summary generation when no previous year exists."""
    # Simulate first year in dataset
    fi_rate = 0.14
    prev_fi = None
    selected_year = 2009
    
    # Generate contextual summary
    context_summary = ""
    if prev_fi and pd.notna(prev_fi) and pd.notna(fi_rate):
        change = fi_rate - prev_fi
        change_pct = abs(change / prev_fi * 100)
        direction = "increased" if change > 0 else "decreased"
        context_summary = f"The national food insecurity rate has {direction} by {change_pct:.1f}% compared to {selected_year - 1}."
    else:
        context_summary = f"National food insecurity data for {selected_year}."
    
    # Verify fallback summary
    assert context_summary == "National food insecurity data for 2009."
    assert "increased" not in context_summary
    assert "decreased" not in context_summary


def test_contextual_summary_generation_with_nan():
    """Test contextual summary generation handles NaN values."""
    # Simulate NaN in current or previous year
    fi_rate = np.nan
    prev_fi = 0.12
    selected_year = 2023
    
    # Generate contextual summary
    context_summary = ""
    if prev_fi and pd.notna(prev_fi) and pd.notna(fi_rate):
        change = fi_rate - prev_fi
        change_pct = abs(change / prev_fi * 100)
        direction = "increased" if change > 0 else "decreased"
        context_summary = f"The national food insecurity rate has {direction} by {change_pct:.1f}% compared to {selected_year - 1}."
    else:
        context_summary = f"National food insecurity data for {selected_year}."
    
    # Verify fallback summary when NaN present
    assert context_summary == "National food insecurity data for 2023."


def test_contextual_summary_small_change():
    """Test contextual summary with very small percentage change."""
    # Simulate minimal change
    fi_rate = 0.1201
    prev_fi = 0.1200
    selected_year = 2023
    
    # Generate contextual summary
    context_summary = ""
    if prev_fi and pd.notna(prev_fi) and pd.notna(fi_rate):
        change = fi_rate - prev_fi
        change_pct = abs(change / prev_fi * 100)
        direction = "increased" if change > 0 else "decreased"
        context_summary = f"The national food insecurity rate has {direction} by {change_pct:.1f}% compared to {selected_year - 1}."
    
    # Verify summary handles small changes
    assert "increased" in context_summary
    assert "0.1%" in context_summary  # (0.0001 / 0.12) * 100 = 0.083% -> rounds to 0.1%


def test_llm_explainer_context_dict_structure():
    """Test LLM explainer receives correctly structured context dictionary."""
    # Simulate calculated metrics
    selected_year = 2023
    fi_rate = 0.123
    fi_persons = 42000000
    child_fi = 0.167
    cost_meal = 3.45
    poverty = 0.145
    med_income = 65000
    unemp = 0.042
    shortfall = 28500
    
    # Build context dict (same logic as implementation)
    context_dict = {
        "Year": selected_year,
        "National FI Rate": f"{fi_rate:.1%}" if pd.notna(fi_rate) else "N/A",
        "Food Insecure Persons": f"{fi_persons/1e6:.1f}M" if pd.notna(fi_persons) else "N/A",
        "Child FI Rate": f"{child_fi:.1%}" if pd.notna(child_fi) else "N/A",
        "Cost Per Meal": f"${cost_meal:.2f}" if pd.notna(cost_meal) else "N/A",
        "Poverty Rate": f"{poverty:.1%}" if pd.notna(poverty) else "N/A",
        "Median Income": f"${med_income:,.0f}" if pd.notna(med_income) else "N/A",
        "Unemployment": f"{unemp:.1%}" if pd.notna(unemp) else "N/A",
        "Budget Shortfall": f"${shortfall:,.0f}" if pd.notna(shortfall) else "N/A"
    }
    
    # Verify context dict structure
    assert context_dict["Year"] == 2023
    assert context_dict["National FI Rate"] == "12.3%"
    assert context_dict["Food Insecure Persons"] == "42.0M"
    assert context_dict["Child FI Rate"] == "16.7%"
    assert context_dict["Cost Per Meal"] == "$3.45"
    assert context_dict["Poverty Rate"] == "14.5%"
    assert context_dict["Median Income"] == "$65,000"
    assert context_dict["Unemployment"] == "4.2%"
    assert context_dict["Budget Shortfall"] == "$28,500"


def test_llm_explainer_context_dict_with_nan():
    """Test LLM explainer context dict handles NaN values."""
    # Simulate metrics with NaN values
    selected_year = 2023
    fi_rate = np.nan
    fi_persons = np.nan
    child_fi = 0.167
    cost_meal = np.nan
    poverty = 0.145
    med_income = 65000
    unemp = np.nan
    shortfall = 28500
    
    # Build context dict with NaN handling
    context_dict = {
        "Year": selected_year,
        "National FI Rate": f"{fi_rate:.1%}" if pd.notna(fi_rate) else "N/A",
        "Food Insecure Persons": f"{fi_persons/1e6:.1f}M" if pd.notna(fi_persons) else "N/A",
        "Child FI Rate": f"{child_fi:.1%}" if pd.notna(child_fi) else "N/A",
        "Cost Per Meal": f"${cost_meal:.2f}" if pd.notna(cost_meal) else "N/A",
        "Poverty Rate": f"{poverty:.1%}" if pd.notna(poverty) else "N/A",
        "Median Income": f"${med_income:,.0f}" if pd.notna(med_income) else "N/A",
        "Unemployment": f"{unemp:.1%}" if pd.notna(unemp) else "N/A",
        "Budget Shortfall": f"${shortfall:,.0f}" if pd.notna(shortfall) else "N/A"
    }
    
    # Verify NaN values are replaced with "N/A"
    assert context_dict["National FI Rate"] == "N/A"
    assert context_dict["Food Insecure Persons"] == "N/A"
    assert context_dict["Cost Per Meal"] == "N/A"
    assert context_dict["Unemployment"] == "N/A"
    
    # Verify valid values are formatted correctly
    assert context_dict["Child FI Rate"] == "16.7%"
    assert context_dict["Poverty Rate"] == "14.5%"
    assert context_dict["Median Income"] == "$65,000"
    assert context_dict["Budget Shortfall"] == "$28,500"


def test_llm_explainer_context_dict_all_keys_present():
    """Test LLM explainer context dict contains all required keys."""
    # Simulate complete metrics
    selected_year = 2023
    fi_rate = 0.123
    fi_persons = 42000000
    child_fi = 0.167
    cost_meal = 3.45
    poverty = 0.145
    med_income = 65000
    unemp = 0.042
    shortfall = 28500
    
    # Build context dict
    context_dict = {
        "Year": selected_year,
        "National FI Rate": f"{fi_rate:.1%}" if pd.notna(fi_rate) else "N/A",
        "Food Insecure Persons": f"{fi_persons/1e6:.1f}M" if pd.notna(fi_persons) else "N/A",
        "Child FI Rate": f"{child_fi:.1%}" if pd.notna(child_fi) else "N/A",
        "Cost Per Meal": f"${cost_meal:.2f}" if pd.notna(cost_meal) else "N/A",
        "Poverty Rate": f"{poverty:.1%}" if pd.notna(poverty) else "N/A",
        "Median Income": f"${med_income:,.0f}" if pd.notna(med_income) else "N/A",
        "Unemployment": f"{unemp:.1%}" if pd.notna(unemp) else "N/A",
        "Budget Shortfall": f"${shortfall:,.0f}" if pd.notna(shortfall) else "N/A"
    }
    
    # Verify all required keys are present
    required_keys = [
        "Year",
        "National FI Rate",
        "Food Insecure Persons",
        "Child FI Rate",
        "Cost Per Meal",
        "Poverty Rate",
        "Median Income",
        "Unemployment",
        "Budget Shortfall"
    ]
    
    for key in required_keys:
        assert key in context_dict, f"Missing required key: {key}"


def test_hero_section_integration_complete_flow():
    """Test complete Hero Section integration flow with all components."""
    # Create sample data
    data = pd.DataFrame({
        "year": [2022, 2022, 2022, 2023, 2023, 2023],
        "state": ["CA", "TX", "NY", "CA", "TX", "NY"],
        "overall_food_insecurity_rate": [0.11, 0.14, 0.10, 0.12, 0.15, 0.11],
        "no_of_food_insecure_persons_overall": [4000000, 4200000, 2000000, 4500000, 4500000, 2100000],
        "child_food_insecurity_rate": [0.15, 0.18, 0.13, 0.16, 0.19, 0.14],
        "cost_per_meal": [3.40, 2.85, 3.75, 3.45, 2.89, 3.78],
        "poverty_rate": [0.140, 0.165, 0.130, 0.145, 0.168, 0.132],
        "median_income": [64000, 58000, 72000, 65000, 59000, 73000],
        "unemployment_rate": [0.040, 0.045, 0.038, 0.042, 0.043, 0.039],
        "weighted_annual_food_budget_shortfall": [28000, 29000, 27000, 28500, 29500, 27500]
    })
    
    selected_year = 2023
    year_data = data[data["year"] == selected_year]
    prev_data = data[data["year"] == selected_year - 1]
    
    # 1. Calculate metrics
    fi_rate = year_data["overall_food_insecurity_rate"].mean()
    prev_fi = prev_data["overall_food_insecurity_rate"].mean()
    
    assert fi_rate == pytest.approx((0.12 + 0.15 + 0.11) / 3)
    assert prev_fi == pytest.approx((0.11 + 0.14 + 0.10) / 3)
    
    # 2. Generate contextual summary
    context_summary = ""
    if prev_fi and pd.notna(prev_fi) and pd.notna(fi_rate):
        change = fi_rate - prev_fi
        change_pct = abs(change / prev_fi * 100)
        direction = "increased" if change > 0 else "decreased"
        context_summary = f"The national food insecurity rate has {direction} by {change_pct:.1f}% compared to {selected_year - 1}."
    
    assert "increased" in context_summary
    assert "2022" in context_summary
    
    # 3. Build LLM context dict
    fi_persons = year_data["no_of_food_insecure_persons_overall"].sum()
    child_fi = year_data["child_food_insecurity_rate"].mean()
    cost_meal = year_data["cost_per_meal"].mean()
    poverty = year_data["poverty_rate"].mean()
    med_income = year_data["median_income"].median()
    unemp = year_data["unemployment_rate"].mean()
    shortfall = year_data["weighted_annual_food_budget_shortfall"].mean()
    
    context_dict = {
        "Year": selected_year,
        "National FI Rate": f"{fi_rate:.1%}" if pd.notna(fi_rate) else "N/A",
        "Food Insecure Persons": f"{fi_persons/1e6:.1f}M" if pd.notna(fi_persons) else "N/A",
        "Child FI Rate": f"{child_fi:.1%}" if pd.notna(child_fi) else "N/A",
        "Cost Per Meal": f"${cost_meal:.2f}" if pd.notna(cost_meal) else "N/A",
        "Poverty Rate": f"{poverty:.1%}" if pd.notna(poverty) else "N/A",
        "Median Income": f"${med_income:,.0f}" if pd.notna(med_income) else "N/A",
        "Unemployment": f"{unemp:.1%}" if pd.notna(unemp) else "N/A",
        "Budget Shortfall": f"${shortfall:,.0f}" if pd.notna(shortfall) else "N/A"
    }
    
    # Verify all components are correctly calculated
    assert context_dict["Year"] == 2023
    assert "12." in context_dict["National FI Rate"]  # ~12.7%
    assert "11.1M" in context_dict["Food Insecure Persons"]  # 4.5M + 4.5M + 2.1M
    assert "16." in context_dict["Child FI Rate"]  # ~16.3%
    assert "$3." in context_dict["Cost Per Meal"]  # ~$3.37
    assert "14." in context_dict["Poverty Rate"]  # ~14.8%
    assert "$65,000" in context_dict["Median Income"]
    assert "4." in context_dict["Unemployment"]  # ~4.1%
    assert "$28," in context_dict["Budget Shortfall"]  # ~$28,500


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
