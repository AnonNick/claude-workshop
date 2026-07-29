"""Tests for the user-facing operations.

``test_to_height_thermosphere_telec`` is **expected to fail** at workshop
start. Fixing it is the main exercise. The other tests should pass.
"""

from __future__ import annotations

import numpy as np

from wxpost import open_waccmx, to_height, to_pressure, zonal_mean


def test_to_pressure_basic(waccmx_path):
    """T on three standard pressure levels has the right shape and physics."""
    ds = open_waccmx(waccmx_path, variables=("T",))
    levels = np.array([1e4, 1e3, 1e2])  # 100, 10, 1 hPa
    T = to_pressure(ds, "T", levels)
    assert "pressure" in T.dims
    assert "lev" not in T.dims
    assert T.sizes["pressure"] == 3
    # T anywhere on Earth at these pressures is between 150 K and 350 K.
    assert T.min().values > 150.0
    assert T.max().values < 350.0


def test_to_pressure_methods_agree_in_stratosphere(waccmx_path):
    """Linear and loglinear give the same answer when the source coordinate
    is well-resolved — which it is for WACCM-X (~145 levels)."""
    ds = open_waccmx(waccmx_path, variables=("T",))
    levels = np.array([1e4, 1e3, 1e2])

    lin = to_pressure(ds, "T", levels, method="linear")
    log = to_pressure(ds, "T", levels, method="loglinear")
    assert np.allclose(lin.values, log.values, atol=2.0, rtol=0.01)


def test_to_height_thermosphere_telec(waccmx_path):
    """Electron temperature at 300 km altitude should be order 1000–3000 K.

    Below ~150 km, electrons thermalise with the neutral gas, so TElec ≈ T
    (a few hundred K). Above ~200 km, solar photoelectrons heat the plasma
    and TElec rises into the thousands of kelvin. The monthly global mean
    of TElec at 300 km in this run is around 1700 K.

    If ``to_height`` returns ~255 K at 300 km, the field is being paired
    with surface altitudes instead — the bug lives in the interpolation
    helper's handling of a descending source coordinate (Z3 runs from
    ~460 km at the model top down to a few hundred metres at the surface).
    """
    ds = open_waccmx(waccmx_path, variables=("TElec", "Z3"))
    altitudes = np.array([300_000.0])  # metres
    te = to_height(ds, "TElec", altitudes)

    g = float(te.mean().values)

    assert 1000.0 < g < 3000.0, (
        f"to_height returned TElec={g:.1f} K at 300 km altitude. "
        "Expected something in the 1000–3000 K range. Got a value that "
        "looks like a neutral-atmosphere temperature, which means the "
        "field has been paired with the wrong altitudes. The bug is in "
        "the interpolation helper, not in to_height itself."
    )


def test_to_height_loglinear_method_works(waccmx_path):
    """If the user passes method='loglinear', to_height returns sensible values.

    This test exists to highlight that the bug above is method-specific:
    one of the interp implementations handles descending source axes
    correctly, the other does not.
    """
    ds = open_waccmx(waccmx_path, variables=("TElec", "Z3"))
    altitudes = np.array([300_000.0])
    te = to_height(ds, "TElec", altitudes, method="loglinear")
    g = float(te.mean().values)
    assert 1000.0 < g < 3000.0


def test_zonal_mean_basic(waccmx_path):
    ds = open_waccmx(waccmx_path, variables=("T",))
    zm = zonal_mean(ds, "T")
    assert "lon" not in zm.dims
    assert "lat" in zm.dims
    assert "lev" in zm.dims
