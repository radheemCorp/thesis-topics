# Reproduction Report: Wadud et al. vs QACM

**Scope:** fidelity of the reimplementation in this repository, the data we added,
and what remains outstanding.
**Track:** `conductor/tracks/wadud-baseline_20261101`
**Papers:**

| Ref | Title | Authors | Year |
|---|---|---|---|
| `2311.13389v1` | *Conflict management in the near-RT-RIC of Open RAN: A game theoretic approach* | A. Wadud, F. Golpayegani, N. Afraz | 2023 |
| `2405.07324v2` | *QACM: QoS-Aware xApp Conflict Mitigation in Open RAN* | A. Wadud, F. Golpayegani, N. Afraz | 2024 |

Both papers share the same authors, so the comparison is not an adversarial
reimplementation: QACM is the authors' own successor to `2311.13389v1` and
positions itself explicitly against NSWF/EG.

**Companion:** how the papers describe their inputs (`p1 … p8`), why almost none
of them is named, and what a real testbed would have to measure for each xApp is
in [`ICP-MAPPING-AND-TESTBED-DATA.md`](ICP-MAPPING-AND-TESTBED-DATA.md).

---

## 1. The problem both papers address

Open RAN disaggregates the RAN into independently developed xApps running on the
Near-RT-RIC. Because those xApps share control parameters, they issue
incompatible requests. Both papers use the same three-way taxonomy:

| Conflict | Definition | Paper example |
|---|---|---|
| **Direct** | Two or more xApps request different values for the same IPC | ES and CCO both set transmission power |
| **Indirect** | One xApp's parameter change moves another xApp's operating domain | MLB adjusts tilt, MRO's handover boundary shifts |
| **Implicit** | Two xApps optimise different KPIs and degrade each other through a hidden coupling | QoS xApp and handover xApp interfere without a shared parameter |

The consequence is KPI degradation and SLA/QoS violations. Both papers reject
"winner-takes-all" prioritisation: discarding one xApp's request loses
collective efficiency, and vendor xApps are black boxes that will not share
training data.

### Where QACM departs from `2311.13389v1`

| | `2311.13389v1` (Wadud) | `2405.07324v2` (QACM) |
|---|---|---|
| Objective | Maximise aggregate utility (NSWF or weighted EG) | Minimise weighted QoS deviation **and** maximise the number of xApps meeting their own threshold |
| QoS awareness | None — aggregate utility can hide a starved xApp | Per-xApp satisfaction term `− (Σ s_i)²` with big-M constraints |
| Utility scaling | Min–max onto `[0, 10]` | z-score (chosen to preserve Gaussian shape) |
| Predictor | Polynomial regression blocks | ANN (4×128, tanh, dropout 0.2, Adam, MSE) benchmarked against polynomial regression |
| Solver | Closed-form/grid over candidate `x` | Grid heuristic, `O(N · |X'|)` |
| Weights | MNO-assigned, `Σ w_i = 1` | Supplied by a Conflict Supervision xApp |

That difference is the entire thesis-relevant claim: **QACM should satisfy at
least as many xApps as NSWF/EG, and strictly more somewhere.** Our testbed exists
to test that claim on a shared substrate.

---

## 2. How each paper approached it

### 2.1 `2311.13389v1` (Wadud)

1. Model each xApp as a regression block mapping ICPs to a KPI, trained on
   synthetic Gaussian surfaces.
2. Normalise KPIs to a common utility:

   ```
   u_i(x) = (1/|J_i|) · Σ_j ( (o_ij(x) − o_ij^min) / (o_ij^max − o_ij^min) ) × 10
   ```

3. Have the CMC bargain over a candidate `x` (one shared ICP), asking each xApp
   for its range, weight and predicted KPI.
4. Select `x*` by one of three rules:

   | Method | Rule | Priority support |
   |---|---|---|
   | AM | `x* = mean_i(p_i^req)` | no |
   | NSWF | `x* = argmax_x Π_i u_i(x)` | no |
   | EG | `x* = argmax_x Σ_i w_i u_i(x)`, `Σ w_i = 1` | yes |

