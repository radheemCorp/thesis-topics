# Iteration 3: A2C Scheduler vs. QACM — Comparative Evaluation

**Slide deck for the iter-3 experiment proposal**

- Common scenario: **Power + RBG indirect conflict** (TXP + RBG allocation)
- Two mitigation paradigms: **action scheduling** (A2C) vs. **parameter bargaining** (QACM)
- Open decisions to resolve before implementation (Q1, Q4–Q10)

> Format: one slide per `---` block. Citations use `(filepath, line number)` and point into the repository docs. Full detail lives in `plan/iteration-3/spec.md`, `plan/iteration-3/implementation-plan.md`, `a2c-qacm/approach-and-implementation.md`, `a2c-qacm/iter-3-flow.md`, and `open-questions.md`.

---

## Agenda

1. Context & motivation
2. The two frameworks at a glance
3. Iteration history — why iter-3
4. Iter-3 approach & the common scenario
5. Testbed adaptation
6. Framework flows (A2C, QACM)
7. Evaluation metrics & baselines
8. Open questions (Q1–Q10)
9. Decision summary & next steps

---

## Context & Motivation

- O-RAN disaggregates the RAN and lets **third-party xApps** run inside the **Near-RT RIC** (10 ms – 1 s control loops).
- Independent xApps each pursue a narrow objective → **uncoordinated control loops** that oscillate parameters and degrade KPIs.
- Central question of the repository: *"How can independently developed SON xApps safely share RAN control while preserving their objectives, QoS/SLA requirements, and near-real-time constraints?"* (README.md, 7)
- Two dominant runtime-mitigation paradigms are compared head-to-head on a **common scenario**:
  - **A2C Context-Aware Scheduler** — macro-level *action scheduling* (which xApps are active).
  - **QACM** — micro-level *parameter bargaining* (what compromise value to apply).

> **Notes:** The "So What?" example — a Power xApp and an RBG xApp both maximize the same KPM (normalized rate τe) but act on different NCPs, causing wasted power on unallocated RBGs and underpowered allocations (approach-and-implementation.md, 17).

---

## The Two Frameworks at a Glance

| | **A2C Context-Aware Scheduler** | **QACM** |
| :--- | :--- | :--- |
| **Role** | Macro-level action coordinator | Micro-level parameter bargaining engine |
| **Core engine** | Advantage Actor-Critic (A2C) DRL | Constrained optimization / heuristic + ANN KPI regression |
| **Input** | Context $c^\dagger=[d,v]$ + intent $f^\dagger$ | Joint vector $\mathbf{p}=[p_{power},p_{RBG}]$ + context $(d,v)$, QoS thresholds $q'$, weights $w_i$ |
| **Output** | xApp activation mask $\mu^\dagger \in \{0,1\}^n$ | Optimal joint compromise $\mathbf{p}^{opt}$ via E2SM-RC |
| **QoS guarantee** | System-wide (native reward $\tau_e$) | Explicit per-xApp QoS threshold satisfaction |
| **Re-training** | Lightweight scheduler only; xApps immutable | ANN regression models per xApp |
| **Fidelity (iter-3)** | **As published** (2504.06867v3) | **Extended** (joint-parameter bargaining, context ANN, scalarized RBG) |

(approach-and-implementation.md, 74-77, 209-217; plan/iteration-3/spec.md, 18-26)

---

## Iteration History — Why iter-3

| Iteration | Common scenario | Problem |
| :--- | :--- | :--- |
| **iter-1** | Undecided | Left the common evaluation scenario open (plan/iteration-index.md, 15-22) |
| **iter-2** (Proposal A) | QACM scenario: ES vs. CCO direct conflict over TXP | Adapted the A2C scheduler to it → **distorted A2C**: reward redesign, conflict-type extension, destroyed Method 1/2 semantics, no compromise granularity (plan/iteration-index.md, 72-74) |
| **iter-3** (Proposal B) | **A2C scenario**: Power + RBG indirect conflict | Keeps A2C as published; **extends QACM** to joint-parameter bargaining (plan/iteration-index.md, 76-94) |

