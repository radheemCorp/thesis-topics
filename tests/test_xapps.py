"""Tests for the xApp classes, decision logic, and control-request schema."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from surrogate_xapps.config import CCO_CONFIG, ES_CONFIG, CMSORAN_SPEC, XAppConfig
from surrogate_xapps.data_loader import load_dataset
from surrogate_xapps.xapps import (
    REQUIRED_ACTION_KEYS,
    CCOxApp,
    ESxApp,
    validate_action,
)


@pytest.fixture
def trained_cco(cco_file: Path) -> CCOxApp:
    X, y, _ = load_dataset(cco_file, CCO_CONFIG.spec)
    return CCOxApp(CCO_CONFIG).train(X, y)


@pytest.fixture
def trained_es(es_file: Path) -> ESxApp:
    X, y, _ = load_dataset(es_file, ES_CONFIG.spec)
    return ESxApp(ES_CONFIG).train(X, y)


def test_infer_action_has_required_keys(trained_cco: CCOxApp):
    action = trained_cco.infer_action()
    for key in REQUIRED_ACTION_KEYS:
        assert key in action


def test_requested_value_is_full_tuple(trained_cco: CCOxApp):
    action = trained_cco.infer_action()
    assert action["target_parameter"] == ["p1", "p2"]
    assert len(action["requested_value"]) == 2
    assert len(action["parameter_range"]) == 2


def test_requested_value_within_range(trained_cco: CCOxApp):
    action = trained_cco.infer_action()
    for value, (lo, hi) in zip(action["requested_value"], action["parameter_range"]):
        assert lo <= value <= hi


def test_cco_selects_grid_argmax(trained_cco: CCOxApp):
    action = trained_cco.infer_action()
    grid = trained_cco._candidate_grid()
    preds = trained_cco.predict_kpi(grid)
    best = grid[int(np.argmax(preds))]
    np.testing.assert_allclose(action["requested_value"], best)


def test_es_selects_grid_argmin(trained_es: ESxApp):
    action = trained_es.infer_action()
    grid = trained_es._candidate_grid()
    preds = trained_es.predict_kpi(grid)
    best = grid[int(np.argmin(preds))]
    np.testing.assert_allclose(action["requested_value"], best)


def test_cco_and_es_conflict(trained_cco: CCOxApp, trained_es: ESxApp):
    a = trained_cco.infer_action()
    b = trained_es.infer_action()
    assert abs(a["requested_value"][0] - b["requested_value"][0]) > 1.0


def test_infer_before_train_raises():
    with pytest.raises(RuntimeError):
        CCOxApp(CCO_CONFIG).infer_action()


def test_validate_action_rejects_missing_key():
    with pytest.raises(ValueError, match="missing required key"):
        validate_action({"xapp_id": "x"})


def test_validate_action_rejects_out_of_range():
    bad = {
        "xapp_id": "xApp_CCO",
        "target_parameter": ["p1", "p2"],
        "requested_value": [999.0, 0.0],
        "parameter_range": [[-150.0, 150.0], [20.0, 20.0]],
        "predicted_kpi": 1.0,
        "qos_threshold": 0.9,
        "priority_weight": 0.5,
    }
    with pytest.raises(ValueError, match="outside range"):
        validate_action(bad)


def test_qos_satisfied_semantics():
    cco = CCOxApp(XAppConfig(xapp_id="c", spec=CMSORAN_SPEC, objective="max", qos_threshold=0.9))
    es = ESxApp(XAppConfig(xapp_id="e", spec=CMSORAN_SPEC, objective="min", qos_threshold=0.5))
    assert cco.qos_satisfied(0.95) is True
    assert cco.qos_satisfied(0.5) is False
    assert es.qos_satisfied(0.4) is True
    assert es.qos_satisfied(0.6) is False
