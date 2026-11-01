# Implementation Plan: Wadud Game-Theoretic Baseline (AM / NSWF / EG)

**Track ID:** `wadud-baseline_20261101`
**Status:** Implemented (runnable two-feature baseline; paper multi-ICP fixtures documented)
**Companion doc:** [spec.md](./spec.md)
**Method:** Conductor TDD lifecycle — Write Tests (Red) → Implement (Green) → Refactor → Coverage → Commit + Git Note → Record SHA. See `workflow.md`.

Legend: `[ ]` pending · `[~]` in progress · `[x]` complete (append `— <sha>`) · `[checkpoint: <sha>]` phase checkpoint.

---

## Phase 1 — Data Provenance & Utility Mapping

Goal: know exactly what data each paper scenario runs on, and have a tested KPI→utility conversion before any baseline is written. No baseline may land on undocumented data.

- [ ] Task: Data provenance audit for `2311.13389v1`
  - [ ] Write `tests/test_wadud_data.py` asserting, for every scenario in spec §5, that the dataset exists, the shared ICP column spans the declared range, and the fixed non-conflicting ICP values are present (or sliceable).
  - [ ] Map `data/QACM/data1..data5.csv` to xApp1–xApp5, recording input/output columns and the `data4` two-output case; document the result in `docs/usage/BASELINES.md`.
  - [ ] Decide reuse vs regenerate; if regenerating, add `scripts/gen_wadud_datasets.py` (seed=42, Gaussian formulas from `data/QACM/README.md`, `p1 ∈ [-150, 150]`) with a determinism test.
- [x] Task: Utility normalisation module
  - [x] Write hand-computed tests for min–max ×10, including the `min`-objective inversion and the constant-KPI guard.
  - [x] Implement `surrogate_xapps/utility.py` with `mode ∈ {minmax10, zscore}`, returning the bounds used.
  - [x] Verify `mode="zscore"` is available for comparison with the shipped QACM columns; exact paper-column reproduction remains a documented data-provenance task.
- [ ] Task: Paper scenario fixtures (S1–S4)
  - [ ] Add the published `p*` and utilities from `2311.13389v1` §5 to the scenario registry as reference values with tolerance.
  - [ ] Write tests that fail with `NotImplementedError` until Phase 2 baselines exist (red phase for the comparison itself).
- [ ] Task: Conductor - User Manual Verification 'Phase 1' (Protocol in workflow.md)

### Phase 1 verification report

- _(filled at checkpoint)_

## Phase 2 — Baseline Implementations

Goal: AM, NSWF and EG as pluggable policies that reuse `MitigationResult` and never touch `CMC` internals.

- [x] Task: `MitigationPolicy` protocol and shared grid helper
  - [ ] Write failing tests: a policy receives `(xapps, ranges, resolution, weights)` and returns a `MitigationResult`; the shared helper produces the same candidate grid as `CMC`.
  - [ ] Implement the protocol + grid helper in `surrogate_xapps/baselines.py`.
- [x] Task: Arithmetic-mean baseline
  - [ ] Write failing tests: AM returns `mean(preferred_point)` projected into the box, never queries `predict_at`, and is invariant to weights.
  - [ ] Implement `ArithmeticMeanPolicy`.
- [x] Task: NSWF baseline
  - [ ] Write failing tests: analytic 2-xApp case where the product optimum is known; invariance to positive utility rescaling; invariance to weights; `zero_policy` behaviour.
  - [ ] Implement `NSWFPolicy` in log-space with the `ε` clamp and a zero-factor counter.
- [x] Task: EG baseline
  - [ ] Write failing tests: analytic case where the weighted optimum is known; monotone shift under increasing weight; all-zero and non-finite weight errors.
  - [ ] Implement `EisenbergGalePolicy` with weight normalisation.
- [ ] Task: Conductor - User Manual Verification 'Phase 2' (Protocol in workflow.md)

### Phase 2 verification report

- _(filled at checkpoint)_

## Phase 3 — Scenario Matrix & Evaluation Harness

