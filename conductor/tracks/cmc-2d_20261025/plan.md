# Implementation Plan: CMC Joint 2-D Mitigation

**Track ID:** `cmc-2d_20261025`
**Status:** Draft
**Companion doc:** [spec.md](./spec.md)
**Method:** Conductor TDD lifecycle — Write Tests (Red) → Implement (Green) → Refactor → Coverage → Commit + Git Note → Record SHA. See `workflow.md`.

Legend: `[ ]` pending · `[~]` in progress · `[x]` complete (append `— <sha>`) · `[checkpoint: <sha>]` phase checkpoint.

---

## Phase 1 — Baseline Characterization & Dimension-Aware Protocol

- [x] Task: Capture current 1-D behavior as regression fixtures — e30180a
  - [x] Write tests that pin `optimal_value`, per-xApp `satisfied_before`, and `improved()` for the cmsORAN CCO/ES demo and one synthetic 2-app run.
  - [x] Run the suite and record the baseline values in the test docstrings.
- [x] Task: Extend `IQueryableXApp` with `preferred_point` and 2-D `predict_at` — fa01883
  - [x] Write failing tests: a mock exposing `preferred_point` and `predict_at(p1, p2=None)` satisfies the protocol; a 1-arg mock still satisfies it.
  - [x] Update the protocol in `surrogate_xapps/cmc.py`; keep `preferred_value` as a deprecated property.
- [x] Task: Add `preferred_point` and `predict_at(p1, p2=None)` to `BaseXApp` — f9960fb
  - [x] Write failing tests: `predict_at(*x.preferred_point) ≈ x.infer_action()["predicted_kpi"]`; `p2=None` uses the preferred `p2`, not `ranges_` minimum; untrained xApp raises a clear error.
  - [x] Implement both members in `surrogate_xapps/xapps.py`.
- [x] Task: Update existing mocks to the extended protocol — 44d299d
  - [x] Update `_MockXApp` in `tests/test_cmc.py` to expose `preferred_point` and accept an optional `p2`.
  - [x] Confirm the pre-existing 20 CMC tests still pass.
- [x] Task: Conductor - User Manual Verification 'Phase 1' (Protocol in workflow.md) [checkpoint: 81ded6a]

### Phase 1 verification report (2026-10-25)

- **Scope:** `220108e..HEAD` — `surrogate_xapps/cmc.py`, `surrogate_xapps/xapps.py`, `tests/test_cmc.py`, `tests/test_cmc_baseline.py`.
- **Tests:** `uv run pytest -q` → 68 passed.
- **Coverage:** `uv run pytest --cov=surrogate_xapps` → 95% total (`cmc.py` 97%, `xapps.py` 89%).
- **Manual checks:** `predict_at(*preferred_point) == infer_action()["predicted_kpi"]` for CCO and ES; untrained `predict_at`/`preferred_point` raise `RuntimeError`; the synthetic 2-app scalar run reports 2/0 satisfied (the gap Phase 2 closes).
- **Deviations:** none.

## Phase 2 — Joint 2-D CMC Core & Exact Oracle

- [x] Task: Multi-axis range parsing and joint candidate grid — ed35b73
  - [x] Write failing tests: legacy `range=(lo, hi)` is treated as one axis; `ranges=[(lo1,hi1),(lo2,hi2)]` produces the Cartesian product; per-axis `resolution` is respected.
  - [x] Implement range normalization and `np.meshgrid(..., indexing="ij")` grid construction in `surrogate_xapps/cmc.py`.
- [x] Task: Joint 2-D sweep with the unchanged QACM cost — 0d9bebb
  - [x] Write failing tests with analytic 2-D mocks (known minimum): optimum is found; both `max` and `min` objectives work; weights are normalized.
  - [x] Implement the sweep and return `optimal_point`.
- [x] Task: `optimize_over` subset support — 5916113
  - [x] Write failing tests: `optimize_over=[0]` reproduces the 1-D result; `optimize_over=[1]` mitigates a `p2`-mediated conflict; non-optimized ICPs are held at each xApp's `preferred_point`.
  - [x] Implement subset selection and per-xApp fixed-coordinate queries.
- [x] Task: Dimension-aware `MitigationResult` — 31dfcef
  - [x] Write failing tests: `optimal_point` has the right arity; `optimal_value` returns index 0; `per_xapp` contains `preferred_point` and `predicted_at_preferred`; `satisfied_before` matches `predict_at(*preferred_point)`.
  - [x] Implement the dataclass changes with backward-compatible properties.