> **Notes:** The pivot rationale is fully documented in open-questions.md Q2 (48-134). iter-2's Proposal A made the comparison structurally asymmetric in the wrong direction — the A2C side was modified while QACM ran as published.

---

## Iter-3 Approach (Proposal B)

**Decision:** the **A2C scenario** is the common scenario; QACM is extended to joint-parameter bargaining (open-questions.md, 91-115, 129-133).

Why this direction:

1. **A2C runs exactly as published** — native reward (normalized rate $\tau_e$), Method 1/2 semantics, activation masks, pre-trained immutable xApps. No reward redesign → Q3 becomes moot (open-questions.md, 96).
2. **QACM's design intent covers the scenario** — the paper explicitly handles direct/indirect/implicit conflicts and its §VII-C case study evaluates indirect conflicts (open-questions.md, 97).
3. **Context is native** — $c^\dagger=[d,v]$ is passed into QACM's ANN as features, so both paradigms are context-aware (open-questions.md, 98).
4. **The macro-vs-micro asymmetry becomes the intended finding** — activation scheduling vs. parameter bargaining — instead of a distortion (open-questions.md, 99).

**Accepted QACM-side extensions (reported in the thesis):** joint-parameter bargaining, context-conditioned ANN, scalarized RBG allocation, QoS thresholds defined for the A2C scenario (plan/iteration-index.md, 85).

---

## The Common Scenario (iter-3)

**Power xApp ($X_1$) + RBG xApp ($X_2$) — indirect conflict over TXP and RBG allocation** (plan/iteration-3/spec.md, 30-41):

- $X_1$ (Power) maximizes the normalized transmission rate $\tau_e$ by setting per-cell TXP.
- $X_2$ (RBG) maximizes $\tau_e$ by allocating RBGs to users.
- **Conflict triggers** (paper): the Power xApp assigns power to RBGs not allocated to any user (wasted power); the RBG xApp assigns many RBGs to users that receive low power (underpowered allocation) → throughput drops, leftover bits accumulate (approach-and-implementation.md, 17).
- **QoS thresholds (defined for the A2C scenario):** $q_1$: $\tau_e \geq 0.9$; $q_2$: leftover-bits ratio $\leq 0.05$ (plan/iteration-3/spec.md, 69).
- **Reference result to reproduce (qualitative):** Method 2 ≥ Method 1 > conflicting on $\tau_e$; conflict severity context-dependent (16% degradation at high load/speed vs. 5% at low) (plan/iteration-3/spec.md, 41).

---

## Testbed Adaptation

| Parameter | Paper (2504.06867v3) | Iter-3 Testbed |
| :--- | :--- | :--- |
| Topology | 4 O-RUs, 16 UEs | **2 gNBs, 10 UEs** |
| Carrier / RBGs | 20 MHz, 12 RBGs per O-RU | 20 MHz, 12 RBGs per gNB |
| Power range | $P \in [1, 38]$ dBm, $K$ levels | $p_{power} \in [1, 38]$ dBm, $K$ levels |
| Time step / period | $T_s = 100$ ms, scheduling period 10 | 100 ms steps, scheduling period 10 (1 s) |
| Episode | $T = 50$ time steps (5 s) | $T = 50$ time steps (5 s) |
| Simulation length | — | 10 min at 100 ms steps |

(approach-and-implementation.md, 53-60)

**Context variables:** training $d \in \{3,5,7,9\}$ Mbps × $v \in \{10,20,30,40\}$ m/s; test $d \in \{2,5,8\}$ × $v \in \{5,25,45\}$ → **9 test combinations** (plan/iteration-3/spec.md, 43-47).

> **Notes:** The 2 gNB / 10 UE reduction is a deliberate design choice (≥2 cells needed for the interference-mediated conflict; scale kept tractable), not a hard constraint — the existing export has 10 cells / 49 UEs (data/data-report.md, 17). It also matches the QACM paper's own 2 gNB / 10 UE simulation. Caveat: the physical ICS testbed is single-cell (approach-and-implementation.md, 62-68).

