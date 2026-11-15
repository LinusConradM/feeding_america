# US Food Insecurity Atlas

A static site on food insecurity in the United States, rebuilt from a Streamlit app. Every figure links to its source and release date, shows a margin of error where the source publishes one, and says whether it is a share of **households** or a share of **people**.

Live site: https://linusconradm.github.io/feeding_america/ (GitHub Pages, deployed from `main`).

## Pages

| Page | What it shows | Source |
|---|---|---|
| National | Food insecurity 2001 to 2024: share and number of households, people in those households, and children | USDA ERS, ERR-358 |
| Who is affected | Food insecurity and very low food security by household type, income-to-poverty ratio, race and ethnicity of the household reference person, metro/nonmetro and region, 2023 and 2024 with USDA's significance tests, plus each group's 2001 to 2024 series. Map the Meal Gap state rates by race and ethnicity, listed alphabetically, never ranked | USDA ERS change files and chart data file; Map the Meal Gap, newest edition |
| States | Each state's 2022 to 2024 household rate with 90% margin of error and USDA's significance test; Map the Meal Gap rates of people by year | USDA ERS state data file; Map the Meal Gap |
| Counties | Map and table of county rates of people, child rates, cost per meal, annual meal gap, rural-urban code | Map the Meal Gap, newest edition |
| SNAP reach | County food insecurity against the share of households receiving SNAP, a measure that is not an input to the Map the Meal Gap model | Census ACS 5-year B22003 and B17001; Map the Meal Gap |
| Methods & sources | Source ledger, edition release dates, raw file hashes, validation report, derived-figure formulas, limits | All of the above |

## Sources and refresh cadence

| Source | Publisher's cadence | How the pipeline gets it | Checked |
|---|---|---|---|
| USDA ERS, Household Food Security in the United States in 2024 (ERR-358): chart data file, state data file (`mapdata.xlsx`), year-over-year change files for food insecurity and very low food security, report PDF (Table 1A) | Was annual. 2024 is the final year: USDA ended the Current Population Survey Food Security Supplement (announced September 20, 2025) | Direct download from ers.usda.gov | Daily |
| Feeding America, Map the Meal Gap (2011 to 2026 editions, 2009 to 2024 data) | Annual. County files only by request form | Pulled from a private data repo. The pipeline watches Feeding America's site and opens an issue when a newer edition appears | Daily |
| Census ACS 5-year, tables B22003 (SNAP receipt) and B17001 (poverty), with margins of error | Annual, usually December | Census API, newest vintage it serves | Daily |
| Census cartographic boundary files, counties and states, 1:20,000,000 | Annual | Direct download from www2.census.gov, matched to the newest Map the Meal Gap data year | Daily |

Release dates the files do not carry themselves are recorded with a citation in `pipeline/atlas/sources.py`. Map the Meal Gap files from 2020 and earlier state no release date, and the site says "Release date not published" rather than estimating one.

## How the pipeline works

`.github/workflows/pipeline.yml` runs daily at 11:23 UTC, on every push, and on demand.

1. **Fetch.** `python -m atlas fetch` downloads every public source. A file is stored only when its bytes change, unchanged, at `data/raw/<source>/<retrieved date>/<file>`, and `data/manifest.json` records its URL, retrieval time, size, SHA-256 and server headers. New raw files are committed back to the repo.
2. **Pull Map the Meal Gap.** The private data repo is checked out to `data/private/mmg/`, which is git-ignored here.
3. **Build and validate.** `python -m atlas build --strict` parses the raw files and runs about 50 checks: complete state and county coverage, USDA group change files matching the ERS chart data file for both years, unique FIPS codes, value ranges, USDA Table 1A matching the ERS data file, county totals within 6% of state totals (Map the Meal Gap builds states from congressional districts), every county having a boundary. Results are published on the Methods page.
4. **Publish.** The Astro site is built from the generated JSON and deployed to GitHub Pages, but only if every required check passed. A failure on `main` opens an issue and the site keeps its last good version.

## Setup (one time)

1. **Private data repo.** Create a private repo (default name `LinusConradM/feeding_america_data`, or set the repo variable `MMG_DATA_REPO`) and put the Map the Meal Gap `.xlsx` files at its root, with Feeding America's original file names.
2. **Secrets** (Settings → Secrets and variables → Actions):
   - `MMG_DATA_TOKEN`: a fine-grained personal access token with read-only Contents access to the private data repo only.
   - `CENSUS_API_KEY`: a free key from https://api.census.gov/data/key_signup.html. The Census API now rejects requests without one.
3. **Pages.** Settings → Pages → Source: GitHub Actions.

Without the token the workflow still fetches public sources but does not build the site. Without the Census key, the SNAP page says the data is not available yet and every other page builds normally.

## Local development

```bash
pip install -e ".[test]"          # Python 3.11+, needs pdftotext (poppler-utils)
pytest -q
ATLAS_MMG_DIR=/path/to/mmg/files python -m atlas build
cd site && npm ci && npm run dev  # http://localhost:4321/feeding_america/
```

## Data limits

- Map the Meal Gap figures are modeled, not counted, and the 2026 county and state files include no confidence intervals. The site says so and does not rank counties.
- Each Map the Meal Gap data year comes from a different edition. Feeding America advises against comparing across editions, so the state chart shows unconnected points.
- USDA's household-group files publish significance tests but not margins of error, so the group chart shows the test result and no interval.
- Map the Meal Gap's rates by race and ethnicity are rounded to whole percentages by Feeding America, have no published intervals, and leave some states blank. The Black and Hispanic groups overlap. The site shows them as published and does not rank states.
- USDA's household rate and Map the Meal Gap's people rate measure different things and are never compared directly.
- ACS SNAP receipt is self-reported and undercounts administrative SNAP totals; the SNAP page says so and labels counties only when a gap exceeds the ACS margin of error.

Map the Meal Gap data © Feeding America, used with attribution and not redistributed here. USDA and Census data are public domain.
