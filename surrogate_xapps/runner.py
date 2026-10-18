"""Orchestration, conflict demonstration, and CLI for the surrogate xApps.

``main()`` loads the CCO and ES datasets, trains both surrogate xApps, calls
``infer_action()`` on both, prints the requests side-by-side, and reports
whether they conflict.
"""

from __future__ import annotations

import argparse
from dataclasses import replace
from pathlib import Path
from typing import Any, Sequence

from .cmc import CMC, MitigationResult
from .config import CCO_CONFIG, ES_CONFIG
from .data_loader import load_dataset
from .xapps import CCOxApp, ESxApp

#: Default dataset paths (relative to the repository root).
DEFAULT_CCO_FILE = "data/cmsORAN/data1.csv"
DEFAULT_ES_FILE = "data/cmsORAN/data2.csv"


def detect_conflict(
    action_a: dict[str, Any],
    action_b: dict[str, Any],
    tolerance: float = 1e-6,
) -> bool:
    """Return ``True`` if the two requests differ beyond ``tolerance``.

    Conflict is evaluated per shared target parameter: any parameter whose
    requested values differ by more than ``tolerance`` counts as a conflict.
    """
    a = dict(zip(action_a["target_parameter"], action_a["requested_value"]))
    b = dict(zip(action_b["target_parameter"], action_b["requested_value"]))
    for name in set(a) & set(b):
        if abs(float(a[name]) - float(b[name])) > tolerance:
            return True
    return False


def run(
    cco_file: str | Path = DEFAULT_CCO_FILE,
    es_file: str | Path = DEFAULT_ES_FILE,
    model_kind: str = "ann",
    resolution: int = 200,
) -> tuple[dict[str, Any], dict[str, Any], CCOxApp, ESxApp]:
    """Train both xApps and return their control requests and instances.

    Returns
    -------
    (action_cco, action_es, cco, es)
    """
    cco_config = replace(CCO_CONFIG, model_kind=model_kind, resolution=resolution)
    es_config = replace(ES_CONFIG, model_kind=model_kind, resolution=resolution)

    X_cco, y_cco, _ = load_dataset(cco_file, cco_config.spec)
    X_es, y_es, _ = load_dataset(es_file, es_config.spec)

    cco = CCOxApp(cco_config).train(X_cco, y_cco)
    es = ESxApp(es_config).train(X_es, y_es)

    action_cco = cco.infer_action()
    action_es = es.infer_action()
    return action_cco, action_es, cco, es


def run_cmc_demo(
    cco_file: str | Path = DEFAULT_CCO_FILE,
    es_file: str | Path = DEFAULT_ES_FILE,
    model_kind: str = "ann",
    resolution: int = 200,
    cmc_resolution: int = 300,
) -> dict[str, Any]:
    """Train CCO+ES, detect their conflict, and run the CMC mitigation.

    Parameters
    ----------
    cco_file, es_file:
        Paths to the CCO and ES datasets.
    model_kind:
        Surrogate backend (``"ann"`` or ``"poly"``).
    resolution:
        Grid resolution for each xApp's decision search.
    cmc_resolution:
        Number of discrete candidates the CMC sweeps over the shared ICP.

    Returns
    -------
    dict
        ``{"action_cco", "action_es", "conflict", "mitigation", "cco", "es"}``
        where ``mitigation`` is a :class:`~surrogate_xapps.cmc.MitigationResult`.
    """
    action_cco, action_es, cco, es = run(
        cco_file=cco_file, es_file=es_file, model_kind=model_kind,
        resolution=resolution,
    )
    conflict = detect_conflict(action_cco, action_es)

    # Shared ICP p1 range = intersection of both xApps' observed p1 ranges.
    lo = max(cco.ranges_["p1"][0], es.ranges_["p1"][0])
    hi = min(cco.ranges_["p1"][1], es.ranges_["p1"][1])
    cmc = CMC(range=(lo, hi), resolution=cmc_resolution)
    mitigation: MitigationResult = cmc.mitigate([cco, es])

    return {
        "action_cco": action_cco,
        "action_es": action_es,
        "conflict": conflict,
        "mitigation": mitigation,
        "cco": cco,
        "es": es,
    }


def _print_report(
    action_cco: dict[str, Any],
    action_es: dict[str, Any],
    conflict: bool,
) -> None:
    header = f"{'xApp':<10} {'requested [p1, p2]':<26} {'predicted_kpi':>13} {'qos':>6}"
    print(header)
    print("-" * len(header))
    for action in (action_cco, action_es):
        req = action["requested_value"]
        req_str = f"[{req[0]:.2f}, {req[1]:.2f}]"
        print(
            f"{action['xapp_id']:<10} {req_str:<26} "
            f"{action['predicted_kpi']:>13.4f} {action['qos_threshold']:>6.2f}"
        )
    print()
    print("CONFLICT" if conflict else "NO CONFLICT")


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line argument parser."""
    parser = argparse.ArgumentParser(
        prog="surrogate-xapps",
        description=(
            "Train surrogate CCO (throughput-max) and ES (power-min) xApps and "
            "demonstrate their conflicting control requests."
        ),
    )
    parser.add_argument("--cco-file", default=DEFAULT_CCO_FILE, help="CCO dataset CSV")
    parser.add_argument("--es-file", default=DEFAULT_ES_FILE, help="ES dataset CSV")
    parser.add_argument(
        "--model",
        choices=("poly", "ann"),
        default="ann",
        help="Surrogate backend (default: ann)",
    )
    parser.add_argument(
        "--resolution",
        type=int,
        default=200,
        help="Grid points per parameter axis (default: 200)",
    )
    parser.add_argument(
        "--out",
        default="out",
        help="Output directory for the comparison figure (default: out)",
    )
    parser.add_argument(
        "--no-plot",
        action="store_true",
        help="Skip figure generation",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """CLI entry point."""
    args = build_parser().parse_args(argv)

    action_cco, action_es, cco, es = run(
        cco_file=args.cco_file,
        es_file=args.es_file,
        model_kind=args.model,
        resolution=args.resolution,
    )

    conflict = detect_conflict(action_cco, action_es)
    _print_report(action_cco, action_es, conflict)

    if not args.no_plot:
        from .plot_utils import plot_kpi_curves

        out_path = Path(args.out) / "xapp_kpi_comparison.png"
        plot_kpi_curves(cco, es, action_cco, action_es, out_path)
        print(f"\nFigure written to {out_path}")

    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
