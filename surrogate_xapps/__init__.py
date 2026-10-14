"""Surrogate CCO (throughput-maximizing) and ES (power-minimizing) xApps.

The package implements two surrogate xApps over the QACM/cmsORAN CSV dataset
structure. Each xApp trains a regression surrogate to predict a KPI from the
Input Control Parameters (ICPs) ``[p1, p2]`` and then searches the parameter
space to emit a structured control request for a QACM Conflict Mitigation
Controller (CMC).
"""

from __future__ import annotations

from .config import (
    CCO_CONFIG,
    CMSORAN_SPEC,
    ES_CONFIG,
    MODEL_KINDS,
    OBJECTIVES,
    QACM_SPEC,
    DatasetSpec,
    XAppConfig,
)
from .data_loader import load_dataset
from .surrogates import ANNSurrogate, PolyRegSurrogate, SurrogateModel, build_model
from .xapps import BaseXApp, CCOxApp, ESxApp, validate_action

__all__ = [
    "CCO_CONFIG",
    "CMSORAN_SPEC",
    "ES_CONFIG",
    "MODEL_KINDS",
    "OBJECTIVES",
    "QACM_SPEC",
    "DatasetSpec",
    "XAppConfig",
    "load_dataset",
    "ANNSurrogate",
    "PolyRegSurrogate",
    "SurrogateModel",
    "build_model",
    "BaseXApp",
    "CCOxApp",
    "ESxApp",
    "validate_action",
]

__version__ = "0.1.0"
