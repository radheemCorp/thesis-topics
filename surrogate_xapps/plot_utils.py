"""Matplotlib visualization for the surrogate xApps.

Produces a comparison figure of the predicted KPI curves of both xApps with
their requested control points marked.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")  # headless-safe; callers may override before import

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

from .xapps import BaseXApp  # noqa: E402


def _curve(xapp: BaseXApp, n_points: int = 200) -> tuple[np.ndarray, np.ndarray]:
    """Return ``(p1_values, predicted_kpi)`` sweeping p1 with p2 held at its request."""
    if xapp.ranges_ is None:
        raise RuntimeError("xApp must be trained before plotting")
    names = list(xapp.config.spec.feature_names)
    action = xapp.infer_action()
    requested = action["requested_value"]

    p1_lo, p1_hi = xapp.ranges_[names[0]]
    p1_values = np.linspace(p1_lo, p1_hi, n_points)
    grid = np.tile(np.asarray(requested, dtype=float), (n_points, 1))
    grid[:, 0] = p1_values
    return p1_values, xapp.predict_kpi(grid)


def plot_kpi_curves(
    cco: BaseXApp,
    es: BaseXApp,
    action_cco: dict[str, Any],
    action_es: dict[str, Any],
    out_path: str | Path,
    n_points: int = 200,
) -> "plt.Figure":
    """Plot both xApps' predicted KPI curves and requested control points.

    Parameters
    ----------
    cco, es:
        Trained xApps.
    action_cco, action_es:
        Their control requests (from ``infer_action()``).
    out_path:
        Destination PNG path.
    n_points:
        Number of sweep points along ``p1``.

    Returns
    -------
    matplotlib.figure.Figure
        The generated figure (also written to ``out_path``).
    """
    p1_cco, kpi_cco = _curve(cco, n_points)
    p1_es, kpi_es = _curve(es, n_points)

    fig, ax = plt.subplots(figsize=(9, 5.5))
    ax.plot(p1_cco, kpi_cco, color="tab:blue", label=f"{cco.config.xapp_id} (maximize)")
    ax.plot(p1_es, kpi_es, color="tab:red", label=f"{es.config.xapp_id} (minimize)")

    ax.axvline(action_cco["requested_value"][0], color="tab:blue", ls="--", alpha=0.6)
    ax.axvline(action_es["requested_value"][0], color="tab:red", ls="--", alpha=0.6)
    ax.scatter(
        [action_cco["requested_value"][0]],
        [action_cco["predicted_kpi"]],
        color="tab:blue",
        marker="o",
        s=80,
        zorder=5,
        label=f"CCO request p1={action_cco['requested_value'][0]:.1f}",
    )
    ax.scatter(
        [action_es["requested_value"][0]],
        [action_es["predicted_kpi"]],
        color="tab:red",
        marker="o",
        s=80,
        zorder=5,
        label=f"ES request p1={action_es['requested_value'][0]:.1f}",
    )

    ax.set_xlabel("p1 (ICP)")
    ax.set_ylabel("Predicted KPI")
    ax.set_title("Surrogate xApps: predicted KPI curves and requested control points")
    ax.legend(loc="best", fontsize=9)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()

    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=150)
    return fig
