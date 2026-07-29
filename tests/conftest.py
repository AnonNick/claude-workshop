"""Shared fixtures for wxpost tests."""

from __future__ import annotations

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
SAMPLE_FILE = REPO_ROOT / "data" / "sample.nc"


@pytest.fixture(scope="session")
def waccmx_path() -> Path:
    """Path to the sample WACCM-X file that ships with the repo.

    Synthetic, but shaped exactly like a real WACCM-X CAM ``h0`` monthly
    mean. See ``data/make_sample.py``.
    """
    if not SAMPLE_FILE.exists():
        pytest.fail(
            f"sample data file missing: {SAMPLE_FILE}\n"
            "It is committed to the repo — try `git checkout data/sample.nc`, "
            "or regenerate it with `python data/make_sample.py`."
        )
    return SAMPLE_FILE
