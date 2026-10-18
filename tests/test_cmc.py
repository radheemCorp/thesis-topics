"""Tests for the CMC module: IQueryableXApp protocol, heuristic, and results.

These tests define the expected behaviour of the QACM Conflict Mitigation
Controller MVP before it is implemented (TDD Red phase).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, runtime_checkable

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
