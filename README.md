**Investigating U.S. Food Insecurity Through Data**

**Purpose of the App**

This interactive R Shiny dashboard analyzes and visualizes household food-insecurity patterns across U.S. states and demographic groups. It links socioeconomic drivers—income, poverty, education, and employment—to food-access indicators and program participation (SNAP/WIC). The goal is to provide policymakers and researchers with a transparent, data-driven tool to explore disparities and evaluate interventions.

**Group Members**

1.  Conrad Linus Muhirwe (DATA-613) GitHub: LinusConradM
2.  Sharon Wanyana (DATA-613) GitHub: SullenSchemer
3.  Ryann Tompkins (DATA-613) GitHub: ryanntompkins
4.  Alex Arevalo (DATA-413) GitHub: banditox79


**Elements of the App**

1.  Overview Tab – National summary statistics, key indicators, and definitions.
2.  Exploration Tab – Interactive maps and comparative charts for state, county, and demographic trends.
3.  Analysis Tab – Correlation matrices, regression models, and group-comparison tests.
4.  Download/Export Tools – Save filtered data tables or generated plots for reports.
5.  Ethics and Reproducibility – Uses only public, de-identified data consistent with ASA ethical guidelines.

**Data Source**
Primary Dataset: USDA Economic Research Service (ERS) – Food Access Research Atlas (2025 Release)
1.  Geographic Unit: U.S. Census Tract (approximately 72,000 tracts nationwide)
2.  Variables: 147 indicators (income level, food access, poverty rate, urban/rural classification, etc.)
3.  Access Link: https://www.ers.usda.gov/data-products/food-access-research-atlas/

No API keys are required. All data are open access and publicly available.


**License**
This work is licensed under the Creative Commons Attribution 4.0 International License (CC BY 4.0).

You are free to:
- Share — copy and redistribute the material in any medium or format.
- Adapt — remix, transform, and build upon the material for any purpose, even commercially.

Under the following terms:
- Attribution — You must give appropriate credit and indicate if changes were made.

Link to full license text: https://creativecommons.org/licenses/by/4.0/


**Reproducibility**

To reproduce the app locally:
1.  Clone the repository from GitHub.
2.  Open the project in RStudio.
3.  Run shiny::runApp() from the root directory.