#!/usr/bin/env python3
"""Generate deterministic scalar Wadud scenario projections.

The paper varies shared ``p1`` while holding the remaining ICPs fixed. This
generator evaluates the documented Gaussian equations at those fixed values,
so the resulting one-feature files are faithful scalar projections rather than
two-feature files with an arbitrary zero placeholder.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd


def generate(out: Path, points: int = 301, seed: int = 42) -> None:
    """Write scalar xApp datasets and provenance metadata."""
    if points < 2:
        raise ValueError("points must be at least 2")
    rng = np.random.default_rng(seed)
    del rng  # Seed is part of the reproducibility contract; equations are noiseless.
    p1 = np.linspace(-150.0, 150.0, points)
    fixed = {"p2": 20.0, "p3": 60.0, "p4": 60.0, "p5": 60.0, "p6": 0.0, "p7": 60.0, "p8": 0.0}
    k1 = 80.0 * np.exp(-((p1 + 0.0) ** 2) / (2.0 * fixed["p2"] ** 2))
    k2 = 100.0 * np.exp(-((p1 + fixed["p3"]) ** 2) / (2.0 * fixed["p2"] ** 2))
    k3 = 120.0 * np.exp(-((p1 + 45.0) ** 2) / (2.0 * fixed["p4"] ** 2))
    k41 = 120.0 * np.exp(-((fixed["p6"] + (fixed["p2"] - 30.0)) ** 2) / (2.0 * fixed["p5"] ** 2))
    k42 = 150.0 * np.exp(-((fixed["p6"] + (fixed["p2"] - 50.0)) ** 2) / (2.0 * fixed["p5"] ** 2))
    k4 = np.full_like(p1, (k41 + k42) / 2.0)
    k5 = -35.0 * np.exp(-((fixed["p8"] + (p1 - 25.0)) ** 2) / (2.0 * fixed["p7"] ** 2))
    outputs = {"xapp1": k1, "xapp2": k2, "xapp3": k3, "xapp4": k4, "xapp5": k5}
    out.mkdir(parents=True, exist_ok=True)
    for name, values in outputs.items():
        pd.DataFrame({"Input1": p1, "Output": values}).to_csv(out / f"{name}.csv", index=False)
    metadata = {
        "seed": seed,
        "points": points,
        "shared_icp": "p1",
        "range": [-150.0, 150.0],
        "fixed_icps": fixed,
        "equations": ["k1", "k2", "k3", "k41/k42 averaged for xapp4", "k5"],
        "source": "data/QACM/README.md; Wadud et al. 2311.13389v1",
        "projection": "scalar p1 evaluation at declared fixed ICP values",
        "status": "provisional: xApp/KPI mapping and fixed-ICP assignment require paper validation",
    }
    (out / "metadata.json").write_text(json.dumps(metadata, indent=2) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=Path("data/wadud"))
    parser.add_argument("--points", type=int, default=301)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    generate(args.out, args.points, args.seed)


if __name__ == "__main__":
    main()
