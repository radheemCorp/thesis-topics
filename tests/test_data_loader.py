"""Tests for CSV dataset ingestion."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from surrogate_xapps.config import CMSORAN_SPEC, QACM_SPEC
from surrogate_xapps.data_loader import load_dataset, load_threshold


def test_load_cmsoran_data1(cco_file: Path):
    X, y, ranges = load_dataset(cco_file, CMSORAN_SPEC)
    assert X.shape == (10000, 2)
    assert y.shape == (10000,)
    assert set(ranges) == {"p1", "p2"}
    assert ranges["p1"][0] == pytest.approx(-150.0)
    assert ranges["p1"][1] == pytest.approx(150.0)


def test_load_cmsoran_data2(es_file: Path):
    X, y, ranges = load_dataset(es_file, CMSORAN_SPEC)
    assert X.shape == (10000, 2)
    assert ranges["p2"][0] == pytest.approx(60.0)


def test_load_qacm_layout(qacm_file: Path):
    X, y, ranges = load_dataset(qacm_file, QACM_SPEC)
    assert X.shape[1] == 2
    assert y.shape[0] == X.shape[0]


def test_missing_file_raises(tmp_path: Path):
    with pytest.raises(FileNotFoundError):
        load_dataset(tmp_path / "nope.csv", CMSORAN_SPEC)


def test_missing_column_raises(tmp_path: Path):
    bad = tmp_path / "bad.csv"
    bad.write_text("a,b,c\n1,2,3\n")
    with pytest.raises(ValueError, match="missing required column"):
        load_dataset(bad, CMSORAN_SPEC)


def test_empty_file_raises(tmp_path: Path):
    empty = tmp_path / "empty.csv"
    empty.write_text("")
    with pytest.raises(ValueError):
        load_dataset(empty, CMSORAN_SPEC)


def test_non_numeric_rows_dropped(tmp_path: Path):
    csv = tmp_path / "mixed.csv"
    rows = ["Input1,Input2,Output"]
    for i in range(10):
        rows.append(f"{i},{i},{i}")
    rows.append("bad,1,2")
    csv.write_text("\n".join(rows) + "\n")
    with pytest.warns(UserWarning, match="Dropped"):
        X, y, _ = load_dataset(csv, CMSORAN_SPEC)
    assert X.shape[0] == 10


def test_too_few_rows_raises(tmp_path: Path):
    csv = tmp_path / "few.csv"
    csv.write_text("Input1,Input2,Output\n1,2,3\n4,5,6\n")
    with pytest.raises(ValueError, match="valid row"):
        load_dataset(csv, CMSORAN_SPEC)


def test_load_threshold_from_qacm(qacm_file: Path):
    value = load_threshold(qacm_file, QACM_SPEC, default=0.0)
    assert value != 0.0


def test_load_threshold_default_when_no_column(cco_file: Path):
    # CMSORAN_SPEC has no threshold column -> default returned.
    assert load_threshold(cco_file, CMSORAN_SPEC, default=0.42) == 0.42


def test_load_threshold_default_when_file_missing(tmp_path: Path):
    assert load_threshold(tmp_path / "nope.csv", QACM_SPEC, default=0.7) == 0.7
