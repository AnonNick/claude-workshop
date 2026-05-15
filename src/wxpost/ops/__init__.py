"""User-facing operations.

Everything here is built on top of :mod:`wxpost.io`, :mod:`wxpost.coords`,
and :mod:`wxpost.interp`. New operations should follow the same shape:
take an xarray Dataset (or DataArray), do their work using the building
blocks, return an xarray result.
"""

from wxpost.ops.to_pressure import to_pressure
from wxpost.ops.to_height import to_height
from wxpost.ops.zonal_mean import zonal_mean

__all__ = ["to_pressure", "to_height", "zonal_mean"]
