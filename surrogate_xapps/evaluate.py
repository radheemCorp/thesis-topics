"""Machine-readable evaluation helpers for QACM and Wadud baselines."""

from __future__ import annotations

import argparse
import csv
import time
from pathlib import Path

import numpy as np

from .baselines import ArithmeticMeanPolicy, EisenbergGalePolicy, NSWFPolicy
from .cmc import CMC
from .scenarios import SCENARIOS, get_scenario
from .config import CMSORAN_SPEC, DatasetSpec, XAppConfig
from .data_loader import load_dataset
from .xapps import CCOxApp
from .utility import normalize_utility


def evaluate_methods(xapps, ranges, resolution=128, weights=None, methods=("qacm", "am", "nswf", "eg")):
    """Return one deterministic metric record per requested method."""
    policies = {
        "qacm": CMC(ranges=ranges, resolution=resolution),
        "am": ArithmeticMeanPolicy(),
        "nswf": NSWFPolicy(),
        "eg": EisenbergGalePolicy(),
    }
    records = []
    for method in methods:
        started = time.perf_counter()
        if method == "qacm":
            result = policies[method].mitigate(xapps)
        else:
            result = policies[method].mitigate(xapps, ranges, resolution, weights)
        elapsed = (time.perf_counter() - started) * 1000.0
        utilities = []
        regrets = []
        reference_grid = CMC(ranges=ranges, resolution=resolution)
        grid = reference_grid.candidate_grid()
        selected = np.asarray(result.optimal_point, dtype=float)
        grid_index = int(np.argmin(np.sum((grid - selected[:grid.shape[1]]) ** 2, axis=1)))
        for record in result.per_xapp:
            xapp = next(x for x in xapps if x.xapp_id == record["xapp_id"])
            predictions = reference_grid._predict_grid(xapp, grid)
            _, (lo, hi) = normalize_utility(
                predictions, objective=xapp.objective, mode="minmax10"
            )
            if hi == lo:
                preferred_utility = optimum_utility = 0.0
            elif xapp.objective == "max":
                preferred_utility = (record["predicted_at_preferred"] - lo) / (hi - lo) * 10.0
                optimum_utility = (predictions[grid_index] - lo) / (hi - lo) * 10.0
            else:
                preferred_utility = (hi - record["predicted_at_preferred"]) / (hi - lo) * 10.0
                optimum_utility = (hi - predictions[grid_index]) / (hi - lo) * 10.0
            utilities.append(float(optimum_utility))
            regrets.append(float(preferred_utility - optimum_utility))
        weights_array = np.asarray(weights if weights is not None else [x.priority_weight for x in xapps], dtype=float)
        weights_array = weights_array / weights_array.sum()
        records.append({
            "method": method,
            "p_star": result.optimal_point[0] if len(result.optimal_point) == 1 else result.optimal_point,
            "utilities": utilities,
            "regrets": regrets,
            "welfare": float(np.dot(weights_array, utilities)),
            "nash_product": float(np.prod(utilities)),
            "min_utility": float(min(utilities, default=0.0)),
            "utility_spread": float(max(utilities, default=0.0) - min(utilities, default=0.0)),
            "n_satisfied_before": result.n_satisfied_before,
            "n_satisfied_after": result.n_satisfied_after,
            "latency_ms": elapsed,
            "deterministic": True,
            "result": result,
        })
    return records


def write_results(records, output: str | Path) -> None:
    """Write JSON-shaped metric fields as CSV and a compact Markdown table."""
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    fields = [key for key in records[0] if key != "result"]
    with output.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for record in records:
            writer.writerow({key: record[key] for key in fields})
    markdown = output.with_suffix(".md")
    with markdown.open("w") as stream:
        stream.write("| method | p* | satisfied after | latency (ms) |\n|---|---:|---:|---:|\n")
        for record in records:
            stream.write(f"| {record['method']} | {record['p_star']} | {record['n_satisfied_after']} | {record['latency_ms']:.3f} |\n")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Evaluate registered baseline methods")
    parser.add_argument("--scenario", choices=sorted(SCENARIOS), required=True)
    parser.add_argument("--methods", default="all")
    parser.add_argument("--output", default="results/baselines.csv")
    args = parser.parse_args(argv)
    scenario = get_scenario(args.scenario)
    if not scenario.datasets:
        raise SystemExit("S9 is a metadata edge-case scenario and has no datasets")
    root = Path.cwd()
    paths = [root / path for path in scenario.datasets]
    if any(not path.exists() for path in paths):
        raise SystemExit("scenario datasets are unavailable in the current repository")
    xapps = []
    for name, path, weight in zip(scenario.xapps, paths, scenario.weights):
        spec = (
            DatasetSpec(feature_cols=("Input1",), target_col="Output", feature_names=("p1",))
            if "data/wadud/" in path.as_posix()
            else CMSORAN_SPEC
        )
        config = XAppConfig(
            xapp_id=name, spec=spec, objective="max",
            priority_weight=weight, model_kind="poly", resolution=32,
        )
        X, y, _ = load_dataset(path, spec)
        xapps.append(CCOxApp(config).train(X, y))
    lo = max(x.ranges_["p1"][0] for x in xapps)
    hi = min(x.ranges_["p1"][1] for x in xapps)
    if lo > hi:
        raise SystemExit("scenario xApp p1 ranges do not overlap")
    methods = tuple(sorted(("qacm", "am", "nswf", "eg") if args.methods == "all" else args.methods.split(",")))
    records = evaluate_methods(xapps, (lo, hi), weights=scenario.weights, methods=methods)
    write_results(records, args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
