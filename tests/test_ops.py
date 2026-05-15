"""Tests for the user-facing operations.

``test_to_height_thermosphere_edens`` is **expected to fail** at workshop
start. Fixing it is the main exercise. The other tests should pass.
"""

from __future__ import annotations

import numpy as np
import pytest

from wxpost import open_waccmx, to_height, to_pressure, zonal_mean


@pytest.mark.needs_data
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


@pytest.mark.needs_data
def test_to_pressure_methods_agree_in_stratosphere(waccmx_path):
    """Linear and loglinear give the same answer when the source coordinate
    is well-resolved — which it is for WACCM-X (~145 levels)."""
    ds = open_waccmx(waccmx_path, variables=("T",))
    levels = np.array([1e4, 1e3, 1e2])

    lin = to_pressure(ds, "T", levels, method="linear")
    log = to_pressure(ds, "T", levels, method="loglinear")
    assert np.allclose(lin.values, log.values, atol=2.0, rtol=0.01)


@pytest.mark.needs_data
def test_to_height_thermosphere_edens(waccmx_path):
    """Electron density at 300 km altitude should be order 1e5 m^-3 in the monthly mean.

    From the model itself: monthly-mean EDens around the F-region peak
    (200–300 km) averages ~10^5 electrons/m^3. Below the mesopause (~80 km)
    it falls to essentially zero (~10^-15). If ``to_height`` returns a
    value many orders of magnitude away from 10^5 at 300 km altitude,
    something is wrong with the altitude-to-field pairing inside the
    interpolation helper.
    """
    ds = open_waccmx(waccmx_path, variables=("EDens", "Z3"))
    altitudes = np.array([300_000.0])  # metres
    ne = to_height(ds, "EDens", altitudes)

    g = float(ne.mean().values)

    assert 1e4 < g < 1e6, (
        f"to_height returned EDens={g:.3e} m^-3 at 300 km altitude. "
        f"Expected ~10^5. The values are paired with the wrong altitudes — "
        "look at how the interpolation helper handles a descending source axis."
    )


@pytest.mark.needs_data
def test_to_height_loglinear_method_works(waccmx_path):
    """If the user passes method='loglinear', to_height returns sensible values.

    This test exists to highlight that the bug above is method-specific:
    one of the interp implementations handles descending source axes
    correctly, the other does not.
    """
    ds = open_waccmx(waccmx_path, variables=("EDens", "Z3"))
    altitudes = np.array([300_000.0])
    ne = to_height(ds, "EDens", altitudes, method="loglinear")
    g = float(ne.mean().values)
    assert 1e4 < g < 1e6


@pytest.mark.needs_data
def test_zonal_mean_basic(waccmx_path):
    ds = open_waccmx(waccmx_path, variables=("T",))
    zm = zonal_mean(ds, "T")
    assert "lon" not in zm.dims
    assert "lat" in zm.dims
    assert "lev" in zm.dims
