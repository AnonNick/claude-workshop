"""Interpolate a field from native model levels to fixed pressure levels."""

from __future__ import annotations

import numpy as np
import xarray as xr

from wxpost.coords.pressure import pressure_pa
from wxpost.interp import REGISTRY as INTERP


def to_pressure(
    ds: xr.Dataset,
    field: str,
    pressures_pa: np.ndarray,
    method: str = "loglinear",
) -> xr.DataArray:
    """Interpolate ``ds[field]`` from model levels onto ``pressures_pa``.

    Parameters
    ----------
    ds
        WACCM-X dataset opened by :func:`wxpost.io.open_waccmx`.
    field
        Name of the variable to interpolate (e.g. ``"T"``, ``"TElec"``).
    pressures_pa
        Target pressure levels in Pa. 1-D, ascending or descending.
    method
        Interpolation method. One of ``"linear"`` or ``"loglinear"``.
        Defaults to ``"loglinear"`` (linear-in-log-pressure) — the
        standard convention for CAM-style hybrid-sigma output, matching
        NCL's ``vinth2p``, MetPy, and geocat-comp. Pressure spans many
        orders of magnitude vertically, so log-linear is correct on
        physical grounds. ``"linear"`` is provided for parity with the
        height-interpolation operator and for cases where the user
        knows their target pressures fall within densely-spaced model
        levels (e.g. WACCM-X with 145 levels at quarter-scale-height
        spacing, where the two methods agree to <1%).

    Returns
    -------
    xarray.DataArray
        ``field`` interpolated onto the new pressure axis. Dims are the
        same as the source, with ``lev`` replaced by ``pressure``.
    """
    if method not in INTERP:
        raise ValueError(f"unknown method: {method!r}. Options: {list(INTERP)}")

    interp = INTERP[method]
    pressures_pa = np.asarray(pressures_pa, dtype=float)

    # The full 3-D pressure field varies with (lat, lon, time), but the
    # column-to-column variation is small compared to the orders-of-magnitude
    # variation with lev. Take the global-mean pressure profile and
    # interpolate every column onto the same target pressures.
    p = pressure_pa(ds)
    other_dims = [d for d in p.dims if d != "lev"]
    p_profile = p.mean(dim=other_dims).values  # shape: (lev,)

    # Pull the field as a numpy array with lev as the last axis, so
    # interp_1d can interpolate columnwise.
    da = ds[field]
    lev_axis = list(da.dims).index("lev")
    y_src = np.moveaxis(da.values, lev_axis, -1)  # lev now last

    out = interp(p_profile, y_src, pressures_pa)  # last axis: target pressures
    out = np.moveaxis(out, -1, lev_axis)

    new_dims = list(da.dims)
    new_dims[lev_axis] = "pressure"
    new_coords = {d: ds.coords[d] for d in new_dims if d in ds.coords}
    new_coords["pressure"] = ("pressure", pressures_pa, {"units": "Pa"})

    result = xr.DataArray(out, dims=new_dims, coords=new_coords, name=field)
    result.attrs.update(da.attrs)
    return result
