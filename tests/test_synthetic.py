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

from surrogate_xapps.cmc import CMC
from surrogate_xapps.config import CMSORAN_SPEC
from surrogate_xapps.data_loader import load_dataset

REPO_ROOT = Path(__file__).resolve().parents[1]
SYNTHETIC_DIR = REPO_ROOT / "data" / "synthetic"
META_PATH = SYNTHETIC_DIR / "synthetic_meta.json"

#: Joint CMC search box shared by every synthetic dataset.
RANGES = ((-150.0, 50.0), (0.0, 80.0))

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


def test_direct_conflict_compromise_lies_between_requests(synthetic_xapp):
    """app1 vs app2 is a direct 2-D conflict on both ICPs."""
    xapp1 = synthetic_xapp("xapp1_direct", qos=0.35)
    xapp2 = synthetic_xapp("xapp2_direct", qos=0.35)

    result = CMC(ranges=RANGES, resolution=16).mitigate([xapp1, xapp2])
    p1, p2 = result.optimal_point

    request1 = xapp1.preferred_point
    request2 = xapp2.preferred_point
    for axis, value in enumerate((p1, p2)):
        low = min(request1[axis], request2[axis])
        high = max(request1[axis], request2[axis])
        assert low <= value <= high

    assert [record["xapp_id"] for record in result.per_xapp] == [
        "xApp1",
        "xApp2",
    ]
    assert result.n_satisfied_before == 2
    assert result.n_satisfied_after == 2
    assert result.improved() is True


def test_indirect_conflict_shifts_p2_towards_app3(synthetic_xapp, meta):
    """Adding app3 moves the p2 compromise toward app3's p2 peak.

    app3's QoS threshold is set at 0.8 so its deviation term is active at the
    app1/app2 compromise; with looser thresholds app3 is already satisfied
    everywhere in the shared region and cannot influence the optimum.
    """
    pair = [
        synthetic_xapp("xapp1_direct", qos=0.4),
        synthetic_xapp("xapp2_direct", qos=0.4),
    ]
    app3 = synthetic_xapp("xapp3_indirect", qos=0.8)
    cmc = CMC(ranges=RANGES, resolution=16)

    two_app = cmc.mitigate(pair)
    three_app = cmc.mitigate([*pair, app3])

    assert len(three_app.per_xapp) == 3
    assert [record["xapp_id"] for record in three_app.per_xapp] == [
        "xApp1",
        "xApp2",
        "xApp3",
    ]

    peak_p2 = float(meta["peaks"]["xapp3_indirect"]["p2c"])
    p2_two = two_app.optimal_point[1]
    p2_three = three_app.optimal_point[1]

    assert p2_three != pytest.approx(p2_two, abs=1e-9)
    assert abs(p2_three - peak_p2) < abs(p2_two - peak_p2)


def test_priority_weight_pulls_p2_towards_app3(synthetic_xapp):
    """A larger app3 priority weight moves p2* toward app3's preference."""
    pair = [
        synthetic_xapp("xapp1_direct", qos=0.4),
        synthetic_xapp("xapp2_direct", qos=0.4),
    ]
    cmc = CMC(ranges=RANGES, resolution=16)

    p2_optima = []
    app3 = None
    for weight in (0.25, 0.5, 1.0):
        app3 = synthetic_xapp("xapp3_indirect", qos=0.8, weight=weight)
        result = cmc.mitigate([*pair, app3])
        p2_optima.append(result.optimal_point[1])

    assert app3 is not None
    target_p2 = app3.preferred_point[1]
    distances = [abs(p2 - target_p2) for p2 in p2_optima]

    assert all(
        later <= earlier + 1e-9
        for earlier, later in zip(distances, distances[1:])
    )
    assert distances[-1] < distances[0]


def test_tightening_thresholds_never_increases_satisfied_count(
    synthetic_xapp,
):
    """A stricter QoS threshold cannot raise the number of satisfied xApps."""
    cmc = CMC(ranges=RANGES, resolution=16)

    satisfied_after = []
    for threshold in (0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9):
        pair = [
            synthetic_xapp("xapp1_direct", qos=threshold),
            synthetic_xapp("xapp2_direct", qos=threshold),
        ]
        result = cmc.mitigate(pair)
        satisfied_after.append(result.n_satisfied_after)
        assert result.improved() == (
            result.n_satisfied_after >= result.n_satisfied_before
        )

    assert all(
        later <= earlier
        for earlier, later in zip(satisfied_after, satisfied_after[1:])
    )
    assert satisfied_after[0] > satisfied_after[-1]
