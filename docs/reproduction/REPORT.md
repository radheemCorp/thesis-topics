# Reproduction and Comparison Report: Wadud et al. vs QACM

**Scope:** what the two papers do, where the earlier one falls short, how the
later one responds, how faithfully we reproduce them, what data we added, and
what remains outstanding.

**Track:** `conductor/tracks/wadud-baseline_20261101`

**Papers:**

| Ref | Title | Authors | Year |
|---|---|---|---|
| `2311.13389v1` | *Conflict management in the near-RT-RIC of Open RAN: A game theoretic approach* | A. Wadud, F. Golpayegani, N. Afraz | 2023 |
| `2405.07324v2` | *QACM: QoS-Aware xApp Conflict Mitigation in Open RAN* | A. Wadud, F. Golpayegani, N. Afraz | 2024 |

Both papers share the same authors, so the comparison is not an adversarial
reimplementation: QACM is the authors' own successor to `2311.13389v1` and
positions itself explicitly against NSWF/EG. It is an evolution of the same
system, not a competing architecture.

**Companion:** how the papers describe their inputs (`p1 … p8`), why almost none
of them is named, and what a real testbed would have to measure for each xApp is
in [`ICP-MAPPING-AND-TESTBED-DATA.md`](ICP-MAPPING-AND-TESTBED-DATA.md). The
presentation outline is in [`SLIDES.md`](SLIDES.md).

---

## 1. The problem both papers address

Open RAN disaggregates the RAN into independently developed xApps running on the
Near-RT-RIC. Because those xApps share control parameters, they issue
incompatible requests. Both papers use the same three-way taxonomy:

| Conflict | Definition | Paper example |
|---|---|---|
| **Direct** | Two or more xApps request different values for the same ICP | ES and CCO both set transmission power |
| **Indirect** | One xApp's parameter change moves another xApp's operating domain | MLB adjusts tilt, MRO's handover boundary shifts |
| **Implicit** | Two xApps optimise different KPIs and degrade each other through a hidden coupling | QoS xApp and handover xApp interfere without a shared parameter |

The consequence is KPI degradation and SLA/QoS violations. Both papers reject
"winner-takes-all" prioritisation: discarding one xApp's request loses
collective efficiency, and vendor xApps are black boxes that will not share
training data. That combination — shared resources, no data sharing, divergent
objectives — is what makes this a bargaining problem rather than a central
optimisation problem.

---

## 2. Wadud et al. (`2311.13389v1`): approach and shortcomings

### 2.1 What the paper does

1. Model each xApp as a regression block mapping ICPs to a KPI, trained on
   synthetic Gaussian surfaces.
2. Normalise KPIs to a common utility (§V-D):

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

Published outcomes (using the preferences implied by the equations — see W8):

| Scenario | Pair | Weights | AM | NSWF | EG |
|---|---|---|---|---|---|
| Direct, non-priority | xApp1 vs xApp2 | 0.5 / 0.5 | 0 (`u1≈0.02`, `u2≈0.72`) | −18 | — |
| Direct, priority | xApp1 vs xApp2 | 0.4 / 0.6 | — | — | 22 |
| Indirect | xApp2 vs xApp4 | 0.1 / 0.9 | 12 | 66 | 110 |
| Implicit | xApp1 vs xApp3 | 0.9 / 0.1 | −84 | −62 | −75 |

### 2.2 Design shortcomings

These are the weaknesses that motivate QACM.

#### W1 — No QoS awareness

The objective is aggregate utility: a product (NSWF) or a weighted sum (EG).
Neither contains a threshold. A factor of `0.01` still contributes positively to
the NSWF product, and the other factors dominate it; EG's linear sum lets a large
gain for one xApp offset a large loss for another. The result is that an
operating point can be "optimal" while one xApp is far below its SLA.

