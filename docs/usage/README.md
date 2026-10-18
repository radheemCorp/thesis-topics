# Usage Documentation

This directory contains usage guides for the surrogate xApps and CMC.

## Contents

- [RUNNING_XAPPS.md](RUNNING_XAPPS.md) — Run CCO and ES surrogate xApps (pre-mitigation)
- [RUNNING_CMC.md](RUNNING_CMC.md) — Run the QACM CMC demo (mitigation)
- [CLI.md](CLI.md) — CLI for running scenarios with arbitrary datasets/xApps
- [SYNTHETIC_DATASETS.md](SYNTHETIC_DATASETS.md) — Synthetic 2D datasets (peaks, ranges, layout)
- [SCENARIOS.md](SCENARIOS.md) — Direct vs indirect conflict scenarios and test guidance

## Quick Start

### CMC Demo (2-app)
```bash
cd /home/radr/tuilm/thesis-topics
uv run python -c "
from surrogate_xapps.runner import run_cmc_demo, print_cmc_report
result = run_cmc_demo(resolution=100, cmc_resolution=300)
print_cmc_report(result)
"
```

### CLI (Direct + Indirect)
```bash
cd /home/radr/tuilm/thesis-topics
uv run python cli/cli.py \
  --datasets data/synthetic/xapp1_direct.csv data/synthetic/xapp2_direct.csv data/synthetic/xapp3_indirect.csv \
  --xapps app1,app2,app3 --qos 0.2 0.2 0.2 --weights 0.33 0.33 0.34
```
