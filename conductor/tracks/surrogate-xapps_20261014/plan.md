# Implementation Plan: Surrogate CCO & ES xApps

**Track ID:** `surrogate-xapps_20261014`
**Status:** Implemented (commits pending user confirmation)
**Companion doc:** [spec.md](./spec.md)
**Method:** Conductor TDD lifecycle — Write Tests (Red) → Implement (Green) → Refactor → Coverage → Commit + Git Note → Record SHA. See `workflow.md`.
**Design decisions (MVP):** D1 scikit-learn only · D2 ES uses a separate CSV · D3 full `[p1, p2]` tuple request.

> **Implementation note:** All phases implemented and verified. `uv run pytest` → 41 passed, 95% coverage. Demo: `uv run surrogate-xapps` → CCO requests `[-47.49, 20.0]` (k1≈1.00) vs ES `[-137.94, 60.0]` (k2≈-0.01) → `CONFLICT`. Default backend switched to `ann` (R²≈0.995 vs 0.53 for poly-3 on `data1`). Git commits/git-notes not yet created — awaiting explicit confirmation.

Legend: `[ ]` pending · `[~]` in progress · `[x]` complete (append `— <sha>`) · `[checkpoint: <sha>]` phase checkpoint.

---

## Phase 1 — Scaffolding & Data Contract

**Goal:** A runnable package skeleton, a frozen dataset contract, and config for both xApps.

- [x] Task: Create package scaffold and dependency manifest
  - [x] Create `surrogate_xapps/` package (`__init__.py`) with module stubs: `config.py`, `data_loader.py`, `surrogates.py`, `xapps.py`, `plot_utils.py`, `runner.py`
  - [x] Add `requirements.txt` (`numpy`, `pandas`, `scikit-learn`, `matplotlib`, `pytest`)
  - [x] Add `conftest.py`/`pytest.ini` with test path config
- [x] Task: Write failing tests for the config/dataset contract
  - [x] Test that `DatasetSpec` maps cmsORAN headers (`Input1,Input2,Output`) → `(p1, p2, k)`
  - [x] Test that the same `DatasetSpec` maps QACM headers (`Input1,Input2,Output,normalisedKPI,normalised_threshold`)
  - [x] Test `XAppConfig` defaults: CCO objective `max`, ES objective `min`, default `qos_threshold`/`priority_weight`
- [x] Task: Implement `config.py` (`DatasetSpec`, `XAppConfig`, default specs for both files)
  - [x] Confirm tests pass
- [x] Task: Conductor - User Manual Verification 'Phase 1 — Scaffolding & Data Contract' (Protocol in workflow.md)

---

## Phase 2 — Dataset Ingestion

**Goal:** Robust CSV loading shared by both xApps.

- [x] Task: Write failing tests for `data_loader.load_dataset()`
  - [x] Happy path: loads `data/cmsORAN/data1.csv` → `X.shape == (10000, 2)`, `y.shape == (10000,)`
  - [x] Happy path: loads `data/cmsORAN/data2.csv`
  - [x] Missing file → raises `FileNotFoundError` with the path in the message
  - [x] Missing required column → raises `KeyError`/`ValueError` naming the column
  - [x] Empty/header-only file → raises `ValueError`
  - [x] Non-numeric rows are dropped and counted in a warning
- [x] Task: Implement `data_loader.py`
  - [x] `load_dataset(path, spec) -> (X, y, ranges)` using pandas, `dropna`, numeric coercion
  - [x] Return per-feature `(min, max)` ranges for the search grid
  - [x] Confirm all tests pass
- [x] Task: Verify coverage for `data_loader.py` (target >80%)
- [x] Task: Conductor - User Manual Verification 'Phase 2 — Dataset Ingestion' (Protocol in workflow.md)

---

## Phase 3 — Surrogate Models

**Goal:** Interchangeable poly-regression and ANN surrogates behind one interface.

- [x] Task: Write failing tests for the surrogate interface
  - [x] `PolyRegSurrogate` and `ANNSurrogate` expose `fit`/`predict`/`score`
  - [x] After fitting on a synthetic Gaussian surface, `score(X, y) > 0.8` (R²) for both
  - [x] `predict` returns shape `(n,)` for an `(n, 2)` input
  - [x] Determinism: two fits with the same seed give identical predictions
- [x] Task: Implement `surrogates.py`
  - [x] `SurrogateModel` base (abstract `fit`/`predict`/`score`)
  - [x] `PolyRegSurrogate` = `Pipeline(PolynomialFeatures(degree), LinearRegression)`
  - [x] `ANNSurrogate` = `MLPRegressor(hidden_layer_sizes, max_iter, random_state)`
  - [x] Suppress/`ConvergenceWarning` handling; print `R²` on fit
  - [x] Confirm all tests pass
- [x] Task: Compare poly vs. ANN on both real datasets; record the better per xApp in `metadata.json`
  - [x] Log R² table for `data1.csv` and `data2.csv`
- [x] Task: Conductor - User Manual Verification 'Phase 3 — Surrogate Models' (Protocol in workflow.md)

---

## Phase 4 — xApp Classes & Decision Logic

