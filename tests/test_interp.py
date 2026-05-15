"""Unit tests for the interp methods. No data file required."""

from __future__ import annotations

import numpy as np

from wxpost.interp import linear, loglinear


def test_linear_matches_numpy():
    x = np.array([0.0, 1.0, 2.0, 3.0])
    y = np.array([0.0, 10.0, 20.0, 30.0])
    target = np.array([0.5, 2.5])
    assert np.allclose(linear(x, y, target), [5.0, 25.0])


def test_loglinear_geometric_midpoint():
    """The log-linear midpoint between p=1 and p=0.01 is p=0.1.

    A field that varies linearly in log(p) — say, y = -log10(p) — should
    interpolate exactly at the geometric midpoint.
    """
    x = np.array([1.0, 0.01])
    y = np.array([0.0, 2.0])  # -log10(p)
    target = np.array([0.1])  # geometric midpoint
    out = loglinear(x, y, target)
    assert np.allclose(out, [1.0])  # -log10(0.1) == 1.0


def test_linear_and_loglinear_diverge_at_low_pressures():
    """For pressures that span orders of magnitude, the two methods give
    very different answers — by design.

    Use ascending source coords so we exercise the straightforward path
    of both methods.
    """
    x = np.array([1e-5, 1e-3])
    y = np.array([1000.0, 100.0])  # field decreases with pressure
    target = np.array([1e-4])

    lin = linear(x, y, target)
    log = loglinear(x, y, target)

    # Linear in pressure: 1e-4 is much closer to 1e-5 than to 1e-3, so
    # the result hugs y(1e-5) = 1000. Specifically (1e-4 - 1e-5)/(1e-3 - 1e-5)
    # ≈ 0.091, so result ≈ 1000 - 0.091 * 900 ≈ 918.
    assert lin[0] > 900
    # Linear in log(p): 1e-4 sits exactly at the log midpoint, so result is
    # the arithmetic mean of the two endpoints = 550.
    assert 500 < log[0] < 600