This is not a corner case — it is the central failure mode of welfare
maximisation under heterogeneous constraints, and the paper's own examples
demonstrate it (AM at `p1 = 0` leaves `u1 ≈ 0.02` while claiming a compromise).

> **QACM's answer:** replace welfare with a satisfaction count (§3.1).

#### W2 — The utility scale is anchor-dependent and direction-blind

Two separate problems in one formula:

- **Anchoring.** Min–max uses only the observed `o_min` and `o_max`. A single
  tail sample sets the scale for every other point, so one outlier compresses the
  usable range.
- **Direction.** The formula is monotone increasing in the KPI. There is no way
  to say "lower is better". Yet the paper's ES xApp is explicitly described as
  minimising power consumption. The formula cannot express that without an
  unstated inversion — and the paper never states one.

> **QACM's answer:** z-score normalisation plus a per-KPI `δ_i` direction flag
> (§3.2).

#### W3 — Scope is pairwise only

All three scenarios are two-xApp duels. The framework is described for `n`
xApps, but it is never exercised beyond two, and never with two conflicts
occurring at once. A production RIC has more than two xApps sharing more than one
parameter.

> **QACM's answer:** 3-way direct, concurrent direct+indirect, and concurrent
> direct+implicit scenarios, up to five xApps (§3.3).

#### W4 — Weights are exogenous and unexplained

`w_i` are "assigned by the MNO". There is no mechanism, no policy mapping, and no
derivation. Every priority result is therefore only as meaningful as an arbitrary
weight, and the paper does not examine sensitivity to it.

> **QACM's answer:** a Conflict Supervision (CS) xApp that assigns weights from
> policy and network state. Partial — still future work (§4).

#### W5 — The predictor is a weak model

Each xApp is a polynomial-regression block. The bargaining loop queries the
predictor many times per conflict, so prediction error propagates into the chosen
operating point. Polynomial fits struggle with the Gaussian surfaces' tails,
which is exactly where threshold decisions are made.

> **QACM's answer:** an ANN (4×128, tanh, dropout 0.2, Adam, MSE) benchmarked
> against polynomial regression (§3.2). An enabler, not the core contribution.

#### W6 — The reported metric is not the operational one

The paper reports the chosen `p*` and the utilities at that point. That does not
tell an operator how many xApps are within SLA. Two methods can report similar
utilities while differing sharply in compliance.

> **QACM's answer:** report the number of xApps meeting QoS for every case (§3.3).

#### W7 — Validation is synthetic only

All results come from Gaussian surfaces with no physical units and no measured
KPI. There is no evidence that the method survives a real RAN's dynamics.

> **QACM's answer:** a MATLAB 5G study with measured throughput and power
> (§3.3). Partial — still no RIC (§4).

### 2.3 Reporting shortcomings that block reproduction

These are not addressed by QACM; they are defects in how `2311.13389v1` is
specified, and they are why our reproduction cannot yet match its numbers.

#### W8 — The prose contradicts the equations

§VI states: *"xApp1 demands `p1 = 50` … whereas xApp2 demands `p1 = −50`."*
But `o1` peaks at `p1 = −50` and `o2` at `p1 = +50`. The equations are
self-consistent; the sentence has the two xApps swapped. A reproduction built
from the prose gets the conflict backwards.

#### W9 — The utility scale is stated twice, differently

§V-D defines the utility on `[0, 10]`; the numerical-results section says
"converted to utilities within the range `[0, 1]`". The formula implies `[0, 10]`.
Both cannot be right, and the choice changes the absolute utility values quoted
in the results table.

#### W10 — Scenario-specific surfaces are unpublished

The paper uses `o1, o2` for the direct and indirect scenarios and `o1′, o2′` for
the implicit scenario, with different amplitudes (0.6 and 0.35) and different
centres. There is no published table mapping which variant belongs to which
figure. Worse, `o1′` peaks at `p1 = +85` while the text says xApp1 "sets
`p1 = −85`" — a second sign inconsistency.

