# AGENTS.md — cli/

Scope: `cli/cli.py` — argparse front-end that runs CMC scenarios on synthetic datasets.

## Rules
- Keep `XAPP_MAP` the single place mapping names (`cco`, `es`, `app1`–`app4`) to `(BaseXApp subclass, XAppConfig)`.
- Base configs on `CMSORAN_SPEC` / `QACM_SPEC`; any per-scenario override must be explicit and documented.
- CLI delegates all logic to `surrogate_xapps` (`CMC`, `load_dataset`, `detect_conflict`, `print_cmc_report`); no duplicate math here.
- Args mirror `runner.build_parser` where applicable (`--datasets`, `--xapps`, `--qos`, `--weights`, `--model`, `--resolution`).
- Exit non-zero on validation failure; print actionable errors to stderr.

## Verify
`uv run python cli/cli.py --datasets data/synthetic/*.csv --xapps cco,es`
