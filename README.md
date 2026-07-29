# claude-workshop

A tiny Python package — `wxpost` — for post-processing WACCM-X CAM history
files. This is the demo repository for the HAO Claude workshop.

What it does, in one line: load a WACCM-X NetCDF, interpolate fields from
the native hybrid sigma-pressure grid onto fixed pressure or altitude
levels, and a few standard reductions on top of that.

It also ships two deliberate bugs. Finding and fixing them is the workshop.

## Setup

You need Python 3.10+ and about two minutes. `wxpost` goes into its **own**
environment — never a base or system interpreter.

```bash
git clone https://github.com/AnonNick/claude-workshop.git
cd claude-workshop

python3 -m venv .venv && source .venv/bin/activate
pip install -e .[dev]
```

Prefer `uv` or conda? `uv venv && source .venv/bin/activate` works, so does
`conda create -n wxpost python=3.12 -y && conda activate wxpost`. Any
isolated 3.10+ interpreter is fine. All deps (numpy, xarray, netCDF4,
matplotlib) come in via pip.

Then run the tests:

```bash
pytest
```

You should see:

```
2 failed, 10 passed
```

**The two failures are intentional.** They are the workshop exercises —
please don't fix them before you show up:

| Test | Role |
|---|---|
| `tests/test_io.py::test_lat_orientation` | the warm-up bug |
| `tests/test_ops.py::test_to_height_thermosphere_telec` | the main bug — the interpolation one |

If you see a different count, something is wrong with your environment.
Flag it and someone will help.

## The data

`data/sample.nc` (about 550 KiB) ships with the repo, so everything runs on
your laptop with no HPC access and nothing to download.

It is **synthetic**. It has the shape, coordinates, variables and attributes
of a real WACCM-X CAM `h0` monthly-mean file — 96 levels from 4e-10 hPa down
to the surface, 49 latitudes, 24 longitudes, one January 2020 time step,
with `T`, `U`, `V`, `Z3`, `TElec`, `TIon`, `PS` and the hybrid-sigma
coefficients. Its fields follow analytic profiles chosen to be physically
plausible, but no number in it came out of a model run. Don't put it in a
paper.

`data/make_sample.py` generates it and documents every profile. You should
never need to run it — the file is committed.

## See the warm-up bug

```bash
python examples/plot_surface_temperature.py
```

January is northern winter, so 60°N should be far colder than 60°S. Before
the fix, the script reports the opposite and says so:

```
  60°N (label):  -0.3°C    expected ~ -12°C  (NH winter)
  60°S (label): -12.3°C    expected ~   0°C  (SH summer)
  ⚠ The plot shows 60°N WARMER than 60°S in January. That's impossible.
```

It writes `examples/surface_temperature.png` (not committed).

## Package layout

```
src/wxpost/
├── io.py          open WACCM-X files, basic accessors
├── coords/        vertical-coordinate systems
│   ├── pressure.py    hyam*P0 + hybm*PS  →  Pa, on every gridpoint
│   └── height.py      uses Z3 (geopotential height) directly
├── interp/        1-D interpolation methods
│   ├── linear.py      linear-in-pressure
│   └── loglinear.py   linear-in-log-pressure (correct for atmospheric work)
└── ops/           user-facing operations
    ├── to_pressure.py   field on model levels → field on fixed pressure
    ├── to_height.py     field on model levels → field on fixed altitude
    └── zonal_mean.py    mean over longitude
```

## During the workshop

Part 2 walks through Claude Code on this repo. Every command, in order:
[docs/COMMANDS.md](docs/COMMANDS.md) — that's the handout.

## License

For internal HAO workshop use. Not packaged for distribution.
