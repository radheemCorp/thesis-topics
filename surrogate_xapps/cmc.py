"""QACM Conflict Mitigation Controller (CMC) module.

Provides the :class:`IQueryableXApp` protocol that any xApp must satisfy to
participate in conflict mitigation, plus the CMC itself (added in later phases).
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Protocol, Sequence, runtime_checkable

import numpy as np


@runtime_checkable
class IQueryableXApp(Protocol):
    """Structural protocol for xApps the CMC can query during mitigation.

    An xApp is *queryable* if it can answer: "if forced to use parameter
    value ``p1``, what is my predicted KPI?" plus expose the metadata the CMC
    needs to score QoS. The CMC never touches xApp internals or training data
    (QACM's no-data-sharing requirement).
    """

    @property
    def xapp_id(self) -> str:
        """Identifier of the xApp."""
        ...

    @property
    def objective(self) -> str:
        """``"max"`` or ``"min"``."""
        ...

    @property
    def qos_threshold(self) -> float:
        """QoS threshold for the predicted KPI."""
        ...

    @property
    def priority_weight(self) -> float:
        """Relative priority weight used by the CMC."""
        ...

    @property
    def preferred_point(self) -> tuple[float, ...]:
        """The xApp's own uncoordinated optimum over all ICPs."""
        ...

    def predict_at(self, p1: float, p2: float | None = None) -> float:
        """Return the predicted KPI if this xApp is forced to use ``(p1, p2)``.

        Parameters
        ----------
        p1:
            The value of the first Input Control Parameter.
        p2:
            The value of the second Input Control Parameter. When omitted, the
            xApp should use its own preferred ``p2`` (not a dataset extreme),
            so the result agrees with its uncoordinated request.

        Returns
        -------
        float
            The predicted KPI at the requested point.
        """
        ...


@dataclass(init=False)
class MitigationResult:
    """Outcome of a CMC mitigation run.

    Parameters
    ----------
    optimal_point:
        The compromise point ``p*`` minimizing the QACM cost. Its arity matches
        the CMC's :attr:`~CMC.ranges`.
    per_xapp:
        Per-xApp records (``xapp_id``, ``preferred_point``,
        ``predicted_at_preferred``, ``predicted_at_optimum``,
        ``qos_threshold``, ``satisfied_at_optimum``, ``satisfied_before``).
    n_satisfied_before:
        Number of xApps meeting QoS at their own (conflicting) requests.
    n_satisfied_after:
        Number of xApps meeting QoS at the compromise ``p*``.
    optimal_value:
        Deprecated 1-D view of ``optimal_point[0]`` (keyword-only).
    """

    optimal_point: tuple[float, ...]
    per_xapp: list[dict[str, Any]]
    n_satisfied_before: int
    n_satisfied_after: int

    def __init__(
        self,
        optimal_point: Sequence[float] | None = None,
        per_xapp: list[dict[str, Any]] | None = None,
        n_satisfied_before: int = 0,
        n_satisfied_after: int = 0,
        *,
        optimal_value: float | None = None,
    ) -> None:
        if optimal_point is None:
            if optimal_value is None:
                raise TypeError("MitigationResult requires 'optimal_point'")
            optimal_point = (float(optimal_value),)
        elif optimal_value is not None:
            raise TypeError(
                "pass either 'optimal_point' or 'optimal_value', not both"
            )
        self.optimal_point = tuple(float(value) for value in optimal_point)
        self.per_xapp = list(per_xapp) if per_xapp is not None else []
        self.n_satisfied_before = int(n_satisfied_before)
        self.n_satisfied_after = int(n_satisfied_after)

    @property
    def optimal_value(self) -> float:
        """Deprecated 1-D view: the first coordinate of :attr:`optimal_point`."""
        return float(self.optimal_point[0])

    def improved(self) -> bool:
        """Whether mitigation did not reduce QoS satisfaction (after >= before)."""
        return self.n_satisfied_after >= self.n_satisfied_before


class CMC:
    """QACM Conflict Mitigation Controller (discrete joint grid heuristic).

    Sweeps a discrete grid over the shared Input Control Parameters (ICPs),
    queries each conflicting xApp's predicted KPI, and returns the compromise
    point ``p*`` that minimizes the QACM cost
    ``Σ_i w_i·d_i·ζ − (Σ_i s_i)²``.

    Parameters
    ----------
    ranges:
        Either a legacy ``(lo, hi)`` pair for a single ICP, or a sequence of
        ``(lo, hi)`` pairs, one per ICP.
    resolution:
        Number of candidate points per axis. An ``int`` applies to every axis;
        a sequence specifies each axis independently (default ``128``).
    zeta:
        Tuning constant scaling the weighted QoS deviation (default ``1e3``).
    optimize_over:
        ICP indices to sweep. ``None`` optimizes the first two ICPs (or the
        only ICP for 1-D). Non-optimized ICPs are held at each xApp's own
        :attr:`~surrogate_xapps.cmc.IQueryableXApp.preferred_point`.
    range:
        Deprecated keyword alias for a 1-D ``ranges`` pair.

    Notes
    -----
    The grid is the Cartesian product of per-axis ``linspace`` samples, laid
    out in lexicographic order so that cost ties resolve deterministically to
    the lexicographically smallest point. Grids larger than
    :attr:`MAX_GRID_POINTS` are rejected before allocation.
    """

    MAX_GRID_POINTS = 1_000_000

    def __init__(
        self,
        ranges: Sequence[tuple[float, float]] | tuple[float, float] | None = None,
        resolution: int | Sequence[int] = 128,
        zeta: float = 1e3,
        optimize_over: Sequence[int] | None = None,
        *,
        range: tuple[float, float] | None = None,
    ):
        if ranges is None and range is None:
            raise TypeError("CMC requires 'ranges' (or the legacy 'range')")
        if ranges is not None and range is not None:
            raise TypeError("pass either 'ranges' or 'range', not both")
        if ranges is None:
            ranges = range

        axes = self._normalize_ranges(ranges)
        resolutions = self._normalize_resolutions(resolution, len(axes))
        optimize = self._normalize_optimize_over(optimize_over, len(axes))
        self._check_grid_size(resolutions, optimize)

        self.ranges = tuple(axes)
        self.resolutions = tuple(resolutions)
        self.resolution = resolution  # legacy attribute (int for 1-D callers)
        self.optimize_over = optimize
        self.zeta = float(zeta)

    # -- construction helpers ---------------------------------------------
    @staticmethod
    def _normalize_ranges(
        ranges: Sequence[tuple[float, float]] | tuple[float, float],
    ) -> list[tuple[float, float]]:
        seq = list(ranges)
        if not seq:
            raise ValueError("ranges must contain at least one (lo, hi) pair")
        if len(seq) == 2 and not isinstance(seq[0], (tuple, list, np.ndarray)):
            pairs = [(seq[0], seq[1])]
        else:
            pairs = []
            for item in seq:
                if len(item) != 2:
                    raise ValueError("each range must be a (lo, hi) pair")
                pairs.append((item[0], item[1]))
        normalized = []
        for lo, hi in pairs:
            lo_f, hi_f = float(lo), float(hi)
            if not (math.isfinite(lo_f) and math.isfinite(hi_f)):
                raise ValueError("range bounds must be finite")
            if lo_f > hi_f:
                raise ValueError(f"invalid range ({lo_f}, {hi_f}): lo > hi")
            normalized.append((lo_f, hi_f))
        return normalized

    @staticmethod
    def _normalize_resolutions(
        resolution: int | Sequence[int], dimension: int
    ) -> list[int]:
        if isinstance(resolution, (int, np.integer)):
            values = [int(resolution)] * dimension
        else:
            values = [int(value) for value in resolution]
            if len(values) != dimension:
                raise ValueError(
                    f"resolution has {len(values)} entries but ranges has "
                    f"{dimension} axes"
                )
        if any(value < 2 for value in values):
            raise ValueError("each resolution must be >= 2")
        return values

    @staticmethod
    def _normalize_optimize_over(
        optimize_over: Sequence[int] | None, dimension: int
    ) -> tuple[int, ...]:
        queryable = min(dimension, 2)
        if optimize_over is None:
            return tuple(range(queryable))
        indices = tuple(int(index) for index in optimize_over)
        if not indices:
            raise ValueError("optimize_over must contain at least one index")
        if len(set(indices)) != len(indices):
            raise ValueError("optimize_over contains duplicate indices")
        for index in indices:
            if index < 0 or index >= queryable:
                raise ValueError(
                    f"optimize_over index {index} is out of range; "
                    f"predict_at exposes the first {queryable} ICP(s)"
                )
        return tuple(sorted(indices))

    def _check_grid_size(
        self, resolutions: Sequence[int], optimize: Sequence[int]
    ) -> None:
        size = math.prod(resolutions[index] for index in optimize)
        if size > self.MAX_GRID_POINTS:
            raise ValueError(
                f"candidate grid has {size} points (limit {self.MAX_GRID_POINTS}); "
                "reduce resolution or restrict optimize_over"
            )

    @property
    def dimension(self) -> int:
        """Number of Input Control Parameters covered by :attr:`ranges`."""
        return len(self.ranges)

    def candidate_grid(self) -> np.ndarray:
        """Return the ``(n_points, n_optimized)`` candidate grid.

        Points are ordered lexicographically: the first optimized axis varies
        slowest, matching ``np.meshgrid(..., indexing="ij")`` + ``ravel``.
        """
        axes = [
            np.linspace(lo, hi, self.resolutions[index])
            for index, (lo, hi) in enumerate(self.ranges)
            if index in self.optimize_over
        ]
        mesh = np.meshgrid(*axes, indexing="ij")
        return np.stack([axis.ravel() for axis in mesh], axis=1)

    def _satisfied(self, kpi: float, objective: str, threshold: float) -> bool:
        """QoS satisfaction for a predicted KPI (mirrors BaseXApp.qos_satisfied)."""
        if objective == "max":
            return kpi >= threshold
        return kpi <= threshold

    def mitigate(self, xapps: Sequence[IQueryableXApp]) -> MitigationResult:
        """Find the QoS-aware compromise ``p*`` over the joint candidate grid.

        Parameters
        ----------
        xapps:
            Conflicting xApps satisfying :class:`IQueryableXApp`. The sequence
            must be non-empty and its priority weights must sum to a positive
            value.

        Returns
        -------
        MitigationResult
            The optimal point and before/after QoS satisfaction.

        Raises
        ------
        ValueError
            If ``xapps`` is empty, a weight is negative, or the weights sum to
            a non-positive value.
        """
        weights = self._validate_xapps(xapps)
        grid = self.candidate_grid()
        costs = np.zeros(grid.shape[0], dtype=float)
        n_satisfied = np.zeros(grid.shape[0], dtype=int)

        for weight, xapp in zip(weights, xapps):
            kpis = self._predict_grid(xapp, grid)
            threshold = float(xapp.qos_threshold)
            if xapp.objective == "max":
                deviation = np.maximum(0.0, threshold - kpis)
                satisfied = kpis >= threshold
            elif xapp.objective == "min":
                deviation = np.maximum(0.0, kpis - threshold)
                satisfied = kpis <= threshold
            else:
                raise ValueError(
                    f"unsupported objective {xapp.objective!r}; expected 'max' or 'min'"
                )
            costs += weight * deviation * self.zeta
            n_satisfied += satisfied

        costs -= n_satisfied.astype(float) ** 2
        best_index = self._select_best(costs)
        grid_point = grid[best_index]
        optimal_point = self._assemble_point(grid_point, xapps, weights)
        return self._build_result(optimal_point, xapps, weights)

    # -- sweep helpers -----------------------------------------------------
    def _validate_xapps(
        self, xapps: Sequence[IQueryableXApp]
    ) -> list[float]:
        if not xapps:
            raise ValueError("at least one xApp is required for mitigation")
        raw = [float(xapp.priority_weight) for xapp in xapps]
        if any(weight < 0 for weight in raw):
            raise ValueError("priority weights must be non-negative")
        total = sum(raw)
        if total <= 0:
            raise ValueError("priority weights must sum to a positive value")
        return [weight / total for weight in raw]

    def _preferred_row(self, xapp: IQueryableXApp) -> list[float]:
        """Full preferred ICP vector of an xApp (not truncated to CMC arity)."""
        preferred = tuple(float(value) for value in xapp.preferred_point)
        if len(preferred) < self.dimension:
            raise ValueError(
                f"xApp {xapp.xapp_id!r} exposes {len(preferred)} ICP(s) "
                f"but the CMC is {self.dimension}-D"
            )
        return list(preferred)

    def _row_for(self, xapp: IQueryableXApp, point: Sequence[float]) -> list[float]:
        row = self._preferred_row(xapp)
        for axis_index in self.optimize_over:
            row[axis_index] = float(point[axis_index])
        return row

    def _grid_rows(self, xapp: IQueryableXApp, grid: np.ndarray) -> np.ndarray:
        preferred = np.asarray(self._preferred_row(xapp), dtype=float)
        rows = np.tile(preferred, (grid.shape[0], 1))
        rows[:, list(self.optimize_over)] = grid
        return rows

    @staticmethod
    def _predict_row(xapp: IQueryableXApp, row: Sequence[float]) -> float:
        if len(row) == 1:
            return float(xapp.predict_at(float(row[0])))
        if len(row) == 2:
            return float(xapp.predict_at(float(row[0]), float(row[1])))
        batch = getattr(xapp, "predict_many", None)
        if callable(batch):
            return float(np.asarray(batch(np.asarray([row], dtype=float)))[0])
        raise TypeError(
            "xApp must provide predict_many() when optimizing more than two ICPs"
        )

    def _predict_grid(self, xapp: IQueryableXApp, grid: np.ndarray) -> np.ndarray:
        rows = self._grid_rows(xapp, grid)
        batch = getattr(xapp, "predict_many", None)
        if callable(batch):
            kpis = np.asarray(batch(rows), dtype=float).reshape(-1)
            if kpis.shape[0] != rows.shape[0]:
                raise ValueError(
                    "predict_many() returned a different number of rows than requested"
                )
            return kpis
        return np.asarray(
            [self._predict_row(xapp, row) for row in rows], dtype=float
        )

    @staticmethod
    def _select_best(costs: np.ndarray) -> int:
        """Return the first index of the minimum cost (lexicographic tie-break)."""
        minimum = float(np.min(costs))
        close = np.flatnonzero(np.isclose(costs, minimum, rtol=0.0, atol=1e-12))
        return int(close[0])

    def _assemble_point(
        self,
        grid_point: np.ndarray,
        xapps: Sequence[IQueryableXApp],
        weights: Sequence[float],
    ) -> tuple[float, ...]:
        """Combine optimized coordinates with a weighted-mean fixed setting.

        Non-optimized axes are only representative in the returned tuple; each
        xApp is still queried at its own preferred value on those axes.
        """
        preferred = np.asarray(
            [self._preferred_row(xapp)[: self.dimension] for xapp in xapps],
            dtype=float,
        )
        representative = np.average(preferred, axis=0, weights=weights)
        representative[list(self.optimize_over)] = grid_point
        return tuple(float(value) for value in representative)

    def _build_result(
        self,
        optimal_point: tuple[float, ...],
        xapps: Sequence[IQueryableXApp],
        weights: Sequence[float],
    ) -> MitigationResult:
        per_xapp: list[dict[str, Any]] = []
        n_before = 0
        n_after = 0
        for xapp in xapps:
            preferred = tuple(float(value) for value in xapp.preferred_point)
            row_at_optimum = self._row_for(xapp, optimal_point)
            kpi_optimum = self._predict_row(xapp, row_at_optimum)
            kpi_preferred = self._predict_row(xapp, self._preferred_row(xapp))
            threshold = float(xapp.qos_threshold)
            sat_optimum = self._satisfied(kpi_optimum, xapp.objective, threshold)
            sat_before = self._satisfied(kpi_preferred, xapp.objective, threshold)
            n_before += int(sat_before)
            n_after += int(sat_optimum)
            per_xapp.append(
                {
                    "xapp_id": xapp.xapp_id,
                    "preferred_point": preferred,
                    "predicted_at_preferred": kpi_preferred,
                    "predicted_at_optimum": kpi_optimum,
                    "qos_threshold": threshold,
                    "satisfied_at_optimum": sat_optimum,
                    "satisfied_before": sat_before,
                }
            )
        return MitigationResult(
            optimal_point=optimal_point,
            per_xapp=per_xapp,
            n_satisfied_before=n_before,
            n_satisfied_after=n_after,
        )
