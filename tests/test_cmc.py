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
    """Analytic mock xApp whose KPI is a simple linear function of p1.

    Exposes the flat metadata contract the CMC reads (xapp_id, objective,
    qos_threshold, priority_weight, preferred_value) plus ``predict_at``.
    """

    def __init__(self, xapp_id: str, slope: float, intercept: float, objective: str,
                 qos_threshold: float, priority_weight: float,
                 preferred_value: float = 0.0, p2_const: float = 0.0,
                 p2_slope: float = 0.0):
        self.xapp_id = xapp_id
        self.slope = slope
        self.intercept = intercept
        self.objective = objective
        self.qos_threshold = qos_threshold
        self.priority_weight = priority_weight
        self.preferred_value = preferred_value
        self.p2_const = p2_const
        self.p2_slope = p2_slope

    @property
    def preferred_point(self) -> tuple[float, ...]:
        return (self.preferred_value, self.p2_const)

    def predict_at(self, p1: float, p2: float | None = None) -> float:
        effective_p2 = self.p2_const if p2 is None else float(p2)
        return self.slope * p1 + self.p2_slope * effective_p2 + self.intercept


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


def test_mock_predict_at_honours_p2_and_prefers_its_own():
    xapp = _MockXApp(
        "x", 1.0, 0.5, "max", 0.5, 0.5,
        preferred_value=1.0, p2_const=2.0, p2_slope=3.0,
    )
    assert xapp.preferred_point == (1.0, 2.0)
    assert xapp.predict_at(1.0) == pytest.approx(1.0 + 3.0 * 2.0 + 0.5)
    assert xapp.predict_at(1.0, 4.0) == pytest.approx(1.0 + 3.0 * 4.0 + 0.5)


def test_protocol_requires_preferred_point():
    class NoPreferredPoint:
        xapp_id = "x"
        objective = "max"
        qos_threshold = 0.5
        priority_weight = 0.5

        def predict_at(self, p1, p2=None):
            return p1

    assert not isinstance(NoPreferredPoint(), IQueryableXApp)


def test_protocol_accepts_preferred_point_and_optional_p2():
    class TwoDimensional:
        xapp_id = "x"
        objective = "max"
        qos_threshold = 0.5
        priority_weight = 0.5
        preferred_point = (0.0, 0.0)

        def predict_at(self, p1, p2=None):
            return p1 + (p2 or 0.0)

    xapp = TwoDimensional()
    assert isinstance(xapp, IQueryableXApp)
    assert xapp.predict_at(1.0, 2.0) == pytest.approx(3.0)


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


def test_predict_at_defaults_to_preferred_p2(trained_cco: CCOxApp):
    p1, p2 = trained_cco.preferred_point
    row = np.array([[p1, p2]])
    expected = float(trained_cco.predict_kpi(row)[0])
    assert trained_cco.predict_at(p1) == pytest.approx(expected)


def test_predict_at_honours_explicit_p2(trained_cco: CCOxApp):
    p1, p2 = -47.49, 60.0
    row = np.array([[p1, p2]])
    expected = float(trained_cco.predict_kpi(row)[0])
    assert trained_cco.predict_at(p1, p2) == pytest.approx(expected)


def test_preferred_point_matches_infer_action(trained_es: ESxApp):
    action = trained_es.infer_action()
    assert trained_es.preferred_point == pytest.approx(
        tuple(action["requested_value"])
    )
    assert trained_es.predict_at(*trained_es.preferred_point) == pytest.approx(
        float(action["predicted_kpi"]), abs=1e-9
    )


def test_predict_at_requires_training():
    from surrogate_xapps.config import CCO_CONFIG

    with pytest.raises(RuntimeError):
        CCOxApp(CCO_CONFIG).predict_at(0.0)
    with pytest.raises(RuntimeError):
        _ = CCOxApp(CCO_CONFIG).preferred_point


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


# --- CMC discrete heuristic -------------------------------------------

from surrogate_xapps.cmc import CMC  # noqa: E402


def _two_conflicting():
    # A wants high p1 (max), B wants low p1 (min) over the SAME KPI f(p1)=p1.
    # Hand-computed optimum on grid [0..5] with zeta=1e3, w=(0.6,0.4):
    # cost(p1=3) = 399, unique min. See spec FR-2.
    a = _MockXApp("A", slope=1.0, intercept=0.0, objective="max",
                  qos_threshold=3.0, priority_weight=0.6, preferred_value=5.0)
    b = _MockXApp("B", slope=1.0, intercept=0.0, objective="min",
                  qos_threshold=2.0, priority_weight=0.4, preferred_value=0.0)
    return [a, b]


def test_cmc_returns_hand_computed_optimum():
    cmc = CMC(range=(0.0, 5.0), resolution=6, zeta=1e3)
    res = cmc.mitigate(_two_conflicting())
    assert res.optimal_value == pytest.approx(3.0)


