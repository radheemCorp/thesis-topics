"""QACM Conflict Mitigation Controller (CMC) module.

Provides the :class:`IQueryableXApp` protocol that any xApp must satisfy to
participate in conflict mitigation, plus the CMC itself (added in later phases).
"""

from __future__ import annotations

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
    """QACM Conflict Mitigation Controller (discrete heuristic, Algorithm 1).

    Sweeps a discrete grid of candidate values for the shared ICP, queries each
    conflicting xApp's predicted KPI, and returns the compromise ``p*`` that
    minimizes the QACM cost ``Σ w_i·d_i·ζ − (Σ s_i)²``.

    Parameters
    ----------
    range:
        ``(lo, hi)`` bounds for the shared Input Control Parameter.
    resolution:
        Number of discrete candidate points across ``range``.
    zeta:
        Tuning constant scaling the weighted QoS deviation (default ``1e3``).
    """

    def __init__(self, range: tuple[float, float], resolution: int, zeta: float = 1e3):
        if resolution < 2:
            raise ValueError("resolution must be >= 2")
        self.range = (float(range[0]), float(range[1]))
        self.resolution = resolution
        self.zeta = float(zeta)

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

        lo, hi = self.range
        candidates = np.linspace(lo, hi, self.resolution)

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
