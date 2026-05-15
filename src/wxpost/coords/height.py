"""Geometric height on every (lev, lat, lon) gridpoint, in metres."""

from __future__ import annotations

import xarray as xr


def height_m(ds: xr.Dataset) -> xr.DataArray:
    """Return geometric height in metres on the model grid.

    WACCM-X writes ``Z3`` (geopotential height) in metres on every
    gridpoint. Above the lower thermosphere the difference between
    geopotential and geometric height becomes non-trivial, but for the
    purposes of this workshop we treat ``Z3`` as height in metres.
    """
    if "Z3" not in ds:
        raise KeyError(
            "Z3 (geopotential height) not present in dataset. "
            "Re-open the file with Z3 in the variables list."
        )
    z = ds["Z3"]
    z.attrs.setdefault("units", "m")
    z.attrs.setdefault("long_name", "geometric height")
    return z