#### W11 — KPIs depend on other xApps' KPIs

`o3 = f(p4, p5, o1)` and `o4 = f(p6, p7, o2)`. Two of the four KPIs take another
xApp's output as an input. That is how the "implicit" and "indirect" conflicts
are constructed — by editing the data model, not by a hidden coupling in the
network. It means the xApps are not independent `ICPs → KPI` regressors, which is
exactly what the regression-block design assumes.

#### W12 — Inputs are anonymous, dimensionless, and not tied to the datasets

The model uses `p1 … p7` with one name (`p1 = TxP`) and dimensionless ranges.
The referenced `data1.csv … data4.csv` are column-indexed (`Input1, Input2, …`)
and the paper never states which column is which symbol. Recovering the mapping
requires inferring it from value ranges — see
[`ICP-MAPPING-AND-TESTBED-DATA.md`](ICP-MAPPING-AND-TESTBED-DATA.md) §3.

---

## 3. QACM (`2405.07324v2`): how it improves on Wadud

### 3.1 The core change: welfare → compliance

The one-line version:

> Wadud asks *"which `p` maximises aggregate utility?"*
> QACM asks *"which `p` maximises the number of xApps that meet their own QoS
> threshold?"* — and only then breaks ties on utility.

Formally, QACM (`2405.07324v2` §VI-D, Eq. 3a) replaces NSWF/EG with:

```
min   Σ_i w_i d_i · ζ  −  (Σ_i s_i)²        ζ = 10³
s.t.  d_i ≥ q′_i − U_i(p)   if δ_i = 0   (KPI maximised)
      d_i ≥ U_i(p) − q′_i   if δ_i = 1   (KPI minimised)
      U_i(p) ≥ q′_i − M(1 − s_i)         s_i ∈ {0,1}
      Σ_i w_i = 1,   Σ_i s_i ≤ |X′|,   |X′| ≥ 2
```

Two terms carry the change:

- `d_i` is the **shortfall from the threshold**, not the utility itself.
- `s_i` is a binary **satisfaction switch** — 1 if xApp *i* clears `q′_i`.

#### Why this actually changes the answer

The cost function is `1000 · (weighted shortfall) − (count satisfied)²`.

- `Σ w_i d_i` is a weighted *average* of z-scored distances, so it can move by at
  most `max d ≈ 3`. The entire deviation term therefore lives in `[0, 3000]`.
- Gaining one more satisfied xApp when `k` are already satisfied changes
  `(Σ s_i)²` by `2k + 1`, worth `1000 · (2k + 1)`.

| Step | Satisfaction gain | Max possible deviation swing | Winner |
|---|---:|---:|---|
| 0 → 1 satisfied | 1000 | 3000 | deviation can win |
| 1 → 2 satisfied | 3000 | 3000 | tie at the extreme |
| 2 → 3 satisfied | 5000 | 3000 | **count always wins** |
| 3 → 4 satisfied | 7000 | 3000 | **count always wins** |

**From the second satisfied xApp onward the objective is effectively
lexicographic: maximise the count, then minimise deviation.** NSWF and EG cannot
express that preference at all, however they are tuned. This is a structural
difference, not a tuning difference — and it is the thesis-relevant claim our
testbed exists to test.

Because the utility is z-scored, `q′_i` is also z-scored: "meets QoS" means
"within the tail the operator declared acceptable". The threshold is a point on
the same axis as the utility, which is what makes the big-M switch work.

### 3.2 Supporting changes

