"""Interpolate a field from native model levels to fixed altitudes."""

from __future__ import annotations

import numpy as np
import xarray as xr

from wxpost.coords.height import height_m
from wxpost.interp import REGISTRY as INTERP


def to_height(
    ds: xr.Dataset,
    field: str,
    altitudes_m: np.ndarray,
    method: str = "linear",
) -> xr.DataArray:
    """Interpolate ``ds[field]`` from model levels onto ``altitudes_m``.

    Uses ``Z3`` (geopotential height) from the dataset as the source
    coordinate.
    """
    if method not in INTERP:
        raise ValueError(f"unknown method: {method!r}. Options: {list(INTERP)}")

    interp = INTERP[method]
    altitudes_m = np.asarray(altitudes_m, dtype=float)

    z = height_m(ds)
    other_dims = [d for d in z.dims if d != "lev"]
    z_profile = z.mean(dim=other_dims).values  # shape: (lev,)

    da = ds[field]
    lev_axis = list(da.dims).index("lev")
    y_src = np.moveaxis(da.values, lev_axis, -1)

    out = interp(z_profile, y_src, altitudes_m)
    out = np.moveaxis(out, -1, lev_axis)

    new_dims = list(da.dims)
    new_dims[lev_axis] = "altitude"
    new_coords = {d: ds.coords[d] for d in new_dims if d in ds.coords}
    new_coords["altitude"] = ("altitude", altitudes_m, {"units": "m"})

    result = xr.DataArray(out, dims=new_dims, coords=new_coords, name=field)
    result.attrs.update(da.attrs)
    return result
