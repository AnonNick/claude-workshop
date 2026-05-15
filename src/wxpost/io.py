"""I/O for WACCM-X CAM history files.

Opens a NetCDF file, exposes the variables and the hybrid-sigma vertical
coordinate coefficients in a single xarray Dataset.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import xarray as xr

# Default subset of variables that the workshop cares about.
# (Files have ~360 variables; we don't want to materialise them all.)
DEFAULT_VARS: tuple[str, ...] = (
    "T", "U", "V", "OMEGA",      # neutral atmosphere
    "PS", "Z3",                  # surface pressure, geopotential height
    "EDens", "TElec", "TIon",    # ionosphere (WACCM-X)
)

HYBRID_COEFS: tuple[str, ...] = ("hyam", "hybm", "P0", "PS")


def open_waccmx(
    path: str | Path,
    variables: tuple[str, ...] = DEFAULT_VARS,
) -> xr.Dataset:
    """Open a WACCM-X CAM history file and return a tidy Dataset.

    Reorders latitude so it runs north-to-south, which matches the way
    maps are drawn (north at the top) and the way most of our plotting
    helpers expect it.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"WACCM-X file not found: {path}")

    ds = xr.open_dataset(path, decode_times=True)

    keep = list(variables) + list(HYBRID_COEFS)
    ds = ds[[v for v in keep if v in ds.variables]]

    # Reorder latitude north-to-south so plots have north at the top.
    ds = ds.assign_coords(lat=ds.lat.values[::-1])

    # Convert lev (hPa) to Pa internally; document the convention in CLAUDE.md.
    if ds["lev"].attrs.get("units", "").lower() == "hpa":
        ds = ds.assign_coords(lev=ds["lev"].values * 100.0)
        ds["lev"].attrs["units"] = "Pa"

    # WACCM-X writes EDens with units = "cm^3" in the NetCDF header. That is
    # an upstream typo — electron density is in cm^-3 (per cubic centimetre).
    # The numerical values are correct; only the attribute string is wrong.
    # We override it here so downstream plotting/labelling code sees the
    # right unit.
    if "EDens" in ds and ds["EDens"].attrs.get("units") == "cm^3":
        ds["EDens"].attrs["units"] = "cm-3"

    return ds


def pressure_on_levels(ds: xr.Dataset) -> xr.DataArray:
    """Compute 3-D pressure (Pa) on each (lev, lat, lon) gridpoint.

    Uses the standard hybrid-sigma formula:

        p(lev, lat, lon, t) = hyam(lev) * P0 + hybm(lev) * PS(t, lat, lon)
    """
    hyam = ds["hyam"]
    hybm = ds["hybm"]
    P0 = ds["P0"]
    PS = ds["PS"]

    return hyam * P0 + hybm * PS