| Change | Wadud | QACM | Addresses |
|---|---|---|---|
| **Objective** | Aggregate utility (product or weighted sum) | Satisfied count, then weighted deviation | W1, W6 |
| **Utility scale** | min–max onto `[0, 10]` | z-score `(k−μ)/σ` | W2 |
| **KPI direction** | Monotone increasing only | `δ_i` binary flag per KPI | W2 |
| **Predictor** | Polynomial regression blocks | ANN (4×128, tanh, dropout 0.2, Adam, MSE) | W5 |
| **Multi-KPI xApps** | Formula allows `\|J\|>1`; example uses one KPI each | `x4` has `k41` and `k42`, combined into one utility | (exercises the formula) |
| **Conflict scope** | Three pairwise scenarios | 2-way, 3-way, concurrent direct+indirect, concurrent direct+implicit | W3 |
| **Weights** | MNO hand-assigns | CS xApp reads policy + network state | W4 (partial) |
| **Validation** | Synthetic only | Synthetic **plus** MATLAB 5G (2 gNBs, 10 UEs, 7.2 split) | W7 |
| **Reported metric** | `p*` and utilities | Number of xApps meeting QoS | W6 |

#### On the utility change specifically

Both papers normalise *per KPI*, so neither solves cross-KPI comparability. The
differences that matter:

- **Sensitivity to extremes.** Min–max uses only `o_min` and `o_max`; a single
  tail sample sets the scale for everything. Z-score uses all samples.
- **Shape.** Min–max is a linear re-scaling, so it compresses the tails of a
  Gaussian. Z-score is affine in the KPI, so it preserves the Gaussian shape —
  the authors' stated reason, and a real prerequisite for threshold arithmetic.
- **Cost.** Z-score is unbounded, so a high-variance KPI can dominate a weighted
  sum of utilities. Min–max bounds every KPI to the same interval. QACM buys
  threshold semantics at the price of cross-KPI scale balance.

### 3.3 What the evidence shows

The paper's four case studies:

| Scenario | QACM | NSWF / EG |
|---|---|---|
| Direct, 2 xApps | **2/2** | 1/2 |
| Direct, 3 xApps | **2/3** | 1/3 |
| Direct + indirect | **2/3** | 1/3 |
| Direct + implicit | **3/4** | 2/4 |
| MATLAB, ES vs CCO | **2/2** | 1/2 |

Selected operating points:

- **Case A** (direct, `p2`): QACM 27 → both satisfied. NSWF 23 → only `x1`.
  Priority: QACM 25 → both. EG 22 → only `x1`.
- **Case B** (direct, 3-way, `p1`): QACM 23 → `x1`,`x2`. NSWF −45 → only `x3`.
  Priority: QACM 5 → `x3`,`x1`; EG 1 → `x1`,`x3` but larger `k2` deviation.
- **Case D** (direct + implicit): QACM 22 → 3 of 4 satisfied. NSWF −13 → 2 of 4.

The MATLAB study (§VIII-A) is the clearest illustration:

| Method | TXP | Outcome |
|---|---:|---|
| NSWF | 6 dBm | Power threshold met, throughput **39 % below** threshold |
| **QACM** | **15 dBm** | Power exactly at threshold, throughput shortfall cut 39 % → **3 %** |
| EG (`w_ES=0.1`, `w_CCO=0.9`) | 40 dBm | Power **+256 %**, throughput **+200 %** — maximises the favoured xApp with no balance |

The pattern is consistent: the baselines optimise a sum or a product; QACM
optimises a count; the count is what the operator cares about.

### 3.4 What is new vs inherited

**New in QACM:**

- the satisfaction term `−(Σ s_i)²` and its big-M linearisation
- the `δ_i` per-KPI direction flag
- the reformulation from threshold-free welfare to threshold-aware compliance
- the QoS-count evaluation metric
- multi-party and concurrent-conflict scenarios
- the MATLAB validation outside the Gaussian model

**Inherited from Wadud / the CMS line of work:**

- the entire CMS architecture — PMon, CDC, CMC, PGD, RCP, RCPG, PKR, DCKD, KDO —
  adopted from `[1]` and `[6]`
- the Gaussian KPI model and the `p1 … p8` abstraction
- NSWF and EG, which become the baselines
- the discrete grid over the optimal configuration range and the
  `O(N · \|X′\|)` scan
