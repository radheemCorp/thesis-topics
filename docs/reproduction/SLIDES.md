# Presentation Structure — Wadud vs QACM Reproduction

**Audience:** academic researchers.
**Rule for this deck:** no code, no file paths on slides. Every claim is about
experimental fidelity, the data, or the comparison method. Put implementation
detail in speaker notes only.

**Talk length assumed:** 15–20 minutes + questions (10 slides).

---

## Slide 1 — Title

**On slide**

- Title: *Reproducing Game-Theoretic Conflict Mitigation in O-RAN*
- Subtitle: *Wadud et al. (2023) vs QACM (2024): fidelity, data, and what we changed*
- Your name / group / date

**Speaker notes**

- Both papers are by the same authors: Wadud, Golpayegani and Afraz. QACM is
  their own successor to the 2023 paper, not a rival work.
- The talk is about whether the comparison between them holds up when both are
  run on the same substrate — not about our codebase.

---

## Slide 2 — The problem

**On slide**

- Multi-vendor xApps on the Near-RT-RIC share control parameters.
- Three conflict classes, with a one-line example each:
  - **Direct** — both xApps set the same parameter (ES vs CCO on TXP)
  - **Indirect** — one parameter moves another xApp's domain (MLB tilt → MRO handover)
  - **Implicit** — different KPIs, hidden coupling
- Consequence: KPI degradation, SLA/QoS violations.
- Why the obvious fixes fail:
  - Winner-takes-all → loses collective efficiency
  - Joint optimisation → vendor xApps will not share data

*Visual: the three conflict types as a small diagram, not the full CMS
architecture.*

**Speaker notes**

- Emphasise that both papers agree on the taxonomy; the disagreement is purely
  about the objective.
- The "no data sharing" constraint is what makes this a bargaining problem
  rather than a central optimisation problem.

---

## Slide 3 — Two approaches to the same problem

**On slide**

| | Wadud 2023 | QACM 2024 |
|---|---|---|
| Objective | maximise aggregate utility | minimise QoS deviation **and** maximise satisfied xApps |
| Utility | min–max → [0,10] | z-score |
| Predictor | polynomial regression | ANN (vs polynomial) |
| Solver | candidate grid | `O(N·\|X'\|)` grid heuristic |
| Weights | MNO-assigned | Conflict Supervision xApp |

- One-line takeaway: **QACM = Wadud + a per-xApp QoS constraint.**

**Speaker notes**

- AM, NSWF, EG are Wadud's three rules: mean of requests, product of utilities,
  weighted sum of utilities.
- QACM keeps NSWF/EG as its own benchmarks. That is the comparison we reproduce.
- The claim under test: QACM satisfies at least as many xApps as NSWF/EG, and
  strictly more on at least one scenario.

---

## Slide 4 — The datasets in each paper

**On slide**

| | Wadud 2023 | QACM 2024 |
|---|---|---|
| xApps | 4 (MLB, CCO, ES, MRO) | 5 |
| Model | 8 ICPs, 6 KPIs | 8 ICPs, 6 KPIs |
| Generation | Gaussian KPI surfaces | same closed-form surfaces |
| Files | `data1`–`data4` | `data1`–`data5` |
| Shared ICP | `p1 ∈ [−150, 150]` | per case study |
| Fixed ICPs | `p2=20, p3=60, p4∈[−100,100], p5=60, p6∈[−50,150], p7=60` | per case |
| Utility | min–max ×10 | z-score |

- Show the six Gaussian forms once, on one line each.
- Note the published QoS thresholds (`q1…q5`).

**Speaker notes**

- Key point: this is synthetic data in both papers, so a faithful reproduction
  should be achievable without a simulator.
- The QACM repository ships the z-score columns, so its files are not directly
  usable as Wadud inputs — different normalisation and, for `data4`/`data5`,
  different dimensionality and multiple outputs.

---

## Slide 5 — What the shipped data actually contains

