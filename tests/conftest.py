"""Shared fixtures for wxpost tests."""

from __future__ import annotations

from pathlib import Path

import pytest

WACCMX_FILE = Path(
    "/glade/campaign/hao/itmodel/joemci/archive/"
    "f.e22.FXSD.f19_f19_mg17.001/atm/hist/2020/"
    "f.e22.FXSD.f19_f19_mg17.001.cam.h0.2020-01.nc"
)


@pytest.fixture(scope="session")
def waccmx_path() -> Path:
    """Path to the workshop WACCM-X file on /glade/campaign."""
    if not WACCMX_FILE.exists():
        pytest.skip(f"WACCM-X workshop file not accessible: {WACCMX_FILE}")
    return WACCMX_FILE
