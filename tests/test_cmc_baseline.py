"""Characterization fixtures for the pre-2-D (scalar) CMC behaviour.

These tests pin the current 1-D results so the joint 2-D refactor cannot
silently change the legacy path. Values were recorded on 2026-10-25 with the
default ANN surrogates (``random_state=42``).

Baselines
---------
cmsORAN CCO/ES demo (``run_cmc_demo`` defaults):
    optimal_value = -56.68896321070234
    satisfied before/after = 2/2, improved = True
    CCO predicted_at_optimum = 0.9109220629337655 (q=0.9)
    ES  predicted_at_optimum = 0.21277627847327146 (q=0.5)

Synthetic app1/app2 (``xapp1_direct.csv`` / ``xapp2_direct.csv``, q=0.4 each,
CMC resolution 300):
    optimal_value = -100.50167224080268
    satisfied before/after = 2/0, improved = False
    app1 predicted_at_optimum = 0.30360654186539204 (q=0.4, unsatisfied)
    app2 predicted_at_optimum = 0.39972216321487314 (q=0.4, unsatisfied)

Note: the synthetic value differs from the pre-refactor -83.110368 because
``predict_at(p1)`` now holds ``p2`` at each xApp's preferred value instead of
the dataset minimum. With only ``p1`` free, neither xApp can be satisfied --
this is precisely the gap that joint 2-D mitigation closes in Phase 2.
"""

from __future__ import annotations

import pytest

from surrogate_xapps.cmc import CMC
from surrogate_xapps.config import CMSORAN_SPEC, XAppConfig
from surrogate_xapps.data_loader import load_dataset
from surrogate_xapps.runner import run_cmc_demo
from surrogate_xapps.xapps import CCOxApp


def test_baseline_cmsoran_demo_is_stable() -> None:
    result = run_cmc_demo()
    mit = result["mitigation"]

    assert mit.optimal_value == pytest.approx(-56.68896321070234, abs=1e-6)
    assert mit.n_satisfied_before == 2
    assert mit.n_satisfied_after == 2
    assert mit.improved() is True

    by_id = {rec["xapp_id"]: rec for rec in mit.per_xapp}
    assert by_id["xApp_CCO"]["predicted_at_optimum"] == pytest.approx(
        0.9109220629337655, abs=1e-6
    )
    assert by_id["xApp_ES"]["predicted_at_optimum"] == pytest.approx(
        0.21277627847327146, abs=1e-6
    )


def test_baseline_synthetic_two_app_is_stable() -> None:
    configs = [
        XAppConfig(
            xapp_id="xApp1",
            spec=CMSORAN_SPEC,
            objective="max",
            qos_threshold=0.4,
            priority_weight=0.5,
            model_kind="ann",
            resolution=200,
        ),
        XAppConfig(
            xapp_id="xApp2",
            spec=CMSORAN_SPEC,
            objective="max",
            qos_threshold=0.4,
            priority_weight=0.5,
            model_kind="ann",
            resolution=200,
        ),
    ]
    files = ["data/synthetic/xapp1_direct.csv", "data/synthetic/xapp2_direct.csv"]
    xapps = []
    for cfg, path in zip(configs, files):
        X, y, _ = load_dataset(path, cfg.spec)
        xapps.append(CCOxApp(cfg).train(X, y))

    lo = min(x.ranges_["p1"][0] for x in xapps)
    hi = max(x.ranges_["p1"][1] for x in xapps)
    mit = CMC(range=(lo, hi), resolution=300).mitigate(xapps)

    assert mit.optimal_value == pytest.approx(-100.50167224080268, abs=1e-6)
    assert mit.n_satisfied_before == 2
    assert mit.n_satisfied_after == 0
    assert mit.improved() is False

    by_id = {rec["xapp_id"]: rec for rec in mit.per_xapp}
    assert by_id["xApp1"]["predicted_at_optimum"] == pytest.approx(
        0.30360654186539204, abs=1e-6
    )
    assert by_id["xApp2"]["predicted_at_optimum"] == pytest.approx(
        0.39972216321487314, abs=1e-6
    )
