"""Surrogate xApp classes and the QACM CMC control-request schema.

Each xApp wraps a :class:`~surrogate_xapps.surrogates.SurrogateModel`, searches a
2-D candidate grid over the ICPs ``[p1, p2]``, and emits a structured control
request for a QACM Conflict Mitigation Controller (CMC).

* :class:`CCOxApp` maximizes the throughput KPI.
* :class:`ESxApp` minimizes the power KPI.
"""

from __future__ import annotations

from typing import Any, TypeVar

import numpy as np

from .config import XAppConfig
from .surrogates import SurrogateModel, build_model

XAppT = TypeVar("XAppT", bound="BaseXApp")

#: Keys required in a control request by the QACM CMC.
REQUIRED_ACTION_KEYS = (
    "xapp_id",
    "target_parameter",
    "requested_value",
    "parameter_range",
    "predicted_kpi",
    "qos_threshold",
    "priority_weight",
)


def validate_action(action: dict[str, Any]) -> dict[str, Any]:
    """Validate a control-request payload against the QACM CMC schema.

    Parameters
    ----------
    action:
        The candidate control request.

    Returns
    -------
    dict
        The same ``action`` if valid.

    Raises
    ------
    ValueError
        If a required key is missing, a value has the wrong type, the requested
        tuple length does not match ``target_parameter``, or a requested value
        falls outside its declared range.
    """
    missing = [key for key in REQUIRED_ACTION_KEYS if key not in action]
    if missing:
        raise ValueError(f"Control request missing required key(s): {missing}")

    target = action["target_parameter"]
    requested = action["requested_value"]
    ranges = action["parameter_range"]

    if not isinstance(target, (list, tuple)) or not target:
        raise ValueError("target_parameter must be a non-empty list/tuple")
    if not isinstance(requested, (list, tuple)) or len(requested) != len(target):
        raise ValueError(
            "requested_value must be a list/tuple matching target_parameter length"
        )
    if not isinstance(ranges, (list, tuple)) or len(ranges) != len(target):
        raise ValueError(
            "parameter_range must be a list/tuple matching target_parameter length"
        )

    for name, value, bounds in zip(target, requested, ranges):
        if not isinstance(bounds, (list, tuple)) or len(bounds) != 2:
            raise ValueError(f"parameter_range for {name!r} must be [min, max]")
        lo, hi = float(bounds[0]), float(bounds[1])
        if not lo <= float(value) <= hi:
            raise ValueError(
                f"requested value {value} for {name!r} is outside range [{lo}, {hi}]"
            )

    for key in ("predicted_kpi", "qos_threshold", "priority_weight"):
        if not isinstance(action[key], (int, float)):
            raise ValueError(f"{key} must be numeric")

    return action


class BaseXApp:
    """Base surrogate xApp: train, grid-search, and emit a control request.

    Subclasses only override :meth:`_best_index` to select the objective.
    """

    def __init__(self, config: XAppConfig, model: SurrogateModel | None = None) -> None:
        self.config = config
        self.model: SurrogateModel = model if model is not None else build_model(config)
        self.ranges_: dict[str, tuple[float, float]] | None = None

    # -- training ---------------------------------------------------------
    def train(self: XAppT, X: np.ndarray, y: np.ndarray) -> XAppT:
        """Fit the surrogate and record the observed parameter ranges."""
        X = np.asarray(X, dtype=float)
        y = np.asarray(y, dtype=float)
        if X.ndim != 2 or X.shape[1] != len(self.config.spec.feature_names):
            raise ValueError(
                f"X must have shape (n, {len(self.config.spec.feature_names)})"
            )
        self.model.fit(X, y)
        self.ranges_ = {
            name: (float(X[:, i].min()), float(X[:, i].max()))
            for i, name in enumerate(self.config.spec.feature_names)
        }
        return self

    # -- inference --------------------------------------------------------
    def predict_kpi(self, X: np.ndarray) -> np.ndarray:
        """Predict the KPI for a ``(n, n_features)`` feature matrix."""
        return self.model.predict(np.asarray(X, dtype=float))

    def _candidate_grid(self) -> np.ndarray:
        """Build the 2-D candidate grid over the observed parameter ranges."""
        if self.ranges_ is None:
            raise RuntimeError("xApp must be trained before infer_action()")
        axes = [
            np.linspace(lo, hi, self.config.resolution)
            for (lo, hi) in (self.ranges_[name] for name in self.config.spec.feature_names)
        ]
        mesh = np.meshgrid(*axes, indexing="ij")
        return np.stack([m.ravel() for m in mesh], axis=1)

    def _best_index(self, predictions: np.ndarray) -> int:
        raise NotImplementedError

    def infer_action(self) -> dict[str, Any]:
        """Search the parameter grid and return a validated control request."""
        if self.ranges_ is None:
            raise RuntimeError("xApp must be trained before infer_action()")
        ranges = self.ranges_
        grid = self._candidate_grid()
        predictions = self.predict_kpi(grid)
        best = int(self._best_index(predictions))
        requested = [float(v) for v in grid[best]]
        predicted_kpi = float(predictions[best])

        action: dict[str, Any] = {
            "xapp_id": self.config.xapp_id,
            "target_parameter": list(self.config.spec.feature_names),
            "requested_value": requested,
            "parameter_range": [
                [ranges[name][0], ranges[name][1]]
                for name in self.config.spec.feature_names
            ],
            "predicted_kpi": predicted_kpi,
            "qos_threshold": float(self.config.qos_threshold),
            "priority_weight": float(self.config.priority_weight),
        }
        return validate_action(action)

    def qos_satisfied(self, predicted_kpi: float) -> bool:
        """Whether ``predicted_kpi`` meets the configured QoS threshold."""
        if self.config.objective == "max":
            return predicted_kpi >= self.config.qos_threshold
        return predicted_kpi <= self.config.qos_threshold


class CCOxApp(BaseXApp):
    """Coverage & Capacity Optimization xApp: maximizes the throughput KPI."""

    def _best_index(self, predictions: np.ndarray) -> int:
        return int(np.argmax(predictions))


class ESxApp(BaseXApp):
    """Energy Saving xApp: minimizes the power KPI."""

    def _best_index(self, predictions: np.ndarray) -> int:
        return int(np.argmin(predictions))
