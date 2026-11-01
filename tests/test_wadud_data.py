from __future__ import annotations

import hashlib
from pathlib import Path

import pandas as pd

from scripts.gen_wadud_datasets import generate


def test_wadud_generator_is_deterministic(tmp_path: Path) -> None:
    first, second = tmp_path / "first", tmp_path / "second"
    generate(first)
    generate(second)
    for path in first.iterdir():
        assert hashlib.sha256(path.read_bytes()).digest() == hashlib.sha256(
            (second / path.name).read_bytes()
        ).digest()


def test_generated_scalar_surfaces_have_paper_range_and_columns(tmp_path: Path) -> None:
    generate(tmp_path)
    for name in ("xapp1", "xapp2", "xapp3", "xapp4", "xapp5"):
        frame = pd.read_csv(tmp_path / f"{name}.csv")
        assert list(frame.columns) == ["Input1", "Output"]
        assert frame["Input1"].min() == -150
        assert frame["Input1"].max() == 150
