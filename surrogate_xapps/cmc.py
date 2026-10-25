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


@dataclass
class MitigationResult:
    """Outcome of a CMC mitigation run.

    Parameters
    ----------
    optimal_value:
        The compromise parameter value ``p*`` minimizing the QACM cost.
    per_xapp:
        Per-xApp records (``xapp_id``, ``predicted_at_optimum``,
        ``qos_threshold``, ``satisfied_at_optimum``, ``satisfied_before``).
    n_satisfied_before:
        Number of xApps meeting QoS at their own (conflicting) requests.
    n_satisfied_after:
        Number of xApps meeting QoS at the compromise ``p*``.
    """

    optimal_value: float
    per_xapp: list[dict[str, Any]]
    n_satisfied_before: int
    n_satisfied_after: int

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
        """Find the QoS-aware compromise ``p*`` over the candidate grid.

        Parameters
        ----------
        xapps:
            Conflicting xApps satisfying :class:`IQueryableXApp` and exposing
            ``xapp_id``, ``objective``, ``qos_threshold``, ``priority_weight``,
            and ``preferred_point``.

        Returns
        -------
        MitigationResult
            The optimal compromise and before/after QoS satisfaction.
        """
        # Normalize weights to sum to 1 (QACM constraint).
        raw = [float(x.priority_weight) for x in xapps]
        total = sum(raw)
        if total <= 0:
            raise ValueError("priority weights must sum to a positive value")
        weights = [w / total for w in raw]

        lo, hi = self.ranges[0]
        candidates = np.linspace(lo, hi, self.resolutions[0])

        best_p = float(candidates[0])
        best_cost = float("inf")
        for p in candidates:
            cost = 0.0
            n_sat = 0
            for w, x in zip(weights, xapps):
                u = float(x.predict_at(float(p)))
                if x.objective == "max":
                    d = max(0.0, x.qos_threshold - u)
                else:
                    d = max(0.0, u - x.qos_threshold)
                cost += w * d * self.zeta
                if self._satisfied(u, x.objective, x.qos_threshold):
                    n_sat += 1
            cost -= n_sat ** 2
            if cost < best_cost:
                best_cost = cost
                best_p = float(p)

        # Build per-xApp records and before/after satisfaction counts.
        per_xapp: list[dict[str, Any]] = []
        n_after = 0
        n_before = 0
        for x in xapps:
            u_opt = float(x.predict_at(best_p))
            sat_opt = self._satisfied(u_opt, x.objective, x.qos_threshold)
            u_before = float(x.predict_at(float(x.preferred_point[0])))
            sat_before = self._satisfied(u_before, x.objective, x.qos_threshold)
            n_after += int(sat_opt)
            n_before += int(sat_before)
            per_xapp.append(
                {
                    "xapp_id": x.xapp_id,
                    "predicted_at_optimum": u_opt,
                    "qos_threshold": float(x.qos_threshold),
                    "satisfied_at_optimum": sat_opt,
                    "satisfied_before": sat_before,
                }
            )

        return MitigationResult(
            optimal_value=best_p,
            per_xapp=per_xapp,
            n_satisfied_before=n_before,
            n_satisfied_after=n_after,
        )
