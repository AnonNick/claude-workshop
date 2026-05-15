"""Zonal (longitude) mean of a field."""

from __future__ import annotations

import xarray as xr


def zonal_mean(ds: xr.Dataset | xr.DataArray, field: str | None = None) -> xr.DataArray:
    """Mean over the longitude dimension.

    Parameters
    ----------
    ds
        Either an xarray Dataset (then ``field`` must be given) or a
        DataArray (then ``field`` is ignored).
    field
        Variable name when ``ds`` is a Dataset.
    """
    da = ds[field] if isinstance(ds, xr.Dataset) else ds
    if "lon" not in da.dims:
        raise ValueError(f"{da.name!r} has no 'lon' dim; got {da.dims}")
    return da.mean(dim="lon", keep_attrs=True)
