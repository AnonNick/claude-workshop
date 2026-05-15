"""Geopotential height on every (lev, lat, lon) gridpoint, in metres."""

from __future__ import annotations

import xarray as xr


def height_m(ds: xr.Dataset) -> xr.DataArray:
    """Return geopotential height (Z3) in metres on the model grid.

    Z3 in CAM/WACCM-X output is geopotential height (Φ/g₀), not geometric
    altitude. The two are identical near the surface and diverge with
    altitude. Using R_E = 6371 km:

        - at  100 km geopotential, geometric height is ~101.6 km   (Δ ~1.6 km)
        - at  200 km geopotential, geometric height is ~206.5 km   (Δ ~6.5 km)
        - at  300 km geopotential, geometric height is ~314.8 km   (Δ ~14.8 km)
        - at  400 km geopotential, geometric height is ~426.9 km   (Δ ~26.9 km)
        - at  450 km geopotential, geometric height is ~484.2 km   (Δ ~34.2 km)

    The exact conversion is::

        z_geometric = R_E * Z3 / (R_E - Z3)

    For the workshop demos (interpolating onto round-number altitudes like
    300 km) we treat Z3 as height in metres directly, matching what
    legacy HAO post-processors like ``tgcmproc`` do with the analogous Z
    variable in TIE-GCM. If you want true geometric altitude, apply the
    correction above to the array this function returns before calling
    :func:`wxpost.ops.to_height`.
    """
    if "Z3" not in ds:
        raise KeyError(
            "Z3 (geopotential height) not present in dataset. "
            "Re-open the file with Z3 in the variables list."
        )
    z = ds["Z3"]
    z.attrs.setdefault("units", "m")
    z.attrs.setdefault("long_name", "geopotential height (Φ/g₀)")
    return z
