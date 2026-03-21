# U.S. Food Insecurity Analytics Platform

A professional interactive dashboard analyzing county-level food insecurity patterns across 3,100+ U.S. counties from 2009 to 2023. Built with Python Streamlit and styled with Tailwind CSS.

---

## Overview

This platform provides policymakers, researchers, and nonprofit practitioners with evidence-based insights into food insecurity disparities, socioeconomic drivers, and intervention impacts. The dashboard integrates data from Feeding America's Map the Meal Gap and the U.S. Census Bureau's American Community Survey.

**Key Numbers:**
- **44.2 million** Americans affected by food insecurity
- **3,100+** counties analyzed
- **15 years** of longitudinal data (2009-2023)
- **47,000+** county-year observations

---

## Features

### 9 Interactive Pages

| Page | Description |
|------|-------------|
| **Home** | Landing page with project overview and key statistics |
| **Executive Overview** | National KPIs, trend analysis, regional comparisons, state rankings |
| **Geographic Intelligence** | Interactive choropleth maps, state drill-down, distribution analysis |
| **Correlation Analysis** | Bivariate correlation testing, scatter plots, correlation matrices |
| **Regression Models** | OLS, Ridge, LASSO, Elastic Net, Random Forest with diagnostics |
| **Equity & Disparities** | Racial/ethnic gaps, urban-rural divide, income inequality analysis |
| **County Clustering** | K-Means clustering with PCA visualization, radar charts, geographic mapping |
| **Time Series Explorer** | Temporal trends, state comparison, pre/post COVID analysis |
| **Policy Scenarios** | Simulate intervention impacts with cost estimation |
| **Data & Downloads** | Browse, filter, and export data in CSV, Excel, or JSON |

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
| Styling | Tailwind CSS (CDN) |
| Charts | Plotly |
| Data | Pandas, NumPy |
| Statistics | scikit-learn, statsmodels, SciPy |
| Maps | Plotly Choropleth |
| Fonts | Inter (Google Fonts) |
| Icons | Font Awesome 6 |

---

## Project Structure

```
gp-food-basket/
├── app.py                          # Landing page
├── requirements.txt                # Python dependencies
├── .streamlit/
│   └── config.toml                 # Streamlit configuration
├── pages/
│   ├── 1_Executive_Overview.py     # National KPIs & trends
│   ├── 2_Geographic_Intelligence.py # Choropleth maps
│   ├── 3_Correlation_Analysis.py   # Correlation testing
│   ├── 4_Regression_Models.py      # Model building
│   ├── 5_Equity_Disparities.py     # Disparity analysis
│   ├── 6_County_Clustering.py      # K-Means clustering
│   ├── 7_Time_Series_Explorer.py   # Temporal analysis
│   ├── 8_Policy_Scenarios.py       # Policy simulation
│   └── 9_Data_Downloads.py         # Data export
├── utils/
│   ├── __init__.py
│   ├── data_loader.py              # Data loading pipeline
│   ├── theme.py                    # Colors, Tailwind injection
│   └── components.py               # Reusable UI components
├── data/
│   ├── feeding_america(2009-2018).xlsx
│   └── feeding_america(2019-2023).xlsx
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
**Course:** DATA-613: Data Science Practicum (Fall 2025)

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