5. Evaluate on direct (non-priority and priority), indirect and implicit
   scenarios, comparing AM against NSWF/EG.

### 2.2 `2405.07324v2` (QACM)

1. Same CMS framing (PMon → CDC → CMC), plus a Conflict Supervision xApp that
   assigns weights.
2. Replace min–max with z-score: `U(p) = (k(p) − μ)/σ`.
3. Replace the aggregate objective with a QoS-aware one:

   ```
   min_p  Σ_i w_i d_i ζ − (Σ_i s_i)²      ζ = 10³
   s.t.   Σ_i w_i = 1,  Σ_i s_i ≤ |X'|,
          d_i ≥ q'_i − U_i(p)   (KPI maximised)
          d_i ≥ U_i(p) − q'_i   (KPI minimised)
          U_i(p) − q'_i + M(1 − s_i) ≥ 0   (big-M satisfaction switch)
   ```

4. Solve over the union of per-xApp optimal ranges with the `O(N·|X'|)` grid
   heuristic.
5. Benchmark against NSWF and EG and report, for every case, how many xApps
   each method leaves satisfied.

**The key structural point:** all three baselines and QACM are *selectors over
the same discrete candidate grid*. That is why a faithful comparison needs no
simulator and no training loop — only identical data, thresholds and grid.

---

## 3. Datasets in each paper

### 3.1 `2311.13389v1`

| Item | Value |
|---|---|
| xApps | 4: MLB (`xApp1`), CCO (`xApp2`), ES (`xApp3`), MRO (`xApp4`) |
| Model | 8 ICPs, 6 KPIs |
| Generation | Gaussian KPI surfaces; `data1.csv`…`data4.csv` referenced |
| Shared ICP | `p1` (TXP), swept over `[-150, 150]` |
| Fixed ICPs | `p2 = 20`, `p3 = 60`, `p4 ∈ [-100, 100]`, `p5 = 60`, `p6 ∈ [-50, 150]`, `p7 = 60` |
| Predictor | Polynomial regression blocks |

Published outcomes:

| Scenario | Pair | Weights | AM | NSWF | EG |
|---|---|---|---|---|---|
| Direct, non-priority | x1 vs x2 | 0.5 / 0.5 | 0 (`u1≈0.02`, `u2≈0.72`) | −18 | — |
| Direct, priority | x1 vs x2 | 0.4 / 0.6 | — | — | 22 |
| Indirect | x2 vs x4 | 0.1 / 0.9 | 12 | 66 | 110 |
| Implicit | x1 vs x3 | 0.9 / 0.1 | −84 | −62 | −75 |

### 3.2 `2405.07324v2`

| Item | Value |
|---|---|
| xApps | 5 (`x₁`…`x₅`), 8 ICPs, 6 KPIs |
| Generation | Gaussian surfaces with published closed forms (below) |
| Files | `data1.csv`…`data5.csv`, columns `ICPs, KPI, normalisedKPI, normalised_threshold` |
| Utility | z-score (`normalisedKPI`) |
| Predictor | ANN, compared with polynomial regression |

Documented surfaces (`data/QACM/README.md`):

```
k1   =  80 · exp( −(p1)²            / (2 p2²) )
k2   = 100 · exp( −(p1 + p3)²       / (2 p2²) )
k3   = 120 · exp( −(p1 + 45)²       / (2 p4²) )
k41  = 120 · exp( −(p6 + (p2 − 30))² / (2 p5²) )
k42  = 150 · exp( −(p6 + (p2 − 50))² / (2 p5²) )
k5   = −35 · exp( −(p8 + (p1 − 25))² / (2 p7²) )
```

QoS thresholds: `q1 = 55, q2 = 95, q3 = 85, q41 = 75, q42 = 80, q5 = −25`.

Published QACM results (satisfied xApps, QACM vs NSWF/EG): 2/2 vs 1/2 (direct
2-way), 2/3 vs 1/3 (direct 3-way), 2/3 vs 1/3 (direct+indirect), 3/4 vs 2/4
(direct+implicit), 2/2 vs 1/2 (MATLAB ES-vs-CCO over TXP).

