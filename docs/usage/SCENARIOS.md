# Synthetic Conflict Scenarios (Direct + Indirect)

This document explains the synthetic datasets and how to test direct and indirect conflicts using the CMC.

## Datasets

Generated with `scripts/gen_synthetic_2d.py` (cmsORAN layout: Input1,Input2,Output). Peaks create overlapping regions of influence on (p1,p2).

| xApp | File | Peak (p1c,p2c) | Objective | Role |
|---|---|---|---|---|
| app1/xApp1 | `xapp1_direct.csv` | (-50, 20) | max | Direct party 1 |
| app2/xApp2 | `xapp2_direct.csv` | (-120, 60) | max | Direct party 2 (opposes app1) |
| app3/xApp3 | `xapp3_indirect.csv` | (-80, 40) | max | Indirect/coupled (strong p2 dependence) |
| app4/xApp4 | `xapp4_extra.csv` | (-90, 35) | max | Extra coupling (implicit-like mix) |

**Direct conflict**: app1 and app2 want different (p1,p2) optima → their requested values differ.  
**Indirect conflict**: app3’s optimum lies between app1/app2 on p2; when CMC compromises to satisfy the direct pair, app3’s KPI changes relative to its own peak (coupling). Adding app4 increases coupling.

## Running scenarios with the CLI

The CLI accepts multiple datasets and xapp names with per-xapp QoS/weights.

```bash
cd /home/radr/tuilm/thesis-topics

# Direct conflict only (2-app)
uv run python cli/cli.py \
  --datasets data/synthetic/xapp1_direct.csv data/synthetic/xapp2_direct.csv \
  --xapps app1,app2 \
  --qos 0.8 0.8 --weights 0.5 0.5

# Direct + Indirect (3-app)
uv run python cli/cli.py \
  --datasets data/synthetic/xapp1_direct.csv data/synthetic/xapp2_direct.csv data/synthetic/xapp3_indirect.csv \
  --xapps app1,app2,app3 \
  --qos 0.4 0.4 0.8 --weights 1 1 1

# Direct + Indirect + Extra (4-app)
uv run python cli/cli.py \
  --datasets data/synthetic/xapp1_direct.csv data/synthetic/xapp2_direct.csv data/synthetic/xapp3_indirect.csv data/synthetic/xapp4_extra.csv \
  --xapps app1,app2,app3,app4 \
  --qos 0.2 0.2 0.2 0.2 --weights 0.25 0.25 0.25 0.25
```

## What to test (illustrating direct vs indirect)

Key observations from the synthetic cases:

1. **Direct conflict (2-app)**: CMC finds a compromise `p*` between the conflicting requests. With tight QoS thresholds, total satisfaction can drop; with looser thresholds, both may remain satisfied. The key is the compromise lies in the conflict interval.
2. **Indirect coupling (3-app)**: Adding app3 (coupled strongly to p2, peak at middle) shifts the joint optimum vs 2-app alone. The per-xApp `kpi@p*` shows trade-offs — app3 can gain/lose satisfaction depending on thresholds/weights.
3. **Trade-off behavior**: As QoS thresholds tighten, satisfying all becomes harder; CMC’s objective (`Σ w_i·d_i·ζ − (Σ s_i)^2`) balances deviation vs maximizing satisfied count. The `IMPROVED`/`NOT IMPROVED` line reflects whether total satisfied count didn’t worsen.
4. **Weights matter**: Increasing app3’s weight pulls the compromise toward its preferred region (demonstrates priority effects).
5. **N-app modularity**: The CLI works with arbitrary counts (3,4+). The CMC itself accepts any `Sequence[IQueryableXApp]` with no code changes.

## Automated coverage

The Phase 4 scenario suite turns the observations above into regression tests:

| Test | What it pins |
|---|---|
| `tests/test_synthetic.py::test_dataset_matches_metadata` | Ranges, peak coordinates, and amplitudes of all four CSVs |
| `...::test_direct_conflict_compromise_lies_between_requests` | `p*` inside the app1/app2 request bounding box; both xApps recorded |
| `...::test_indirect_conflict_shifts_p2_towards_app3` | Adding app3 changes `p2*` and moves it toward app3’s peak |
| `...::test_priority_weight_pulls_p2_towards_app3` | Higher app3 weight moves `p2*` monotonically toward its preference |
| `...::test_tightening_thresholds_never_increases_satisfied_count` | Threshold sweeps never raise `n_satisfied_after`; `improved()` stays consistent |
| `tests/test_cli.py` (2-, 3-, 4-app) | Exit 0, `(p1, p2)` optimum printed, every xApp listed, no `nan` |

Run them with:

```bash
uv run pytest tests/test_synthetic.py -q   # 10 tests
uv run pytest tests/test_cli.py -q         # 3 tests
```

At the documented `--cmc-resolution 16 --resolution 16`, the app1/app2 run
gives `p2* = 48.00`; adding app3 (`q=0.8`, equal weights) gives
`p2* = 42.67`, visibly closer to app3’s `p2 = 40` peak.

## Reproducibility

- Datasets generated deterministically (seed=42).
- Surrogates use `random_state=42` (ANN) for reproducible predictions.
- Visualizations: `docs/synthetic/*.png` show the 2D KPI surfaces.
