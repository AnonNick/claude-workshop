"""Tests for wxpost.io.

The ``test_lat_orientation`` test below is **expected to fail** at workshop
start. Fixing it is the warm-up exercise.
"""

from __future__ import annotations

import numpy as np
import xarray as xr

from wxpost.io import open_waccmx, pressure_on_levels


def test_open_keeps_requested_variables(waccmx_path):
    ds = open_waccmx(waccmx_path, variables=("T", "TElec"))
    assert "T" in ds
    assert "TElec" in ds
    # We always keep the hybrid coefficients for downstream coords.
    for coef in ("hyam", "hybm", "P0"):
        assert coef in ds


def test_lev_in_pascals(waccmx_path):
    """After open_waccmx, ``lev`` should be in Pa, not hPa."""
    ds = open_waccmx(waccmx_path, variables=("T",))
    assert ds["lev"].attrs.get("units") == "Pa"
    # Surface level in WACCM-X is roughly 1000 hPa == 1e5 Pa.
    assert ds["lev"].values.max() > 5e4


def test_lat_orientation(waccmx_path):
    """The value at a given latitude should match what's actually in the file.

    Regression test for the lat-orientation bug: if the IO layer reorders
    the latitude axis without reordering the data, ``sel(lat=...)`` will
    return the wrong row.
    """
    raw = xr.open_dataset(waccmx_path)
    ds = open_waccmx(waccmx_path, variables=("T",))

    # Pick a high-northern-latitude column and a surface-level temperature.
    target_lat = 70.0
    # Index in the raw file:
    raw_idx = int(np.argmin(np.abs(raw["lat"].values - target_lat)))
    raw_val = raw["T"].isel(time=0, lev=-1, lat=raw_idx, lon=0).values

    # Same gridpoint via our wrapper. Should match.
    our_val = ds["T"].isel(time=0, lev=-1, lon=0).sel(lat=target_lat, method="nearest").values

    assert np.isclose(our_val, raw_val, rtol=1e-5), (
        f"Mismatch at lat={target_lat}: raw file has {raw_val:.2f} K, "
        f"open_waccmx returns {our_val:.2f} K. "
        "The IO layer is rearranging latitude labels without rearranging "
        "the data underneath."
    )


def test_pressure_on_levels_has_right_shape(waccmx_path):
    ds = open_waccmx(waccmx_path, variables=("T",))
    p = pressure_on_levels(ds)
    assert "lev" in p.dims
    assert "lat" in p.dims
    assert "lon" in p.dims
    # Pressures should span at least 8 orders of magnitude for WACCM-X.
    assert p.values.max() / p.values.min() > 1e8