def test_cmc_satisfaction_counts():
    cmc = CMC(range=(0.0, 5.0), resolution=6, zeta=1e3)
    res = cmc.mitigate(_two_conflicting())
    # At p1=3: A (max, q=3) satisfied; B (min, q=2) not -> 1 after.
    # Before: A at preferred 5 (5>=3 satisfied), B at preferred 0 (0<=2 satisfied) -> 2.
    assert res.n_satisfied_after == 1
    assert res.n_satisfied_before == 2


def test_cmc_per_xapp_records():
    cmc = CMC(range=(0.0, 5.0), resolution=6, zeta=1e3)
    res = cmc.mitigate(_two_conflicting())
    by_id = {r["xapp_id"]: r for r in res.per_xapp}
    assert by_id["A"]["satisfied_at_optimum"] is True
    assert by_id["B"]["satisfied_at_optimum"] is False
    assert by_id["A"]["satisfied_before"] is True
    assert by_id["B"]["satisfied_before"] is True
    assert by_id["A"]["predicted_at_optimum"] == pytest.approx(3.0)


def test_cmc_normalizes_weights():
    # Scaling all weights by a constant must not change the optimum.
    a1 = _MockXApp("A", 1.0, 0.0, "max", 3.0, 0.6, 5.0)
    b1 = _MockXApp("B", 1.0, 0.0, "min", 2.0, 0.4, 0.0)
    a2 = _MockXApp("A", 1.0, 0.0, "max", 3.0, 6.0, 5.0)
    b2 = _MockXApp("B", 1.0, 0.0, "min", 2.0, 4.0, 0.0)
    r1 = CMC(range=(0.0, 5.0), resolution=6).mitigate([a1, b1])
    r2 = CMC(range=(0.0, 5.0), resolution=6).mitigate([a2, b2])
    assert r1.optimal_value == pytest.approx(r2.optimal_value)


# --- Modularity (arbitrary xApp count, no concrete imports) --------------

def test_cmc_accepts_three_xapps():
    # Adding a 3rd xApp only changes the input list — no CMC code change.
    a = _MockXApp("A", 1.0, 0.0, "max", 3.0, 0.5, 5.0)
    b = _MockXApp("B", 1.0, 0.0, "min", 2.0, 0.3, 0.0)
    c = _MockXApp("C", 0.5, 1.0, "max", 2.0, 0.2, 4.0)
    res = CMC(range=(0.0, 5.0), resolution=6).mitigate([a, b, c])
    assert len(res.per_xapp) == 3
    # Hand-computed min cost at p1=3 (cost 296) beats p1=2 (496) and p1=0 (1699).
    assert res.optimal_value == pytest.approx(3.0)


def test_cmc_does_not_import_concrete_xapps():
    import inspect

    import surrogate_xapps.cmc as cmc_mod

    src = inspect.getsource(cmc_mod)
    assert "CCOxApp" not in src
    assert "ESxApp" not in src


# --- Runner integration (run_cmc_demo) ------------------------------------

from surrogate_xapps.runner import run_cmc_demo  # noqa: E402


def test_run_cmc_demo_returns_result(cco_file: Path, es_file: Path):
    result = run_cmc_demo(cco_file=cco_file, es_file=es_file, resolution=100)
    assert result["conflict"] is True
    assert result["mitigation"].optimal_value is not None
    assert len(result["mitigation"].per_xapp) == 2
    assert result["mitigation"].n_satisfied_after >= 0


def test_run_cmc_demo_optimum_between_requests(cco_file: Path, es_file: Path):
    result = run_cmc_demo(cco_file=cco_file, es_file=es_file, resolution=100)
    cco_req = result["action_cco"]["requested_value"][0]
    es_req = result["action_es"]["requested_value"][0]
    lo, hi = min(cco_req, es_req), max(cco_req, es_req)
    p_star = result["mitigation"].optimal_value
    # Optimum must lie within the conflict interval [min, max] of the requests.
    assert lo - 1.0 <= p_star <= hi + 1.0


# --- Before/after comparison report ---------------------------------------

from surrogate_xapps.runner import print_cmc_report  # noqa: E402


def test_print_cmc_report_output(cco_file: Path, es_file: Path, capsys):
    result = run_cmc_demo(cco_file=cco_file, es_file=es_file, resolution=100)
    print_cmc_report(result)
    out = capsys.readouterr().out
    assert "Satisfied before" in out
    assert "Satisfied after" in out
    assert "xApp_CCO" in out
    assert "xApp_ES" in out


def test_print_cmc_report_shows_optimum(cco_file: Path, es_file: Path, capsys):
    result = run_cmc_demo(cco_file=cco_file, es_file=es_file, resolution=100)
    print_cmc_report(result)
    out = capsys.readouterr().out
    assert "optimal" in out.lower() or "p*" in out
