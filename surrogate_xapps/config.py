"""Configuration and dataset contracts for the surrogate CCO/ES xApps.

This module freezes the *data contract* shared by both xApps. It is deliberately
schema-agnostic: a :class:`DatasetSpec` maps arbitrary CSV column names onto the
canonical ``(p1, p2, k)`` roles so that both the cmsORAN and QACM file layouts
load through the same code path.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Sequence

#: Objectives understood by the xApps.
OBJECTIVES = ("max", "min")

#: Surrogate model backends understood by the xApps (MVP: scikit-learn only).
MODEL_KINDS = ("poly", "ann")


@dataclass(frozen=True)
class DatasetSpec:
    """Maps CSV columns onto the canonical ``(p1, p2, k)`` roles.

    Parameters
    ----------
    feature_cols:
        Names of the Input Control Parameter (ICP) columns, in order.
    target_col:
        Name of the KPI column to predict.
    feature_names:
        Canonical names for the features (default ``("p1", "p2")``).
    threshold_col:
        Optional column holding a per-row QoS threshold (QACM files only).
    """

    feature_cols: Sequence[str]
    target_col: str
    feature_names: Sequence[str] = ("p1", "p2")
    threshold_col: str | None = None

    def __post_init__(self) -> None:
        if len(self.feature_cols) != len(self.feature_names):
            raise ValueError(
                f"feature_cols ({len(self.feature_cols)}) and feature_names "
                f"({len(self.feature_names)}) must have equal length"
            )
        if not self.feature_cols:
            raise ValueError("feature_cols must not be empty")


#: cmsORAN layout: ``Input1,Input2,Output``.
CMSORAN_SPEC = DatasetSpec(
    feature_cols=("Input1", "Input2"),
    target_col="Output",
    feature_names=("p1", "p2"),
)

#: QACM layout: ``Input1,Input2,Output,normalisedKPI,normalised_threshold``.
QACM_SPEC = DatasetSpec(
    feature_cols=("Input1", "Input2"),
    target_col="Output",
    feature_names=("p1", "p2"),
    threshold_col="normalised_threshold",
)


@dataclass
class XAppConfig:
    """Everything an xApp needs to train, search, and emit a control request.

    Parameters
    ----------
    xapp_id:
        Identifier emitted in the control request (e.g. ``"xApp_CCO"``).
    spec:
        The :class:`DatasetSpec` describing the xApp's dataset.
    objective:
        ``"max"`` (CCO) or ``"min"`` (ES).
    qos_threshold:
        QoS threshold for the predicted KPI. For ``"max"`` the KPI is satisfied
        when ``predicted >= threshold``; for ``"min"`` when ``predicted <= threshold``.
    priority_weight:
        Relative priority used by a downstream CMC (0..1).
    model_kind:
        ``"poly"`` (polynomial regression) or ``"ann"`` (MLP regressor).
    resolution:
        Number of grid points per parameter axis for the decision search.
    poly_degree:
        Degree of the polynomial regression surrogate.
    """

    xapp_id: str
    spec: DatasetSpec
    objective: str
    qos_threshold: float = 0.0
    priority_weight: float = 1.0
    model_kind: str = "poly"
    resolution: int = 200
    poly_degree: int = 3

    def __post_init__(self) -> None:
        if self.objective not in OBJECTIVES:
            raise ValueError(
                f"objective must be one of {OBJECTIVES}, got {self.objective!r}"
            )
        if self.model_kind not in MODEL_KINDS:
            raise ValueError(
                f"model_kind must be one of {MODEL_KINDS}, got {self.model_kind!r}"
            )
        if self.resolution < 2:
            raise ValueError("resolution must be >= 2")
        if not 0.0 <= self.priority_weight <= 1.0:
            raise ValueError("priority_weight must be within [0, 1]")


#: Default CCO xApp: maximize throughput ``k1`` from ``data/cmsORAN/data1.csv``.
CCO_CONFIG = XAppConfig(
    xapp_id="xApp_CCO",
    spec=CMSORAN_SPEC,
    objective="max",
    qos_threshold=0.9,
    priority_weight=0.5,
)

#: Default ES xApp: minimize power ``k2`` from ``data/cmsORAN/data2.csv``.
ES_CONFIG = XAppConfig(
    xapp_id="xApp_ES",
    spec=CMSORAN_SPEC,
    objective="min",
    qos_threshold=0.5,
    priority_weight=0.5,
)
