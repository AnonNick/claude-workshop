"""Linear interpolation in the logarithm of the source coordinate.

For atmospheric work the vertical coordinate (pressure) spans many orders
of magnitude, so linear-in-log-pressure is the right thing to do almost
everywhere — especially above the stratopause where layer-to-layer
pressure ratios are large.

Don't use this when ``x_src`` contains non-positive values.
"""

from __future__ import annotations

import numpy as np


def interp_1d(
    x_src: np.ndarray,
    y_src: np.ndarray,
    x_target: np.ndarray,
) -> np.ndarray:
    """Linear interpolation of ``y_src`` from ``log(x_src)`` to ``log(x_target)``."""
    x_src = np.asarray(x_src, dtype=float)
    x_target = np.asarray(x_target, dtype=float)

    if np.any(x_src <= 0) or np.any(x_target <= 0):
        raise ValueError("loglinear interp requires strictly positive coordinates")

    log_src = np.log(x_src)
    log_target = np.log(x_target)

    if log_src[0] > log_src[-1]:
        log_src = log_src[::-1]
        y_src = np.flip(y_src, axis=-1)

    return np.apply_along_axis(
        lambda y: np.interp(log_target, log_src, y),
        axis=-1,
        arr=y_src,
    )
