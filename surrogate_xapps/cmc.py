"""QACM Conflict Mitigation Controller (CMC) module.

Provides the :class:`IQueryableXApp` protocol that any xApp must satisfy to
participate in conflict mitigation, plus the CMC itself (added in later phases).
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable


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
