# CLI Usage

The `cli/cli.py` tool runs CMC scenarios on synthetic or custom datasets.

## Basic Usage

```bash
cd /home/radr/tuilm/thesis-topics

uv run python cli/cli.py \
  --datasets data/synthetic/xapp1_direct.csv data/synthetic/xapp2_direct.csv \
  --xapps app1,app2 \
  --qos 0.8 0.8 --weights 0.5 0.5
```

## Arguments

- `--datasets`: One or more CSV files in cmsORAN layout (`Input1,Input2,Output`)
- `--xapps`: Comma-separated xApp names. Supported: `cco`, `es`, `app1`, `app2`, `app3`, `app4`
- `--qos`: Per-xApp QoS thresholds (same order as xapps)
- `--weights`: Per-xApp priority weights (same order as xapps)
- `--cmc-resolution`: CMC grid resolution (default: 300)
- `--model`: Surrogate backend `ann` or `poly` (default: `ann`)
- `--resolution`: xApp grid resolution (default: 200)

## Examples

### Direct conflict (2-app)
```bash
uv run python cli/cli.py \
  --datasets data/synthetic/xapp1_direct.csv data/synthetic/xapp2_direct.csv \
  --xapps app1,app2 --qos 0.4 0.4 --weights 0.5 0.5
```

### Direct + Indirect (3-app)
```bash
uv run python cli/cli.py \
  --datasets data/synthetic/xapp1_direct.csv data/synthetic/xapp2_direct.csv data/synthetic/xapp3_indirect.csv \
  --xapps app1,app2,app3 --qos 0.2 0.2 0.2 --weights 0.33 0.33 0.34
```

### Direct + Indirect + Extra (4-app)
```bash
uv run python cli/cli.py \
  --datasets data/synthetic/xapp1_direct.csv data/synthetic/xapp2_direct.csv data/synthetic/xapp3_indirect.csv data/synthetic/xapp4_extra.csv \
  --xapps app1,app2,app3,app4 --qos 0.1 0.1 0.1 0.1 --weights 0.25 0.25 0.25 0.25
```

## Notes

- The CLI uses the existing CMC (`surrogate_xapps.cmc.CMC`) and xApp infrastructure.
- For N>2, the report shows all xApps; `req_p1` may be `nan` if not in the original 2-app display mapping (the CLI still computes correct mitigation).
- All xApps default to `max` objective in the CLI mapping except `es` (min). Synthetic datasets are max-objective peaks.
