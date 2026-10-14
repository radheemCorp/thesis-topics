"""Tests for the dataset contract and xApp configuration."""

from __future__ import annotations

import pytest

from surrogate_xapps.config import (
    CCO_CONFIG,
    CMSORAN_SPEC,
    ES_CONFIG,
    QACM_SPEC,
    DatasetSpec,
    XAppConfig,
)


def test_cmsoran_spec_maps_headers():
    assert list(CMSORAN_SPEC.feature_cols) == ["Input1", "Input2"]
    assert CMSORAN_SPEC.target_col == "Output"
    assert list(CMSORAN_SPEC.feature_names) == ["p1", "p2"]
    assert CMSORAN_SPEC.threshold_col is None


def test_qacm_spec_maps_headers():
    assert list(QACM_SPEC.feature_cols) == ["Input1", "Input2"]
    assert QACM_SPEC.target_col == "Output"
    assert QACM_SPEC.threshold_col == "normalised_threshold"


def test_dataset_spec_length_mismatch_raises():
    with pytest.raises(ValueError):
        DatasetSpec(feature_cols=("a", "b"), target_col="k", feature_names=("p1",))


def test_cco_config_defaults():
    assert CCO_CONFIG.xapp_id == "xApp_CCO"
    assert CCO_CONFIG.objective == "max"
    assert 0.0 <= CCO_CONFIG.priority_weight <= 1.0


def test_es_config_defaults():
    assert ES_CONFIG.xapp_id == "xApp_ES"
    assert ES_CONFIG.objective == "min"


def test_invalid_objective_raises():
    with pytest.raises(ValueError):
        XAppConfig(xapp_id="x", spec=CMSORAN_SPEC, objective="maximize")


def test_invalid_model_kind_raises():
    with pytest.raises(ValueError):
        XAppConfig(xapp_id="x", spec=CMSORAN_SPEC, objective="max", model_kind="torch")


def test_invalid_priority_weight_raises():
    with pytest.raises(ValueError):
        XAppConfig(xapp_id="x", spec=CMSORAN_SPEC, objective="max", priority_weight=2.0)
