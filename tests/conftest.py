"""Shared pytest fixtures and configuration."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

# Force a headless matplotlib backend for the whole test session.
os.environ.setdefault("MPLBACKEND", "Agg")

REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = REPO_ROOT / "data"
SYNTHETIC_DIR = DATA_DIR / "synthetic"

#: Synthetic 2-D scenario datasets keyed by xApp name.
SYNTHETIC_FILES = {
    "xapp1_direct": SYNTHETIC_DIR / "xapp1_direct.csv",
    "xapp2_direct": SYNTHETIC_DIR / "xapp2_direct.csv",
    "xapp3_indirect": SYNTHETIC_DIR / "xapp3_indirect.csv",
    "xapp4_extra": SYNTHETIC_DIR / "xapp4_extra.csv",
}

#: Report identifiers used for the synthetic xApps.
SYNTHETIC_IDS = {
    "xapp1_direct": "xApp1",
    "xapp2_direct": "xApp2",
    "xapp3_indirect": "xApp3",
    "xapp4_extra": "xApp4",
}


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


@pytest.fixture(scope="session")
def synthetic_xapp():
    """Factory for trained max-objective xApps on the synthetic datasets.

    Trained instances are cached per ``(name, qos, weight, resolution)`` so the
    Phase 4 scenario tests do not refit the same ANN repeatedly.
    """
    from surrogate_xapps.config import CMSORAN_SPEC, XAppConfig
    from surrogate_xapps.data_loader import load_dataset
    from surrogate_xapps.xapps import CCOxApp

    cache = {}

    def make(
        name: str,
        *,
        qos: float = 0.4,
        weight: float = 1.0,
        resolution: int = 16,
        model_kind: str = "ann",
    ):
        key = (name, qos, weight, resolution, model_kind)
        if key not in cache:
            config = XAppConfig(
                xapp_id=SYNTHETIC_IDS[name],
                spec=CMSORAN_SPEC,
                objective="max",
                qos_threshold=qos,
                priority_weight=weight,
                model_kind=model_kind,
                resolution=resolution,
            )
            X, y, _ = load_dataset(SYNTHETIC_FILES[name], CMSORAN_SPEC)
            cache[key] = CCOxApp(config).train(X, y)
        return cache[key]

    return make

