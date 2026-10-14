"""Tests for the matplotlib visualization."""

from __future__ import annotations

from pathlib import Path

from surrogate_xapps.config import CCO_CONFIG, ES_CONFIG
from surrogate_xapps.data_loader import load_dataset
from surrogate_xapps.plot_utils import plot_kpi_curves
from surrogate_xapps.xapps import CCOxApp, ESxApp


def test_plot_writes_png(cco_file: Path, es_file: Path, tmp_path: Path):
    Xc, yc, _ = load_dataset(cco_file, CCO_CONFIG.spec)
    Xe, ye, _ = load_dataset(es_file, ES_CONFIG.spec)
    cco = CCOxApp(CCO_CONFIG).train(Xc, yc)
    es = ESxApp(ES_CONFIG).train(Xe, ye)

    out = tmp_path / "fig.png"
    fig = plot_kpi_curves(cco, es, cco.infer_action(), es.infer_action(), out)

    assert out.exists()
    assert out.stat().st_size > 0
    assert fig is not None
