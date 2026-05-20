# U.S. Food Insecurity Analytics Platform

An interactive dashboard analyzing county-level food insecurity patterns across 3,100+ U.S. counties from 2009 to 2023. Built with Python Streamlit on a custom editorial design system.

---

## Overview

This platform provides policymakers, researchers, and nonprofit practitioners with evidence-based insights into food insecurity disparities, socioeconomic drivers, and intervention impacts. The dashboard integrates data from Feeding America's Map the Meal Gap and the U.S. Census Bureau's American Community Survey.

**Key Numbers:**
- **Tens of millions** of Americans affected by food insecurity each year — the current national figure is computed live from Feeding America's MMG data on the dashboard's home page (year-stamped + source-cited)
- **3,100+** counties analyzed
- **15 years** of longitudinal data (2009-2023)
- **47,000+** county-year observations

---

## Features

### 13 Interactive Pages

| Page | Description |
|------|-------------|
| **Home** | Landing page with audience-routed CTAs (policymaker / nonprofit / researcher) and live KPIs |
| **Executive Overview** | National KPIs, weighted-rate trends, disparity snapshot, counties-in-crisis callout |
| **Geographic Intelligence** | Interactive choropleth maps, urban/rural filter, state drill-down |
| **Data Explorer** | Exploratory data analysis — summary stats, missingness, distributions, box plots, pair plots, rankings |
| **Correlation Analysis** | Bivariate correlation testing, scatter plots, correlation matrices |
| **Regression Models** | OLS, Ridge, LASSO, Elastic Net, Random Forest with AI-generated interpretation |
| **Equity & Disparities** | Racial/ethnic gaps, urban-rural divide, income inequality analysis |
| **County Clustering** | K-Means clustering with PCA visualization, spatial-contiguity weighting |
| **Time Series Explorer** | Temporal trends, state comparison, pre/post COVID analysis |
| **Policy Scenarios** | Difference-in-Differences causal inference + predictive scenario simulation |
| **Data & Downloads** | Browse, filter, and export data in CSV, Excel, or JSON |
| **AI Data Analyst** | Plain-English questions answered by Gemini 2.5 Flash with a code-execution sandbox |
| **Anomaly Detection** | Isolation Forests scanning for counties with severe macroeconomic decoupling |

### Key Capabilities

- **Interactive Plotly Charts** with hover tooltips and zoom
- **Tailwind CSS** styled UI with gradient KPI cards and responsive layout
- **State & County Drill-Down** for geographic analysis
- **Multiple Regression Models** including ensemble methods
- **K-Means Clustering** with PCA projection and silhouette scoring
- **Policy Simulation** with scenario comparison and cost estimation
- **Data Export** in CSV, Excel, and JSON formats

---

## Tech Stack

| Component | Technology |
|-----------|------------|
| Framework | Python Streamlit |
| Styling | Custom editorial design system (light/pearl tokens, Georgia headlines) |
| Charts | Plotly |
| Data | Pandas, NumPy |
| Statistics | scikit-learn, statsmodels, SciPy |
| Maps | Plotly Choropleth |
| AI | Gemini 2.5 Flash + Groq (LLM fallback chain), LangChain |
| Fonts | Inter + Georgia (Google Fonts) |
| Icons | Font Awesome 6 |

---

## Project Structure