- [x] Task: `exact_mitigate` reference solver — afc103b
  - [x] Write failing tests: heuristic cost equals exact cost on small 2–3 xApp analytic instances; exact solver rejects empty xApps and unnormalizable weights.
  - [x] Implement the brute-force oracle in `surrogate_xapps/cmc.py` (numpy only).
- [x] Task: Deterministic tie-break and complexity guard — 961fd10
  - [x] Write failing tests: equal-cost plateaus resolve to the lexicographically smallest point; a grid above the configured cap raises/warns with an actionable message.
  - [x] Implement the tie-break rule and cap check.
- [x] Task: Conductor - User Manual Verification 'Phase 2' (Protocol in workflow.md) [checkpoint: PENDING]

### Phase 2 verification report (2026-10-25)

- **Scope:** `81ded6a..HEAD` — `surrogate_xapps/cmc.py`, `surrogate_xapps/xapps.py`, `tests/test_cmc.py`.
- **Tests:** `uv run pytest -q` → 93 passed.
- **Coverage:** 94% total (`cmc.py` 95%, `xapps.py` 90%).
- **Manual checks:** analytic 2-D max/min both give `p*=(2.0,0.0)` and `exact_mitigate` agrees; synthetic app1+app2 at `q=0.35` goes from `1/2` satisfied (1-D) to `2/2` satisfied (joint 2-D); equal-cost plateau picks the lexicographic smallest point; grid cap and NaN guard raise actionable `ValueError`s.
- **Performance:** 2 xApps at 128×128 (16,384 points) in ~0.05 s via `predict_many` batching.
- **Deviations:** none.

## Phase 3 — Runner, Report, and CLI

- [ ] Task: Dimension-aware report
  - [ ] Write failing tests: `print_cmc_report(result, actions=...)` prints `p* = (p1, p2)` and each xApp's requested point; no `nan` values for 3rd/4th xApps.
  - [ ] Refactor `print_cmc_report` to accept the full action list while keeping the legacy two-action call valid.
- [ ] Task: CLI joint/1-D selection and per-axis resolution
  - [ ] Write failing tests: `--optimize-over joint|p1|p2` changes the printed `p*` dimension; `--cmc-resolution` accepts one or two values.
  - [ ] Implement the arguments in `cli/cli.py` and thread them to `CMC`.
- [ ] Task: `run_cmc_demo` uses joint range intersection
  - [ ] Write failing tests: the demo's `p*` lies within the intersection of both xApps' observed ranges on each axis.
  - [ ] Update `surrogate_xapps/runner.py`.
- [ ] Task: Conductor - User Manual Verification 'Phase 3' (Protocol in workflow.md)

## Phase 4 — Synthetic Scenarios & Test Coverage

- [ ] Task: Dataset contract tests
  - [ ] Write `tests/test_synthetic.py`: load all four CSVs, assert ranges, known peak coordinates, and that the maxima match the metadata.
- [ ] Task: Direct 2-D conflict test
  - [ ] Write a test training app1/app2 and assert `p*` lies within the bounding box of their requested points and that both xApps are recorded.
- [ ] Task: Indirect conflict test
  - [ ] Write a test asserting `p2*` for `[app1, app2, app3]` differs from `[app1, app2]` and moves toward app3's peak.
- [ ] Task: Priority-weight test
  - [ ] Write a test: raising app3's weight moves `p2*` monotonically toward app3's preferred `p2`.
- [ ] Task: Threshold sweep test
  - [ ] Write a test: tightening QoS thresholds never increases `n_satisfied_after`; `improved()` reflects the before/after counts.
- [ ] Task: CLI integration tests
  - [ ] Write `tests/test_cli.py`: 2-, 3-, and 4-app invocations exit 0, print no `nan`, and print a `(p1, p2)` optimum.
- [ ] Task: Coverage gate
  - [ ] Run `uv run pytest --cov=surrogate_xapps --cov-report=term-missing`; ensure >80% on `cmc.py`, `xapps.py`, `runner.py`, and `cli/cli.py`.
- [ ] Task: Conductor - User Manual Verification 'Phase 4' (Protocol in workflow.md)

## Phase 5 — Documentation & Finalization

- [ ] Task: Update usage docs
  - [ ] Update `docs/usage/RUNNING_CMC.md` (2-D example), `docs/usage/CLI.md` (`--optimize-over`), and `docs/usage/SCENARIOS.md` (now covered by tests).
