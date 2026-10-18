# Running surrogate_xapps (without CMC)

This guide shows how to run the surrogate CCO and ES xApps **without** the QACM Conflict Mitigation Controller (CMC). Running them independently produces their own best control requests; when compared together, they conflict over shared ICPs [p1, p2].

## Prerequisites

- `uv` installed
- Dependencies available (pandas, numpy, scikit-learn, matplotlib). Use `uv run` so the correct environment is used.
- All commands assume you are in the repo root:

```bash
cd /home/radr/tuilm/thesis-topics
```

## 1) Run both xApps together (with conflict detection)

### Option A: CLI

```bash
uv run python -m surrogate_xapps --no-plot
```

This trains both xApps, prints their requested [p1,p2], predicted KPI, QoS threshold, and reports whether they conflict. To also generate a figure, omit `--no-plot` (writes to `out/xapp_kpi_comparison.png`).

CLI options:
- `--cco-file` (default: `data/cmsORAN/data1.csv`)
- `--es-file` (default: `data/cmsORAN/data2.csv`)
- `--model {poly,ann}` (default: `ann`)
- `--resolution RESOLUTION` (default: 200)
- `--out OUT` (default: `out`)
- `--no-plot`

### Option B: Python API

```bash
uv run python -c "
from surrogate_xapps import runner
action_cco, action_es, cco, es = runner.run()
runner._print_report(action_cco, action_es, runner.detect_conflict(action_cco, action_es))
"
```

Customize datasets/model/resolution:

```bash
uv run python -c "
from surrogate_xapps import runner
action_cco, action_es, cco, es = runner.run(
    cco_file='data/cmsORAN/data1.csv',
    es_file='data/cmsORAN/data2.csv',
    model_kind='ann',
    resolution=200,
)
print('conflict:', runner.detect_conflict(action_cco, action_es))
"
```

### Example output

```
xApp       requested [p1, p2]         predicted_kpi    qos
----------------------------------------------------------
xApp_CCO   [-47.49, 20.00]                   1.0037   0.90
xApp_ES    [-137.94, 60.00]                 -0.0077   0.50

CONFLICT
```

Note: Values may vary slightly between runs due to ANN initialization.

## 2) Run individual xApps

### CCO only (throughput-maximizing)

```bash
uv run python << 'PY'
from surrogate_xapps import CCOxApp, CCO_CONFIG
from surrogate_xapps.data_loader import load_dataset

X, y, _ = load_dataset('data/cmsORAN/data1.csv', CCO_CONFIG.spec)
cco = CCOxApp(CCO_CONFIG).train(X, y)
action = cco.infer_action()
print(action)
PY
```

Check QoS satisfaction:

```bash
uv run python << 'PY'
from surrogate_xapps import CCOxApp, CCO_CONFIG
from surrogate_xapps.data_loader import load_dataset

X, y, _ = load_dataset('data/cmsORAN/data1.csv', CCO_CONFIG.spec)
cco = CCOxApp(CCO_CONFIG).train(X, y)
action = cco.infer_action()
print('satisfied:', cco.qos_satisfied(action['predicted_kpi']))
PY
```

Example action:
```json
{
  "xapp_id": "xApp_CCO",
  "target_parameter": ["p1", "p2"],
  "requested_value": [-59.55, 20.00],
  "parameter_range": [[-150.0, 150.0], [20.0, 20.0]],
  "predicted_kpi": 0.4882,
  "qos_threshold": 0.9,
  "priority_weight": 0.5
}
```

### ES only (power-minimizing)

```bash
uv run python << 'PY'
from surrogate_xapps import ESxApp, ES_CONFIG
from surrogate_xapps.data_loader import load_dataset

X, y, _ = load_dataset('data/cmsORAN/data2.csv', ES_CONFIG.spec)
es = ESxApp(ES_CONFIG).train(X, y)
action = es.infer_action()
print(action)
PY
```

Example action:
```json
{
  "xapp_id": "xApp_ES",
  "target_parameter": ["p1", "p2"],
  "requested_value": [-121.36, 60.00],
  "parameter_range": [[-150.0, 150.0], [60.0, 60.0]],
  "predicted_kpi": -0.0192,
  "qos_threshold": 0.5,
  "priority_weight": 0.5
}
```

## 3) Tweak configuration (optional)

Override defaults like `qos_threshold`, `priority_weight`, `model_kind`, `resolution`, `poly_degree`:

```bash
uv run python << 'PY'
from surrogate_xapps import CCOxApp, CCO_CONFIG
from surrogate_xapps.data_loader import load_dataset
from dataclasses import replace

cfg = replace(CCO_CONFIG, qos_threshold=0.8, priority_weight=0.7, model_kind='poly', resolution=150)
X, y, _ = load_dataset('data/cmsORAN/data1.csv', cfg.spec)
cco = CCOxApp(cfg).train(X, y)
print(cco.infer_action())
PY
```

## Notes

- `infer_action()` searches the 2D grid over observed parameter ranges [p1,p2] and returns each xApp’s own best request (argmax for CCO, argmin for ES). **No joint optimization or CMC is applied.**
- The action schema is validated by `validate_action()` and matches what a QACM CMC expects.
- Datasets: `data/cmsORAN/data1.csv` (CCO), `data/cmsORAN/data2.csv` (ES). Both use `Input1,Input2,Output` (cmsORAN layout).
