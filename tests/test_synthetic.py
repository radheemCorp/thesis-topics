"""Contract tests for the synthetic 2-D conflict datasets.

Pins the on-disk data contract in ``data/synthetic`` (ranges, peak
coordinates, and amplitudes) so the CMC scenario tests can rely on the
documented peaks.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

from surrogate_xapps.config import CMSORAN_SPEC
from surrogate_xapps.data_loader import load_dataset

REPO_ROOT = Path(__file__).resolve().parents[1]
SYNTHETIC_DIR = REPO_ROOT / "data" / "synthetic"
META_PATH = SYNTHETIC_DIR / "synthetic_meta.json"

#: Expected cmsORAN layout advertised by the metadata file.
LAYOUT = "cmsORAN (Input1,Input2,Output)"

#: Synthetic datasets, in the order documented in ``docs/synthetic/README.md``.
PEAK_NAMES = (
    "xapp1_direct",
    "xapp2_direct",
    "xapp3_indirect",
    "xapp4_extra",
)


@pytest.fixture(scope="module")
def meta() -> dict:
    """Parsed contents of ``synthetic_meta.json``."""
    return json.loads(META_PATH.read_text())


def test_metadata_layout_and_peak_set(meta: dict) -> None:
    assert meta["layout"] == LAYOUT
    assert set(meta["peaks"]) == set(PEAK_NAMES)
    assert all(
        info["objective"] == "max" for info in meta["peaks"].values()
    )


def test_all_synthetic_files_exist() -> None:
    for name in PEAK_NAMES:
        assert (SYNTHETIC_DIR / f"{name}.csv").is_file()


@pytest.mark.parametrize("name", PEAK_NAMES)
def test_dataset_matches_metadata(name: str, meta: dict) -> None:
    path = SYNTHETIC_DIR / f"{name}.csv"
    X, y, ranges = load_dataset(path, CMSORAN_SPEC)
    info = meta["peaks"][name]

    assert X.shape[1] == 2
    assert len(X) == len(y) > 0
    assert np.all(np.isfinite(X))
    assert np.all(np.isfinite(y))

    for feature, index in (("p1", 0), ("p2", 1)):
        expected = meta["range"][feature]
        assert ranges[feature] == pytest.approx(tuple(expected), abs=1e-9)
        assert X[:, index].min() == pytest.approx(expected[0], abs=1e-9)
        assert X[:, index].max() == pytest.approx(expected[1], abs=1e-9)

    peak_index = int(np.argmax(y))
    assert X[peak_index] == pytest.approx(
        [info["p1c"], info["p2c"]], abs=1e-9
    )
    assert y[peak_index] == pytest.approx(info["A"], abs=1e-9)
    assert float(np.max(y)) == pytest.approx(info["A"], abs=1e-9)