- [ ] Task: Document the paper-vs-extension distinction
  - [ ] Add a short note to `docs/usage/RUNNING_CMC.md` and `README.md`: the QACM paper is scalar; joint 2-D follows iter-3 FR-4.6 and is an explicit extension.
- [ ] Task: Performance benchmark
  - [ ] Measure mitigation latency for `N ∈ {64,128,256}` × `|X'| ∈ {2,3,4}`; record the table in the run guide; confirm the default stays within the 1 s budget.
- [ ] Task: Final regression and coverage check
  - [ ] `uv run pytest` green; existing 61 tests unchanged; coverage >80% on touched modules.
- [ ] Task: Conductor - User Manual Verification 'Phase 5' (Protocol in workflow.md)

---

## Appendix A — Target API Sketches

```python
# surrogate_xapps/cmc.py
@runtime_checkable
class IQueryableXApp(Protocol):
    xapp_id: str
    objective: str                 # "max" | "min"
    qos_threshold: float
    priority_weight: float
    preferred_point: tuple[float, ...]

    def predict_at(self, p1: float, p2: float | None = None) -> float: ...

@dataclass
class MitigationResult:
    optimal_point: tuple[float, ...]
    per_xapp: list[dict[str, Any]]
    n_satisfied_before: int
    n_satisfied_after: int

    @property
    def optimal_value(self) -> float:      # deprecated 1-D view
        return self.optimal_point[0]

class CMC:
    def __init__(
        self,
        ranges: Sequence[tuple[float, float]] | tuple[float, float],
        resolution: int | Sequence[int] = 128,
        zeta: float = 1e3,
        optimize_over: Sequence[int] | None = None,
    ) -> None: ...

    def mitigate(self, xapps: Sequence[IQueryableXApp]) -> MitigationResult: ...
    def exact_mitigate(self, xapps: Sequence[IQueryableXApp]) -> MitigationResult: ...
```

```python
# surrogate_xapps/xapps.py
class BaseXApp:
    @property
    def preferred_point(self) -> tuple[float, ...]:
        return tuple(float(v) for v in self.infer_action()["requested_value"])

    def predict_at(self, p1: float, p2: float | None = None) -> float:
        # p2=None -> preferred_point[1] (NOT ranges_ min)
        ...
```

## Appendix B — Test Matrix

| Scenario | xApps | ICPs | Assertion |
|---|---|---|---|
| Legacy 1-D | 2 mocks | p1 | `optimal_value` unchanged |
| Analytic 2-D | 2 mocks | p1,p2 | `optimal_point` == known minimum |
| Direct 2-D | app1, app2 | p1,p2 | `p*` between requests; both recorded |
| Indirect | app1, app2, app3 | p1,p2 | `p2*(3)` ≠ `p2*(2)` |
| Priority | app1, app2, app3 | p1,p2 | higher weight pulls optimum |
| Restrict axis | 2 mocks | `optimize_over=[0]` | equals 1-D result |
| Tie-break | 2 mocks | p1,p2 | deterministic smallest point |
| Exact oracle | 2–3 mocks | p1,p2 | heuristic cost == exact cost |
| Report | 4 actions | — | no `nan`; all IDs present |
| CLI | 2/3/4 apps | p1,p2 | exit 0; `(p1, p2)` printed |

## Appendix C — Risks

| Risk | Impact | Mitigation |
|---|---|---|
| 2-D sweep latency | Medium | Default `N=128`; per-axis override; benchmark in Phase 5 |
| Surrogate fit error dominates | Medium | Compare poly vs ANN in tests; document R²; default `ann` |
| Backward-compat break in protocol | High | Keep `preferred_value`; 1-arg `predict_at`; regression tests |
| Ambiguity of "preferred" for non-optimized ICPs | Medium | Explicit: hold at each xApp's own `preferred_point` |
| Tie-break instability | Low | Deterministic lexicographic rule + test |

## Appendix D — Compatibility & Complexity

- **1-D callers:** `CMC((lo, hi), resolution)` still works; `optimal_value` still readable.
- **Protocol mocks:** 1-arg `predict_at` remains valid; the CMC calls `predict_at(p1)` when only one axis is optimized.
- **Cost:** `O(N1·N2·|X'|)` evaluations, each an ANN forward pass. At `N=128`, `|X'|=4` → 65,536 predictions; benchmark in Phase 5.
- **Memory:** build grids per axis; avoid materializing `N^d × d` when `d > 2`.
