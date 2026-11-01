"""Game-theoretic mitigation policies from Wadud et al. (2311.13389v1)."""

from __future__ import annotations

import math
from typing import Protocol, Sequence

import numpy as np

from .cmc import IQueryableXApp, MitigationResult
from .utility import normalize_utility


class MitigationPolicy(Protocol):
    """Common policy interface for alternative CMC selectors."""

    def mitigate(
        self,
        xapps: Sequence[IQueryableXApp],
        ranges: Sequence[tuple[float, float]] | tuple[float, float],
        resolution: int | Sequence[int],
        weights: Sequence[float] | None = None,
        *,
        optimize_over: Sequence[int] | None = None,
    ) -> MitigationResult: ...


def _axes(ranges, resolution, optimize_over):
    pairs = list(ranges)
    if len(pairs) == 2 and not isinstance(pairs[0], (tuple, list, np.ndarray)):
        pairs = [tuple(pairs)]
    pairs = [(float(lo), float(hi)) for lo, hi in pairs]
    if optimize_over is None:
        optimize_over = tuple(range(len(pairs)))
    else:
        optimize_over = tuple(int(i) for i in optimize_over)
    if isinstance(resolution, (int, np.integer)):
        resolutions = [int(resolution)] * len(pairs)
    else:
        resolutions = [int(v) for v in resolution]
    if len(resolutions) != len(pairs) or not optimize_over:
        raise ValueError("resolution and ranges must have matching non-empty dimensions")
    axes = [np.linspace(pairs[i][0], pairs[i][1], resolutions[i]) for i in optimize_over]
    mesh = np.meshgrid(*axes, indexing="ij")
    return pairs, optimize_over, np.stack([m.ravel() for m in mesh], axis=1)


def _row(xapp, point, optimize_over, dimension):
    preferred = list(float(v) for v in xapp.preferred_point)
    if len(preferred) < dimension:
        raise ValueError(f"xApp {xapp.xapp_id!r} does not expose {dimension} ICPs")
    for index in optimize_over:
        preferred[index] = float(point[index])
    return preferred


def _predict(xapp, row):
    if len(row) == 1:
        return float(xapp.predict_at(row[0]))
    if len(row) == 2:
        return float(xapp.predict_at(row[0], row[1]))
    batch = getattr(xapp, "predict_many", None)
    if callable(batch):
        return float(np.asarray(batch(np.asarray([row], dtype=float))).reshape(-1)[0])
    raise TypeError("xApp must provide predict_many() for more than two ICPs")


def _result(xapps, point, optimize_over, dimension) -> MitigationResult:
    records = []
    before = after = 0
    for xapp in xapps:
        preferred = tuple(float(v) for v in xapp.preferred_point)
        kpi_before = _predict(xapp, list(preferred))
        kpi_after = _predict(xapp, _row(xapp, point, optimize_over, dimension))
        if xapp.objective == "max":
            sat_before = kpi_before >= float(xapp.qos_threshold)
            sat_after = kpi_after >= float(xapp.qos_threshold)
        elif xapp.objective == "min":
            sat_before = kpi_before <= float(xapp.qos_threshold)
            sat_after = kpi_after <= float(xapp.qos_threshold)
        else:
            raise ValueError(f"unsupported objective {xapp.objective!r}")
        before += int(sat_before)
        after += int(sat_after)
        records.append({
            "xapp_id": xapp.xapp_id,
            "preferred_point": preferred,
            "predicted_at_preferred": kpi_before,
            "predicted_at_optimum": kpi_after,
            "qos_threshold": float(xapp.qos_threshold),
            "satisfied_before": sat_before,
            "satisfied_at_optimum": sat_after,
        })
    return MitigationResult(tuple(point), records, before, after)


