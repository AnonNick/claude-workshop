# claude-workshop

Tiny Python package (`wxpost`) for WACCM-X post-processing.

## Build / test

```bash
pip install -e .[dev]
pytest                    # all tests
pytest -m "not needs_data"  # skip ones that read /glade
```

## Conventions

- Python 3.10+, type hints where useful, no Fortran.
- Coord order in our internal arrays: `(time, lev, lat, lon)`.
- Pressure stored in **Pa** internally, even though WACCM-X files use hPa
  on `lev`. Convert at the I/O boundary.

## Data

The workshop file (read-only):

```
/glade/campaign/hao/itmodel/joemci/archive/f.e22.FXSD.f19_f19_mg17.001/atm/hist/
  2020/f.e22.FXSD.f19_f19_mg17.001.cam.h0.2020-01.nc
```

Don't copy it into the repo. Open it from there.

## Known-failing tests

Two tests are expected to fail on a fresh clone. They are the workshop
exercises. Don't fix them before the workshop.

- `tests/test_io.py::test_lat_orientation` — warm-up exercise.
- `tests/test_ops.py::test_to_height_thermosphere_edens` — main exercise.