---

## Flow A: A2C Scheduler (as published)

Full flow: a2c-scheduler-flow.md (46-66); iter-3 adaptation: iter-3-flow.md §2.

- **State:** $s^\dagger = [c_1^\dagger, c_2^\dagger, f^\dagger] = [d, v, \text{intent}]$ (context via simulated A1 EI).
- **Actor** $\pi_\theta(a^\dagger|s^\dagger)$ → distribution over activation mask $\mu^\dagger \in \{0,1\}^n$.
- **Critic** $V_\phi(s^\dagger)$ → baseline; **Advantage** $A = G_{\dagger:\dagger+1} - V_\phi(s^\dagger)$.
- **Confidence-gated fallback:** EWMA of critic mean/dispersion; z-score below MNO threshold → deterministic $\pi_{safe}$ for $T_{back}$ decisions; stats frozen (a2c-scheduler-flow.md, 61).
- **Method 1** (retain previous action) / **Method 2** (baseline extension over $\{X_1,X_2,X_3,X_4\}$, $\mu_1+\mu_3=1$, $\mu_2+\mu_4=1$) (a2c-scheduler-flow.md, 63-65).
- **Reward (native):** $\tau_e = \frac{\sum_t \tau_{t,e}}{d_e \cdot R \cdot B}$ — no redesign (Q3 moot).
- **Training:** policy gradient + critic MSE, $\eta=10^{-4}$, $\gamma=0.95$, $10^5$ episodes, $T=50$, period 10; only the scheduler is re-trained, xApps immutable (a2c-scheduler-flow.md, 66).

---

## Flow B: QACM (extended to joint-parameter bargaining)

Full flow: qacm-flow.md (53-63); iter-3 adaptation: iter-3-flow.md §3.

