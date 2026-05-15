"""1-D interpolation methods used by the ``ops`` module.

Each module exposes a single function with the signature::

    interp_1d(x_src, y_src, x_target) -> y_target

where ``x_src`` is strictly monotonic. We use this for interpolation
along the vertical dimension only.
"""

from wxpost.interp.linear import interp_1d as linear
from wxpost.interp.loglinear import interp_1d as loglinear

REGISTRY = {
    "linear": linear,
    "loglinear": loglinear,
}

__all__ = ["linear", "loglinear", "REGISTRY"]