- the closed-loop bargaining protocol

The honest framing:

> **QACM = Wadud's CMS + a QoS constraint + a different utility scale +
> a threshold-aware objective.**

The contribution is the objective, not the framework.

#### At a glance

| Question | Wadud `2311.13389v1` | QACM `2405.07324v2` |
|---|---|---|
| What is maximised? | Aggregate utility (product or weighted sum) | Count of QoS-satisfied xApps, then utility |
| What is the threshold for? | Not used in the objective | Defines `d_i` and `s_i`; drives the objective |
| Utility | min–max `[0,10]` | z-score, unbounded, signed |
| Min/max KPIs | Not expressible | `δ_i` flag per KPI |
| Comparison metric | `p*` and utilities | xApps meeting QoS |
| Conflict scope | 3 pairwise scenarios | 2-way, 3-way, concurrent, 5 xApps |
| Validation | Synthetic only | Synthetic + MATLAB 5G |
| Framework | CMS (own design) | Same CMS, reused |
| Baselines | AM | NSWF, EG (from Wadud) |
| Weights | MNO, ad hoc | CS xApp (proposed) |

---

## 4. What QACM still does not fix

Worth knowing before presenting this as a clean win:

1. **Weights are still exogenous.** The CS xApp that assigns `w_i` is explicitly
   future work. Every priority result depends on a weight nobody has defined.
   W4 is only partially addressed.
2. **No RIC.** §VIII-A states the simulation is "performed without a RIC, and
   xApps are implemented as logic functions". Even the practical validation is
   not a deployment.
3. **Grid-optimal, not optimal.** The solution is the best point on a discrete
   candidate grid. The complexity argument is about the heuristic, not about
   optimality.
4. **No latency measurement.** The 10 ms – 1 s Near-RT budget is discussed as a
   risk, never measured.
5. **The z-score threshold is sample-dependent.** `q′_i = (q_i − μ)/σ` uses
   statistics of the sampled grid, so the satisfaction count is partly a property
   of the sampling. Re-normalising on a 1-D sweep instead of the paper's 2-D grid
   moves `q′5` by ~0.2σ — enough to flip satisfaction at the boundary. This is a
   weakness in the very mechanism that makes QACM work. See
   [`ICP-MAPPING-AND-TESTBED-DATA.md`](ICP-MAPPING-AND-TESTBED-DATA.md) §3.
6. **The ANN claim is overstated.** Table III shows `x3`'s MSE getting *worse*
   under ANN (0.0003 → 0.0045) while `R²` stays at 0.99, so "ANN outperforms PR
   across all xApps" is not uniformly true.
7. **The `p2` case studies cannot be derived from the printed equations.**
   Case A reports `k1` peaking at `p2 = 18` and `k2` at `p2 = 25`, but `p2` is a
   *width* in those equations, so neither can have a peak in it. Cases A and C
   can only be reproduced from the shipped CSVs, not from the text.
8. **No independent replication.** Same three authors. This is a successor paper,
   not external validation of the objective.

It does **not** inherit Wadud's reporting defects wholesale — QACM publishes its
datasets and its equations — but it introduces two of its own (items 5 and 7).

---

## 5. Datasets in each paper

### 5.1 `2311.13389v1`

| Item | Value |
|---|---|
| xApps | 4: MLB (`xApp1`), CCO (`xApp2`), ES (`xApp3`), MRO (`xApp4`) |
| Model | 7 ICPs (`p1 … p7`), 4 KPIs (`o1 … o4`, plus `o1′`, `o2′` variants) |
| Generation | Gaussian KPI surfaces; `data1.csv`…`data4.csv` referenced |
| Shared ICP | `p1` (TXP), swept over `[-150, 150]` |
| Declared values | `p2 = 20`, `p3 = 60`, `p4 ∈ [-100, 100]`, `p5 = 60`, `p6 ∈ [-50, 150]`, `p7 = 60` |
| Predictor | Polynomial regression blocks |
| Utility | min–max ×10 |

