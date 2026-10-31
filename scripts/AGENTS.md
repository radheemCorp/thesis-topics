# AGENTS.md — scripts/

Scope: standalone generators for synthetic data and figures.

## Files
- `gen_synthetic_2d.py` — 2-D `(p1,p2)` KPI surfaces → `data/synthetic/` CSVs + metadata JSON.
- `gen_timeseries.py` — 1-D/2-D time-series plots for scenario illustration.
- `plot_synthetic.py` — contour plots of synthetic surfaces.

## Rules
- Every generator is deterministic: explicit `random_state`/seed; no unseeded `numpy.random`.
- Accept `--out`/paths via argparse; default into `data/` or `docs/visualizations/` only.
- No imports from `cli/` or `tests/`; may import `surrogate_xapps` for consistency.
- Regenerating must be idempotent (same inputs → same outputs).
