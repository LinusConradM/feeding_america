# Investigating U.S. Food Insecurity Through Data

### Purpose of the App
This interactive **R Shiny dashboard** analyzes and visualizes **household food-insecurity patterns** across U.S. states and demographic groups.  
It links **socioeconomic drivers**—income, poverty, education, and employment—to food insecurity outcomes and program participation (e.g., **SNAP, WIC**).  
The goal is to provide policymakers, researchers, and nonprofit practitioners with a **transparent, data-driven tool** to explore disparities and evaluate interventions that improve food affordability and access.

---

## Group Members

| Name | Course | Role | GitHub |
|------|---------|------|---------|
| **Conrad Linus Muhirwe** | DATA-613 | Repository management, statistical modeling | [@LinusConradM](https://github.com/LinusConradM) |
| **Sharon Wanyana** | DATA-613 | Correlation and regression analysis, hypothesis testing | [@SullenSchemer](https://github.com/SullenSchemer) |
| **Ryann Tompkins** | DATA-613 | Literature & ethics review, exploratory visualization & mapping | [@ryanntompkins](https://github.com/ryanntompkins) |
| **Alex Arevalo** | DATA-413 | Data acquisition, cleaning, and UI/UX design | [@banditox79](https://github.com/banditox79) |

**Instructor:** Professor Richard Ressler  
**Course:** DATA-613: Data Science Practicum (Fall 2025)  
**Report Date:** November 11, 2025  

---

## Project Context

Food insecurity—the **economic inability to consistently afford adequate food**—disproportionately affects low-income households, racial and ethnic minorities, and families with children.  
It reflects broader structural inequities including income volatility, housing costs, and access to education and employment.

This project:
- Quantifies **food insecurity prevalence** and geographic distribution across states and demographic groups.  
- Analyzes **relationships** with socioeconomic factors (poverty, unemployment, education, income).  
- Visualizes **insights through a Shiny dashboard** supporting evidence-based policymaking.  

The app enables exploration of **trends, disparities, and intervention impacts** to guide more equitable food policy decisions.

---

## Key Elements of the App

1. **Overview Tab** – National summary statistics, KPIs, definitions, and trend summaries.  
2. **Exploration Tab** – Interactive choropleth maps, line charts, and demographic comparisons.  
3. **Analysis Tab** – Correlation matrices, regression modeling, and group-comparison tests.  
4. **Data Table (Planned)** – Interactive filtering and export tools using `{DT}`.  
5. **Ethics & Reproducibility** – Uses only public, de-identified data consistent with **ASA ethical guidelines**.

---

## Data Source (Updated & Corrected)

**Primary Dataset:**  
**Feeding America – Map the Meal Gap (2009–2023)**  
➡️ [https://www.feedingamerica.org/research/map-the-meal-gap/by-county](https://www.feedingamerica.org/research/map-the-meal-gap/by-county)

### What It Measures
- Food insecurity rate  
- Child food insecurity rate  
- Number of food insecure persons and children  
- Cost per meal  
- Food budget shortfall  
- Race/ethnicity-based food insecurity (Black, Hispanic, White non-Hispanic)

### Geographic Levels
- County, State, and Congressional District  

### Methodological Note
Feeding America adjusted its estimation methods post-2020 due to COVID-19 impacts.  
We harmonized variables across 15 years (2009–2023) and built a **dual-dataset strategy**:
- **Longitudinal Trends (2009–2023)** – Core variables available all years  
- **Equity Analysis (2019–2023)** – Includes demographic breakdowns  

**Progress:** ~75% complete  
- FIPS codes standardized  
- Variables harmonized across schema changes  
- Missing values documented and validated  

---

## Literature Context

- **National Trends:** Food insecurity affected **13.5% of U.S. households** in 2023 (USDA ERS, 2024).  
- **Geographic Disparities:** Rural and southern counties remain the most affected (Feeding America, 2024).  
- **Socioeconomic Determinants:** Income, race/ethnicity, family structure, and education strongly predict food insecurity (Gundersen & Ziliak, 2015).  
- **Policy Impact:** SNAP participation reduces household food insecurity by ~6 percentage points (Gundersen, Kreider, & Pepper, 2017).  

---

## Application Design Overview

| Tab | Description |
|-----|--------------|
| **Overview** | National KPIs and summary statistics |
| **Exploration** | Interactive maps, trends, and subgroup comparisons |
| **Analysis** | Regression and correlation tools with diagnostic plots |
| **Data Table (Planned)** | Search, filter, and export functions via `{DT}` |

### User Options
- **Geographic Filters:** State/region and county dropdowns  
- **Temporal Sliders:** Year range selection (2009–2023)  
- **Variable Selection:** Income, poverty, education, unemployment  
- **Demographic Focus:** Race/ethnicity, households with children, rural vs. urban  

---

## Statistical Modeling Capabilities

- **DATA-413 Track:** Correlation (Pearson/Spearman), multiple linear regression, diagnostic plots.  
- **DATA-613 Track:** Classification models (predicting high/low food insecurity) and model comparison tools.

---

## Ethics and Reproducibility

We adhere to the **American Statistical Association’s Ethical Guidelines (2023)**:
- All data are **public and de-identified**.  
- Transparent R scripts with version control and commit documentation.  
- Neutral and accessible visualization choices.  
- Repository structure supports full reproducibility.  

---


## Reproducibility – Run Locally

To reproduce the app locally:

```bash
# Clone the repository
git clone https://github.com/LinusConradM/FoodInsecurityDashboard.git
cd FoodInsecurityDashboard

---

## License
This work is licensed under the Creative Commons Attribution 4.0 International License (CC BY 4.0).

You are free to:
- Share — copy and redistribute the material in any medium or format.
- Adapt — remix, transform, and build upon the material for any purpose, even commercially.

Under the following terms:
- Attribution — You must give appropriate credit and indicate if changes were made.

Link to full license text: https://creativecommons.org/licenses/by/4.0/