### 5.2 `2405.07324v2`

| Item | Value |
|---|---|
| xApps | 5 (`x₁`…`x₅`), 8 ICPs, 6 KPIs |
| Generation | Gaussian surfaces with published closed forms (below) |
| Files | `data1.csv`…`data5.csv`, columns `ICPs, KPI, normalisedKPI, normalised_threshold` |
| Utility | z-score (`normalisedKPI`) |
| Predictor | ANN, benchmarked against polynomial regression |

Documented surfaces (`data/QACM/README.md`):

```
k1   =  80 · exp( −(p1)²              / (2 p2²) )
k2   = 100 · exp( −(p1 + p3)²         / (2 p2²) )
k3   = 120 · exp( −(p1 + 45)²         / (2 p4²) )
k41  = 120 · exp( −(p6 + (p2 − 30))²  / (2 p5²) )
k42  = 150 · exp( −(p6 + (p2 − 50))²  / (2 p5²) )
k5   = −35 · exp( −(p8 + (p1 − 25))²  / (2 p7²) )
```

QoS thresholds: `q1 = 55, q2 = 95, q3 = 85, q41 = 75, q42 = 80, q5 = −25`.
Declared ICP values: `p1 ∈ [−100,100]`, `p2 ∈ [−10,50]`, `p3 = −20`, `p4 = 60`,
`p5 = −20`, `p6 ∈ [−50,150]`, `p7 = 60`, `p8 ∈ [−100,150]`.

---

## 6. What is actually in this repository

`data/QACM/` holds five files whose mapping to the paper is recoverable from
their value ranges and verifiable against the formulas (full derivation in
[`ICP-MAPPING-AND-TESTBED-DATA.md`](ICP-MAPPING-AND-TESTBED-DATA.md) §3):

| File | Shape | Reconstructed mapping |
|---|---|---|
| `data1.csv` | 10 000 × 5 | `(p1, p2) → k1` |
| `data2.csv` | 10 000 × 6 | `(p1, p2, p3 = −20) → k2` |
| `data3.csv` | 10 000 × 5 | `(p1, p4 = 60) → k3` |
| `data4.csv` | 10 000 × 10 | `(p6, p5 = −20, p2, p2) → k41, k42` |
| `data5.csv` | 10 000 × 6 | `(p8, p7 = 60, p1) → k5` |

Consequences for use as a Wadud substrate:

- The files carry QACM's z-score columns, not Wadud's min–max utilities.
- `data1`–`data3` span `p1 ∈ [−100, 100]` — QACM's range, not Wadud's
  `[−150, 150]`.
- `data4`/`data5` cannot be loaded by the current single-output `DatasetSpec`.
- `data4.csv` carries a duplicated `Input3`/`Input4` column.
- The files are z-scored on their own 10 000-point sampling, so their
  `normalised_threshold` is not transferable to a different grid.

So the shipped QACM data cannot serve as a drop-in Wadud dataset. That
provenance gap drove the data additions below.

---

## 7. Data we added for the new scenarios

### 7.1 Deterministic scalar projections

`scripts/gen_wadud_datasets.py` (seed 42, 301 points) evaluates the documented
surfaces over `p1 ∈ [−150, 150]` at declared fixed values and writes
`data/wadud/xapp1.csv` … `xapp5.csv`, each with a single `Input1,Output` pair.

`data/wadud/metadata.json` records the seed, point count, range, declared
constants, source equations and a `status: provisional` flag. The generator is
noiseless and deterministic; the seed is part of the reproducibility contract,
not a random component.

| File | KPI | Output range |
|---|---|---|
| `xapp1.csv` | `k1` | 0 – 80 |
| `xapp2.csv` | `k2` | 0 – 100 |
| `xapp3.csv` | `k3` | 0.61 – 120 |
| `xapp4.csv` | mean(`k41`,`k42`) | 125.36 – 125.36 (**constant in `p1`**) |
| `xapp5.csv` | `k5` | −35 – −0.5 |

