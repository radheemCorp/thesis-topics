# Runbook: Surrogate CCO & ES xApps

Track: `surrogate-xapps_20261014`

## Environment (uv)

```bash
uv sync                 # create .venv and install deps
```

## Run the conflict demo

```bash
uv run surrogate-xapps --out out
```

Expected output (cmsORAN `data1` vs `data2`, ANN backend):

```
xApp       requested [p1, p2]         predicted_kpi    qos
----------------------------------------------------------
xApp_CCO   [-47.49, 20.00]                   1.0037   0.90
xApp_ES    [-137.94, 60.00]                 -0.0077   0.50

CONFLICT

Figure written to out/xapp_kpi_comparison.png
```

### CLI options

| Flag | Default | Description |
| :--- | :--- | :--- |
| `--cco-file` | `data/cmsORAN/data1.csv` | CCO (throughput) dataset |
| `--es-file` | `data/cmsORAN/data2.csv` | ES (power) dataset |
| `--model` | `ann` | Surrogate backend: `ann` or `poly` |
| `--resolution` | `200` | Grid points per parameter axis |
| `--out` | `out` | Output directory for the figure |
| `--no-plot` | off | Skip figure generation |

## Tests

```bash
uv run pytest -q
uv run pytest --cov=surrogate_xapps --cov-report=term-missing
```

## Programmatic use

```python
from surrogate_xapps import CCO_CONFIG, ES_CONFIG, load_dataset
from surrogate_xapps.xapps import CCOxApp, ESxApp

Xc, yc, _ = load_dataset("data/cmsORAN/data1.csv", CCO_CONFIG.spec)
Xe, ye, _ = load_dataset("data/cmsORAN/data2.csv", ES_CONFIG.spec)

cco = CCOxApp(CCO_CONFIG).train(Xc, yc)
es = ESxApp(ES_CONFIG).train(Xe, ye)

print(cco.infer_action())   # {"xapp_id": "xApp_CCO", "requested_value": [p1, p2], ...}
print(es.infer_action())    # {"xapp_id": "xApp_ES",  "requested_value": [p1, p2], ...}
```

## Notes

- The cmsORAN files hold `p2` constant per file, so the second tuple axis is
  degenerate in the demo (still returned as requested).
- The ANN backend is the default because it fits the sharp Gaussian KPI surface
  far better than low-degree polynomial regression (R² ≈ 0.995 vs 0.53 on `data1`).
- `qos_threshold` semantics: for `max` objectives the KPI is satisfied when
  `predicted >= threshold`; for `min` objectives when `predicted <= threshold`.
