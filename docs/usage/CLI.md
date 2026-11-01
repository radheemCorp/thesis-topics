# CLI Usage

The `cli/cli.py` tool runs CMC scenarios on synthetic or custom datasets. It
trains one surrogate per dataset, asks each xApp for its preferred point, and
mitigates the conflict with the QACM CMC.

## Basic Usage

```bash
cd /home/radr/tuilm/thesis-topics

uv run python cli/cli.py \
  --datasets data/synthetic/xapp1_direct.csv data/synthetic/xapp2_direct.csv \
  --xapps app1,app2 \
  --qos 0.4 0.4 --weights 1 1
```

```
QACM Conflict Mitigation — before/after QoS
============================================================
Optimal compromise p* = (p1=-91.94, p2=46.45)

xApp         requested                  kpi@req    kpi@p*     thr  sat_before  sat_after
----------------------------------------------------------------------------------------
xApp1        [-40.32, 18.06]              0.896     0.411    0.40        True       True
xApp2        [-150.00, 80.00]             0.821     0.391    0.40        True      False

Satisfied before: 2/2  ->  Satisfied after: 1/2
NOT IMPROVED
```

## Arguments

- `--datasets`: One or more CSV files in cmsORAN layout
  (`Input1,Input2,Output`)
- `--xapps`: Comma-separated xApp names. Supported: `cco`, `es`, `app1`,
  `app2`, `app3`, `app4`
- `--qos`: Per-xApp QoS thresholds (same order as xapps)
- `--weights`: Per-xApp priority weights (same order as xapps, each in `[0, 1]`)
- `--cmc-resolution`: CMC points per axis. One value broadcasts to every axis;
  two values set `p1` and `p2` independently (default: `300`)
- `--optimize-over {joint,p1,p2}`: ICP subset to sweep (default: `joint`).
  With `p1` or `p2`, only that coordinate is printed and the other ICP is
  fixed at each xApp's preferred value.
- `--model`: Surrogate backend `ann` or `poly` (default: `ann`)
- `--resolution`: xApp grid resolution (default: 200)
- `--method {qacm,am,nswf,eg}`: mitigation selector (default: `qacm`)
- `--utility-mode {minmax10,zscore}`: utility normalization for NSWF/EG

## Examples

### Direct conflict (2-app, joint 2-D)
```bash
uv run python cli/cli.py \
  --datasets data/synthetic/xapp1_direct.csv data/synthetic/xapp2_direct.csv \
  --xapps app1,app2 --qos 0.4 0.4 --weights 1 1 \
  --cmc-resolution 32 --resolution 32
```

### Direct + Indirect (3-app, joint 2-D)
```bash
uv run python cli/cli.py \
  --datasets data/synthetic/xapp1_direct.csv data/synthetic/xapp2_direct.csv data/synthetic/xapp3_indirect.csv \
  --xapps app1,app2,app3 --qos 0.4 0.4 0.8 --weights 1 1 1 \
  --cmc-resolution 32 --resolution 32
```

Adding `app3` pulls `p2*` from `46.45` to `43.87`, toward its own `p2` peak at
`40`.

### Direct + Indirect + Extra (4-app, joint 2-D)
```bash
uv run python cli/cli.py \
  --datasets data/synthetic/xapp1_direct.csv data/synthetic/xapp2_direct.csv data/synthetic/xapp3_indirect.csv data/synthetic/xapp4_extra.csv \
  --xapps app1,app2,app3,app4 --qos 0.4 0.4 0.4 0.4 --weights 1 1 1 1
```

### Scalar views and per-axis resolution
```bash
# Optimize p1 only (p2 fixed at each xApp's preference)
uv run python cli/cli.py \
  --datasets data/synthetic/xapp1_direct.csv data/synthetic/xapp2_direct.csv \
  --xapps app1,app2 --qos 0.4 0.4 --optimize-over p1

# Optimize p2 only, with 64 p1 points and 128 p2 points
uv run python cli/cli.py \
  --datasets data/synthetic/xapp1_direct.csv data/synthetic/xapp2_direct.csv \
  --xapps app1,app2 --qos 0.4 0.4 \
  --optimize-over p2 --cmc-resolution 64 128
```

## Notes

- The CLI uses `surrogate_xapps.cmc.CMC` and the xApp infrastructure; no
  scenario-specific CMC code exists.
- Every xApp appears in the report with its real requested point. Earlier
  versions printed `nan` for the 3rd+ xApp; that fallback is gone.
- All xApps default to `max` objective in the CLI mapping except `es` (min).
  The synthetic datasets are max-objective peaks.
- `--weights` values are normalized by the CMC, so only their ratios matter.
