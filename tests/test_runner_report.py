"""Tests for the dimension-aware CMC report and Phase 3 orchestration."""

from __future__ import annotations

from pathlib import Path

import pytest

from surrogate_xapps.cmc import CMC
from surrogate_xapps.config import CMSORAN_SPEC, XAppConfig
from surrogate_xapps.data_loader import load_dataset
from surrogate_xapps.runner import print_cmc_report, run_cmc_demo
from surrogate_xapps.xapps import CCOxApp

REPO_ROOT = Path(__file__).resolve().parents[1]
SYNTHETIC = REPO_ROOT / "data" / "synthetic"
SYNTHETIC_FILES = {
    "1": "xapp1_direct.csv",
    "2": "xapp2_direct.csv",
    "3": "xapp3_indirect.csv",
    "4": "xapp4_extra.csv",
}


def trained_synthetic(names: list[str], resolution: int = 32,
                      qos: float = 0.35) -> list[CCOxApp]:
    xapps = []
    for name in names:
        config = XAppConfig(
            xapp_id=f"xApp{name}",
            spec=CMSORAN_SPEC,
            objective="max",
            qos_threshold=qos,
            priority_weight=1.0,
            model_kind="ann",
            resolution=resolution,
        )
        X, y, _ = load_dataset(SYNTHETIC / SYNTHETIC_FILES[name], config.spec)
        xapps.append(CCOxApp(config).train(X, y))
    return xapps


def test_report_shows_four_xapps_without_nan(capsys):
    xapps = trained_synthetic(["1", "2", "3", "4"])
    actions = [xapp.infer_action() for xapp in xapps]
    mitigation = CMC(
        ranges=[(-150.0, 50.0), (0.0, 80.0)], resolution=32
    ).mitigate(xapps)
    print_cmc_report({"mitigation": mitigation, "conflict": True}, actions=actions)
    out = capsys.readouterr().out
    for name in ("xApp1", "xApp2", "xApp3", "xApp4"):
        assert name in out
    assert "nan" not in out.lower()
    assert "p* = (" in out
    assert "p1=" in out and "p2=" in out


def test_report_accepts_explicit_axis_selection(capsys):
    xapps = trained_synthetic(["1", "2"])
    actions = [xapp.infer_action() for xapp in xapps]
    mitigation = CMC(
        ranges=[(-150.0, 50.0), (0.0, 80.0)], resolution=16
    ).mitigate(xapps)
    print_cmc_report(
        {"mitigation": mitigation, "conflict": True}, actions=actions, axes=[0]
    )
    out = capsys.readouterr().out
    assert "p1=" in out
    assert "p2=" not in out


def test_report_legacy_two_action_result_still_works(cco_file: Path, es_file: Path,
                                                     capsys):
    result = run_cmc_demo(
        cco_file=cco_file, es_file=es_file, resolution=60, cmc_resolution=60
    )
    print_cmc_report(result)
    out = capsys.readouterr().out
    assert "xApp_CCO" in out
    assert "xApp_ES" in out
    assert "p* = (" in out
    assert "nan" not in out.lower()


# --- run_cmc_demo range intersection -------------------------------------

def test_demo_optimizes_only_shared_axes(cco_file: Path, es_file: Path):
    result = run_cmc_demo(
        cco_file=cco_file, es_file=es_file, resolution=60, cmc_resolution=60
    )
    mitigation = result["mitigation"]
    cco, es = result["cco"], result["es"]
    # cmsORAN: p1 is shared, but p2 is 20 for CCO and 60 for ES, so p2 has no
    # intersection and must stay fixed at each xApp's preferred value.
    assert len(mitigation.optimal_point) == 1
    lo = max(cco.ranges_["p1"][0], es.ranges_["p1"][0])
    hi = min(cco.ranges_["p1"][1], es.ranges_["p1"][1])
    assert lo <= mitigation.optimal_point[0] <= hi


def test_demo_optimizes_both_axes_when_they_overlap():
    result = run_cmc_demo(
        cco_file=SYNTHETIC / "xapp1_direct.csv",
        es_file=SYNTHETIC / "xapp2_direct.csv",
        resolution=32,
        cmc_resolution=32,
    )
    mitigation = result["mitigation"]
    cco, es = result["cco"], result["es"]
    assert len(mitigation.optimal_point) == 2
    for index, name in enumerate(("p1", "p2")):
        lo = max(cco.ranges_[name][0], es.ranges_[name][0])
        hi = min(cco.ranges_[name][1], es.ranges_[name][1])
        assert lo <= mitigation.optimal_point[index] <= hi