**On slide**

- QACM's five files do not match either paper's model one-to-one:
  - two live on `p1 ∈ [−100,100]`, not `[−150,150]`
  - two have three inputs; one has four inputs and **two** outputs
  - one pins `p2 = 60`; the columns are z-scored, not min–max
  - none is labelled with its xApp
- Conclusion: **cannot be used as a drop-in Wadud dataset.**

**Speaker notes**

- Be explicit that this is a provenance finding, not a complaint. The files were
  published for QACM's own experiments.
- Foreshadow the fix: generate the paper's surfaces ourselves at declared fixed
  values.

---

## Slide 6 — Data additions for the new scenarios

**On slide**

- **Scalar projections** of the documented Gaussian surfaces:
  - `p1 ∈ [−150,150]`, 301 points, deterministic, seed recorded
  - every non-shared ICP held at a **declared** paper value
  - no feature silently set to zero
  - metadata file records seed, range, fixed ICPs, source, and a
    `provisional` status
- **Nine scenarios:**

| Group | Scenarios |
|---|---|
| Paper fidelity | S1 direct (non-priority), S2 direct (priority), S3 indirect, S4 implicit |
| Scale | S5 four-way |
| Out-of-sample | S6 synthetic pair, S7 synthetic trio |
| Robustness | S8 weight sweep, S9 edge cases |

- Why scalar: the paper's comparison contract is one shared ICP; joint 2-D is
  **our** extension, not a claim about Wadud.

**Speaker notes**

- State plainly that the projections are provisional and why: the paper does not
  unambiguously state the xApp/KPI mapping.
- The out-of-sample scenarios are the only evidence not shaped by the paper's
  data.

---

## Slide 7 — What we reproduced faithfully

**On slide**

- ✅ AM, NSWF, EG exactly as defined (AM prediction-free; NSWF product,
  log-space; EG weighted sum with `Σw=1`)
- ✅ Same candidate grid, same deterministic tie-break for every method
- ✅ MNO priority weights per scenario
- ✅ Direct / indirect / implicit scenario structure
- ✅ Identical data, resolution and thresholds across methods
- ✅ Baselines are pluggable and do not modify the QACM controller
- ⚠ One documented deviation: min–max scaling is inverted for minimised KPIs
  (the printed formula assumes higher-is-better)

**Speaker notes**

- The deviation matters for the ES/power xApp; it is documented in the module
  and in the docs.
- 128 automated tests pass; the existing QACM behaviour is unchanged and
  remains the default.

---

## Slide 8 — Reproduction results (the honest slide)

**On slide**

- Published vs reproduced operating point, S1–S4:

| Scenario | Method | Paper | Ours |
|---|---|---:|---:|
| S1 | AM | 0 | −33.9 |
| S1 | NSWF | −18 | −41.3 |
| S2 | EG | 22 | −48.4 |
| S3 | NSWF | 66 | −65.0 |
| S3 | EG | 110 | −65.0 |
| S4 | AM | −84 | −29.0 |

- **0 of 10 published points reproduced.**
- All four methods satisfy **all** xApps in every scenario → the QACM-vs-baseline
  claim is not yet exercised.
- This is an **input** failure, not a solver failure. Four identified causes:

  1. xApp4's KPI is **constant in `p1`** (it depends on `p2`, `p6` only) → the
     indirect scenario cannot work as specified.
  2. `k5` is negative-valued and must be **minimised**, but is currently
     maximised.
  3. The xApp ↔ KPI mapping is unverified and cannot produce `−50` vs `+50`.
  4. Fixed ICPs appear to be **scenario-specific**, not one global table.

**Speaker notes**

- Do not soften this. The value of the talk is that the failure is diagnosed,
  not hidden.
- Cause 1 is the most interesting: the paper's indirect scenario over `p1` is
  structurally impossible with the documented `k41/k42` forms at the declared
  fixed values.

---

## Slide 9 — A testable mapping hypothesis