- **CMS framework:** PMon, CDC, CMC, CS xApp + DB (RCP, PGD, RCPG, PKR, DCKD, KDO) (qacm-flow.md, 55-63).
- **Joint control vector:** $\mathbf{p} = [p_{power}, p_{RBG}]$, $p_{power} \in [1,38]$ dBm, $p_{RBG} \in \{0,\dots,12\}$ (scalarized).
- **Context-conditioned ANN:** predicts KPIs ($\tau_e$, leftover bits) from $(\mathbf{p}, d, v)$ — 4×128, tanh, dropout 0.2, Adam, MSE, 10 epochs (qacm-flow.md, 58).
- **Utility:** z-score $U(\mathbf{p}) = (k(\mathbf{p})-\mu)/\sigma$, range $[-3,+3]$ (qacm-flow.md, 59).
- **Objective:** $\min_{\mathbf{p}} \sum_i w_i d_i \zeta - (\sum_i s_i)^2$ over the joint range; **exact** = 2D search ($|P| \times (R+1)$ candidates); **heuristic** = 2D-grid search $O(N \cdot |X'|)$ (qacm-flow.md, 60-62).
- **Dispatch:** $\mathbf{p}^{opt} = [p_{power}^{opt}, p_{RBG}^{opt}]$ via E2SM-RC; PMon → KDO loop on new degradation (qacm-flow.md, 63, 67-69).

---

## Iter-3 Deviations from the Paper Flows

| Aspect | Paper flow | Iter-3 flow |
| :--- | :--- | :--- |
| Common scenario | A2C: Power+RBG (4 O-RUs/16 UEs); QACM: ES vs CCO over TXP | **Single common scenario** (2 gNBs / 10 UEs) |
| A2C reward | Native $\tau_e$ | Same — no redesign (Q3 moot) |
| QACM bargaining space | Single scalar $p_l$ | **Joint vector** $\mathbf{p} = [p_{power}, p_{RBG}]$ |
| QACM KPI prediction | ANN from $p_l$ only | **Context-conditioned ANN** $(\mathbf{p}, d, v)$ |
| QACM RBG handling | Not applicable | **Scalarized** $p_{RBG} \in \{0,\dots,12\}$ |
| QACM QoS thresholds | SLA-derived | **Defined for A2C scenario:** $q_1$, $q_2$ |
| QACM solver | Single-parameter MILP / Heuristic Alg. 1 | **2D search** / **2D-grid heuristic** |
| Leftover bits | Native per-RBG discard model | **Derived:** $L = \max(0, d - \sum_u R_{u,t})$ |
| A1 EI | Non-RT RIC | **Simulated** (no Non-RT RIC in testbed) |

(iter-3-flow.md §4)

---

## Evaluation Metrics & Baselines

**Metrics** (plan/iteration-3/spec.md, 192-198):
- Normalized transmission rate $\tau_e$ and leftover (discarded) bits.
- Per-xApp QoS satisfaction $s_i$ and KPI shortfall $d_i$ (thresholds $q_1$, $q_2$).
- Control-policy volatility: COV, SD, RMSSD of TXP and RBG series.
- Mitigation latency: QACM solver/ANN vs. A2C forward pass (vs. 10 ms–1 s budget).
- Conflict rate and context-dependence (low vs. high load/speed).

**Methods / baselines** (plan/iteration-3/spec.md, 180-185):
- Conflicting independent deployment (no mitigation), A2C M1, A2C M2, QACM, QACMP, NSWF, EG, baseline policies $X_3$/$X_4$.

**Run matrix:** 9 test scenarios × 7 methods × N repetitions, fixed seeds, isolated runs under identical conditions (plan/iteration-3/spec.md, 187-190).

**Acceptance criteria:** both engines run end-to-end on ns-O-RAN; A2C reproduces M2 ≥ M1 > conflicting; QACM satisfies more QoS thresholds than NSWF/EG; latency within budget; reproducible (plan/iteration-3/spec.md, 254-261).

---

## Open Questions — Overview

| # | Question | Status | Decide before |
| :--- | :--- | :--- | :--- |
| Q1 | QACM fallback when no compromise satisfies QoS | **OPEN** | Phase 4 (implementation-plan.md, 95) |
| Q2 | Common evaluation scenario | **RESOLVED** → Proposal B | — |
| Q3 | A2C reward | **MOOT** (native $\tau_e$) | — |
| Q4 | QoS thresholds for the A2C scenario | **OPEN** | Phase 2 / 4 |
| Q5 | Scalarized RBG allocation definition/enforcement | **OPEN** | Phase 2 / 4 |
| Q6 | QACM joint-parameter optimization formulation | **OPEN** | Phase 4 |
| Q7 | Power xApp control granularity | **OPEN** | Phase 2 |
| Q8 | Context-conditioned ANN training data / leakage | **OPEN** | Phase 2.6 |
| Q9 | Testbed scenario parameters | **OPEN** | Phase 0.6 |
| Q10 | Leftover-bits KPI derivation | **OPEN** | Phase 1.2 |

(open-questions.md, 7-423)

---

## Q1 — QACM Fallback (OPEN)

**Question:** What happens when no compromise value is found that satisfies the QoS requirements? (open-questions.md, 7-46)

**Context:** The search space is the bounded joint range, so QACM *always* returns a $\mathbf{p}^{opt}$ — a strictly infeasible case cannot occur. The unhandled case is weaker: the best compromise still leaves some/all xApps below their QoS thresholds ($s_i = 0$). Neither the paper nor the flowchart specifies what the CMC does then (open-questions.md, 11-25).

**Candidates:**

| Option | Behavior | Trade-off |
| :--- | :--- | :--- |
| (a) Dispatch-and-log | Send $\mathbf{p}^{opt}$ anyway; record shortfall in KDO | Faithful to paper; may violate QoS/SLA |
| (b) Reject-and-keep-previous | Block control; retain last parameter values | Safe; freezes network at possibly stale values |
| (c) Escalate to CS xApp / MNO policy | Defer to supervision layer / operator intent | Adds a component the paper only envisions |

**Comparison note:** the A2C scheduler already has a safety net — the confidence-gated fallback (EWMA critic z-score → $\pi_{safe}$) (open-questions.md, 34-40). The chosen QACM fallback (or its absence) is a legitimate comparison point and should be reported in the thesis.

---

## Q2 — Common Scenario (RESOLVED → Proposal B)

**Question:** Which scenario should be the common evaluation scenario for both methods? (open-questions.md, 48-134)

**Why Proposal A (iter-2) was rejected:** adapting the A2C scheduler to the QACM scenario (ES vs. CCO over TXP) required a reward redesign, a conflict-type extension, destroyed Method 1/2 semantics, and produced a discrete selector that cannot express a continuous compromise (open-questions.md, 63-70).

**Decision (iter-3):** **Proposal B** — the A2C scenario (Power + RBG indirect conflict) is the common scenario; QACM is extended to joint-parameter bargaining (open-questions.md, 129-133).

| Dimension | Proposal A (QACM scenario) | Proposal B (A2C scenario) |
| :--- | :--- | :--- |
| A2C fidelity | Modified | **As published** |
| QACM fidelity | **As published** | Extended (joint-vector, context ANN, scalarized RBG) |
| Context | Re-derived | Native $(d,v)$ for both |
| Q3 (A2C reward) | Required | Moot |
| Main risk | A2C distortion | QACM extension complexity |

(open-questions.md, 117-127)

---

## Q3 — A2C Reward (MOOT)

**Question:** What reward should the A2C scheduler use in the QACM scenario? (open-questions.md, 136-157)

**Status:** **Moot under Proposal B (iter-3)** — the A2C scenario keeps the native reward (normalized rate $\tau_e$); no redesign needed (open-questions.md, 139).

**Why it was a question:** in the QACM scenario (ES vs. CCO over TXP), the scheduler would have to balance two opposing objectives (throughput vs. power), so a single-rate reward would be insufficient. Candidates considered (QoS satisfaction, weighted throughput+power, rate+power penalty) are now irrelevant (open-questions.md, 141-151).

---

## Q4 — QoS Thresholds for the A2C Scenario (OPEN)

**Question:** What QoS thresholds should be defined for the A2C scenario? (open-questions.md, 160-180)

**Context:** The A2C paper has no QoS thresholds (it optimizes $\tau_e$). QACM's objective is QoS-threshold satisfaction ($s_i$), so thresholds must be defined to make QACM's objective and the comparison meaningful (open-questions.md, 164-166).

**Candidates:**

| Option | Thresholds | Trade-off |
| :--- | :--- | :--- |
| (a) Spec defaults | $q_1$: $\tau_e \geq 0.9$; $q_2$: leftover $\leq 0.05$ | Simple; arbitrary — must be justified and sensitivity-tested |
| (b) Data-driven | Set from the conflicting-baseline distribution (e.g., median $\tau_e$) | Anchored to scenario; thresholds vary per context, complicating comparison |
| (c) MNO-policy | Operator intent (e.g., $\tau_e \geq 0.85$, leftover $\leq 0.10$) | Realistic; adds a policy-design dimension |

**Decide:** Phase 2 / Phase 4 (implementation-plan.md, 45-59, 81-98). A sensitivity analysis over threshold values is recommended (open-questions.md, 179).

---

## Q5 — Scalarized RBG Allocation (OPEN)

**Question:** How is the scalarized RBG allocation ($p_{RBG}$) defined and enforced? (open-questions.md, 182-203)

**Context:** The A2C paper's RBG allocation is combinatorial (which RBGs, which UEs). QACM bargains over a scalar $p_{RBG} \in \{0,\dots,12\}$ RBGs per gNB. The mapping from scalar to actual allocation is unspecified, and E2SM-RC Style 2 exposes a PRB quota (percentage), not an RBG count (open-questions.md, 186-189).

**Candidates:**

| Option | Mapping | Trade-off |
| :--- | :--- | :--- |
| (a) Equal distribution | $p_{RBG}$ RBGs split evenly among active UEs | Simple; matches the paper's training baseline |
| (b) PRB-quota percentage | $p_{RBG}/12 \to$ PRB quota % via E2SM-RC Style 2 | Directly enforceable; loses RBG granularity |
| (c) Per-UE quota | $p_{RBG}$ as a per-UE RBG cap | Closer to the paper's per-user allocation; more complex |

**Decide:** Phase 2 / Phase 4 (implementation-plan.md, 52, 93). The scalarization is an accepted QACM-side extension; the mapping choice affects how fairly QACM's output is compared with the RBG xApp's combinatorial allocation (open-questions.md, 202).

---

## Q6 — QACM Joint-Parameter Optimization (OPEN)

**Question:** How is QACM's joint-parameter optimization formulated? (open-questions.md, 206-226)

**Context:** The paper's exact solver is single-parameter ($4|X'|$ vars, $4|X'|+2|N|+3$ constraints); its §VII-C indirect case study is still single-parameter. Bargaining over $\mathbf{p} = [p_{power}, p_{RBG}]$ requires a 2D search space; the formulation and its latency are unspecified (open-questions.md, 210-212).

**Candidates:**

| Option | Formulation | Trade-off |
| :--- | :--- | :--- |
| (a) 2D grid search | Enumerate $|P| \times (R+1)$ candidates, evaluate objective | Simple; exact for discrete ranges; latency grows with granularity |
| (b) MILP extension | Reformulate the paper's MILP over two parameters | Closer to the paper's exact solver; more implementation effort |
| (c) Alternating optimization | Optimize $p_{power}$ then $p_{RBG}$ iteratively | Fast; may miss joint optima |

**Decide:** Phase 4 (implementation-plan.md, 91-92). NSWF/EG benchmarks must use the same joint-vector machinery for a fair comparison (open-questions.md, 225). **Note:** Q7 constrains this — $p_{power}$ must be scalar for the joint-vector approach (open-questions.md, 285).

---

## Q7 — Power xApp Control Granularity (OPEN)

**Question:** What control granularity does the Power xApp use? (open-questions.md, 229-286)

**Context:** The paper's Power xApp allocates power **per RBG** ($p_{b,r,u}$); the testbed likely supports only **per-cell TXP** (E2SM-RC Style 8, unverified). Granularity changes the conflict structure and QACM's $p_{power}$ dimensionality (open-questions.md, 233-240).

**Candidates:**

| Option | Granularity | Trade-off |
| :--- | :--- | :--- |
| (a) Per-cell TXP | Single TXP per gNB | Implementable; fits QACM's scalar $p_{power}$; diverges from the paper's per-RBG power and loses trigger 1 (wasted power) |
| (b) Per-RBG power | Power per RBG (paper) | Faithful to the paper; likely unsupported in ns-O-RAN; breaks QACM's scalar bargaining |
| (c) Per-UE power | Power per UE | Middle ground; preserves per-user triggers; $U$-dim action space; breaks QACM's scalar bargaining |

**Decide:** Phase 2 (implementation-plan.md, 51). Primary determinant = Phase 0 feasibility of E2SM-RC power control (open-questions.md, 266). The granularity choice also constrains Q6 (joint-parameter formulation) (open-questions.md, 285).

---

## Q8 — Context-Conditioned ANN Training Data (OPEN)

**Question:** How is the context-conditioned ANN training data generated, and are test contexts excluded? (open-questions.md, 288-309)

**Context:** QACM's ANN predicts KPIs from $(\mathbf{p}, d, v)$. Training data must be generated via TXP × RBG sweep runs across context values. The sweep size and the train/test context split determine generalization and fairness (open-questions.md, 292-294).

**Candidates:**

| Option | Sweep design | Trade-off |
| :--- | :--- | :--- |
| (a) Training contexts only | Sweep over $d \in \{3,5,7,9\}$, $v \in \{10,20,30,40\}$ | No leakage; ANN must generalize to test contexts |
| (b) All contexts | Sweep over training + test contexts | Better ANN; risks data leakage into the test set |
| (c) Coarse grid | Sweep over a coarse $(d,v)$ grid, interpolate | Fewer runs; interpolation error |

**Decide:** Phase 2.6 / Phase 4.3 (implementation-plan.md, 56, 89). The A2C scheduler is trained on training contexts only; QACM's ANN should follow the same split for fairness (open-questions.md, 308).

---

## Q9 — Testbed Scenario Parameters (OPEN)

**Question:** Which testbed scenario parameters best approximate the A2C paper? (open-questions.md, 312-373)

**Context:** The paper's simulation is a **simplified Python model** (4 O-RUs, 16 UEs, 900 m ISD, analytic propagation, Poisson-per-RBG arrivals); the testbed is a **full-stack ns-3 simulator**. Exact reproduction is impossible — only qualitative reproduction is feasible (open-questions.md, 316-350). The existing export has 10 cells / 49 UEs, so the 2 gNB / 10 UE reduction is itself a design choice (open-questions.md, 337).

**Candidates:**

| Option | Parameters | Trade-off |
| :--- | :--- | :--- |
| (a) Paper-like | ISD 900 m, 3GPP propagation, 12 RBGs/gNB | Closest to the paper; may not fit the testbed topology |
| (b) Testbed-native | Testbed defaults (existing ns-O-RAN config) | Fits the testbed; diverges from the paper |
| (c) Calibrated | Tune ISD/propagation to reproduce the paper's qualitative ordering | Best of both; extra calibration effort |

**Decide:** Phase 0.6 (implementation-plan.md, 21). Acceptance criterion 3 (M2 ≥ M1 > conflicting) is qualitative; exact degradation percentages are not required (open-questions.md, 372).

---

## Q10 — Leftover-Bits KPI Derivation (OPEN)

**Question:** How is the leftover-bits KPI derived? (open-questions.md, 375-423)

**Context:** The paper's discard model is **per-RBG, per-user, per-time-slot**; the testbed has no per-RBG throughput (finest signal is per-UE PDCP $R_{u,t}$, currently missing from exports). The spec's proposed derivation $L = \max(0, d - \sum_u R_{u,t})$ is a **cell-level** approximation that collapses the per-RBG discard model (open-questions.md, 379-400).

**Candidates:**

| Option | Derivation | Trade-off |
| :--- | :--- | :--- |
| (a) Cell-level | $L = \max(0, d - \sum_u R_{u,t})$ per gNB per period | Simple; needs $R_{u,t}$ (missing) + offered load $d$ |
| (b) Per-UE | $L_u = \max(0, d_u - R_{u,t})$ | Finer; needs per-UE offered load |
| (c) Per-RBG | Paper-faithful per-RBG discard | Faithful; needs per-RBG throughput (unavailable) |

**Decide:** Phase 1.2 (implementation-plan.md, 35). The derivation feeds both the leftover-bits metric and the $q_2$ threshold; the choice affects both paradigms equally (open-questions.md, 422).

---

## Decision Summary & Next Steps

**Decisions required before each phase** (implementation-plan.md, 10-161):

| Phase | Gate | Open questions |
| :--- | :--- | :--- |
| **Phase 0** | Verify E2SM-RC TXP (Style 8) + RBG/PRB quota (Style 2) control; scenario config | **Q9** (topology/parameters) |
| **Phase 1** | Data pipeline, leftover-bits, simulated A1 | **Q10** (leftover-bits derivation) |
| **Phase 2** | xApp training, KPI sweep datasets | **Q4** (QoS), **Q5** (RBG), **Q7** (granularity), **Q8** (ANN data) |
| **Phase 4** | QACM solver, fallback decision | **Q1** (fallback), **Q6** (joint optimization) |

**Suggested resolution order:**
1. **Q9** first — Phase 0 gate; determines the topology and scenario config.
2. **Q7** next — constrains Q6 (scalar $p_{power}$ needed for joint-vector bargaining) and the A2C actor action space.
3. **Q6** + **Q1** together — the solver formulation and the fallback behavior are the core QACM design.
4. **Q4, Q5, Q8, Q10** — data/metrics definitions; must be consistent across both paradigms for a fair comparison.

**Key risks to track:** R1 (TXP control unsupported — extend ns-O-RAN), R2 (RBG control unsupported), R5 (ANN drift), R6 (QACM fallback undefined) (implementation-plan.md, 178-191).