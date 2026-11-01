# Running the QACM CMC Demo

This guide shows how to run the **Conflict Mitigation Controller (CMC)**, which
resolves conflicting xApp control requests with the QACM QoS-aware discrete
heuristic. The same code handles the scalar `p1` case from the paper and joint
`(p1, p2)` bargaining over overlapping ICPs.

## What it does

1. Trains both xApps (CCO maximizes throughput, ES minimizes power) on the
   cmsORAN datasets.
2. Detects the conflict (each requests a different `p1`).
3. Sweeps shared ICP axes and finds the compromise `p*` that minimizes
   weighted QoS deviation while maximizing the number of satisfied xApps.
4. Prints a before/after QoS comparison table.

By default the CMC optimizes every shared axis it is given (`joint` mode). For
the cmsORAN CCO/ES pair the `p2` ranges do not overlap (CCO observes 20, ES 60),
so `run_cmc_demo` drops that axis and negotiates only `p1`. Synthetic datasets
share both axes, so the same code performs joint `(p1, p2)` bargaining.

## Prerequisites

- `uv` installed
- Run all commands from the repo root:
  ```bash
  cd /home/radr/tuilm/thesis-topics
  ```

## Run the scalar (cmsORAN) demo

```bash
uv run python -c "
from surrogate_xapps.runner import run_cmc_demo, print_cmc_report
result = run_cmc_demo(resolution=100, cmc_resolution=300)
print_cmc_report(result)
"
```

### Example output

```
QACM Conflict Mitigation — before/after QoS
============================================================
Optimal compromise p* = (p1=-56.69)

xApp         requested                  kpi@req    kpi@p*     thr  sat_before  sat_after
----------------------------------------------------------------------------------------
xApp_CCO     [-46.97, 20.00]              1.004     0.911    0.90        True       True
xApp_ES      [-137.88, 60.00]            -0.008     0.213    0.50        True       True

Satisfied before: 2/2  ->  Satisfied after: 2/2
IMPROVED
```

- **p\*** lies between the conflicting requests (`-46.97` and `-137.88`).
- Both xApps remain QoS-satisfied at the compromise.
- Only one coordinate is printed because the non-overlapping `p2` axis is
  fixed at each xApp's preferred value.

## Run a joint 2-D demo

The synthetic datasets share `p1 ∈ [-150, 50]` and `p2 ∈ [0, 80]`, so both
axes participate in the search.

Direct conflict (`app1` vs `app2`):

```bash
uv run python cli/cli.py \
  --datasets data/synthetic/xapp1_direct.csv data/synthetic/xapp2_direct.csv \
  --xapps app1,app2 --qos 0.4 0.4 --weights 1 1 \
  --cmc-resolution 32 --resolution 32
```

```
Optimal compromise p* = (p1=-91.94, p2=46.45)
...
Satisfied before: 2/2  ->  Satisfied after: 1/2
NOT IMPROVED
```

Add the indirectly coupled `app3` (note its tighter `0.8` threshold):

```bash
uv run python cli/cli.py \
  --datasets data/synthetic/xapp1_direct.csv data/synthetic/xapp2_direct.csv data/synthetic/xapp3_indirect.csv \
  --xapps app1,app2,app3 --qos 0.4 0.4 0.8 --weights 1 1 1 \
  --cmc-resolution 32 --resolution 32
```

```
Optimal compromise p* = (p1=-79.03, p2=43.87)
...
Satisfied before: 3/3  ->  Satisfied after: 1/3
NOT IMPROVED
```

Adding `app3` pulls `p2*` from `46.45` toward its own `p2` peak at `40`. See
[SCENARIOS.md](SCENARIOS.md) for the full scenario walkthrough.

## Options

`run_cmc_demo(...)` accepts:

- `cco_file`, `es_file` — dataset paths (default: `data/cmsORAN/data1.csv`,
  `data2.csv`)
- `model_kind` — `"ann"` (default) or `"poly"`
- `resolution` — grid resolution for each xApp's decision search (default 200)
- `cmc_resolution` — number of discrete candidates per CMC axis (default 300)

`cli/cli.py` additionally exposes:

| Argument | Meaning |
|---|---|
| `--optimize-over {joint,p1,p2}` | Which ICP subset the CMC sweeps (default `joint`) |
| `--cmc-resolution N [N2]` | One value broadcast to every axis, or one per axis (`p1`, `p2`) |
| `--resolution N` | xApp decision-grid points per axis |
| `--model {ann,poly}` | Surrogate backend |
| `--qos`, `--weights` | Per-xApp QoS thresholds and priority weights |

With `--optimize-over p1` or `p2`, only the selected coordinate is printed and
the other ICP is held at each xApp's preferred value.

## Using the CMC programmatically

The CMC only needs xApps that satisfy the `IQueryableXApp` protocol
(`preferred_point` plus `predict_at(p1, p2=None)` and metadata). Adding a new
xApp requires no CMC changes:

```python
from surrogate_xapps.cmc import CMC

# Joint 2-D: ranges has one (lo, hi) pair per ICP.
cmc = CMC(ranges=[(-150, 50), (0, 80)], resolution=128)
result = cmc.mitigate([app1, app2, app3])
print(result.optimal_point, result.n_satisfied_after)

# Restrict the sweep to p2; p1 is held at each xApp's preferred value.
p2_only = CMC(
    ranges=[(-150, 50), (0, 80)],
    resolution=128,
    optimize_over=[1],
).mitigate([app1, app2])

# Exact brute-force oracle (small grids only, test/reference use).
exact = CMC(ranges=[(-150, 50), (0, 80)], resolution=16).exact_mitigate([app1, app2])
```

Per-axis resolutions are supported by passing a sequence:

```python
cmc = CMC(ranges=[(-150, 50), (0, 80)], resolution=[64, 128])
```

`result.optimal_value` remains available as a deprecated 1-D view of
`result.optimal_point[0]`.

See `surrogate_xapps/cmc.py` for the `CMC`, `MitigationResult`, and
`IQueryableXApp` definitions.