**On slide**

- Pair `xApp1 → k3` (max) with `xApp2 → k5` (min), with `p4 ≈ 41`, `p8 = −25`:

| Target | Paper | Fit |
|---|---:|---:|
| xApp1 demand | −50 | −45 |
| xApp2 demand | +50 | +50 |
| AM | 0 | 2.5 |
| NSWF | −18 | −14.6 |
| EG | 22 | 22.5 |

- All inside the ±5 tolerance.
- **Post-hoc fit, not a reproduction** — two free parameters tuned to three
  targets.
- But it converts an open gap into a falsifiable check: confirm the mapping and
  `k5`'s minimisation in the paper, then re-run.

**Speaker notes**

- Be very clear about the post-hoc nature. Say "this is a hypothesis with a
  test, not a result."
- If confirmed, S1/S2 move to reproduced and the same correction transfers to
  S3/S4.

---

## Slide 10 — Contributions and what remains

**On slide**

**Contributions**

- A modular, method-agnostic comparison harness: QACM and all three Wadud
  baselines on one grid, one dataset, one metric schema.
- Multi-metric reporting: `p*`, per-xApp utility, regret, welfare, Nash product,
  worst-off utility, spread, QoS satisfaction count, latency, determinism.
  (10 of 13 currently emitted.)
- Deterministic, provenance-recorded data generation for the paper's surfaces.
- Out-of-sample scenarios (S6/S7) and property/edge tests (S8/S9).
- Explicit deviation log and provisional-status flag instead of silent
  assumptions.

**Remaining**

- Confirm xApp ↔ KPI mapping and per-scenario fixed ICPs.
- Implement per-xApp objective (`k5` minimised).
- Reproduce S1–S4 within ±5, or record a `discrepancy_reason`.
- Demonstrate QACM satisfaction advantage (currently a tie).
- Complete metric coverage (M3, M10, M11) and test the harness.

**Closing line:** the machinery is faithful; the paper's inputs are the open
problem, and we can now name exactly which ones.

---

## Backup slides (not presented, for questions)

- **B1 — Full metric definitions** (M1–M13).
- **B2 — Utility formulas**, min–max and z-score, including the `min` inversion.
- **B3 — Why EG is a grid scan, not an LP**: on a discrete ICP grid the
  weighted sum is a linear scan; the optimum is identical, so no solver is used.
- **B4 — NSWF numerical detail**: log-space with an epsilon clamp; a `literal`
  mode preserves zero factors for fidelity.
- **B5 — Latency**: all methods inside the 1 s Near-RT-RIC budget; AM ~1 ms,
  NSWF/EG ~30–65 ms at resolution 128, QACM ~1 ms.
- **B6 — Test and coverage state**: 128 tests, 83% total.
- **B7 — Scope boundary**: CMS messaging, SDL tables and CDC classification are
  out of scope; joint 2-D is a QACM extension, not part of this comparison.

---

## Anticipated questions

| Question | Answer |
|---|---|
| "Why not use the paper's own CSVs?" | They are QACM's z-scored, differently dimensioned files (`data4` has two outputs; `data5` three inputs). Using them as Wadud inputs would mix normalisations and change the model. |
| "Isn't generating data just fitting the answer?" | The generator is the paper's own equations at declared fixed ICPs, with fixed seed and recorded metadata. The one genuinely post-hoc step — the mapping hypothesis — is labelled as such. |
| "Why does QACM always win on satisfaction?" | It doesn't yet — all methods currently tie because every threshold is met. That is why the mapping fix is the priority: the discriminating scenarios are not being exercised. |
| "Is 2-D bargaining part of the reproduction?" | No. Wadud is scalar. Joint 2-D is our extension and is labelled as such wherever it appears. |
| "What is the single biggest threat to validity?" | The unverified xApp/KPI mapping. It sets every operating point, and the current mapping demonstrably cannot produce the paper's `−50` vs `+50`. |
