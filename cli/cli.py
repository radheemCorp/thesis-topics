#!/usr/bin/env python3
"""CLI to run CMC scenarios on synthetic datasets."""

from __future__ import annotations

import argparse
from dataclasses import replace
from pathlib import Path
from typing import Any

from surrogate_xapps.cmc import CMC
from surrogate_xapps.config import CMSORAN_SPEC, XAppConfig
from surrogate_xapps.data_loader import load_dataset
from surrogate_xapps.runner import detect_conflict, print_cmc_report
from surrogate_xapps.xapps import BaseXApp, CCOxApp, ESxApp

# Map names to (class, default config)
XAPP_MAP = {
    "cco": (CCOxApp, XAppConfig(xapp_id="xApp_CCO", spec=CMSORAN_SPEC, objective="max", qos_threshold=0.8, priority_weight=1.0)),
    "es": (ESxApp, XAppConfig(xapp_id="xApp_ES", spec=CMSORAN_SPEC, objective="min", qos_threshold=0.2, priority_weight=1.0)),
    "app1": (CCOxApp, XAppConfig(xapp_id="xApp1", spec=CMSORAN_SPEC, objective="max", qos_threshold=0.8, priority_weight=1.0)),
    "app2": (CCOxApp, XAppConfig(xapp_id="xApp2", spec=CMSORAN_SPEC, objective="max", qos_threshold=0.8, priority_weight=1.0)),
    "app3": (CCOxApp, XAppConfig(xapp_id="xApp3", spec=CMSORAN_SPEC, objective="max", qos_threshold=0.8, priority_weight=1.0)),
    "app4": (CCOxApp, XAppConfig(xapp_id="xApp4", spec=CMSORAN_SPEC, objective="max", qos_threshold=0.8, priority_weight=1.0)),
}


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Run CMC scenarios on synthetic datasets")
    p.add_argument("--datasets", nargs="+", required=True, help="CSV files (Input1,Input2,Output)")
    p.add_argument("--xapps", required=True, help="Comma-separated xapp names: cco,es,app1,app2,app3,app4")
    p.add_argument("--qos", nargs="+", type=float, help="QoS thresholds per xapp (in same order)")
    p.add_argument("--weights", nargs="+", type=float, help="Priority weights per xapp (in same order)")
    p.add_argument(
        "--cmc-resolution",
        nargs="+",
        type=int,
        default=[300],
        help="CMC points per axis: one value broadcasts, two set p1/p2",
    )
    p.add_argument(
        "--optimize-over",
        choices=("joint", "p1", "p2"),
        default="joint",
        help="ICP subset to optimize (default: joint)",
    )
    p.add_argument("--model", choices=("ann", "poly"), default="ann")
    p.add_argument("--resolution", type=int, default=200, help="xApp grid resolution")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    names = [n.strip() for n in args.xapps.split(",") if n.strip()]
    if len(names) != len(args.datasets):
        raise SystemExit(f"Number of xapps ({len(names)}) must equal number of datasets ({len(args.datasets)})")

    xapps: list[BaseXApp] = []
    for i, (name, dpath) in enumerate(zip(names, args.datasets)):
        if name not in XAPP_MAP:
            raise SystemExit(f"Unknown xapp name: {name}")
        cls, cfg = XAPP_MAP[name]
        cfg = replace(cfg, model_kind=args.model, resolution=args.resolution)
        if args.qos and i < len(args.qos):
            cfg = replace(cfg, qos_threshold=args.qos[i])
        if args.weights and i < len(args.weights):
            cfg = replace(cfg, priority_weight=args.weights[i])
        X, y, _ = load_dataset(dpath, cfg.spec)
        xapps.append(cls(cfg).train(X, y))

    # Get actions
    actions = [x.infer_action() for x in xapps]
    # Detect conflicts
    conflict = False
    for a in actions[1:]:
        if detect_conflict(actions[0], a):
            conflict = True
            break
    def intersection(name: str) -> tuple[float, float]:
        lo = max(float(xapp.ranges_[name][0]) for xapp in xapps)
        hi = min(float(xapp.ranges_[name][1]) for xapp in xapps)
        return lo, hi

    p1_range = intersection("p1")
    if p1_range[0] > p1_range[1]:
        raise SystemExit("xApp p1 ranges do not overlap")
    p2_range = intersection("p2")
    if args.optimize_over != "p1" and p2_range[0] > p2_range[1]:
        raise SystemExit(
            "xApp p2 ranges do not overlap; use --optimize-over p1"
        )

    if args.optimize_over == "p1":
        ranges = [p1_range]
        optimize_over = None
        display_axes = [0]
    elif args.optimize_over == "p2":
        ranges = [p1_range, p2_range]
        optimize_over = [1]
        display_axes = [1]
    else:
        ranges = [p1_range, p2_range]
        optimize_over = None
        display_axes = [0, 1]

    if len(args.cmc_resolution) == 1:
        cmc_resolution: int | list[int] = args.cmc_resolution[0]
    elif len(args.cmc_resolution) == 2:
        cmc_resolution = args.cmc_resolution
    else:
        raise SystemExit("--cmc-resolution accepts one or two values")

    cmc = CMC(
        ranges=ranges, resolution=cmc_resolution, optimize_over=optimize_over
    )
    mitigation = cmc.mitigate(xapps)

    result: dict[str, Any] = {
        "actions": actions,
        "conflict": conflict,
        "mitigation": mitigation,
    }
    print_cmc_report(result, actions=actions, axes=display_axes)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
