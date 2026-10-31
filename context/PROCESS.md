# PROCESS

1. **TDD** — write/adjust the failing test in `tests/` first, then implement.
2. **Data-first** — regenerate synthetic inputs with `scripts/gen_synthetic_2d.py` / `gen_timeseries.py` before tuning CMC or surrogates.
3. **Verify** — `uv run pytest` (target >80%); run the relevant CLI scenario from `docs/usage/SCENARIOS.md`.
4. **Document** — update `docs/usage/` and the affected `README.md`; record deviations from QACM in the docstring or `docs/`.
5. **Commit hygiene** — no secrets; keep `data/` generated artifacts reproducible from scripts.