This is a *scalar projection*, not synthetic data invented to fit results: every
non-shared input is held at a declared paper value rather than silently zeroed.
The alternative — dropping the second feature of a two-feature file — would have
introduced an undocumented zero.

**Known defect:** `metadata.json` mixes the two papers' symbol tables. It applies
QACM's equations but fills `p3 = 60`, `p5 = 60`, `p7 = 60` from Wadud's table,
where QACM defines `p3 = p5 = −20`; `p8` does not exist in Wadud and is set to
`0`. The projections therefore need regenerating from one consistent table.

### 7.2 Scenario registry (`surrogate_xapps/scenarios.py`)

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

### 7.3 Evaluation harness

`surrogate_xapps/evaluate.py` runs `qacm`, `am`, `nswf`, `eg` on identical xApps,
grid, resolution and weights, and writes CSV plus Markdown. It currently emits 10
of the 13 specified metrics (see §9.3).

---

## 8. Fidelity: what reproduces, what does not

**The key structural point:** all three Wadud selectors and QACM are *selectors
over the same discrete candidate grid*. That is why a faithful comparison needs
no simulator and no training loop — only identical data, thresholds and grid.

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

### 8.1 Cause A — xApp4's surface is flat in `p1`

`k41`/`k42` depend on `p6`, `p2` and `p5` but **not on `p1`**. At fixed
`p6 = 0`, `p2 = 20`, xApp4's KPI is the constant 125.36, which produces the
`constant KPI has zero utility range` warning seen in the S3/S5 runs.

Consequence: the indirect scenario S3 (xApp2 vs xApp4 over `p1`) **cannot be
reproduced with the documented equations at the declared values**, because xApp4
has no `p1` response to collapse. Either xApp4 does not map to `k41/k42`, or
`p2`/`p6` — not `p1` — is the shared variable in that scenario.

### 8.2 Cause B — `k5` is a minimisation KPI but is evaluated as maximisation

`k5 = −35·exp(…)` is negative-valued and peaks at its most negative point.
Maximising it drives the xApp to the far tail of the range. The harness
(`evaluate.py`) hard-codes `objective="max"` for every Wadud xApp, so xApp5
cannot express its true preference. The utility module already supports
`objective="min"` inversion; the harness does not pass it. This is the same gap
as W2, now in our code.

### 8.3 Cause C — the xApp → KPI mapping is unverified

The current mapping (`xapp1→k1`, `xapp2→k2`, …) was a convenience choice, and it
cannot produce the published direct-conflict preferences (`−50` vs `+50`): `k1`
peaks at `0`, `k2` at `p1 = −p3`, `k3` at `−45`, and `k5` at `p1 = 25 − p8`.

### 8.4 Cause D — declared values are scenario-specific

The paper's constants are given for one setup, yet the indirect scenario says
"xApp2 sets `p1 = 0`" while the direct scenario has xApp2 demanding `+50`. The
same xApp cannot have both preferences under one constant assignment. The
constants are therefore scenario-dependent, and the single global table in
`metadata.json` is insufficient.

### 8.5 A testable mapping hypothesis (post-hoc, not yet a reproduction)

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
parameters were tuned against three targets, so it is a hypothesis, not evidence
of reproduction. It does, however, identify a specific, falsifiable next step:
confirm from the paper whether xApp1↔`k3`, xApp2↔`k5`, `p4 ≈ 41`, `p8 = −25`, and
whether `k5` is a minimised power KPI. If confirmed, S1 and S2 move from "not
reproduced" to "reproduced", and the same correction can be applied to S3/S4.

---

## 9. Reproduced faithfully / added / outstanding

### 9.1 Faithfully reproduced

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

### 9.2 What we added, and why