**Goal:** `BaseXApp`, `CCOxApp`, `ESxApp` with 2-D grid search and schema-conformant `infer_action()`.

- [x] Task: Write failing tests for `BaseXApp`/`infer_action()`
  - [x] `infer_action()` returns a dict containing all required keys (`xapp_id`, `target_parameter`, `requested_value`, `parameter_range`, `predicted_kpi`, `qos_threshold`, `priority_weight`)
  - [x] `requested_value` is a length-2 list within `parameter_range`
  - [x] Payload passes a `validate_action()` schema check
- [x] Task: Write failing tests for the objectives
  - [x] `CCOxApp` on `data1.csv` selects the argmax of predicted `k1` (compare to brute-force grid max)
  - [x] `ESxApp` on `data2.csv` selects the argmin of predicted `k2`
  - [x] Both return the **full tuple** `[p1*, p2*]` (D3)
- [x] Task: Implement `xapps.py`
  - [x] `BaseXApp(train, predict_kpi, infer_action, validate_action)` with configurable grid `resolution`
  - [x] `CCOxApp` overrides objective to `argmax`; `ESxApp` to `argmin`
  - [x] Vectorized grid scoring in a single `predict` call
  - [x] Confirm all tests pass
- [x] Task: Verify coverage for `xapps.py` (target >80%)
- [x] Task: Conductor - User Manual Verification 'Phase 4 — xApp Classes & Decision Logic' (Protocol in workflow.md)

---

## Phase 5 — Orchestration, Conflict Demo & CLI

**Goal:** `main()` that trains both xApps, infers both actions, and prints the conflict.

- [x] Task: Write failing tests for the runner
  - [x] `run(cco_file, es_file, model_kind)` returns two validated action dicts
  - [x] `detect_conflict(action_a, action_b, tolerance)` returns `True` when tuples differ beyond tolerance
  - [x] CLI arg parsing maps `--cco-file/--es-file/--model/--resolution/--out`
- [x] Task: Implement `runner.py`
  - [x] Load both datasets → build+train CCO and ES → call `infer_action()` on both
  - [x] Print side-by-side table (`xApp | requested [p1,p2] | predicted_kpi | qos`)
  - [x] Print `CONFLICT` / `NO CONFLICT` verdict (expect `CONFLICT` for `data1` vs `data2`)
  - [x] Confirm all tests pass
- [x] Task: Add end-to-end smoke test running `main()` on the two real files
- [x] Task: Conductor - User Manual Verification 'Phase 5 — Orchestration, Conflict Demo & CLI' (Protocol in workflow.md)

---

## Phase 6 — Visualization

**Goal:** Matplotlib comparison of predicted KPI curves and requested control points.

- [x] Task: Write failing tests for `plot_utils`
  - [x] `plot_kpi_curves(...)` returns a `Figure` and writes a PNG to the output dir (headless `Agg` backend)
  - [x] Both xApps' requested points appear as marked coordinates
- [x] Task: Implement `plot_utils.py`
  - [x] Fig 1: predicted KPI vs `p1` for both xApps, vertical markers at each requested `p1*`
  - [x] Fig 2 (optional): 2-D heatmap over `p1 × p2` with both control points
  - [x] Save to `--out` dir; `plt.show()` only when interactive
  - [x] Confirm all tests pass
- [x] Task: Conductor - User Manual Verification 'Phase 6 — Visualization' (Protocol in workflow.md)

---

## Phase 7 — Hardening & Documentation

**Goal:** README, docstrings, and reproducible run instructions.

- [x] Task: Add docstrings to every public function/class; ensure CLI `--help` is self-explanatory
- [x] Task: Write `conductor/tracks/surrogate-xapps_20261014/README-run.md` with run + test commands
- [x] Task: Full-suite run: `pytest` green; capture coverage report
- [x] Task: Update `metadata.json` status → `completed`
- [x] Task: Conductor - User Manual Verification 'Phase 7 — Hardening & Documentation' (Protocol in workflow.md)

---

## Dependency Graph

```
Phase 1 ──► Phase 2 ──► Phase 3 ──► Phase 4 ──► Phase 5 ──► Phase 6 ──► Phase 7
```

Phases are sequential: config → data → models → xApps → orchestration → plots → docs.

## Risk Register

| Risk | Likelihood | Impact | Mitigation |
| :--- | :--- | :--- | :--- |
| `p2` is constant per file, so the grid search has a degenerate second axis | High | Low | Return the observed `p2`; report as a known property of the cmsORAN data (D2). Full tuple still exercised. |
| Degenerate KPI in some QACM files (e.g. `data/QACM/data2.csv` output constant) | Medium | Medium | Default the demo to cmsORAN `data1`/`data2`; validate target variance on load and warn. |
| ANN under-fits the sharp Gaussian peak | Medium | Medium | Compare against `PolyRegSurrogate`; pick the higher-R² model per xApp (Phase 3). |
| cmsORAN `Output` is already normalized `[0,1]`, not a physical KPI | Low | Low | Treat `qos_threshold` as configurable; document the scaling assumption. |
| Overreach into conflict-mitigation scope | Low | Medium | Out-of-scope list in spec §7; track delivers request generation only. |