### 3.3 What is actually in this repository

`data/QACM/` holds five files, not a one-to-one match to either paper's model:

| File | Shape | Inputs | Notes |
|---|---|---|---|
| `data1.csv` | 10 000 × 5 | `Input1 ∈ [-100,100]`, `Input2 ∈ [-10,50]` | single output |
| `data2.csv` | 10 000 × 6 | 3 inputs (third constant −20) | single output |
| `data3.csv` | 10 000 × 5 | `Input1 ∈ [-100,100]`, `Input2 = 60` | `p2` pinned |
| `data4.csv` | 10 000 × 10 | 4 inputs, **2 outputs** | dual KPI (`k41`,`k42`) |
| `data5.csv` | 10 000 × 6 | 3 inputs | single output |

Consequences:

- The files carry QACM's z-score columns, not Wadud's min–max utilities.
- `data1`–`data3` span `p1 ∈ [−100, 100]`, not the paper's `[−150, 150]`.
- `data4`/`data5` cannot be loaded by the current single-output `DatasetSpec`.
- None of the files is unambiguously labelled with the xApp it belongs to.

So the shipped QACM data cannot serve as a drop-in Wadud dataset. This is the
provenance question that drove the data additions below.

---

## 4. Data we added for the new scenarios

### 4.1 Deterministic scalar projections

`scripts/gen_wadud_datasets.py` (seed 42, 301 points) evaluates the documented
surfaces over `p1 ∈ [−150, 150]` at the declared fixed ICPs and writes
`data/wadud/xapp1.csv` … `xapp5.csv`, each with a single `Input1,Output` pair.

`data/wadud/metadata.json` records the seed, point count, range, fixed ICPs,
source equations and a `status: provisional` flag. The generator is noiseless
and deterministic; the seed is part of the reproducibility contract, not a
random component.

| File | KPI | Output range |
|---|---|---|
| `xapp1.csv` | `k1` | 0 – 80 |
| `xapp2.csv` | `k2` | 0 – 100 |
| `xapp3.csv` | `k3` | 0.61 – 120 |
| `xapp4.csv` | mean(`k41`,`k42`) | 125.36 – 125.36 (**constant in `p1`**) |
| `xapp5.csv` | `k5` | −35 – −0.5 |

This is a *scalar projection*, not synthetic data invented to fit results: every
non-shared ICP is held at a declared paper value rather than silently zeroed.
The alternative — dropping the second feature of a two-feature file — would
have introduced an undocumented zero.

### 4.2 Scenario registry (`surrogate_xapps/scenarios.py`)

| ID | Purpose | Data |
|---|---|---|
| S1 | Direct, non-priority | `data/wadud/xapp1`, `xapp2` |
| S2 | Direct, priority | same pair |
| S3 | Indirect | `xapp2`, `xapp4` |
| S4 | Implicit | `xapp1`, `xapp3` |
| S5 | Four-way scaling | `xapp1`…`xapp4` |
| S6 | Synthetic direct pair (out-of-sample) | `data/synthetic/xapp1_direct`, `xapp2_direct` |
| S7 | Synthetic indirect trio (out-of-sample) | `data/synthetic/xapp1..3` |
| S8 | Weight sweep | scaffolded |
| S9 | Edge cases (constant KPI, zero utility, single xApp, zero weights) | metadata only |

S6/S7 deliberately use data the baselines were never tuned around, so they are
the only genuinely out-of-sample evidence in the current run.

### 4.3 Evaluation harness

`surrogate_xapps/evaluate.py` runs `qacm`, `am`, `nswf`, `eg` on identical
xApps, grid, resolution and weights, and writes CSV plus Markdown. It currently
emits 10 of the 13 specified metrics (see §6).

---

## 5. Fidelity: what reproduces, what does not

Run at the default resolution (128) on the provisional projections:

