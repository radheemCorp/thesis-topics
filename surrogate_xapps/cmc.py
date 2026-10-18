"""QACM Conflict Mitigation Controller (CMC) module.

Provides the :class:`IQueryableXApp` protocol that any xApp must satisfy to
participate in conflict mitigation, plus the CMC itself (added in later phases).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class IQueryableXApp(Protocol):
    """Structural protocol for xApps the CMC can query during mitigation.

    An xApp is *queryable* if it can answer: "if forced to use parameter
    value ``p1``, what is my predicted KPI?" This is the only capability the
    CMC needs — it never touches xApp internals or training data (QACM's
    no-data-sharing requirement).
    """

    def predict_at(self, p1: float) -> float:
        """Return the predicted KPI if this xApp is forced to use ``p1``.

        Parameters
        ----------
        p1:
            The value of the shared Input Control Parameter.

        Returns
        -------
        float
            The predicted KPI at ``p1``.
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
