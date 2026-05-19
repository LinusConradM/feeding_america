---
name: data-scientist
description: >-
  Data science and statistical analysis skill for the gp-food-basket project.
  Use this skill when the user asks for data analysis, statistical testing,
  correlation analysis, regression modeling, clustering, EDA, visualization
  design, feature engineering, anomaly detection, time series analysis, or
  data quality assessment. Triggers on phrases like "analyze the data",
  "run a regression", "find correlations", "cluster counties", "build a model",
  "explore the data", "what patterns exist", "visualize trends", "statistical
  test", or "data quality check".
---

# Data Scientist

> **Read `.claude/skills/_shared/PROJECT_CONTEXT.md` first** for project description, architecture, design tokens, component library, responsive breakpoints, and data access patterns. This skill assumes that context is loaded.

You are a senior data scientist working on the **GP Food Basket** platform — analyzing U.S. county-level food insecurity across 3,100+ counties (2009-2023) using Feeding America Map the Meal Gap + Census ACS data (~47K county-year observations).

## Dataset Overview

### Data Access
```python
from utils.data_loader import load_data, get_numeric_columns, get_variable_label
data = load_data()  # Returns cleaned, feature-engineered DataFrame
```

### Key Variables
| Column | Description | Type |
|--------|-------------|------|
| `fips` | County FIPS code | str |
| `county` | County name | str |
| `state` | State abbreviation | str |
| `year` | Data year (2009-2023) | Int64 |
| `food_insecurity_rate` | % food insecure | float |
| `food_insecure_persons` | Count of food insecure | float |
| `child_food_insecurity_rate` | % children food insecure | float |
| `cost_per_meal` | Avg meal cost ($) | float |
| `weighted_annual_food_budget_shortfall` | Annual budget gap ($) | float |
| `median_household_income` | Median income ($) | float |
| `poverty_rate` | % below poverty line | float |
| `unemployment_rate` | % unemployed | float |
| `homeownership_rate` | % homeowners | float |
| `percent_african_american` | % Black population | float |
| `percent_hispanic` | % Hispanic population | float |
| `percent_with_bachelor_degree_or_higher` | % college educated | float |

### Engineered Features (from data_loader.py)
| Column | Values |
|--------|--------|
| `urban_rural` | Urban (>250K), Suburban (50-250K), Small Town (10-50K), Rural (<10K) |
| `fi_category` | Low (<10%), Moderate (10-15%), High (15-20%), Very High (>20%) |
| `poverty_category` | Low (<10%), Moderate (10-20%), High (>20%) |
| `income_category` | Low, Lower-Middle, Middle, Upper-Middle, High |
| `education_category` | Low, Moderate, High |

### Race-Specific Columns
- `food_insecurity_rate_among_black_persons_all_ethnicities`
- `food_insecurity_rate_among_hispanic_persons_any_race`
- `food_insecurity_rate_among_white_non_hispanic_persons`

## Analysis Patterns

### Statistical Testing
Follow patterns in `views/3_Correlation_Analysis.py`:
```python
from scipy import stats
# Pearson/Spearman/Kendall correlation
r, p = stats.pearsonr(x, y)
r, p = stats.spearmanr(x, y)
tau, p = stats.kendalltau(x, y)
```

### Regression Modeling
Follow patterns in `views/4_Regression_Models.py`:
```python
import statsmodels.api as sm
from sklearn.linear_model import Ridge, Lasso, ElasticNet
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
```

### Clustering
Follow patterns in `views/6_County_Clustering.py`:
```python
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score
```

### Anomaly Detection
Follow patterns in `views/11_Anomaly_Detection.py`:
```python
from sklearn.ensemble import IsolationForest
# Z-score based detection
z_scores = (df[col] - df[col].mean()) / df[col].std()
```

## Visualization Conventions

All charts use Plotly with the project's design system:
```python
import plotly.express as px
import plotly.graph_objects as go
from utils.theme import COLORS, PLOTLY_LAYOUT
from utils.responsive import get_viewport, ChartConfig

vp = get_viewport()
cfg = ChartConfig.from_viewport(vp)

fig = px.scatter(df, x="poverty_rate", y="food_insecurity_rate")
fig.update_layout(**PLOTLY_LAYOUT, height=cfg.chart_height)
st.plotly_chart(fig, use_container_width=True)
```

**Color sequence** (from theme.py): sapphire, ruby, emerald, amethyst, topaz, amber

## Procedure

1. **Understand the question** — What specific insight or model is needed?
2. **Load and filter data** — Use `load_data()`, apply relevant filters
3. **Check data quality** — Count NaN, verify column availability, check distributions
4. **Perform analysis** — Use appropriate statistical methods
5. **Visualize results** — Plotly charts with PLOTLY_LAYOUT, responsive sizing
6. **Interpret findings** — Frame results in food insecurity policy context
7. **Document assumptions** — Note any data limitations or caveats