```
gp-food-basket/
├── app.py                          # Streamlit entry point + global nav
├── requirements.txt                # Python dependencies
├── pyproject.toml                  # pytest config
├── .github/workflows/tests.yml     # CI: pytest on every PR + push to main
├── .streamlit/
│   └── config.toml                 # Streamlit configuration
├── views/
│   ├── home.py                     # Landing page (audience-routed CTAs)
│   ├── 0_Data_Explorer.py          # EDA: summary stats, distributions
│   ├── 1_Executive_Overview.py     # National KPIs, trends, disparities
│   ├── 2_Geographic_Intelligence.py # Choropleth maps, urban/rural filter
│   ├── 3_Correlation_Analysis.py   # Correlation testing
│   ├── 4_Regression_Models.py      # OLS/Ridge/LASSO/RF + AI interpretation
│   ├── 5_Equity_Disparities.py     # Disparity analysis
│   ├── 6_County_Clustering.py      # K-Means clustering, PCA
│   ├── 7_Time_Series_Explorer.py   # Temporal analysis, SARIMAX
│   ├── 8_Policy_Scenarios.py       # DiD causal inference + simulation
│   ├── 9_Data_Downloads.py         # Data export
│   ├── 10_AI_Data_Analyst.py       # Gemini-powered Q&A with code sandbox
│   ├── 11_Anomaly_Detection.py     # Isolation Forests
│   ├── home.css                    # Home page styles (marketing surface)
│   └── templates/                  # Home page HTML partials
├── utils/
│   ├── data_loader.py              # Data loading + weighted_rate helpers
│   ├── theme.py                    # COLORS palette, design tokens
│   ├── components.py               # Reusable UI components (kpi_row, etc.)
│   ├── navigation.py               # Global navigation ribbon
│   ├── ticker.py                   # Shared FI rate ticker
│   ├── responsive.py               # Viewport-aware chart sizing
│   ├── llm.py                      # Gemini / Groq fallback chain
│   └── nav.css                     # Navigation styles (incl. mobile)
├── tests/                          # pytest suite (run via CI on every PR)
├── data/
│   ├── feeding_america(2009-2018).xlsx
│   └── feeding_america(2019-2023).xlsx
├── Project Documents/              # Tracker, decisions memo, onboarding
└── README.md
```

---

## Installation

### Prerequisites

- Python 3.9 or higher
- pip package manager

### Setup

```bash
# Clone the repository
git clone https://github.com/LinusConradM/gp-food-basket.git
cd gp-food-basket

source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

The app will open at `http://localhost:8501`.

---

## Data Sources

### Feeding America (Primary)

**Map the Meal Gap (2009-2023)**
- County-level food insecurity estimates
- Cost per meal and budget shortfall data
- Child food insecurity rates
- SNAP participation rates

URL: [feedingamerica.org/research/map-the-meal-gap](https://www.feedingamerica.org/research/map-the-meal-gap/by-county)

### U.S. Census Bureau (Secondary)

**American Community Survey 5-Year Estimates**
- Demographic characteristics
- Socioeconomic indicators
- Educational attainment
- Income distribution

URL: [census.gov/data/developers/data-sets/acs-5year.html](https://www.census.gov/data/developers/data-sets/acs-5year.html)

---

## Statistical Methods

| Method | Library | Use Case |
|--------|---------|----------|
| Pearson/Spearman/Kendall Correlation | SciPy | Identify variable relationships |
| Linear Regression (OLS) | statsmodels | Predict continuous outcomes |
| Ridge / LASSO / Elastic Net | scikit-learn | Regularized regression |
| Random Forest | scikit-learn | Non-linear prediction |
| K-Means Clustering | scikit-learn | County segmentation |
| PCA | scikit-learn | Dimensionality reduction |

---

## Author

| Name | Role | GitHub |
|------|------|--------|
| **Conrad Linus Muhirwe** | Full-Stack Developer & Data Scientist | [@LinusConradM](https://github.com/LinusConradM) |

**Institution:** American University, College of Arts & Sciences
**Origin:** Independent research, developed at American University.

---

## Ethics & Data Privacy

- All data are public, de-identified, and aggregated at county level
- No individual-level data is used or stored
- Tool designed for policy analysis and research
- Adheres to ASA Ethical Guidelines for Statistical Practice

---

## License

This work is licensed under the **Creative Commons Attribution 4.0 International License (CC BY 4.0)**.

---

## Citation

```
Muhirwe, C. L. (2025). U.S. Food Insecurity Analytics Platform.
American University. https://github.com/LinusConradM/gp-food-basket

Data sources:
- Feeding America. (2025). Map the Meal Gap. https://www.feedingamerica.org/research/map-the-meal-gap
- U.S. Census Bureau. (2024). American Community Survey 5-Year Estimates. https://www.census.gov/programs-surveys/acs
```

---

## Acknowledgments

- **Feeding America** for comprehensive county-level food insecurity data
- **U.S. Census Bureau** for American Community Survey data
- **American University** for institutional support

---

**Last Updated:** February 2026
**Version:** 2.0.0 (Python/Streamlit)
**Status:** Production Ready
