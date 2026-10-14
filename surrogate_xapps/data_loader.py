"""CSV dataset ingestion for the surrogate xApps.

Loads a CSV file described by a :class:`~surrogate_xapps.config.DatasetSpec`
into a feature matrix ``X`` and target vector ``y``, with defensive error
handling for missing files, malformed schemas, and non-numeric rows.
"""

from __future__ import annotations

import warnings
from pathlib import Path
from typing import Union

import numpy as np
import pandas as pd

from .config import DatasetSpec

#: Minimum number of valid rows required to train a surrogate.
MIN_ROWS = 5


def load_dataset(
    path: Union[str, Path],
    spec: DatasetSpec,
) -> tuple[np.ndarray, np.ndarray, dict[str, tuple[float, float]]]:
    """Load a CSV dataset into ``(X, y, ranges)``.

    Parameters
    ----------
    path:
        Path to the CSV file.
    spec:
        The :class:`DatasetSpec` mapping columns onto ``(p1, p2, k)``.

    Returns
    -------
    X:
        Feature matrix of shape ``(n_samples, n_features)``.
    y:
        Target vector of shape ``(n_samples,)``.
    ranges:
        Mapping ``feature_name -> (min, max)`` observed in the data, used to
        bound the decision search.

    Raises
    ------
    FileNotFoundError
        If ``path`` does not exist.
    ValueError
        If the file is empty, missing required columns, or has too few valid rows.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Dataset not found: {path}")

    try:
        df = pd.read_csv(path)
    except pd.errors.EmptyDataError as exc:
        raise ValueError(f"Dataset is empty (no columns): {path}") from exc

    if df.empty:
        raise ValueError(f"Dataset has no data rows: {path}")

    required = list(spec.feature_cols) + [spec.target_col]
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise ValueError(
            f"Dataset {path} is missing required column(s) {missing}; "
            f"found columns {list(df.columns)}"
        )

    subset = df[required].apply(pd.to_numeric, errors="coerce")
    n_before = len(subset)
    subset = subset.dropna()
    dropped = n_before - len(subset)
    if dropped:
        warnings.warn(
            f"Dropped {dropped} row(s) with missing/non-numeric values from {path}",
            stacklevel=2,
        )

    if len(subset) < MIN_ROWS:
        raise ValueError(
            f"Dataset {path} has only {len(subset)} valid row(s); "
            f"at least {MIN_ROWS} are required"
        )

    X = subset[list(spec.feature_cols)].to_numpy(dtype=float)
    y = subset[spec.target_col].to_numpy(dtype=float)

    ranges = {
        name: (float(X[:, i].min()), float(X[:, i].max()))
        for i, name in enumerate(spec.feature_names)
    }
    return X, y, ranges


def load_threshold(
    path: Union[str, Path],
    spec: DatasetSpec,
    default: float,
) -> float:
    """Return the mean QoS threshold from ``spec.threshold_col`` if present.

    Falls back to ``default`` when the spec has no threshold column or the
    column is absent from the file.
    """
    if spec.threshold_col is None:
        return default
    path = Path(path)
    if not path.exists():
        return default
    df = pd.read_csv(path)
    if spec.threshold_col not in df.columns:
        return default
    values = pd.to_numeric(df[spec.threshold_col], errors="coerce").dropna()
    if values.empty:
        return default
    return float(values.mean())
