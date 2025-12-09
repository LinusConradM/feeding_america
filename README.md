# Investigating U.S. Food Insecurity Through Data

## Overview

An interactive R Shiny App analyzing household food insecurity patterns across U.S. counties, states, and demographic groups from 2009–2023. The application provides policymakers, researchers, and nonprofit practitioners with evidence-based insights into food insecurity disparities, socioeconomic drivers, and intervention impacts.

------------------------------------------------------------------------

## Features

### Three Interactive Tabs

**1. Overview Tab** 
- National summary statistics and KPI cards
- Food insecurity definitions and methodology
- Trend summaries and key takeaways
- Data quality indicators

**2. Exploration Tab** 
- Interactive choropleth maps with 15+ food insecurity indicators 
- Time series visualizations (2009–2023):
 - State-level trends 
 - Racial/ethnic disparities 
 - Child vs. overall food insecurity
 - Cost burden analysis 
 - Rural vs. urban comparisons 
 - Regional trends 
 - Inequality gap analysis 
- Dynamic filtering by state, county, year, and time period
- Summary tables and data viewer with export capabilities

**3. Analysis Tab** 
- **7 Statistical Methods:**
    1. Correlation Analysis (heatmaps and tables)
    2. Linear Regression (with diagnostics)
    3. Multinomial Logistic Regression (3+ category outcomes)
    4. Decision Trees (classification with ROC/AUC for binary outcomes)
    5. Principal Component Analysis (PCA)
    6. K-Means Clustering
    7. Group Comparisons (t-tests and ANOVA)
- Interactive variable selection
- Model diagnostics and interpretation guides

### Key Capabilities

-   **Geographic Analysis:** County-level resolution across all 50 states + DC
-   **Temporal Coverage:** 15 years of data (2009–2023)
-   **Demographic Breakdowns:** Race/ethnicity, rural/urban, income categories
-   **Auto-updating Visualizations:** Responsive filters with real-time updates
-   **Professional Theme:** Custom ggplot2 theme applied globally
-   **Tidyverse-Compliant Code:** All code follows tidyverse style guidelines

------------------------------------------------------------------------

## App Structure

```         
FoodInsecurityDashboard/
├── app.R                           # Main app launcher
├── global.R                        # Data loading, theme, packages
├── data/
│   ├── feeding_america(2009-2018).xlsx
│   └── feeding_america(2019-2023).xlsx
├── R/
│   ├── ui_overview.R              # Overview tab UI
│   ├── ui_exploration.R           # Exploration tab UI
│   ├── ui_analysis.R              # Analysis tab UI
│   ├── server_overview.R          # Overview tab server logic
│   ├── server_exploration.R       # Exploration tab server logic
│   └── server_analysis.R          # Analysis tab server logic
├── www/
│   └── AU-Logo-on-white-small.png # Logo assets
└── README.md                       # This file
```

### Module Architecture

The app uses a **modular design pattern** separating UI and server logic:

-   **UI Modules:** Define layout, inputs, and output placeholders
-   **Server Modules:** Handle reactive logic, data processing, and rendering
-   **Global Environment:** Loads data once, sets theme, manages packages

------------------------------------------------------------------------

## Data Sources

### Primary Data Source: Feeding America

