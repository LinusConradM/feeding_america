"""Publisher facts that are not inside the downloaded files: titles, landing pages
and release dates. Each date here was read from the publisher's own page on the
access date given. A release the pipeline has not seen before gets no date until
one is added here with its citation; the site then says the date is not recorded.
"""

USDA = {
    "title": "USDA ERS, Household Food Security in the United States in 2024 (ERR-358)",
    "short": "USDA ERS, ERR-358",
    "publisher": "USDA Economic Research Service",
    "url": "https://www.ers.usda.gov/publications/pub-details?pubid=113622",
    "release_date": "2025-12-30",
    "release_cite": "Report landing page, accessed 2026-11-15",
    "kind": "survey",
    "data_note": "Direct estimates from the Current Population Survey Food Security Supplement (about 95,000 households a year). "
                 "USDA ended the supplement after the December 2024 collection (announced September 20, 2025), so 2024 is the final year.",
}

ACS_RELEASES = {
    2024: {"period": "2020-2024", "release_date": "2026-01-29",
           "release_cite": "Census Bureau 2024 ACS 5-year release schedule, accessed 2026-11-15"},
}

ACS = {
    "title": "Census Bureau, American Community Survey 5-year estimates, tables B22003 and B17001",
    "short": "Census ACS 5-year",
    "publisher": "US Census Bureau",
    "url": "https://data.census.gov/table/ACSDT5Y{vintage}.B22003",
    "kind": "survey",
}

GEO = {
    "title": "Census Bureau, cartographic boundary files, counties and states, 1:20,000,000",
    "short": "Census boundaries",
    "publisher": "US Census Bureau",
    "url": "https://www.census.gov/geographies/mapping-files/time-series/geo/cartographic-boundary.html",
    "kind": "geography",
}

MMG = {
    "publisher": "Feeding America",
    "url": "https://www.feedingamerica.org/research/map-the-meal-gap/by-county",
    "kind": "model",
    "license_note": "Data requested from Feeding America. Raw files are not redistributed here.",
}

SNAP_UNDERREPORTING = {
    "cite": "Meyer, B. D., Mok, W. K. C., and Sullivan, J. X. (2015). Household Surveys in Crisis. Journal of Economic Perspectives 29(4): 199-226.",
    "url": "https://doi.org/10.1257/jep.29.4.199",
}
