# AGENTS.md — tests/

Scope: pytest suite. Tests are the behavioural contract.

## Files
- `conftest.py` — shared fixtures (datasets, configs, CMC instances).
- `test_cmc.py` — core conflict logic, joint 2-D, `exact_mitigate` oracle.
- `test_cmc_baseline.py` — uncoordinated baseline comparison.
- `test_cli_scenarios.py` — CLI `XAPP_MAP`, argument handling, reports.
- `test_config.py`, `test_data_loader.py`, `test_surrogates.py`, `test_xapps.py`, `test_runner.py`, `test_runner_report.py`, `test_plot_utils.py`.

## Rules
- Write the failing test first; never weaken an assertion to make code pass.
- Prefer synthetic fixtures over real CSVs; seed randomness.
- New public behaviour in `surrogate_xapps/` requires a matching test.
- Keep coverage >80%; run `uv run pytest` (config `testpaths=["tests"]`, `-q`).