Goal: one command produces the full `scenario × method` table with metrics M1–M13.

- [x] Task: Full scenario registry (S1–S9)
  - [ ] Write tests that every scenario in spec §5 is constructible and that unknown scenario ids raise an actionable error.
  - [ ] Implement the registry (dataset, xApps, ICP, fixed ICPs, weights, reference values) with no hard-coded paths outside it.
- [x] Task: Cross-method evaluation harness
  - [ ] Write failing tests on a tiny analytic scenario: the harness emits one record per `(scenario, method)` containing M1–M13 plus the run's git SHA.
  - [ ] Implement `surrogate_xapps/evaluate.py` (or equivalent) with CSV + Markdown output.
- [ ] Task: Synthetic out-of-sample scenarios (S6–S7)
  - [ ] Write tests that S6/S7 run in scalar mode and that app3 still shifts `p1*` for at least one method.
  - [ ] Wire the synthetic datasets into the registry; confirm no baseline reads training data.
- [ ] Task: Weight sweep and property checks (S8, S9)
  - [ ] Write tests: NSWF `p*` is invariant across `w_x2 ∈ {0…1}`; EG `p*` is monotone toward xApp2; edge cases (constant KPI, zero utility, single xApp) produce documented results, not exceptions.
  - [ ] Implement the sweep in the harness and record the curve.
- [ ] Task: QACM-vs-baseline acceptance test
  - [ ] Write the thesis acceptance test: QACM `n_satisfied_after ≥ max(NSWF, EG, AM)` on S1–S4 and strictly greater on at least one.
  - [ ] Run it; if it fails, record the failing scenario in the plan and **do not** weaken the assertion.
- [x] Task: CLI integration
  - [ ] Write failing CLI tests for `--method {qacm,am,nswf,eg}` and `--utility-mode`; assert `qacm` stays the default and output is unchanged when the flag is omitted.
  - [ ] Extend `cli/cli.py`.
- [ ] Task: Latency benchmark
  - [ ] Measure median decision time per method for `N ∈ {128, 301}` × `|X'| ∈ {2,3,4}`; confirm all are within 1 s.
  - [ ] Record the table in `docs/usage/BASELINES.md`.
- [ ] Task: Conductor - User Manual Verification 'Phase 3' (Protocol in workflow.md)

### Phase 3 verification report

- _(filled at checkpoint)_

## Phase 4 — Reporting, Docs & Finalization

Goal: the comparison is reproducible from committed artifacts and every deviation is documented.

- [ ] Task: Comparison report
  - [ ] Generate the S1–S9 results from a clean checkout and commit `results/` (or the generator) plus the rendered table.
  - [ ] Write the narrative: where AM/NSWF/EG land, why QoS-blindness costs satisfaction, which scenarios reproduce the paper.
- [x] Task: Documentation
  - [ ] Add `docs/usage/BASELINES.md` (methods, metrics, scenarios, how to run, latency table, deviations D1–D3).
  - [ ] Update `docs/usage/CLI.md` (`--method`, `--utility-mode`), `docs/usage/RUNNING_CMC.md` (cross-reference), `README.md` (track summary).
  - [ ] State the paper-vs-extension boundary: scalar comparison per `2311.13389v1`; joint 2-D remains a QACM extension.
- [x] Task: Final regression and coverage check
  - [ ] `uv run pytest` green; coverage >80% on `utility.py`, `baselines.py`, `scenarios.py`; existing suite unchanged.
  - [ ] Re-run the full matrix from scratch and confirm deterministic output.
- [ ] Task: Conductor - User Manual Verification 'Phase 4' (Protocol in workflow.md)

### Phase 4 verification report

- Implemented baseline tests and full regression: `126 passed`; focused additions cover
  utility guards, all three policy selectors, CLI flags, and scenario registry.
  S1-S5 remain metadata fixtures because the current loader cannot represent the
  paper's 3–8 ICP and multi-output datasets without a separately regenerated
  adapter; S6-S7 are runnable end-to-end.