class _GridPolicy:
    def __init__(self, *, utility_mode: str = "minmax10") -> None:
        self.utility_mode = utility_mode

    def _prepare(self, xapps, ranges, resolution, weights, optimize_over):
        if not xapps:
            raise ValueError("at least one xApp is required")
        pairs, optimize, grid = _axes(ranges, resolution, optimize_over)
        dimension = len(pairs)
        if weights is None:
            weights = [float(x.priority_weight) for x in xapps]
        weights = np.asarray(weights, dtype=float)
        if len(weights) != len(xapps) or not np.all(np.isfinite(weights)):
            raise ValueError("weights must be finite and match xApps")
        if np.any(weights < 0) or float(weights.sum()) <= 0:
            raise ValueError("weights must be non-negative and not all zero")
        predictions = []
        utilities = []
        for xapp in xapps:
            rows = [_row(xapp, [*([0.0] * dimension)], optimize, dimension)
                    for _ in range(len(grid))]
            for row, candidate in zip(rows, grid):
                for index, value in zip(optimize, candidate):
                    row[index] = float(value)
            kpis = np.asarray([_predict(xapp, row) for row in rows], dtype=float)
            utility, _ = normalize_utility(
                kpis, objective=xapp.objective, mode=self.utility_mode
            )
            predictions.append(kpis)
            utilities.append(utility)
        return pairs, optimize, grid, weights, np.asarray(utilities), dimension

    @staticmethod
    def _point(grid, index, pairs, optimize, xapps, weights):
        point = np.average(
            np.asarray([x.preferred_point[:len(pairs)] for x in xapps], dtype=float),
            axis=0,
            weights=weights,
        )
        point[list(optimize)] = grid[index]
        return tuple(float(v) for v in np.clip(point, [p[0] for p in pairs], [p[1] for p in pairs]))

    def mitigate(self, xapps, ranges, resolution, weights=None, *, optimize_over=None):
        raise NotImplementedError


class ArithmeticMeanPolicy(_GridPolicy):
    """Select the projected arithmetic mean of xApp preferred points."""

    def mitigate(self, xapps, ranges, resolution, weights=None, *, optimize_over=None):
        pairs, optimize, grid = _axes(ranges, resolution, optimize_over)
        dimension = len(pairs)
        preferred = np.asarray([x.preferred_point[:dimension] for x in xapps], dtype=float)
        point = np.mean(preferred, axis=0)
        for index, (lo, hi) in enumerate(pairs):
            point[index] = np.clip(point[index], lo, hi)
        return _result(xapps, tuple(float(v) for v in point), optimize, dimension)


class NSWFPolicy(_GridPolicy):
    """Maximize the product of normalized utilities in log space."""

    def __init__(self, *, epsilon: float = 1e-12, zero_policy: str = "clamp",
                 utility_mode: str = "minmax10") -> None:
        super().__init__(utility_mode=utility_mode)
        if zero_policy not in {"clamp", "literal"}:
            raise ValueError("zero_policy must be 'clamp' or 'literal'")
        self.epsilon = float(epsilon)
        self.zero_policy = zero_policy

    def mitigate(self, xapps, ranges, resolution, weights=None, *, optimize_over=None):
        pairs, optimize, grid, weights, utilities, dimension = self._prepare(
            xapps, ranges, resolution, weights, optimize_over
        )
        factors = np.maximum(utilities, self.epsilon) if self.zero_policy == "clamp" else utilities
        with np.errstate(divide="ignore", invalid="raise"):
            objective = np.sum(np.log(factors), axis=0)
        index = int(np.argmax(objective))
        return _result(xapps, self._point(grid, index, pairs, optimize, xapps, weights), optimize, dimension)


class EisenbergGalePolicy(_GridPolicy):
    """Maximize weighted linear utility with normalized positive weights."""

    def mitigate(self, xapps, ranges, resolution, weights=None, *, optimize_over=None):
        pairs, optimize, grid, weights, utilities, dimension = self._prepare(
            xapps, ranges, resolution, weights, optimize_over
        )
        objective = np.sum(utilities * (weights / weights.sum())[:, None], axis=0)
        index = int(np.argmax(objective))
        return _result(xapps, self._point(grid, index, pairs, optimize, xapps, weights), optimize, dimension)


__all__ = ["MitigationPolicy", "ArithmeticMeanPolicy", "NSWFPolicy", "EisenbergGalePolicy"]