**Feeding America – Map the Meal Gap (2009–2023)**  
**URL:** [feedingamerica.org/research/map-the-meal-gap](https://www.feedingamerica.org/research/map-the-meal-gap/by-county)

**Variables from Feeding America:**

**Food Insecurity Metrics:**
- Overall food insecurity rate
- Child food insecurity rate
- Number of food insecure persons (total and children)
- Food insecurity by race/ethnicity (Black, Hispanic, White non-Hispanic)

**Economic Indicators:**
- Cost per meal
- Weighted annual food budget shortfall
- Median household income
- Poverty rate
- Unemployment rate

**Program Participation:**
- SNAP participation rate
- Eligibility thresholds

### Secondary Data Source: U.S. Census Bureau

**American Community Survey (ACS) 5-Year Estimates**  
**URL:** [census.gov/data/developers/data-sets/acs-5year.html](https://www.census.gov/data/developers/data-sets/acs-5year.html)

The ACS 5-Year Estimates provide reliable demographic and socioeconomic data for all U.S. counties, including small population areas. We integrate ACS data to enrich our analysis with additional contextual variables.

**Variables from Census ACS:**

**Demographic Characteristics:**
- Total population by age groups
- Race and ethnicity distributions
- Household composition and family structure

**Socioeconomic Indicators:**
- Educational attainment (% high school or less, % bachelor's degree or higher)
- Employment status and labor force participation
- Income distribution and median household income (validation)
- Poverty rates by demographic groups
- Health insurance coverage rates

**Housing & Geography:**
- Urban/rural classification (derived from population density)
- Housing tenure (owner vs. renter occupied)
- Median home values and gross rent

### Data Integration Methodology

Our analysis integrates both data sources using **county FIPS codes** as the primary key:

1. **Spatial Join:** ACS 5-year estimates matched to Feeding America county-level data
2. **Temporal Alignment:** ACS 5-year periods centered on corresponding Feeding America years
   - Example: 2019-2023 ACS data paired with 2021 Feeding America estimates
3. **Variable Harmonization:** Standardized naming conventions across sources
4. **Quality Validation:** Cross-validation of overlapping variables (income, poverty) between sources
5. **Missing Data Handling:** ACS provides coverage for counties with limited Feeding America reporting

**API Access:** Census ACS data retrieved programmatically using:
- U.S. Census Bureau API: https://api.census.gov/data/2021/acs/acs5
- R packages: `tidycensus`, `censusapi`
- Secure credential management via `keyring` package

### Geographic Coverage

-   **Level:** County (3,100+ counties)
-   **Temporal:** 2009–2023 (15 years)
-   **Spatial:** All 50 states + Washington, D.C.

### Data Processing

The app performs comprehensive data harmonization:

1.  **Schema Alignment:** Reconciles variable name changes across years
2.  **FIPS Standardization:** 5-digit county codes for geographic joins
3.  **Type Conversion:** Numeric, character, and factor variables properly typed
4.  **Derived Variables:** Urban/rural categories, food insecurity categories, poverty/income/education categories
5.  **Geographic Coordinates:** County centroids added for mapping
6.  **Quality Checks:** Missing value reporting and validation

**Methodological Notes:**
- Feeding America revised estimation methods post-2020 due to COVID-19 impacts
- ACS 5-year estimates provide more reliable data for small counties than 1-year estimates
- Our harmonization ensures temporal continuity while documenting methodological changes
- Cross-validation between Feeding America and Census poverty rates shows high correlation (r > 0.85)

------------------------------------------------------------------------

## Installation

### Prerequisites

-   **R:** Version 4.3 or higher
-   **RStudio:** Recommended for development
-   **Git:** For cloning repository
-   **Census API Key:** (Optional) Required for updating ACS data
    - Obtain free key at: https://api.census.gov/data/key_signup.html

### Required Packages

The app automatically installs missing packages on first run:

``` r
# Core Shiny packages
shiny, bslib

# Tidyverse ecosystem
tidyverse (includes dplyr, ggplot2, tidyr, readr, purrr, stringr, forcats)
readxl, janitor

# Visualization
leaflet, leaflet.extras, plotly, DT

# Mapping
maps, scales

# Statistical modeling
nnet (multinomial regression)
rpart, rpart.plot (decision trees)
broom (model tidying)
pROC (ROC analysis)
```

### Clone and Run

``` bash
# Clone repository
git clone https://github.com/25F-DATA-413-613/gp-food-basket.git
cd gp-food-basket

# Open R/RStudio and run
R
> shiny::runApp()
```

**First Run:** The app will: 
1. Check for missing packages and install them 
2. Load and process ~47,000 county-year observations 
3. Integrate Census ACS socioeconomic variables
4. Create derived variables and geographic coordinates 
5. Set global ggplot2 theme 
6. Launch in your default browser

**Typical Load Time:** 10-15 seconds on first run, \<5 seconds on subsequent runs

### Optional: Update Census ACS Data

To refresh ACS data with the latest releases:

```r
# Install Census API key (one-time setup)
library(tidycensus)
census_api_key("YOUR_API_KEY_HERE", install = TRUE)

# Run data update script (in data_raw/)
source("data_raw/02_add_acs_socioeconomic_data.R")
```
------------------------------------------------------------------------

## Usage

### Quick Start

1.  **Launch the app** from RStudio or command line
2.  **Navigate tabs** using the top navigation bar
3.  **Apply filters** in the sidebar (state, year, indicators)
4.  **Interact with visualizations** (hover, click, zoom)
5.  **Run analyses** by selecting variables and clicking "Run" buttons

### Example Workflows

**Workflow 1: Explore State Trends** 
1. Go to **Exploration** tab 
2. Select **Trends** sub-tab 
3. Choose **State Trends** 
4. Use period slider to focus on specific years 
5. Observe food insecurity trajectories by state

**Workflow 2: Analyze Racial Disparities** 
1. Go to **Exploration** tab → **Trends** → **Racial Disparities** 
2. Compare Black, Hispanic, White, and Overall rates over time 
3. Switch to **Inequality Gaps** to see disparity magnitude 
4. Export summary table for further analysis

**Workflow 3: Predict Food Insecurity Categories** 
1. Go to **Analysis** tab 
2. Select **Multinomial Logistic Regression** 
3. Choose outcome: `fi_category` (Low, Moderate, High, Very High) 
4. Select predictors: `poverty_rate`, `median_income`, `unemployment_rate`, `education_hs_or_less`
5. Click **Run Multinomial Regression** 
6. Review model summary, relative risk ratios, and classification accuracy

**Workflow 4: Geographic Deep Dive** 
1. Go to **Exploration** tab → **Map** 
2. Select state (e.g., California) 
3. Choose indicator (e.g., Child FI Rate) 
4. Select year (e.g., 2023) 
5. Map auto-zooms to state 
6. Click counties for detailed popup information

**Workflow 5: Socioeconomic Drivers Analysis**
1. Go to **Analysis** tab → **Correlation Analysis**
2. Select variables: `overall_fi_rate`, `poverty_rate`, `median_income`, `unemployment_rate`, `education_hs_or_less`, `snap_rate`
3. Click **Run Correlation Analysis**
4. Examine heatmap to identify strongest predictors
5. Use findings to inform regression model specification

------------------------------------------------------------------------

## Statistical Methods

### 1. Correlation Analysis

-   **Method:** Pearson or Spearman correlation
-   **Output:** Heatmap, correlation table, interpretation
-   **Use Case:** Identify relationships between multiple variables

### 2. Linear Regression

-   **Method:** Ordinary Least Squares (OLS)
-   **Outputs:**
    -   Model summary (coefficients, R², p-values)
    -   Diagnostic plots (residuals, Q-Q, scale-location, leverage)
    -   Predictions vs. actual scatter plot
    -   Coefficient plot with confidence intervals
-   **Use Case:** Predict continuous outcomes (e.g., food insecurity rate)

### 3. Multinomial Logistic Regression

-   **Method:** Multinomial logit via `nnet::multinom()`
-   **Requirements:** Outcome with 3+ categories
-   **Outputs:**
    -   Model summary with log-odds coefficients
    -   Relative Risk Ratios (exponentiated coefficients)
    -   Classification accuracy
    -   Interpretation guide
-   **Use Case:** Predict categorical outcomes (e.g., FI category, income level)

### 4. Decision Trees

-   **Method:** CART via `rpart`
-   **Outputs:**
    -   Tree visualization
    -   Variable importance plot
    -   Confusion matrix (classification)
    -   ROC curve and AUC (binary classification only)
    -   Model data summary
-   **Use Case:** Non-linear classification/regression, interpretable rules

### 5. Principal Component Analysis (PCA)

-   **Method:** Dimensionality reduction
-   **Outputs:**
    -   Scree plot (variance explained)
    -   Biplot (PC1 vs PC2 with variable loadings)
    -   Loadings table
    -   Interpretation of major components
-   **Use Case:** Reduce multicollinearity, identify data structure

### 6. K-Means Clustering

-   **Method:** Unsupervised clustering
-   **Outputs:**
    -   Cluster visualization (PCA projection)
    -   Cluster summary statistics
    -   Interpretation by risk profile
-   **Use Case:** Segment counties by food insecurity characteristics

### 7. Group Comparison

-   **Methods:**
    -   Two groups: Independent t-test
    -   Three+ groups: One-way ANOVA
-   **Outputs:**
    -   Boxplots and violin plots
    -   Statistical test results
    -   Group means table
    -   Effect size estimates
-   **Use Case:** Compare food insecurity across regions, categories

------------------------------------------------------------------------

## Team

| Name | Course | Role | GitHub |
|------------------|-------------------|------------------|-------------------|
| **Conrad Linus Muhirwe** | DATA-613 | Repository management, statistical modeling | [\@LinusConradM](https://github.com/LinusConradM) |
| **Sharon Wanyana** | DATA-613 | Correlation/regression analysis, hypothesis testing | [\@SullenSchemer](https://github.com/SullenSchemer) |
| **Ryann Tompkins** | DATA-613 | Literature review, ethics, exploratory visualization | [\@ryanntompkins](https://github.com/ryanntompkins) |
| **Alex Arevalo** | DATA-413 | Data acquisition, cleaning, UI/UX design | [\@banditox79](https://github.com/banditox79) |

**Instructor:** Professor Richard Ressler\
**Course:** DATA-613: Data Science Practicum (Fall 2025)\
**Institution:** American University, College of Arts & Sciences\
**Report Date:** December 8, 2025

------------------------------------------------------------------------

## Technical Details

### Code Quality

**Tidyverse Style Compliance:** All R code follows the [tidyverse style guide](https://style.tidyverse.org/): 
- Named function arguments
- Proper spacing (after commas, around operators)
- Pipes broken across lines
- Consistent indentation (2 spaces)
- Lines under 80 characters
- `case_when()` instead of nested `ifelse()`

**Code Organization:** 
- Modular structure (separate UI/server files)
- Clear section headers with comment blocks
- Descriptive variable names (snake_case)
- Comprehensive inline documentation

### Global Theme

All ggplot2 visualizations use a custom theme (`bs_theme`) set in `global.R`:

``` r
bs_theme <- theme(
  text = element_text(family = "Arial", size = 14, color = "black"),
  plot.title = element_text(hjust = 0.5, size = 20, face = "bold"),
  axis.title = element_text(size = 16, face = "bold"),
  axis.text = element_text(size = 14, face = "bold"),
  legend.title = element_text(size = 14, face = "bold"),
  panel.grid.major = element_line(color = "grey85"),
  panel.grid.minor = element_blank()
)
```
------------------------------------------------------------------------
## Technical Implementation

### Performance Optimizations

-   **Reactive Programming:** Efficient dependency tracking
-   **Efficient Rendering:** Plots only re-render when dependencies change
-   **Lazy Loading:** Modules load on-demand
-   **Data Caching:** County coordinates and Census variables calculated once in global environment
-   **Indexed Data:** FIPS codes indexed for fast geographic joins

### Browser Compatibility

Tested on: 
- Chrome 120+ 
- Firefox 121+ 
- Safari 17+ 
- Edge 120+

------------------------------------------------------------------------

## Ethics & Reproducibility

### Ethical Guidelines

We adhere to the **American Statistical Association's Ethical Guidelines for Statistical Practice (2022)**:

1.  **Data Privacy:** All data are public, de-identified, and aggregated
2.  **Transparency:** Open-source code with version control
3.  **Accessibility:** Neutral color palettes, clear labels, alt text ready
4.  **Honesty:** Methodological limitations documented
5.  **Responsibility:** Results contextualized with appropriate caveats

### Data Ethics

-   **No Individual-Level Data:** All metrics are county aggregates
-   **Public Domain:** Feeding America and Census data are freely available
-   **Appropriate Use:** Tool designed for policy analysis, not surveillance
-   **Equity Focus:** Explicit attention to racial/ethnic disparities
-   **Census Compliance:** All use adheres to U.S. Census Bureau terms of service

### Reproducibility

**Version Control:** 
- Full Git history with descriptive commit messages 
- Tagged releases for major milestones 
- Branch-based development workflow

**Documentation:** 
- Inline code comments 
- README with installation instructions 
- Data dictionary (in progress) 
- Session info capture (`sessionInfo()`)

**Environment:**

``` r
# Capture environment details
writeLines(capture.output(sessionInfo()), "session_info.txt")
```

------------------------------------------------------------------------

## Project Context

Food insecurity—the economic inability to consistently afford adequate food— affects **44 million Americans** (13.5% of households, USDA 2023). It disproportionately impacts:

-   **Low-income households:** 29.1% food insecure
-   **Black households:** 22.4% food insecure
-   **Hispanic households:** 20.8% food insecure
-   **Households with children:** 17.9% food insecure

### Policy Relevance

This dashboard supports: 
- **Targeted Interventions:** Identify high-need counties 
- **Program Evaluation:** Assess SNAP and WIC impact 
- **Equity Analysis:** Track racial/ethnic disparities 
- **Resource Allocation:** Guide funding decisions 
- **Academic Research:** Enable hypothesis testing and modeling
  
------------------------------------------------------------------------

## References

### Data Sources

**Feeding America (2024).** *Map the Meal Gap 2024: Overall Food Insecurity in the United States.* Retrieved from https://www.feedingamerica.org/research/map-the-meal-gap/by-county

**U.S. Census Bureau (2024).** *American Community Survey 5-Year Estimates.* Retrieved from https://www.census.gov/data/developers/data-sets/acs-5year.html

**U.S. Census Bureau API.** *American Community Survey 5-Year Data (2009-2023).* Retrieved from https://api.census.gov/data.html

### Government Statistics

**Coleman-Jensen, A., Rabbitt, M. P., Gregory, C. A., & Singh, A. (2023).** *Household Food Security in the United States in 2022.* U.S. Department of Agriculture, Economic Research Service, ERR-325.  
https://www.ers.usda.gov/publications/pub-details/?pubid=107703

**U.S. Department of Agriculture, Economic Research Service (2024).** *Food Security in the U.S.* Retrieved from  
https://www.ers.usda.gov/topics/food-nutrition-assistance/food-security-in-the-u-s/

### Academic Literature

**Gundersen, C., & Ziliak, J. P. (2015).** *Food Insecurity and Health Outcomes.* Health Affairs, 34(11), 1830-1839.  
https://doi.org/10.1377/hlthaff.2015.0645

**Gundersen, C., Kreider, B., & Pepper, J. (2017).** *Reconstructing the Supplemental Nutrition Assistance Program to More Effectively Alleviate Food Insecurity in the United States.* RSF: The Russell Sage Foundation Journal of the Social Sciences, 3(2), 113-130.  
https://doi.org/10.7758/rsf.2017.3.2.06

### Policy Analysis

**Gregory, C. A., & Coleman-Jensen, A. (2017).** *Food Insecurity, Chronic Disease, and Health Among Working-Age Adults.* USDA-ERS Economic Research Report No. 235.

### Geographic Analysis

**Gundersen, C., Dewey, A., Crumbaugh, A., Kato, M., & Engelhard, E. (2024).** *Map the Meal Gap 2024: An Analysis of County and Congressional District Food Insecurity and County Food Cost in the United States.* Feeding America.

### Racial Equity

**Myers, A. M., Painter, M. A., Frelier, J. M., et al. (2020).** *Disparities in Food Insecurity Among Racial and Ethnic Minority Groups.* Journal of Hunger & Environmental Nutrition, 15(6), 717-731.

### R Packages

**Walker, K., & Herman, M. (2023).** *tidycensus: Load US Census Boundary and Attribute Data as 'tidyverse' and 'sf'-Ready Data Frames.* R package version 1.5.  
https://walker-data.com/tidycensus/

------------------------------------------------------------------------

## Future Enhancements

**Planned Features:** 
- [ ] Download buttons for all plots and tables 
- [ ] PDF report generation 
- [ ] Advanced filtering with AND/OR logic 
- [ ] Time series forecasting models 
- [ ] Spatial autocorrelation analysis 
- [ ] Mobile-responsive design improvements 
- [ ] Accessibility audit (WCAG 2.1 AA compliance) 
- [ ] Multi-language support (Spanish)
- [ ] Real-time Census ACS data updates via API
- [ ] Additional ACS variables (disability status, language, transportation)

**Technical Debt:** 
- [ ] Unit tests for server functions 
- [ ] Integration tests for UI interactions 
- [ ] Performance profiling and optimization 
- [ ] Database backend for faster loading 
- [ ] Docker containerization

------------------------------------------------------------------------

## Contributing

We welcome contributions! Please:

1.  Fork the repository
2.  Create a feature branch (`git checkout -b feature/AmazingFeature`)
3.  Follow tidyverse style guidelines
4.  Add tests for new features
5.  Commit with descriptive messages (`git commit -m 'Add AmazingFeature'`)
6.  Push to branch (`git push origin feature/AmazingFeature`)
7.  Open a Pull Request

------------------------------------------------------------------------

## Troubleshooting

**Issue:** App won't load data  
**Solution:** Ensure Excel files are in `data/` directory with exact names: 
- `feeding_america(2009-2018).xlsx` 
- `feeding_america(2019-2023).xlsx`

**Issue:** Missing packages error  
**Solution:** Run `install.packages("package_name")` or let global.R auto-install

**Issue:** Census API key error  
**Solution:** Obtain free key at https://api.census.gov/data/key_signup.html, then run:
```r
library(tidycensus)
census_api_key("YOUR_KEY", install = TRUE)
```

**Issue:** Map not rendering  
**Solution:** Check internet connection (required for Leaflet tiles)

**Issue:** Slow performance  
**Solution:** Filter to specific states/years to reduce data volume

**Issue:** Plots not using custom theme  
**Solution:** Verify `global.R` runs successfully and `theme_set(bs_theme)` executes

------------------------------------------------------------------------

## Citation

If you use this dashboard in research or publications, please cite:

```         
Muhirwe, C. L., Wanyana, S., Tompkins, R., & Arevalo, A. (2024). 
Investigating U.S. Food Insecurity Through Data: An Interactive R Shiny Dashboard. 
American University. https://github.com/LinusConradM/FoodInsecurityDashboard

Data sources:
- Feeding America. (2024). Map the Meal Gap. https://www.feedingamerica.org/research/map-the-meal-gap
- U.S. Census Bureau. (2024). American Community Survey 5-Year Estimates. https://www.census.gov/programs-surveys/acs
```

------------------------------------------------------------------------

## License

This work is licensed under the **Creative Commons Attribution 4.0 International License (CC BY 4.0)**.

You are free to: 
- **Share** — Copy and redistribute the material in any medium or format 
- **Adapt** — Remix, transform, and build upon the material for any purpose, even commercially

Under the following terms: 
- **Attribution** — You must give appropriate credit, provide a link to the license, and indicate if changes were made

Full license text: https://creativecommons.org/licenses/by/4.0/

------------------------------------------------------------------------

## Acknowledgments

-   **Feeding America** for providing comprehensive county-level food insecurity data
-   **U.S. Census Bureau** for American Community Survey data and API access
-   **USDA Economic Research Service** for national food security statistics
-   **American University** for institutional support
-   **Professor Richard Ressler** for course guidance and feedback
-   **R Shiny Community** for extensive documentation and examples
-   **tidycensus developers** (Kyle Walker and Matt Herman) for excellent Census API tools

------------------------------------------------------------------------

**Last Updated:** December 8, 2025\
**Version:** 1.0.0\
**Status:** Production Ready ✅
