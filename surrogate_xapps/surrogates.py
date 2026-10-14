"""Surrogate regression models for KPI prediction.

Two interchangeable backends are provided behind a common interface:

* :class:`PolyRegSurrogate` -- polynomial regression (matches the cmsORAN/QACM
  "polynomial regression block").
* :class:`ANNSurrogate` -- a scikit-learn MLP regressor (the MVP ANN backend).

Both expose ``fit`` / ``predict`` / ``score`` so the xApps are model-agnostic.
"""

from __future__ import annotations

import warnings
from abc import ABC, abstractmethod

import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.neural_network import MLPRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import PolynomialFeatures

from .config import MODEL_KINDS, XAppConfig


class SurrogateModel(ABC):
    """Common interface for KPI surrogate models."""

    @abstractmethod
    def fit(self, X: np.ndarray, y: np.ndarray) -> "SurrogateModel":
        """Fit the surrogate on features ``X`` and targets ``y``."""

    @abstractmethod
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Predict KPI values for a ``(n, n_features)`` feature matrix."""

    def score(self, X: np.ndarray, y: np.ndarray) -> float:
        """Return the coefficient of determination R^2 of the prediction."""
        y = np.asarray(y, dtype=float)
        y_pred = self.predict(X)
        ss_res = float(np.sum((y - y_pred) ** 2))
        ss_tot = float(np.sum((y - np.mean(y)) ** 2))
        if ss_tot == 0.0:
            return 1.0 if ss_res == 0.0 else 0.0
        return 1.0 - ss_res / ss_tot


class PolyRegSurrogate(SurrogateModel):
    """Polynomial regression surrogate (PolynomialFeatures + LinearRegression)."""

    def __init__(self, degree: int = 3) -> None:
        if degree < 1:
            raise ValueError("degree must be >= 1")
        self.degree = degree
        self.pipeline_: Pipeline | None = None

    def fit(self, X: np.ndarray, y: np.ndarray) -> "PolyRegSurrogate":
        pipeline = Pipeline(
            [
                ("poly", PolynomialFeatures(degree=self.degree, include_bias=False)),
                ("linear", LinearRegression()),
            ]
        )
        pipeline.fit(X, y)
        self.pipeline_ = pipeline
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        if self.pipeline_ is None:
            raise RuntimeError("PolyRegSurrogate must be fitted before predict()")
        return self.pipeline_.predict(X)


class ANNSurrogate(SurrogateModel):
    """Artificial neural network surrogate (scikit-learn MLPRegressor)."""

    def __init__(
        self,
        hidden_layer_sizes: tuple[int, ...] = (64, 32),
        max_iter: int = 2000,
        random_state: int = 42,
    ) -> None:
        self.hidden_layer_sizes = hidden_layer_sizes
        self.max_iter = max_iter
        self.random_state = random_state
        self.model_: MLPRegressor | None = None

    def fit(self, X: np.ndarray, y: np.ndarray) -> "ANNSurrogate":
        model = MLPRegressor(
            hidden_layer_sizes=self.hidden_layer_sizes,
            max_iter=self.max_iter,
            random_state=self.random_state,
        )
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            model.fit(X, y)
        self.model_ = model
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        if self.model_ is None:
            raise RuntimeError("ANNSurrogate must be fitted before predict()")
        return self.model_.predict(X)


def build_model(config: XAppConfig) -> SurrogateModel:
    """Instantiate the surrogate backend selected by ``config.model_kind``."""
    if config.model_kind == "poly":
        return PolyRegSurrogate(degree=config.poly_degree)
    if config.model_kind == "ann":
        return ANNSurrogate()
    raise ValueError(f"Unknown model_kind {config.model_kind!r}; expected {MODEL_KINDS}")
