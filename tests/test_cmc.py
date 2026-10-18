"""Tests for the CMC module: IQueryableXApp protocol, heuristic, and results.

These tests define the expected behaviour of the QACM Conflict Mitigation
Controller MVP before it is implemented (TDD Red phase).
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol, runtime_checkable

import numpy as np
import pytest

from surrogate_xapps.cmc import IQueryableXApp


@runtime_checkable
class _HasPredictAt(Protocol):
    """Structural check helper (mirrors the real protocol shape)."""

    def predict_at(self, p1: float) -> float: ...


class _MockXApp:
    """Analytic mock xApp whose KPI is a simple function of p1."""

    def __init__(self, xapp_id: str, slope: float, intercept: float, objective: str,
                 qos_threshold: float, priority_weight: float, p2_const: float = 0.0):
        self.xapp_id = xapp_id
        self.slope = slope
        self.intercept = intercept
        self.objective = objective
        self.qos_threshold = qos_threshold
        self.priority_weight = priority_weight
        self.p2_const = p2_const

    def predict_at(self, p1: float) -> float:
        return self.slope * p1 + self.intercept


def test_protocol_is_runtime_checkable():
    assert isinstance(_MockXApp("x", 1.0, 0.0, "max", 0.5, 0.5), IQueryableXApp)


def test_protocol_requires_predict_at():
    class NoPredict:
        pass

    assert not isinstance(NoPredict(), IQueryableXApp)


def test_protocol_predict_at_returns_float():
    xapp = _MockXApp("x", 1.0, 0.0, "max", 0.5, 0.5)
    result = xapp.predict_at(1.0)
    assert isinstance(result, float)


# --- BaseXApp.predict_at adapter -------------------------------------------

from surrogate_xapps.config import CCO_CONFIG, ES_CONFIG  # noqa: E402
from surrogate_xapps.data_loader import load_dataset  # noqa: E402
from surrogate_xapps.xapps import CCOxApp, ESxApp  # noqa: E402


@pytest.fixture
def trained_cco(cco_file: Path) -> CCOxApp:
    X, y, _ = load_dataset(cco_file, CCO_CONFIG.spec)
    return CCOxApp(CCO_CONFIG).train(X, y)


@pytest.fixture
def trained_es(es_file: Path) -> ESxApp:
    X, y, _ = load_dataset(es_file, ES_CONFIG.spec)
    return ESxApp(ES_CONFIG).train(X, y)


def test_base_xapp_satisfies_protocol(trained_cco: CCOxApp, trained_es: ESxApp):
    assert isinstance(trained_cco, IQueryableXApp)
    assert isinstance(trained_es, IQueryableXApp)


def test_predict_at_matches_predict_kpi(trained_cco: CCOxApp):
    p1 = -47.49
    p2_const = trained_cco.ranges_["p2"][0]
    row = np.array([[p1, p2_const]])
    expected = float(trained_cco.predict_kpi(row)[0])
    got = trained_cco.predict_at(p1)
    assert got == pytest.approx(expected)


def test_predict_at_holds_p2_constant(trained_es: ESxApp):
    # predict_at must hold p2 at the observed constant (min of range for ES=60).
    p2_const = trained_es.ranges_["p2"][0]
    assert p2_const == 60.0
    row1 = np.array([[-100.0, p2_const]])
    row2 = np.array([[-50.0, p2_const]])
    k1 = float(trained_es.predict_kpi(row1)[0])
    k2 = float(trained_es.predict_kpi(row2)[0])
    assert trained_es.predict_at(-100.0) == pytest.approx(k1)
    assert trained_es.predict_at(-50.0) == pytest.approx(k2)


# --- MitigationResult dataclass -------------------------------------------

from surrogate_xapps.cmc import MitigationResult  # noqa: E402


def test_mitigation_result_fields():
    per_xapp = [
        {"xapp_id": "a", "satisfied_at_optimum": True, "satisfied_before": False},
        {"xapp_id": "b", "satisfied_at_optimum": False, "satisfied_before": False},
    ]
    res = MitigationResult(
        optimal_value=1.0,
        per_xapp=per_xapp,
        n_satisfied_before=0,
        n_satisfied_after=1,
    )
    assert res.optimal_value == 1.0
    assert res.per_xapp == per_xapp
    assert res.n_satisfied_before == 0
    assert res.n_satisfied_after == 1


def test_mitigation_result_improved():
    res = MitigationResult(
        optimal_value=0.0,
        per_xapp=[],
        n_satisfied_before=1,
        n_satisfied_after=2,
    )
    assert res.improved() is True


def test_mitigation_result_improved_when_equal():
    # Per spec FR-3: improved() reflects after >= before (did not worsen).
    res = MitigationResult(
        optimal_value=0.0,
        per_xapp=[],
        n_satisfied_before=1,
        n_satisfied_after=1,
    )
    assert res.improved() is True


def test_mitigation_result_not_improved_when_worse():
    res = MitigationResult(
        optimal_value=0.0,
        per_xapp=[],
        n_satisfied_before=2,
        n_satisfied_after=1,
    )
    assert res.improved() is False
