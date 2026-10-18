#!/usr/bin/env python3
"""Generate 1D/2D timeseries visualizations for synthetic datasets."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

OUT_DIR = Path("docs/visualizations")
OUT_DIR.mkdir(parents=True, exist_ok=True)


def plot_timeseries_1d(csv_path: str | Path, out_name: str | None = None) -> Path:
    df = pd.read_csv(csv_path)
    # For 2D grid, fix p2 at its median value and sweep p1
    p2_fixed = float(df["Input2"].median())
    df_slice = df[df["Input2"] == p2_fixed].sort_values("Input1")
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(df_slice["Input1"], df_slice["Output"], lw=2)
    ax.set_xlabel("p1")
    ax.set_ylabel("KPI (Output)")
    ax.set_title(f"1D slice at p2={p2_fixed:.1f}: {Path(csv_path).name}")
    ax.grid(True, alpha=0.3)
    out_path = OUT_DIR / (out_name or Path(csv_path).stem + "_timeseries_p1.png")
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return out_path


def plot_surface_3d(csv_path: str | Path, out_name: str | None = None) -> Path:
    df = pd.read_csv(csv_path)
    p1 = np.unique(df["Input1"])
    p2 = np.unique(df["Input2"])
    Z = df.pivot(index="Input2", columns="Input1", values="Output").values
    P1g, P2g = np.meshgrid(p1, p2)
    fig = plt.figure(figsize=(9, 6))
    ax = fig.add_subplot(111, projection="3d")
    ax.plot_surface(P1g, P2g, Z, cmap="viridis", edgecolor="none", alpha=0.9)
    ax.set_xlabel("p1")
    ax.set_ylabel("p2")
    ax.set_zlabel("KPI (Output)")
    ax.set_title(f"3D surface: {Path(csv_path).name}")
    out_path = OUT_DIR / (out_name or Path(csv_path).stem + "_surface3d.png")
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return out_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate timeseries/surface plots")
    parser.add_argument("csv", help="Path to CSV")
    parser.add_argument("--out1d", help="Output 1D PNG name")
    parser.add_argument("--out3d", help="Output 3D PNG name")
    args = parser.parse_args()
    p1 = plot_timeseries_1d(args.csv, args.out1d)
    p2 = plot_surface_3d(args.csv, args.out3d)
    print(p1)
    print(p2)


if __name__ == "__main__":
    main()
