"""Census ACS 5-year table B22003 (SNAP receipt) and B17001 (poverty), with margins of error.

Shares and their margins of error follow the Census Bureau's formula for a
proportion whose numerator is a subset of its denominator (ACS General Handbook,
2020, ch. 8): MOE(p) = sqrt(MOE_num^2 - p^2 * MOE_den^2) / den, switching to the
ratio formula (plus sign) when the term under the root is negative.
"""
import json

import numpy as np
import pandas as pd


def read(path):
    rows = json.loads(open(path).read())
    df = pd.DataFrame(rows[1:], columns=rows[0])
    for c in df.columns:
        if c[:1] == "B":
            df[c] = pd.to_numeric(df[c], errors="coerce")
            # The API marks unavailable estimates and MOEs with large negative sentinels.
            df.loc[df[c] < 0, c] = np.nan
    return df


def share(num, num_moe, den, den_moe):
    p = num / den
    rad = num_moe ** 2 - p ** 2 * den_moe ** 2
    rad = np.where(rad < 0, num_moe ** 2 + p ** 2 * den_moe ** 2, rad)
    return p, np.sqrt(rad) / den


def tidy(df):
    snap, snap_moe = share(df.B22003_002E, df.B22003_002M, df.B22003_001E, df.B22003_001M)
    pov, pov_moe = share(df.B17001_002E, df.B17001_002M, df.B17001_001E, df.B17001_001M)
    out = pd.DataFrame({
        "households": df.B22003_001E,
        "snap_households": df.B22003_002E,
        "snap_share": snap,
        "snap_moe": snap_moe,
        "poverty_rate": pov,
        "poverty_moe": pov_moe,
    })
    if "county" in df.columns:
        out.insert(0, "fips", df.state + df.county)
    elif "state" in df.columns:
        out.insert(0, "state_fips", df.state)
    return out