| Scenario | Method | Published `p*` | Ours | Within ±5? |
|---|---|---:|---:|---|
| S1 | AM | 0 | −33.87 | ✗ |
| S1 | NSWF | −18 | −41.34 | ✗ |
| S1 | EG | — | −43.70 | — |
| S2 | EG | 22 | −48.43 | ✗ |
| S3 | AM | 12 | −106.45 | ✗ |
| S3 | NSWF | 66 | −64.96 | ✗ |
| S3 | EG | 110 | −64.96 | ✗ |
| S4 | AM | −84 | −29.03 | ✗ |
| S4 | NSWF | −62 | −36.61 | ✗ |
| S4 | EG | −75 | −8.27 | ✗ |

**Zero published values are reproduced by the current mapping.** Every scenario
also returns `n_satisfied_after` equal to the xApp count for *all four* methods,
so the headline QACM-vs-baseline claim is not yet exercised by the run.

This is not a solver failure. The objectives are implemented as stated; the
inputs are wrong. Four concrete causes were identified.

### 5.1 Cause A — xApp4's surface is flat in `p1`

`k41`/`k42` depend on `p6`, `p2` and `p5` but **not on `p1`**. At fixed
`p6 = 0`, `p2 = 20`, xApp4's KPI is the constant 125.36, which produces the
`constant KPI has zero utility range` warning seen in the S3/S5 runs.

Consequence: the indirect scenario S3 (xApp2 vs xApp4 over `p1`) **cannot be
reproduced with the documented equations at the declared fixed ICPs**, because
xApp4 has no `p1` response to collapse. Either xApp4 does not map to `k41/k42`,
or `p2`/`p6` — not `p1` — is the shared variable in that scenario.

### 5.2 Cause B — `k5` is a minimisation KPI but is evaluated as maximisation

`k5 = −35·exp(…)` is negative-valued and peaks at its most negative point.
Maximising it drives the xApp to the far tail of the range. The evaluation
harness (`evaluate.py`) hard-codes `objective="max"` for every Wadud xApp, so
xApp5 cannot express its true preference. The utility module already supports
`objective="min"` inversion; the harness does not pass it.

### 5.3 Cause C — the xApp → KPI mapping is unverified

The repository documents the equations but never states which equation belongs
to which paper xApp. The current mapping (`xapp1→k1`, `xapp2→k2`, …) was a
convenience choice, and it cannot produce the published direct-conflict
preferences (`−50` vs `+50`): `k1` peaks at `0`, `k2` at `−60`, `k3` at `−45`,
and `k5` at `25 − p8`.

### 5.4 Cause D — fixed ICPs are scenario-specific

The paper's fixed values are given for one setup, yet S3 says "xApp2 sets
`p1 = 0`" while S1 has xApp2 demanding `+50`. The same xApp cannot have both
preferences under one fixed-ICP assignment. The fixed values are therefore
scenario-dependent, and the single global table in `metadata.json` is
insufficient.

### 5.5 A testable mapping hypothesis (post-hoc, not yet a reproduction)

A two-parameter search over `p4 ∈ [20, 140]` and `p8 ∈ [−45, 0]`, with
`xApp1 → k3` (max), `xApp2 → k5` (min), reproduces the S1/S2 triplet closely:

| Target | Published | Best fit (`p4 = 41`, `p8 = −25`) |
|---|---:|---:|
| xApp1 demand | −50 | −45 |
| xApp2 demand | +50 | +50 |
| AM | 0 | 2.5 |
| NSWF | −18 | −14.6 |
| EG (w = 0.4/0.6) | 22 | 22.5 |

All five are inside the spec's ±5 tolerance. This is **post-hoc**: two free
parameters were tuned against three targets, so it is a hypothesis, not
evidence of reproduction. It does, however, identify a specific, falsifiable
next step: confirm from the paper whether xApp1↔`k3`, xApp2↔`k5`, `p4 ≈ 41`,
`p8 = −25`, and whether `k5` is a minimised power KPI. If confirmed, S1 and S2
move from "not reproduced" to "reproduced", and the same correction can be
applied to S3/S4.

---

## 6. Reproduced faithfully / added / outstanding

### 6.1 Faithfully reproduced

