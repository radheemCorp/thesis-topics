# Implementation Plan: QACM CMC MVP

**Track ID:** `cmc-mvp_20261018`
**Status:** Draft
**Companion doc:** [spec.md](./spec.md)
**Method:** Conductor TDD lifecycle — Write Tests (Red) → Implement (Green) → Refactor → Coverage → Commit + Git Note → Record SHA. See `workflow.md`.

Legend: `[ ]` pending · `[~]` in progress · `[x]` complete (append `— <sha>`) · `[checkpoint: <sha>]` phase checkpoint.

---

## Phase 1 — `IQueryableXApp` Protocol & Adapter [checkpoint: 27f0b4a]

- [x] Task: Define `IQueryableXApp` protocol — e80ef06
  - [x] Write failing tests: mock xApp satisfying the protocol exposes `predict_at(p1) -> float`; structural check that CCO/ES instances satisfy it (via `typing.runtime_checkable` or duck-typing assertion).
  - [x] Implement `IQueryableXApp` protocol in `surrogate_xapps/cmc.py` (or a new `protocols.py`).
- [x] Task: Add `predict_at` adapter on `BaseXApp` — 77ca894
  - [x] Write failing tests: `predict_at(p1)` on a trained CCO/ES returns the surrogate-predicted KPI with `p2` held at the xApp's observed constant; matches `predict_kpi` on the equivalent feature row.
  - [x] Implement `predict_at` on `BaseXApp` (builds the `[p1, p2_const]` row and calls `predict_kpi`).
- [ ] Task: Conductor - User Manual Verification 'Phase 1' (Protocol in workflow.md)

## Phase 2 — `CMC` Heuristic & `MitigationResult` [checkpoint: 22b23c4]

- [x] Task: Define `MitigationResult` dataclass — 0ea2cc5
  - [x] Write failing tests: fields populated correctly; `improved()` reflects satisfaction counts.
  - [x] Implement `MitigationResult` dataclass.
- [x] Task: Implement `CMC.mitigate` discrete heuristic — d8a0948
  - [x] Write failing tests with **mock** xApps (analytic linear KPIs, known thresholds → hand-computed optimal `p*`); weight normalization to sum 1; deviation `d_i` and satisfaction `s_i` directions for both `max` and `min` objectives; cost `Σ w_i·d_i·ζ − (Σ s_i)²`; returns minimizing `p1`.
  - [x] Implement `CMC` class with `__init__(range, resolution, zeta=1e3)` and `mitigate(xapps)` in pure numpy.
- [x] Task: Modularly accept arbitrary xApp count — 1dd1cb4
  - [x] Write failing test: adding a 3rd mock xApp changes no CMC code (only the input list); CMC never imports CCO/ES concretely.
  - [x] Verify/refactor so CMC depends only on `IQueryableXApp`.
- [ ] Task: Conductor - User Manual Verification 'Phase 2' (Protocol in workflow.md)

## Phase 3 — Runner Integration & Before/After Demo [checkpoint: 8d0b6cb]

- [x] Task: Integrate CMC into the runner — f977181
  - [x] Write failing tests: demo entrypoint trains CCO+ES, detects conflict, runs `CMC.mitigate`, returns a result object with before/after satisfaction.
  - [x] Implement CMC runner path (extend `runner.py` or add `run_cmc_demo`).
- [x] Task: Before/after comparison report — 57b622a
  - [x] Write failing tests: report prints each xApp's requested vs. compromised KPI, QoS met?, and total #satisfied before vs. after.
  - [x] Implement the comparison report (CLI output).
- [x] Task: End-to-end verification on default datasets
  - [x] Run demo on `data/cmsORAN/data1.csv` & `data2.csv`; confirm `p*` lies between conflicting requests and `n_satisfied_after ≥ n_satisfied_before`.
- [ ] Task: Conductor - User Manual Verification 'Phase 3' (Protocol in workflow.md)

## Phase 4 — Documentation & Finalization

- [x] Task: Document CMC public API — a2a4836
  - [x] Add numpydoc docstrings to all new public classes/methods per `product-guidelines.md`.
  - [x] Write a run guide (like `docs/RUNNING_XAPPS.md`) for the CMC demo (`docs/RUNNING_CMC.md`).
- [x] Task: Final coverage & regression check
  - [x] `uv run pytest` green; coverage >80% across new CMC modules.
  - [x] Confirm existing surrogate-xapps tests still pass (no regression).
- [ ] Task: Conductor - User Manual Verification 'Phase 4' (Protocol in workflow.md)
