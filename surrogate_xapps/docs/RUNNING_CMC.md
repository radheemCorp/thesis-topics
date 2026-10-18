# Running the QACM CMC Demo

This guide shows how to run the **Conflict Mitigation Controller (CMC)** MVP, which resolves the direct conflict between the CCO and ES surrogate xApps using the QACM QoS-aware discrete heuristic.

## What it does

1. Trains both xApps (CCO maximizes throughput, ES minimizes power) on the cmsORAN datasets.
2. Detects the conflict (each requests a different `p1`).
3. Runs the CMC over the shared `p1` range and finds the compromise `p*` that minimizes weighted QoS deviation while maximizing the number of satisfied xApps.
4. Prints a before/after QoS comparison table.

## Prerequisites

- `uv` installed
- Run all commands from the repo root:
  ```bash
  cd /home/radr/tuilm/thesis-topics
  ```

## Run the demo

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
Optimal compromise p* (p1) = -56.69

xApp          req_p1   kpi@req    kpi@p*     thr  sat_before  sat_after
-----------------------------------------------------------------------
xApp_CCO      -46.97     1.004     0.911    0.90        True       True
xApp_ES      -137.88    -0.008     0.213    0.50        True       True

Satisfied before: 2/2  ->  Satisfied after: 2/2
IMPROVED
```

- **p\*** lies between the conflicting requests (`-46.97` and `-137.88`).
- Both xApps remain QoS-satisfied at the compromise.

## Options

`run_cmc_demo(...)` accepts:
- `cco_file`, `es_file` — dataset paths (default: `data/cmsORAN/data1.csv`, `data2.csv`)
- `model_kind` — `"ann"` (default) or `"poly"`
- `resolution` — grid resolution for each xApp's decision search (default 200)
- `cmc_resolution` — number of discrete candidates the CMC sweeps (default 300)

## Using the CMC programmatically

The CMC only needs xApps that satisfy the `IQueryableXApp` protocol (`predict_at(p1)` plus metadata). Adding a new xApp requires no CMC changes:

```python
from surrogate_xapps.cmc import CMC

cmc = CMC(range=(-150, 150), resolution=300)
result = cmc.mitigate([cco, es, my_new_xapp])  # any number of xApps
print(result.optimal_value, result.n_satisfied_after)
```

See `surrogate_xapps/cmc.py` for the `CMC`, `MitigationResult`, and `IQueryableXApp` definitions.
