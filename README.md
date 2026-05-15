# claude-workshop

A tiny Python package — `wxpost` — for post-processing WACCM-X CAM history
files. Used as the demo repository for the HAO Claude Code workshop.

What it does, in one line: load a WACCM-X NetCDF, interpolate fields from
the native hybrid sigma-pressure grid onto fixed pressure or altitude levels,
and a few standard reductions on top of that.

## Install

```bash
git clone https://github.com/AnonNick/claude-workshop.git
cd claude-workshop
python -m venv .venv && source .venv/bin/activate
pip install -e .[dev]
```

(`uv sync` works too if you have `uv` installed.)

**Running on Derecho or Casper?** See [docs/SETUP-DERECHO.md](docs/SETUP-DERECHO.md)
— there are two NCAR-specific gotchas (Node `npx -y` bug, libstdc++
mismatch) that you'll hit while installing Claude Code's GitNexus MCP
server. The doc walks through both with copy-pasteable commands.

## The data

Tests reference one file on Derecho `campaign`:

```
/glade/campaign/hao/itmodel/joemci/archive/f.e22.FXSD.f19_f19_mg17.001/
    atm/hist/2020/f.e22.FXSD.f19_f19_mg17.001.cam.h0.2020-01.nc
```

This is a WACCM-X FXSD monthly-mean h0 file for January 2020, on the f19
grid (~1.9°×2.5°), 145 vertical levels. About 1.8 GB. We only read a few
variables out of it (`T`, `U`, `V`, `Z3`, `PS`, `TElec`, `TIon`, plus the
hybrid-sigma coefficients `hyam`, `hybm`, `P0`).

Tests that touch this file are marked `needs_data`. Run only the ones that
don't need the file:

```bash
pytest -m "not needs_data"
```

## Run the tests

```bash
pytest                    # all tests
pytest -m needs_data      # only the ones that read the WACCM-X file
```

You should see **two failures** out of the box. They are intentional — they
are the bugs you'll fix during the workshop. Don't fix them before showing
up.

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

## License

For internal HAO workshop use. Not packaged for distribution.