| Addition | Why it matters |
|---|---|
| Deterministic scalar projections of the paper surfaces (`data/wadud/`, seed 42, recorded constants) | Makes the paper's model testable on our scalar path without inventing or silently zeroing features |
| Unified baseline framework plugged into the existing xApp protocol | Enables a like-for-like comparison without forking the CMC |
| Multi-metric harness (`evaluate.py`): `p*`, utilities, regrets, welfare, Nash product, worst-off, spread, satisfaction counts, latency | Prevents the comparison from being a single-number scoreboard; the thesis claim needs both fidelity and QoS metrics |
| Out-of-sample scenarios S6/S7 | Tests generality on data the baselines were not designed around |
| Property/edge scenarios S8/S9 (scaffolded) | Checks NSWF invariance, EG monotonicity, zero-utility and constant-KPI handling |
| Tests and provenance docs | 128 tests pass; deviations and data status recorded rather than hidden |

### 9.3 Outstanding

| Item | Why it blocks | State |
|---|---|---|
| Confirm xApp ↔ KPI mapping | Determines every `p*`; current mapping cannot produce the published preferences | **Highest priority** |
| Confirm per-scenario declared values (`p4`, `p6`, `p8`) | The global table contradicts S1 vs S3 | Open |
| Regenerate `data/wadud/` from one consistent symbol table | Current metadata mixes Wadud and QACM parameter sets | Open |
| Pass per-xApp `objective` (`k5` must minimise) | xApp5 currently prefers the wrong end of the range | Open |
| Make S3 structurally possible | `k41/k42` are independent of `p1` | Open |
| Reproduce S1–S4 within ±5 or record `discrepancy_reason` | Acceptance criterion 4 | 0/4 today |
| Demonstrate QACM `n_satisfied ≥` baselines | The thesis claim | All methods currently tie at full satisfaction |
| Fix S8 registry paths | S8 points at `data/wadud/data1.csv`, which does not exist | Not runnable |
| Emit M3, M10, M11 | CSV stores 10/13 metrics; concession distance and weighted deviation are absent | Partial |
| Measure `deterministic` instead of hard-coding `True` | Reproducibility gate is asserted, not tested | Partial |
| Test `evaluate.py` | 0% coverage; harness bugs would ship silently | Open |

### 9.4 Current suite state

`uv run pytest` → **128 passed**. Coverage: total **83%**;
`baselines.py` 84%, `scenarios.py` 92%, `utility.py` 62%, `evaluate.py` 0%.

---

## 10. Bottom line

- **Wadud's design shortcomings are real and specific**: no QoS awareness, an
  anchor-dependent and direction-blind utility, pairwise-only scope, exogenous
  weights, a weak predictor, the wrong reported metric, and synthetic-only
  validation (W1–W7).
- **QACM addresses the central one structurally, not by tuning.** The
  satisfaction term makes the objective effectively lexicographic from the second
  satisfied xApp onward, which NSWF and EG cannot express at any weight (§3.1).
  It addresses W2, W3, W5, W6 and W7 directly, and W4 only in principle.
- **It does not address its own limits**: weights remain exogenous, there is no
  RIC, the solution is grid-optimal, latency is unmeasured, and the z-score
  threshold is sample-dependent (§4).
- **The comparison machinery here is faithful and in place**: the three Wadud
  selectors and QACM share one grid, one dataset and one metric schema.
- **The paper data is not yet faithfully reproduced**: 0 of 10 published
  operating points match, because of a flat xApp4 surface, a
  maximised-instead-of-minimised `k5`, an unverified xApp/KPI mapping, and
  mixed symbol tables in our metadata (§8).
- A concrete two-parameter hypothesis recovers the S1/S2 triplet inside
  tolerance, which turns "reproduction failed" into a specific, checkable next
  step rather than an open-ended gap.
- **The contribution is methodological**, not a reimplementation of the CMS: a
  modular, metric-complete, deterministic comparison harness with explicit
  provenance and documented deviations.
