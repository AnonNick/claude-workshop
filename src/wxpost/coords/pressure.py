"""Pressure on every (lev, lat, lon) gridpoint, in Pa."""

from __future__ import annotations

import xarray as xr

from wxpost.io import pressure_on_levels


def pressure_pa(ds: xr.Dataset) -> xr.DataArray:
    """Return pressure in Pa on the model grid.

    Just wraps :func:`wxpost.io.pressure_on_levels` so the ``coords``
    plug-in API is uniform across pressure / height / log-pressure.
    """
    p = pressure_on_levels(ds)
    p.name = "pressure"
    p.attrs["units"] = "Pa"
    p.attrs["long_name"] = "pressure on model levels"
    return p