| Element | Status | Evidence |
|---|---|---|
| AM, NSWF, EG objectives | Reproduced | `baselines.py`; AM is prediction-free, NSWF is `argmax Σ log u`, EG is `argmax Σ w_i u_i` |
| Shared candidate grid and deterministic tie-break | Reproduced | Same grid contract as `CMC`; `baselines.py` `_axes` |
| Priority weights, `Σ w_i = 1` | Reproduced | Per-scenario weights; normalised in EG |
| Scenario structure (direct/indirect/implicit) | Reproduced in structure | S1–S4 |
| Identical substrate across methods | Reproduced | Single harness invocation, same data/grid/weights |
| Min–max ×10 utility | Reproduced with documented deviation | `utility.py`, `mode="minmax10"`; `min` inversion added |
| Modularity, no CMC changes | Reproduced | Baselines depend only on `IQueryableXApp` + `MitigationResult` |
| Backward compatibility | Reproduced | `--method` defaults to `qacm`; 128 tests pass |

### 6.2 What we added, and why

| Addition | Why it matters |
|---|---|
| Deterministic scalar projections of the paper surfaces (`data/wadud/`, seed 42, recorded fixed ICPs) | Makes the paper's 8-ICP model testable on our scalar path without inventing or silently zeroing features |
| Unified baseline framework plugged into the existing xApp protocol | Enables a like-for-like comparison without forking the CMC |
| Multi-metric harness (`evaluate.py`): `p*`, utilities, regrets, welfare, Nash product, worst-off, spread, satisfaction counts, latency | Prevents the comparison from being a single-number scoreboard; the thesis claim needs both fidelity and QoS metrics |
| Out-of-sample scenarios S6/S7 | Tests generality on data the baselines were not designed around |
| Property/edge scenarios S8/S9 (scaffolded) | Checks NSWF invariance, EG monotonicity, zero-utility and constant-KPI handling |
| Tests and provenance docs | 128 tests pass; deviations and data status recorded rather than hidden |

### 6.3 Outstanding

| Item | Why it blocks | State |
|---|---|---|
| Confirm xApp ↔ KPI mapping | Determines every `p*`; current mapping cannot produce the published preferences | **Highest priority** |
| Confirm per-scenario fixed ICPs (`p4`, `p6`, `p8`) | The global fixed table contradicts S1 vs S3 | Open |
| Pass per-xApp `objective` (`k5` must minimise) | xApp5 currently prefers the wrong end of the range | Open |
| Make S3 structurally possible | `k41/k42` are independent of `p1` | Open |
| Rebuild `data/wadud/` after the mapping fix | Current projections encode the unverified mapping | Open |
| Reproduce S1–S4 within ±5 or record `discrepancy_reason` | Acceptance criterion 4 | 0/4 today |
| Demonstrate QACM `n_satisfied ≥` baselines | The thesis claim | All methods currently tie at full satisfaction |
| Fix S8 registry paths | S8 points at `data/wadud/data1.csv`, which does not exist | Not runnable |
| Emit M3, M10, M11 | CSV stores 10/13 metrics; concession distance and weighted deviation are absent | Partial |
| Measure `deterministic` instead of hard-coding `True` | Reproducibility gate is asserted, not tested | Partial |
| Test `evaluate.py` | 0% coverage; harness bugs would ship silently | Open |

### 6.4 Current suite state

`uv run pytest` → **128 passed**. Coverage: total **83%**;
`baselines.py` 84%, `scenarios.py` 92%, `utility.py` 62%, `evaluate.py` 0%.

---

## 7. Bottom line

- The **comparison machinery is faithful and in place**: the three Wadud
  selectors and QACM share one grid, one data set and one metric schema.
- The **paper data is not yet faithfully reproduced**: 0 of 10 published
  operating points match, because of a flat xApp4 surface, a
  maximised-instead-of-minimised `k5`, and an unverified xApp/KPI mapping.
- A concrete two-parameter hypothesis recovers the S1/S2 triplet inside
  tolerance, which turns "reproduction failed" into a specific, checkable
  next step rather than an open-ended gap.
- The **contribution is methodological**, not a reimplementation of the CMS:
  a modular, metric-complete, deterministic comparison harness with explicit
  provenance and documented deviations.
