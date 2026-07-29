# claude-workshop

A tiny Python package — `wxpost` — for post-processing WACCM-X CAM history
files. Used as the demo repository for the HAO Claude Code workshop.

What it does, in one line: load a WACCM-X NetCDF, interpolate fields from
the native hybrid sigma-pressure grid onto fixed pressure or altitude levels,
and a few standard reductions on top of that.

## Install

`wxpost` needs its **own** fresh Python environment (3.10+). Don't install it
into a base or system interpreter — pick one of the two paths below.

```bash
git clone https://github.com/AnonNick/claude-workshop.git
cd claude-workshop
```

### On Derecho / Casper

Any NCAR HPC system with the `conda` module:

```bash
module load conda
conda create -n wxpost python=3.12 -y
conda activate wxpost
pip install -e .[dev]
```

Every new shell needs `module load conda && conda activate wxpost` again —
add both lines to `~/.bashrc` if you'd rather not type them each time.

### Anywhere else

No `conda` module needed; any isolated 3.10+ interpreter works. Pick one:

```bash
python3 -m venv .venv && source .venv/bin/activate   # Option A — stdlib venv
uv venv && source .venv/bin/activate                 # Option B — uv
# Option C — a personal conda/miniforge install, e.g.
#   conda create -n wxpost python=3.12 -y && conda activate wxpost
```

Then:

```bash
pip install -e .[dev]
```

All runtime deps (numpy, xarray, netCDF4, matplotlib) come in via pip, so a
plain venv is enough — conda is only required on NCAR systems.

**For the workshop itself** — every command, in order, end-to-end:
see [docs/COMMANDS.md](docs/COMMANDS.md).

**Running on Derecho or Casper?** See
[docs/SETUP-DERECHO.md](docs/SETUP-DERECHO.md) for conda-env and Claude Code
setup on NCAR systems.

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
