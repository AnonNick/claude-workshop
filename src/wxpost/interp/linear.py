"""Linear interpolation in the source coordinate."""

from __future__ import annotations

import numpy as np


def interp_1d(
    x_src: np.ndarray,
    y_src: np.ndarray,
    x_target: np.ndarray,
) -> np.ndarray:
    """Linear interpolation of ``y_src`` from ``x_src`` to ``x_target``.

    ``x_src`` must be 1-D and monotonic; ``y_src`` must have ``x_src.size``
    as its last dimension. ``x_target`` is 1-D. Returns an array whose
    last dimension is ``x_target.size``.

    Out-of-range targets are clamped to the endpoint values (``np.interp``
    default behaviour).
    """
    x_src = np.asarray(x_src)
    x_target = np.asarray(x_target)

    # numpy.interp requires the source coordinate to be ascending. Pressure
    # in WACCM-X is stored top-down (smallest first), so the source axis is
    # almost always already ascending and this branch is rarely taken.
    if x_src[0] > x_src[-1]:
        x_src = x_src[::-1]

    return np.apply_along_axis(
        lambda y: np.interp(x_target, x_src, y),
        axis=-1,
        arr=y_src,
    )
