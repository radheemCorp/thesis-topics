#!/usr/bin/env python3
"""Generate synthetic 2D (p1,p2) datasets for CMC conflict illustration.

Creates CSVs with columns Input1,Input2,Output (cmsORAN layout) representing
KPI surfaces. Also writes a small metadata JSON.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

OUT_DIR = Path("data/synthetic")
OUT_DIR.mkdir(parents=True, exist_ok=True)


def gaussian_2d(p1: np.ndarray, p2: np.ndarray, p1c: float, p2c: float, A: float, sigma: float) -> np.ndarray:
    return A * np.exp(-((p1 - p1c) ** 2 + (p2 - p2c) ** 2) / (2 * sigma ** 2))


def main() -> None:
    rng = np.random.default_rng(42)
    # Grid over sensible range
    p1 = np.linspace(-150, 50, 141)
    p2 = np.linspace(0, 80, 81)
    P1, P2 = np.meshgrid(p1, p2)
    # Flatten
    p1f = P1.ravel()
    p2f = P2.ravel()

    # x1: CCO-like, max, peak (-50,20)
    k1 = gaussian_2d(p1f, p2f, -50.0, 20.0, 1.0, 25.0)
    df1 = pd.DataFrame({"Input1": p1f, "Input2": p2f, "Output": k1})
    df1.to_csv(OUT_DIR / "xapp1_direct.csv", index=False)

    # x2: opposing, max peak (-120,60) - creates direct conflict with x1
    k2 = gaussian_2d(p1f, p2f, -120.0, 60.0, 1.0, 25.0)
    df2 = pd.DataFrame({"Input1": p1f, "Input2": p2f, "Output": k2})
    df2.to_csv(OUT_DIR / "xapp2_direct.csv", index=False)

    # x3: indirect/coupled to p2, peak (-80,40) - strong p2 dependence
    k3 = gaussian_2d(p1f, p2f, -80.0, 40.0, 1.0, 20.0)
    df3 = pd.DataFrame({"Input1": p1f, "Input2": p2f, "Output": k3})
    df3.to_csv(OUT_DIR / "xapp3_indirect.csv", index=False)

    # x4: extra coupling, peak (-90,35)
    k4 = gaussian_2d(p1f, p2f, -90.0, 35.0, 1.0, 22.0)
    df4 = pd.DataFrame({"Input1": p1f, "Input2": p2f, "Output": k4})
    df4.to_csv(OUT_DIR / "xapp4_extra.csv", index=False)

    meta = {
        "description": "Synthetic 2D (p1,p2) Gaussian peaks for direct+indirect conflict illustration",
        "peaks": {
            "xapp1_direct": {"p1c": -50, "p2c": 20, "A": 1.0, "sigma": 25.0, "objective": "max"},
            "xapp2_direct": {"p1c": -120, "p2c": 60, "A": 1.0, "sigma": 25.0, "objective": "max"},
            "xapp3_indirect": {"p1c": -80, "p2c": 40, "A": 1.0, "sigma": 20.0, "objective": "max"},
            "xapp4_extra": {"p1c": -90, "p2c": 35, "A": 1.0, "sigma": 22.0, "objective": "max"},
        },
        "range": {"p1": [-150, 50], "p2": [0, 80]},
        "layout": "cmsORAN (Input1,Input2,Output)",
    }
    with open(OUT_DIR / "synthetic_meta.json", "w") as f:
        json.dump(meta, f, indent=2)

    print("Generated synthetic datasets in", OUT_DIR)


if __name__ == "__main__":
    main()
