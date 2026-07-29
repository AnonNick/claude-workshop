"""Regenerate ``data/sample.nc``, the workshop's stand-in WACCM-X file.

``sample.nc`` is **synthetic**. It has the shape, coordinates, variables and
attributes of a real WACCM-X CAM ``h0`` monthly-mean history file, and its
fields follow analytic profiles chosen to be physically plausible — but no
number in it came out of a model run. It exists so the repo is
self-contained: every test runs on any laptop, with no HPC access and no
1.8 GB download.

Grid (a coarsened f19-like grid, small enough to commit):

    time     1        January 2020 monthly mean
    lev     96        4e-10 hPa (model top, ~450 km) → 1000 hPa (surface)
    lat     49        -90 → 90, 3.75° spacing
    lon     24        0 → 345, 15° spacing

Fields: ``T``, ``U``, ``V``, ``Z3``, ``TElec``, ``TIon``, ``PS``, plus the
hybrid-sigma coefficients ``hyam``, ``hybm``, ``P0``.

The vertical structure is built from pressure alone: altitude comes from
integrating a height-dependent scale height, and temperature is a function
of that altitude. It is not hydrostatically self-consistent with ``T`` —
close enough to teach with, not close enough to do science with.

Usage
-----

    python data/make_sample.py

Only needs numpy and netCDF4. You should not have to run this — the
generated file is committed.

Every field is deterministic, so a regenerated file holds bit-identical
data. The file itself won't have the same checksum: HDF5 stamps its own
metadata on write.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
from netCDF4 import Dataset

NLEV, NLAT, NLON = 96, 49, 24

P_TOP_HPA = 4e-10  # model top, ~450 km
P_SFC_HPA = 1000.0
P0_PA = 100_000.0


def scale_height_m(x: np.ndarray) -> np.ndarray:
    """Scale height (m) as a function of log-pressure below the surface.

    7 km in the troposphere growing to 25 km in the thermosphere, blended
    smoothly so the resulting altitude profile has no kinks.
    """
    return 7_000.0 + 18_000.0 * 0.5 * (1.0 + np.tanh((x - 14.0) / 4.0))


def altitude_m(p_hpa: np.ndarray) -> np.ndarray:
    """Altitude (m) for each pressure level, top-first to match ``lev``."""
    x = np.log(P_SFC_HPA / p_hpa)  # 0 at surface, ~28.6 at model top
    xa = x[::-1]  # ascending for integration
    h = scale_height_m(xa)
    dz = 0.5 * (h[1:] + h[:-1]) * np.diff(xa)
    za = np.concatenate([[300.0], 300.0 + np.cumsum(dz)])
    return za[::-1]


def temperature_profile_k(z_km: np.ndarray) -> np.ndarray:
    """Global-mean neutral temperature (K) versus altitude.

    Anchored at the surface, tropopause, stratopause and mesopause, then
    rising through the thermosphere. Smoothed so linear-in-p and
    linear-in-log-p interpolation agree to well under a kelvin.
    """
    anchor_km = [0, 12, 20, 50, 90, 120, 200, 300, 450]
    anchor_k = [300, 205, 210, 270, 190, 350, 700, 800, 830]
    t = np.interp(z_km, anchor_km, anchor_k)
    # Smooth the piecewise-linear kinks out (levels are ordered top-first,
    # but a symmetric filter does not care).
    for _ in range(24):
        t[1:-1] = 0.25 * t[:-2] + 0.5 * t[1:-1] + 0.25 * t[2:]
    return t


def lat_anomaly_k(lat_deg: np.ndarray) -> np.ndarray:
    """Surface temperature anomaly (K) versus latitude, for January.

    Zero at the equator, colder toward both poles, with a northern-winter /
    southern-summer asymmetry: 60°N lands near -10 °C and 60°S near +2 °C.
    """
    return -70.0 * (np.abs(lat_deg) / 90.0) ** 2 - 7.0 * np.sin(np.deg2rad(lat_deg))


def main() -> None:
    # ---- coordinates -------------------------------------------------
    lev = np.logspace(np.log10(P_TOP_HPA), np.log10(P_SFC_HPA), NLEV)  # hPa, top-first
    lat = np.linspace(-90.0, 90.0, NLAT)
    lon = np.arange(0.0, 360.0, 360.0 / NLON)

    # Hybrid-sigma coefficients: p = hyam*P0 + hybm*PS reproduces `lev`
    # exactly where PS == P0, with hybm -> 1 and hyam -> 0 at the surface.
    eta = lev / P_SFC_HPA
    hybm = eta**3
    hyam = eta - hybm

    z = altitude_m(lev)
    z_km = z / 1000.0
    t_prof = temperature_profile_k(z_km)

    # ---- fields ------------------------------------------------------
    LEV = lev[:, None, None]
    LAT = lat[None, :, None]
    LON = lon[None, None, :]
    ZKM = z_km[:, None, None]

    lat_r = np.deg2rad(LAT)
    lon_r = np.deg2rad(LON)

    # Surface pressure: gentle land-sea-ish wave, always positive.
    PS = P0_PA + 800.0 * np.cos(lon_r) * np.cos(lat_r)
    PS = np.broadcast_to(PS[0], (NLAT, NLON))

    # Latitudinal structure, strongest at the surface and decaying upward.
    weight = np.exp(-ZKM / 25.0)
    T = (
        t_prof[:, None, None]
        + weight * lat_anomaly_k(LAT)
        + 1.5 * weight * np.cos(lon_r) * np.cos(lat_r)
    )
    T = np.broadcast_to(T, (NLEV, NLAT, NLON))

    # Geopotential height: global profile plus a small thickness anomaly
    # that tracks the temperature of the column below.
    Z3 = z[:, None, None] * (1.0 + 0.004 * np.cos(lat_r) * np.ones_like(LON))
    Z3 = np.broadcast_to(Z3, (NLEV, NLAT, NLON))

    # Electron temperature: thermalised with the neutrals below ~150 km,
    # rising into the F region above ~250 km.
    plasma = 0.5 * (1.0 + np.tanh((ZKM - 230.0) / 55.0))
    te_max = 1750.0 * (1.0 + 0.06 * np.cos(lat_r))
    TElec = T + plasma * (te_max - T)
    TElec = np.broadcast_to(TElec, (NLEV, NLAT, NLON))

    # Ion temperature sits between the neutral and electron temperatures.
    TIon = T + 0.6 * (TElec - T)

    # Zonal wind: tropospheric jets plus a thermospheric superrotation.
    jets = 30.0 * np.exp(-(((np.abs(LAT) - 45.0) / 15.0) ** 2))
    U = jets * np.exp(-((ZKM - 11.0) ** 2) / 200.0) + 60.0 * plasma * np.cos(lat_r)
    U = np.broadcast_to(U, (NLEV, NLAT, NLON))
    V = 4.0 * np.sin(2.0 * lat_r) * np.cos(lon_r) * np.exp(-ZKM / 40.0)
    V = np.broadcast_to(V, (NLEV, NLAT, NLON))

    # ---- write -------------------------------------------------------
    out = Path(__file__).with_name("sample.nc")
    with Dataset(out, "w", format="NETCDF4") as nc:
        nc.title = "Synthetic WACCM-X-like monthly mean (workshop sample)"
        nc.source = "Generated by data/make_sample.py — NOT model output"
        nc.case = "f.e22.FXSD.f19_f19_mg17.001 (imitated)"
        nc.Conventions = "CF-1.0"

        nc.createDimension("time", None)
        nc.createDimension("lev", NLEV)
        nc.createDimension("lat", NLAT)
        nc.createDimension("lon", NLON)

        def var(name, dims, data, **attrs):
            v = nc.createVariable(name, "f4", dims, zlib=True, complevel=6)
            for k, val in attrs.items():
                setattr(v, k, val)
            # np.broadcast_to returns a read-only, non-contiguous view; make it
            # a real contiguous array so netCDF4 can write it without poking
            # at the view's shape (deprecated in numpy 2.5).
            v[...] = np.ascontiguousarray(data, dtype="f4")
            return v

        t = nc.createVariable("time", "f8", ("time",))
        t.units = "days since 2000-01-01 00:00:00"
        t.calendar = "standard"
        t.long_name = "time"
        t[:] = [7320.0]  # 2020-01-16, mid-month

        var("lev", ("lev",), lev, units="hPa",
            long_name="hybrid level at midpoints (1000*(A+B))",
            positive="down", axis="Z")
        var("lat", ("lat",), lat, units="degrees_north", long_name="latitude", axis="Y")
        var("lon", ("lon",), lon, units="degrees_east", long_name="longitude", axis="X")

        var("hyam", ("lev",), hyam, long_name="hybrid A coefficient at layer midpoints")
        var("hybm", ("lev",), hybm, long_name="hybrid B coefficient at layer midpoints")

        p0 = nc.createVariable("P0", "f8", ())
        p0.units = "Pa"
        p0.long_name = "reference pressure"
        p0[...] = P0_PA

        var("PS", ("time", "lat", "lon"), PS[None], units="Pa",
            long_name="surface pressure")
        var("T", ("time", "lev", "lat", "lon"), T[None], units="K",
            long_name="temperature")
        var("U", ("time", "lev", "lat", "lon"), U[None], units="m/s",
            long_name="zonal wind")
        var("V", ("time", "lev", "lat", "lon"), V[None], units="m/s",
            long_name="meridional wind")
        var("Z3", ("time", "lev", "lat", "lon"), Z3[None], units="m",
            long_name="geopotential height (above sea level)")
        var("TElec", ("time", "lev", "lat", "lon"), TElec[None], units="K",
            long_name="electron temperature")
        var("TIon", ("time", "lev", "lat", "lon"), TIon[None], units="K",
            long_name="ion temperature")

    size_kb = out.stat().st_size / 1024
    print(f"wrote {out}  ({size_kb:.0f} KiB)")
    print(f"  lev   {lev[0]:.2e} → {lev[-1]:.1f} hPa   ({NLEV} levels)")
    print(f"  z     {z[0] / 1000:.1f} → {z[-1]:.0f} m")
    print(f"  T     {T.min():.1f} → {T.max():.1f} K")
    print(f"  TElec {TElec.min():.1f} → {TElec.max():.1f} K")


if __name__ == "__main__":
    main()
