"""Utility normalization used by the Wadud baseline policies."""

from __future__ import annotations

import warnings
from typing import Sequence

import numpy as np


def normalize_utility(
    values: Sequence[float] | np.ndarray,
    *,
    objective: str = "max",
    mode: str = "minmax10",
) -> tuple[np.ndarray, tuple[float, float]]:
    """Convert KPI predictions to utility and return the source bounds.

    ``minmax10`` is the paper's [0, 10] scaling. ``zscore`` is retained for
    compatibility with the shipped QACM ``normalisedKPI`` columns.
    """
    if objective not in {"max", "min"}:
        raise ValueError("objective must be 'max' or 'min'")
    if mode not in {"minmax10", "zscore"}:
        raise ValueError("mode must be 'minmax10' or 'zscore'")
    array = np.asarray(values, dtype=float)
    if array.size == 0 or not np.all(np.isfinite(array)):
        raise ValueError("utility inputs must be a non-empty finite sequence")
    lo, hi = float(np.min(array)), float(np.max(array))
    if mode == "minmax10":
        if hi == lo:
            warnings.warn("constant KPI has zero utility range", UserWarning, stacklevel=2)
            utility = np.zeros_like(array)
        elif objective == "max":
            utility = (array - lo) / (hi - lo) * 10.0
        else:
            utility = (hi - array) / (hi - lo) * 10.0
    else:
        mean = float(np.mean(array))
        std = float(np.std(array))
        if std == 0:
            warnings.warn("constant KPI has zero utility range", UserWarning, stacklevel=2)
            utility = np.zeros_like(array)
        else:
            utility = (array - mean) / std
            if objective == "min":
                utility = -utility
    return utility, (lo, hi)
