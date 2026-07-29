"""Plot January surface temperature from ``data/sample.nc``.

Run this *before* fixing the lat-orientation bug to see what the bug
looks like. January is northern winter, so the Arctic should be far
colder than the Antarctic (Antarctica is cold year-round, but January
is its summer — the Arctic in January is the coldest place on Earth).

The buggy IO layer reverses the latitude coordinate without reversing
the data, so the cold winter pole ends up labelled as the South Pole
and the warmer summer pole ends up labelled as the North Pole.

Usage
-----

    python examples/plot_surface_temperature.py

Writes ``surface_temperature.png`` next to the script. That PNG is
generated output — it is not committed.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # write a PNG rather than opening a window
import matplotlib.pyplot as plt

from wxpost.io import open_waccmx

WACCMX_FILE = Path(__file__).resolve().parent.parent / "data" / "sample.nc"


def main() -> None:
    ds = open_waccmx(WACCMX_FILE, variables=("T",))

    T_surface = ds["T"].isel(time=0, lev=-1)
    T_celsius = T_surface - 273.15
    T_zonal_mean = T_celsius.mean(dim="lon")

    fig, (ax_map, ax_zm) = plt.subplots(
        1, 2, figsize=(15, 5), gridspec_kw={"width_ratios": [2, 1]}
    )

    pcm = ax_map.pcolormesh(
        T_surface["lon"],
        T_surface["lat"],
        T_celsius.values,
        cmap="RdBu_r",
        vmin=-50,
        vmax=40,
        shading="auto",
    )
    ax_map.set_xlabel("longitude (°E)")
    ax_map.set_ylabel("latitude (°N)")
    ax_map.set_title("Surface T  ·  January 2020")
    ax_map.axhline(0, color="k", lw=0.5, alpha=0.3)
    fig.colorbar(pcm, ax=ax_map, label="T (°C)")

    ax_zm.plot(T_zonal_mean.values, T_zonal_mean["lat"].values, lw=2)
    ax_zm.set_xlabel("zonal-mean T (°C)")
    ax_zm.set_ylabel("latitude (°N)")
    ax_zm.set_title("zonal mean")
    ax_zm.axhline(0, color="k", lw=0.5, alpha=0.3)
    ax_zm.axvline(0, color="k", lw=0.5, alpha=0.3)
    ax_zm.set_xlim(-50, 40)
    ax_zm.grid(alpha=0.3)

    # The bug is dramatic at mid-latitudes (the poles happen to be cold on
    # both sides because Antarctica is high and icy year-round). Annotate
    # 60°N and 60°S so the hemispheric asymmetry is unmistakable.
    nh_T = float(T_zonal_mean.sel(lat=60, method="nearest").values)
    sh_T = float(T_zonal_mean.sel(lat=-60, method="nearest").values)
    ax_zm.annotate(
        f"label='60°N'\n{nh_T:+.1f}°C",
        xy=(nh_T, 60),
        xytext=(-45, 75),
        fontsize=9,
        arrowprops=dict(arrowstyle="->", color="black", lw=0.5),
    )
    ax_zm.annotate(
        f"label='60°S'\n{sh_T:+.1f}°C",
        xy=(sh_T, -60),
        xytext=(-45, -75),
        fontsize=9,
        arrowprops=dict(arrowstyle="->", color="black", lw=0.5),
    )

    fig.suptitle(
        "WACCM-X surface temperature.  Hint: January is NH winter — "
        "60°N should be far colder than 60°S.",
        fontsize=11,
    )
    fig.tight_layout()

    out = Path(__file__).with_name("surface_temperature.png")
    fig.savefig(out, dpi=120)
    print(f"wrote {out}")
    print(f"  60°N (label):  {nh_T:+.1f}°C    expected ~ -12°C  (NH winter)")
    print(f"  60°S (label):  {sh_T:+.1f}°C    expected ~   0°C  (SH summer)")
    if nh_T > sh_T:
        print(
            "  ⚠ The plot shows 60°N WARMER than 60°S in January. "
            "That's impossible. The latitude axis is mislabeled."
        )


if __name__ == "__main__":
    main()
