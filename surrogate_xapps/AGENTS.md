# AGENTS.md — surrogate_xapps/

Scope: the core package. All production logic lives here.

## Modules
- `config.py` — `DatasetSpec`, `XAppConfig`, `CMSORAN_SPEC`, `QACM_SPEC`, `CCO_CONFIG`, `ES_CONFIG`.
- `data_loader.py` — `load_dataset`, `load_threshold`; enforces `Input1,Input2,Output`.
- `surrogates.py` — `SurrogateModel` ABC, `PolyRegSurrogate`, `ANNSurrogate`, `build_model`.
- `xapps.py` — `BaseXApp`, `CCOxApp`, `ESxApp`, `validate_action`; template method `infer_action`.
- `cmc.py` — `IQueryableXApp` protocol, `CMC`, `MitigationResult`; grid heuristic + `exact_mitigate` oracle.
- `runner.py` — `detect_conflict`, `run`, `run_cmc_demo`, `print_cmc_report`, `main`.
- `plot_utils.py` — `plot_kpi_curves`, `_curve`.

## Rules
- New xApp = subclass `BaseXApp` + `XAppConfig`; do **not** change `CMC` to special-case it.
- Keep `CMC.mitigate` as the production path; `exact_mitigate` stays a test oracle only.
- Joint 2-D bargaining uses `(p1, p2)`; scalar behaviour must remain backward compatible.
- Public API changes require updating `__init__.py` exports and `docs/usage/`.
- Type hints + numpydoc docstrings on public classes/functions.
