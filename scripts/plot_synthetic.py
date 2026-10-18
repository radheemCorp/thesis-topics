#!/usr/bin/env python3
"""Visualize synthetic 2D datasets as contour plots."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

OUT_DIR = Path("docs/synthetic")
OUT_DIR.mkdir(parents=True, exist_ok=True)


def plot_dataset(csv_path: str | Path, out_name: str | None = None) -> Path:
    df = pd.read_csv(csv_path)
    p1 = np.unique(df["Input1"])
    p2 = np.unique(df["Input2"])
    P1 = p1.reshape(-1, 1) if False else None  # dummy
    # easier: pivot
    Z = df.pivot(index="Input2", columns="Input1", values="Output").values
    P1g, P2g = np.meshgrid(p1, p2)
    fig, ax = plt.subplots(figsize=(8, 6))
    cs = ax.contourf(P1g, P2g, Z, levels=20, cmap="viridis")
    ax.set_xlabel("p1")
    ax.set_ylabel("p2")
    ax.set_title(f"Contour: {Path(csv_path).name}")
    fig.colorbar(cs, ax=ax, label="KPI (Output)")
    out_path = OUT_DIR / (out_name or Path(csv_path).stem + ".png")
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return out_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Plot synthetic 2D dataset")
    parser.add_argument("csv", help="Path to CSV (Input1,Input2,Output)")
    parser.add_argument("--out", help="Output PNG name")
    args = parser.parse_args()
    p = plot_dataset(args.csv, args.out)
    print(p)


if __name__ == "__main__":
    main()
