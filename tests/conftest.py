"""Shared pytest fixtures and configuration."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

# Force a headless matplotlib backend for the whole test session.
os.environ.setdefault("MPLBACKEND", "Agg")

REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = REPO_ROOT / "data"


@pytest.fixture
def cco_file() -> Path:
    """Path to the CCO (throughput) dataset."""
    return DATA_DIR / "cmsORAN" / "data1.csv"


@pytest.fixture
def es_file() -> Path:
    """Path to the ES (power) dataset."""
    return DATA_DIR / "cmsORAN" / "data2.csv"


@pytest.fixture
def qacm_file() -> Path:
    """Path to a QACM-layout dataset."""
    return DATA_DIR / "QACM" / "data1.csv"
