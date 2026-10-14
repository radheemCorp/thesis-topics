"""Tests for the surrogate regression models."""

from __future__ import annotations

import numpy as np
import pytest

from surrogate_xapps.config import CMSORAN_SPEC, XAppConfig
from surrogate_xapps.surrogates import ANNSurrogate, PolyRegSurrogate, build_model


def _smooth_dataset(n: int = 400, seed: int = 0):
    rng = np.random.default_rng(seed)
    X = rng.uniform(-5, 5, size=(n, 2))
    y = 3.0 * X[:, 0] - X[:, 0] ** 2 + 0.5 * X[:, 1]
    return X, y


@pytest.mark.parametrize("model", [PolyRegSurrogate(degree=3), ANNSurrogate()])
def test_interface_and_fit_quality(model):
    X, y = _smooth_dataset()
    model.fit(X, y)
    preds = model.predict(X)
    assert preds.shape == (X.shape[0],)
    assert model.score(X, y) > 0.8


def test_predict_before_fit_raises():
    with pytest.raises(RuntimeError):
        PolyRegSurrogate().predict(np.zeros((2, 2)))
    with pytest.raises(RuntimeError):
        ANNSurrogate().predict(np.zeros((2, 2)))


def test_determinism():
    X, y = _smooth_dataset()
    a = ANNSurrogate(random_state=7).fit(X, y).predict(X)
    b = ANNSurrogate(random_state=7).fit(X, y).predict(X)
    np.testing.assert_allclose(a, b)


def test_build_model_selects_backend():
    poly_cfg = XAppConfig(xapp_id="x", spec=CMSORAN_SPEC, objective="max", model_kind="poly")
    ann_cfg = XAppConfig(xapp_id="x", spec=CMSORAN_SPEC, objective="max", model_kind="ann")
    assert isinstance(build_model(poly_cfg), PolyRegSurrogate)
    assert isinstance(build_model(ann_cfg), ANNSurrogate)
