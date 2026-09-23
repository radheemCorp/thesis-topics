# Open Questions

Tracking unresolved design decisions for the A2C Scheduler vs. QACM experiment. Each entry records the question, the context, candidate resolutions, and where it must be decided.

---

## Q1. What happens when no compromise value is found that satisfies the QoS requirements?

**Status:** Open — decision required before Phase 4 (QACM implementation).

### Context

The QACM flowchart (`qacm-flow.md`) and the paper (2405.07324v2) contain **no branch for a missing compromise value**. This is by construction:

- The search space is the bounded range $[p_{min,opt}, p_{max,opt}]$ — the union of the conflicting xApps' parameter ranges.
- Both the exact solver and Heuristic Algorithm 1 iterate over that range and always return the value minimizing the objective.
- Therefore a strictly *infeasible* case cannot occur; QACM always produces a $p_l^{opt}$.

### The actual gap

The unhandled case is weaker: a compromise **exists** but is **unacceptable** — the best $p_l^{opt}$ still leaves some (or all) xApps below their QoS thresholds ($s_i = 0$). Neither the paper nor the flowchart specifies what the CMC does then:

- The objective implicitly returns "as close as possible" (the paper's wording: "meeting **or closely approaching** their respective QoS thresholds", 2405.07324v2:421).
- Section IX (limitations) only discusses KPI-prediction model simplicity — not the no-acceptable-compromise case.

### Candidate resolutions

| Option | Behavior | Trade-off |
| :--- | :--- | :--- |
| (a) Dispatch-and-log | Send $p_l^{opt}$ anyway; record the shortfall in KDO | Faithful to the paper; may violate QoS/SLA |
| (b) Reject-and-keep-previous | Block the control action; retain the last parameter value | Safe, but freezes the network at a possibly stale value |
| (c) Escalate to CS xApp / MNO policy | Defer the decision to the supervision layer or operator intent | Adds a component the paper only envisions; more complexity |

### Related: A2C scheduler fallback

The A2C scheduler already has a safety net for the analogous situation — a **confidence-gated fallback**:

- The critic's value $V_\phi(s)$ is tracked via an **EWMA** (exponentially weighted moving average) with forgetting factor $\beta$.
- When the critic value's **z-score** falls below an MNO-defined threshold, the learned action is overridden by a deterministic safe policy $\pi_{safe}$ (e.g., equal resource allocation, or the single xApp with the highest offline reward).
- This makes the A2C side robust to out-of-distribution states; QACM currently has no equivalent.

### Decision point

- **Where:** Phase 4 (QACM implementation) — `implementation-plan.md` task 4.x.
- **Risk register entry:** "QACM has no defined fallback when the best compromise satisfies zero QoS thresholds" (Medium/Medium).
- **Comparison note:** the chosen fallback (or its absence) is a legitimate point of comparison between the two paradigms and should be reported in the thesis.

---

## Q2. Which scenario should be the common evaluation scenario for both methods?

**Status:** Open — decision required before Phase 2 (xApp training).

### Context

The two papers use different scenarios:

- **QACM (2405.07324v2, §VIII):** ES vs. CCO **direct conflict over TXP** — a single shared scalar NCP. CCO maximizes downlink throughput (δ=0, threshold 9.5 Gbps), ES minimizes power consumption (δ=1, threshold 25 Wh). QACM bargains over the TXP value in [6, 40] dBm → 15/16 dBm.
- **A2C Scheduler (2504.06867v3):** Power xApp (X1) + RBG xApp (X2) **indirect conflict** — two *different* NCPs (TXP and RBG allocation) affecting the same KPM (throughput). The scheduler arbitrates via activation masks.

For an apples-to-apples comparison, both paradigms must run on the **same** scenario. Two directions are possible: implement the QACM scenario in the A2C scheduler, or implement the A2C scenario in QACM.

### Problems with implementing the QACM scenario in the A2C scheduler

1. **Reward redesign** — the A2C paper's reward is normalized transmission rate τe only; the ES/CCO scenario needs a multi-objective reward (throughput + power). This changes scheduler training fundamentally and introduces reward-weighting ambiguity.
2. **Conflict-type extension** — the A2C paper demonstrates an *indirect* conflict; arbitrating a *direct* conflict over one shared NCP goes beyond the paper's demonstrated use case, weakening the "reproducing the paper" claim.
3. **Opposing xApp objectives** — in the A2C paper both xApps maximize the same τe; ES and CCO have opposing objectives, so the xApp training setup diverges from the paper.
4. **No compromise granularity** — the scheduler is a discrete selector (activation mask), not a bargainer. It can only output one xApp's preferred TXP (or a retained previous value), never a true compromise like QACM's 15 dBm. The comparison would be structurally asymmetric.
5. **Method 1/2 semantics** — "retain previous action" and baseline extension were designed for the power+RBG case; baseline TXP policies (e.g., fixed mid-range) are an extra design decision not in the paper.
6. **Context mismatch** — the QACM scenario has UEs at 0–5 m/s and no explicit arrival rate; the A2C context (arrival rate, speed) must be re-derived or the scenario extended.

### Proposal A (iter-2): QACM scenario as the common scenario

Mapping the **QACM scenario** (ES vs. CCO over TXP) as the shared scenario, with the A2C scheduler adapted to arbitrate the direct TXP conflict.

**Rationale:**
- QACM's machinery (z-score utility curves over a scalar range, single-parameter optimization) fits **TXP** perfectly — TXP is a scalar NCP.
- The A2C scenario's RBG allocation is a **combinatorial assignment**, not a scalar parameter; QACM's scalar bargaining cannot express it naturally.
- The A2C scenario has **two NCPs** (TXP + RBG allocation); QACM optimizes a single $p_l$ per conflict.
- The A2C scheduler *can* be adapted to the direct TXP conflict (with the complications above), whereas QACM cannot be adapted to the RBG-allocation conflict without a fundamental redesign.

**Tradeoffs:**

| Pro | Con |
| :--- | :--- |
| QACM runs exactly as published (single-parameter bargaining, native objective, 15/16 dBm reference reproducible) | A2C is modified: reward redesign (Q3), conflict-type extension, discrete selector cannot express a continuous compromise |
| Single scalar NCP keeps the comparison simple | Method 1/2 semantics distorted; baseline TXP policies are an extra design decision |
| | Opposing xApp objectives diverge from the A2C paper's setup |
| | Context must be re-derived (QACM scenario has no context dimension) |

### Proposal B (iter-3): A2C scenario as the common scenario (QACM extended to joint-parameter bargaining)

Keeping the **A2C scenario** (Power xApp $X_1$ + RBG xApp $X_2$, indirect conflict over TXP and RBG allocation) as the shared scenario, with QACM extended to bargain over the **joint control vector** $\mathbf{p} = [p_{power}, p_{RBG}]$.

**Rationale:**
- A2C runs exactly as published: native reward (normalized rate $\tau_e$), Method 1/2 semantics, activation masks, pre-trained immutable xApps.
- QACM's framework is explicitly designed for direct/indirect/implicit conflicts (2405.07324v2:103, 204, 242) and its §VII-C case study evaluates indirect conflicts (2405.07324v2:356) — the two-NCP indirect conflict is within its design intent.
- Context $c^\dagger = [d, v]$ is passed into QACM's ANN as features alongside candidate parameter settings, so both paradigms are context-aware.
- The macro-vs-micro asymmetry (activation scheduling vs. parameter bargaining) becomes the intended comparison dimension, not a distortion.

**Required QACM extensions (beyond the paper):**
1. **Joint-parameter bargaining** — the paper's exact solver is formulated for a single NCP ($4|X'|$ vars, $4|X'|+2|N|+3$ constraints); the §VII-C indirect case study is still single-parameter ($p_2$). Bargaining over $[p_{power}, p_{RBG}]$ requires a 2D search space (MILP reformulation or 2D-grid heuristic).
2. **Context-conditioned ANN** — the paper's ANN predicts KPIs from candidate parameter settings only; adding $(d, v)$ as features is an extension.
3. **Scalarized RBG allocation** — the A2C paper's RBG allocation is combinatorial (which RBGs, which UEs); QACM bargains over a scalar "number of RBGs", simplifying the control space.
4. **QoS thresholds must be defined** — QACM's objective is QoS-threshold satisfaction ($s_i$); the A2C scenario has no QoS thresholds (it optimizes $\tau_e$). Target rate / leftover-bits thresholds must be defined to make QACM's objective and the comparison meaningful.

**Tradeoffs:**

| Pro | Con |
| :--- | :--- |
| A2C runs exactly as published (native reward, Method 1/2, activation masks) | QACM is extended: joint-parameter bargaining, context-conditioned ANN, scalarized RBG |
| No reward redesign → Q3 becomes moot | QACM's published algorithm is single-parameter; 2D search adds complexity and latency |
| Both paradigms context-aware via $c^\dagger = [d, v]$ | RBG scalarization loses the combinatorial structure of the A2C scenario |
| Macro-vs-micro asymmetry is the intended finding | QoS thresholds must be invented for the A2C scenario |
| A2C paper's $\tau_e$ / leftover-bits metrics directly reproducible | Testbed adaptation (2 gNBs/10 UEs vs. 4 O-RUs/16 UEs) needed regardless |

### Tradeoff comparison

| Dimension | Proposal A (QACM scenario) | Proposal B (A2C scenario) |
| :--- | :--- | :--- |
| A2C fidelity | Modified (reward, conflict type, Method 1/2) | **As published** |
| QACM fidelity | **As published** | Extended (joint-vector, context ANN, scalarized RBG) |
| Scenario | ES vs. CCO direct conflict over TXP | Power + RBG indirect conflict |
| Context | Re-derived for the QACM scenario | Native $(d, v)$ for both |
| Q3 (A2C reward) | Required | Moot |
| Paper reference case | QACM 15/16 dBm reproducible | A2C $\tau_e$ / leftover-bits reproducible |
| Main risk | A2C distortion | QACM extension complexity |

### Decision point

- **Where:** Phase 2 (xApp training) / Phase 3 (A2C scheduler) — `implementation-plan.md` tasks 3.x.
- **Risk register entry:** "Scenario mapping between the two papers" (add if not present).
- **Current direction (iter-3):** **Proposal B** — the A2C scenario is the common scenario; QACM is extended to joint-parameter bargaining. The QACM-side extensions are accepted and reported as such in the thesis.

---

## Q3. What reward should the A2C scheduler use in the QACM scenario?

**Status:** **Moot under Proposal B (iter-3)** — the A2C scenario keeps the native reward (normalized rate $\tau_e$); no redesign needed. Only relevant if Proposal A (QACM scenario) is chosen.

### Context

The A2C paper's reward is the normalized transmission rate $\tau_e$ only (2504.06867v3). In the QACM scenario (ES vs. CCO over TXP), the scheduler must balance **two opposing objectives** — CCO maximizes throughput, ES minimizes power — so a single-rate reward is insufficient.

### Candidate resolutions

| Option | Reward | Trade-off |
| :--- | :--- | :--- |
| (a) QoS satisfaction | Number of xApps meeting their QoS thresholds ($\sum s_i$) | **Aligns directly with QACM's objective** → fairest comparison; sparse (0/1/2) reward, harder to learn |
| (b) Weighted throughput + power | $\alpha \cdot \frac{R}{q_{CCO}} + (1-\alpha) \cdot (1 - \frac{P}{q_{ES}})$ | Dense reward, easier to learn; introduces weighting ambiguity ($\alpha$) |
| (c) Normalized rate + power penalty | $\tau_e - \lambda \cdot P$ | Stays close to the A2C paper; power penalty $\lambda$ is an extra design choice |

### Decision point

- **Where:** Phase 3, task 3.5 — `implementation-plan.md`.
- **Comparison note:** option (a) makes the two paradigms directly comparable (both optimize QoS satisfaction); options (b)/(c) favor the A2C side's learning dynamics but complicate the comparison.

---

## Q4. What QoS thresholds should be defined for the A2C scenario?

**Status:** Open — decision required before Phase 2 (xApp training) / Phase 4 (QACM).

### Context

The A2C paper has no QoS thresholds (it optimizes the normalized rate $\tau_e$). QACM's objective is QoS-threshold satisfaction ($s_i$), so thresholds must be defined for the A2C scenario to make QACM's objective and the comparison meaningful. The iter-3 spec proposes $q_1$: $\tau_e \geq 0.9$ and $q_2$: leftover ratio $\leq 0.05$, but these are invented values.

### Candidate resolutions

| Option | Thresholds | Trade-off |
| :--- | :--- | :--- |
| (a) Spec defaults | $q_1$: $\tau_e \geq 0.9$; $q_2$: leftover $\leq 0.05$ | Simple; arbitrary — must be justified and sensitivity-tested |
| (b) Data-driven | Set from the conflicting-baseline distribution (e.g., median $\tau_e$) | Anchored to the scenario; thresholds vary per context, complicating comparison |
| (c) MNO-policy | Define as operator intent (e.g., $\tau_e \geq 0.85$, leftover $\leq 0.10$) | Realistic; adds a policy-design dimension |

### Decision point

- **Where:** Phase 2 / Phase 4 — `implementation-plan.md` tasks 2.x, 4.x.
- **Comparison note:** the chosen thresholds directly determine the QoS-satisfaction metric (FR-8.2); a sensitivity analysis over threshold values is recommended.

---

## Q5. How is the scalarized RBG allocation ($p_{RBG}$) defined and enforced?

**Status:** Open — decision required before Phase 2 (RBG xApp) / Phase 4 (QACM dispatch).

### Context

The A2C paper's RBG allocation is combinatorial (which RBGs, which UEs). QACM bargains over a scalar $p_{RBG} \in \{0, \dots, 12\}$ RBGs per gNB. The mapping from scalar to actual allocation is unspecified, and E2SM-RC Style 2 exposes a PRB quota (percentage), not an RBG count.

### Candidate resolutions

| Option | Mapping | Trade-off |
| :--- | :--- | :--- |
| (a) Equal distribution | $p_{RBG}$ RBGs split evenly among active UEs | Simple; matches the paper's training baseline |
| (b) PRB-quota percentage | $p_{RBG}/12 \to$ PRB quota % via E2SM-RC Style 2 | Directly enforceable; loses RBG granularity |
| (c) Per-UE quota | $p_{RBG}$ as a per-UE RBG cap | Closer to the paper's per-user allocation; more complex |

### Decision point

- **Where:** Phase 2 / Phase 4 — `implementation-plan.md` tasks 2.2, 4.7.
- **Comparison note:** the scalarization is an accepted QACM-side extension; the mapping choice affects how fairly QACM's output is compared with the RBG xApp's combinatorial allocation.

---

## Q6. How is QACM's joint-parameter optimization formulated?

**Status:** Open — decision required before Phase 4 (QACM).

### Context

The paper's exact solver is single-parameter ($4|X'|$ vars, $4|X'|+2|N|+3$ constraints); the §VII-C indirect case study is still single-parameter ($p_2$). Bargaining over $\mathbf{p} = [p_{power}, p_{RBG}]$ requires a 2D search space. The formulation and its latency are unspecified.

### Candidate resolutions

| Option | Formulation | Trade-off |
| :--- | :--- | :--- |
| (a) 2D grid search | Enumerate $|P| \times (R+1)$ candidates, evaluate objective | Simple; exact for the discrete ranges; latency grows with granularity |
| (b) MILP extension | Reformulate the paper's MILP over two parameters | Closer to the paper's exact solver; more implementation effort |
| (c) Alternating optimization | Optimize $p_{power}$ then $p_{RBG}$ iteratively | Fast; may miss joint optima |

### Decision point

- **Where:** Phase 4 — `implementation-plan.md` tasks 4.5, 4.6.
- **Comparison note:** NSWF/EG benchmarks must use the same joint-vector machinery for a fair comparison.

---

## Q7. What control granularity does the Power xApp use?

**Status:** Open — decision required before Phase 2 (Power xApp).

### Context

The A2C paper's Power xApp allocates power **per RBG** ($p_{b,r,u}$): the action vector is a power level for every RBG of every O-RU (2504.06867v3:179–193). The RBG xApp allocates RBGs to users ($\delta_{b,r,u}$). Both xApps maximize the same KPM — the normalized transmission rate $\tau_e$ — and the indirect conflict has two specific triggers (2504.06867v3:295):

1. **Wasted power:** the Power xApp assigns power to RBGs that the RBG xApp did not allocate to any user → power consumed with no throughput contribution.
2. **Underpowered allocation:** the RBG xApp assigns many RBGs to a user while the Power xApp gives those RBGs low power → low SINR, low throughput.

Conflict severity is context-dependent (16% degradation at high load/speed vs. 5% at low). The testbed likely supports only **per-cell TXP** (E2SM-RC Style 8, unverified), so the granularity must be chosen.

### How the conflict structure changes with granularity

**Per-RBG power (paper, option b):**
- Conflict is **per-resource**: for each RBG, power and allocation must be consistent. Both triggers are fully expressible.
- Action space: $R$ power levels per O-RU (12 per O-RU in the paper) → the A2C actor outputs a per-RBG distribution.
- Interference is modeled at RBG granularity.
- **QACM interaction:** $p_{power}$ becomes a 12-dim vector → breaks QACM's scalar joint-vector bargaining (would force a combinatorial extension, see Q6).

**Per-cell TXP (testbed-feasible, option a):**
- Trigger 1 (**wasted power on unallocated RBGs) disappears** — TXP is cell-wide; there is no per-RBG power to waste.
- The conflict becomes **cell-level**: TXP sets the SINR floor for all allocated RBGs (signal power + inter-cell interference), while the RBG xApp decides which UEs get resources. The indirect structure is preserved — $X_1$'s TXP affects the throughput $X_2$'s allocation achieves, and $X_2$'s allocation affects the throughput $X_1$'s TXP achieves — but the mechanism is coarser.
- A **new trigger must be defined**, e.g. "TXP too low for the current allocation to meet the target rate" or "TXP high → interference-limited throughput while allocation is sparse."
- Action space: 1 scalar per gNB ($K$ levels) → simpler actor, faster training.
- Interference becomes a **cell-level dimension** (TXP affects neighbor cells' SINR).
- **QACM interaction:** $p_{power}$ is a clean scalar → fits the joint vector $[p_{power}, p_{RBG}]$ directly.

**Per-UE power (option c):**
- Middle ground: power per UE ≈ power on that UE's allocated RBGs.
- Trigger 2 is preserved per-user (many RBGs, low power → low throughput); trigger 1 is partially preserved (power on UEs with no RBGs).
- Action space: $U$ power levels per gNB.
- **QACM interaction:** $p_{power}$ becomes a $U$-dim vector → again breaks scalar bargaining.

### What needs to be determined to answer Q7

1. **Feasibility (Phase 0 gate):** which granularity does ns-O-RAN's E2SM-RC actually support — per-cell TXP, per-RBG power, or per-UE power? This is the primary determinant.
2. **Conflict preservation:** does the chosen granularity keep the conflict *indirect* (two NCPs → same KPM) and *context-dependent*? Verify the conflicting baseline shows degradation that varies with $(d, v)$.
3. **Conflict-trigger re-expression:** define the concrete trigger(s) for the chosen granularity (the paper's two triggers are per-RBG).
4. **Actor action space:** the number of power actions per gNB (1 vs. $R$ vs. $U$) — affects the A2C actor output and training cost.
5. **QACM interaction (Q6):** $p_{power}$ must be a scalar for QACM's joint-vector bargaining; per-RBG/per-UE power would force a vector extension.
6. **Interference modeling:** the testbed channel model must capture inter-cell interference for TXP to be a meaningful NCP.
7. **Empirical validation:** confirm the conflicting baseline reproduces the paper's qualitative ordering (Method 2 ≥ Method 1 > conflicting) under the chosen granularity.

### Candidate resolutions

| Option | Granularity | Trade-off |
| :--- | :--- | :--- |
| (a) Per-cell TXP | Single TXP per gNB | Implementable; fits QACM's scalar $p_{power}$; diverges from the paper's per-RBG power and loses trigger 1 |
| (b) Per-RBG power | Power per RBG (paper) | Faithful to the paper; likely unsupported in ns-O-RAN; breaks QACM's scalar bargaining |
| (c) Per-UE power | Power per UE | Middle ground; preserves per-user triggers; $U$-dim action space; breaks QACM's scalar bargaining |

### Decision point

- **Where:** Phase 2 — `implementation-plan.md` task 2.1.
- **Comparison note:** the conflict trigger (power assigned to RBGs not allocated to users) depends on the granularity; per-cell TXP weakens this specific trigger. The granularity choice also constrains Q6 (QACM's joint-parameter formulation), since $p_{power}$ must be scalar for the joint-vector approach.

---

## Q8. How is the context-conditioned ANN training data generated, and are test contexts excluded?

**Status:** Open — decision required before Phase 2.6 (KPI sweep).

### Context

QACM's ANN predicts KPIs from $(\mathbf{p}, d, v)$. Training data must be generated via TXP × RBG sweep runs across context values. The sweep size and the train/test context split determine generalization and fairness.

### Candidate resolutions

| Option | Sweep design | Trade-off |
| :--- | :--- | :--- |
| (a) Training contexts only | Sweep over $d \in \{3,5,7,9\}$, $v \in \{10,20,30,40\}$ | No leakage; ANN must generalize to test contexts |
| (b) All contexts | Sweep over training + test contexts | Better ANN; risks data leakage into the test set |
| (c) Coarse grid | Sweep over a coarse $(d, v)$ grid, interpolate | Fewer runs; interpolation error |

### Decision point

- **Where:** Phase 2.6 / Phase 4.3 — `implementation-plan.md`.
- **Comparison note:** the A2C scheduler is trained on the training contexts only; QACM's ANN should follow the same split for fairness.

---

## Q9. Which testbed scenario parameters best approximate the A2C paper?

**Status:** Open — decision required before Phase 0.6 (scenario config).

### Context

The paper's simulation environment (2504.06867v3, Table I) is a **simplified Python model**, not a full-stack simulator:

| Parameter | Paper value |
| :--- | :--- |
| O-RUs ($B$) | 4 |
| Inter-site distance | 900 m |
| RBs | 100, each with 12 subcarriers |
| RBGs ($R$) | 12 per O-RU |
| Carrier | 20 MHz |
| Power range | $P \in [1, 38]$ dBm |
| AWGN | −114 dBm |
| Propagation | $120.9 + 37.6 \log_{10}(\omega)$ dB, log-normal shadowing 8 dB |
| Traffic | Poisson arrivals, mean $d_e \in \{3,5,7,9\}$ Mbps per RBG |
| Users ($U$) | 16, evenly distributed, 150–450 m from their O-RU |
| Speed | $v \in [1, 50]$ m/s, direction-change probability $\rho = 0.3$ |
| Episode / slot | $T = 50$ time steps, $T_s = 100$ ms, scheduling period 10 |

The **testbed reality** differs on three axes:

1. **Topology:** the existing ns-O-RAN export (`data-report.md`) has **10 serving cells and 49 UEs**, not the spec's proposed 2 gNBs / 10 UEs. The spec's reduction is itself a design choice.
2. **Fidelity:** ns-3 is a full protocol-stack simulator with 3GPP channel models; the paper is a simplified analytic model. Exact reproduction of the paper's numbers is impossible — only qualitative reproduction is feasible.
3. **Traffic/mobility:** the paper's Poisson-per-RBG arrivals and constant-speed-with-direction-change mobility must be mapped onto ns-3's traffic and mobility models.

**What each parameter affects:**

- **ISD** → inter-cell interference level → conflict severity (the indirect conflict is interference-mediated).
- **Propagation model** → SINR distribution → achievable $\tau_e$.
- **RBG count** → action granularity for both xApps and QACM's $p_{RBG}$ (12/gNB vs. the standard 25 RBGs at 20 MHz with RBG size 4).
- **UE count/placement** → load distribution and congestion.
- **Traffic model** → offered load $d$ → leftover bits and $\tau_e$ normalization.
- **Mobility** ($v$, $\rho$) → channel variation → context-dependence of conflict severity.

The reference results to reproduce are **qualitative**: Method 2 ≥ Method 1 > conflicting on $\tau_e$, and conflict severity increasing with load/speed (16% vs 5% degradation).

### What needs to be determined to answer Q9

1. **Topology:** use the existing testbed config (10 cells / 49 UEs) or reduce to the paper-like 2 gNBs / 10 UEs?
2. **ISD and propagation model:** paper-like (900 m, analytic model) vs. testbed-native (3GPP channel models, existing ISD)?
3. **RBG count/size:** 12 RBGs/gNB (paper granularity) vs. standard 25 RBGs at 20 MHz?
4. **UE placement and traffic model:** paper-like (150–450 m, Poisson per RBG) vs. testbed-native?
5. **Calibration target:** if "calibrated", which knob(s) to tune (ISD, shadowing, UE count) to reproduce the qualitative ordering?
6. **Acceptance threshold:** confirm that exact degradation percentages are not required (acceptance criterion 3 is qualitative).

### Candidate resolutions

| Option | Parameters | Trade-off |
| :--- | :--- | :--- |
| (a) Paper-like | ISD 900 m, 3GPP propagation, 12 RBGs/gNB | Closest to the paper; may not fit the testbed topology |
| (b) Testbed-native | Testbed defaults (existing ns-O-RAN config) | Fits the testbed; diverges from the paper |
| (c) Calibrated | Tune ISD/propagation to reproduce the paper's qualitative ordering | Best of both; extra calibration effort |

### Decision point

- **Where:** Phase 0.6 — `implementation-plan.md`.
- **Comparison note:** acceptance criterion 3 (Method 2 ≥ Method 1 > conflicting) is qualitative; exact degradation percentages are not required.

---

## Q10. How is the leftover-bits KPI derived?

**Status:** Open — decision required before Phase 1.2.

### Context

The paper's discard model is **per-RBG, per-user, per-time-slot** (2504.06867v3:129, 293):

- Traffic arrivals $\varrho_{b,r,u}$ follow a Poisson distribution with mean $d_e$ per RBG allocated to user $u$.
- Transmission rate $\Psi_{b,r,u} = \min(\varrho_{b,r,u}, C_{b,r,u} T_s)$ — data beyond capacity is **discarded**.
- Leftover bits per slot = $\max(0, \varrho_{b,r,u} - C_{b,r,u} T_s)$; Fig. 7 reports the **mean leftover bits per episode**.
- The reward is the normalized rate $\tau_e = \sum \Psi / (d_e \cdot R \cdot B)$ — the denominator is the maximum achievable transmission (average load × total RBGs).

The **testbed reality** differs:

- No per-RBG throughput is exported; the finest throughput signal is per-UE PDCP $R_{u,t}$ (and even that is currently **missing** from the CU-CP exports, see `data-vs-implementation.md`).
- The offered load $d$ is a simulation configuration, not a telemetry column — its mapping to the paper's per-RBG Poisson arrivals is unspecified.
- The spec's proposed derivation $L = \max(0, d - \sum_u R_{u,t})$ is a **cell-level** approximation that collapses the per-RBG discard model.

**What the derivation affects:**

- The **$\tau_e$ reward** (the A2C scheduler's native reward) — its normalization constant depends on how $d$ and the RBG count are defined.
- The **leftover-bits metric** (FR-8.1) and the **$q_2$ threshold** (leftover ratio $\leq 0.05$).
- The **QACM ANN's KPI prediction target** (leftover bits as a function of $\mathbf{p}$).
- Both paradigms equally — the choice must be consistent across A2C and QACM for a fair comparison.

### What needs to be determined to answer Q10

1. **Granularity:** cell-level vs. per-UE vs. per-RBG — constrained by the available throughput signal (per-RBG is unavailable in the testbed).
2. **Offered-load configuration:** how $d$ is set in ns-3 (per-gNB total, per-UE, or per-RBG Poisson) and how it maps to the paper's model.
3. **$\tau_e$ normalization:** the paper's denominator $d_e \cdot R \cdot B$ must be re-expressed for the chosen granularity (e.g., $\tau_e = \sum_u R_{u,t} / (d \cdot R \cdot B)$ or delivered/offered ratio).
4. **Aggregation window:** leftover computed per scheduling period (1 s) vs. per episode (5 s) — the paper reports per-episode means.
5. **$q_2$ threshold definition:** how "leftover ratio $\leq 0.05$" is computed relative to the chosen derivation (leftover / offered load).
6. **Consistency:** the same derivation must feed the A2C reward, the QACM ANN target, and the comparison metrics.

### Candidate resolutions

| Option | Derivation | Trade-off |
| :--- | :--- | :--- |
| (a) Cell-level | $L = \max(0, d - \sum_u R_{u,t})$ per gNB per period | Simple; needs $R_{u,t}$ (missing) + offered load $d$ |
| (b) Per-UE | $L_u = \max(0, d_u - R_{u,t})$ | Finer; needs per-UE offered load |
| (c) Per-RBG | Paper-faithful per-RBG discard | Faithful; needs per-RBG throughput (unavailable) |

### Decision point

- **Where:** Phase 1.2 — `implementation-plan.md`.
- **Comparison note:** the derivation feeds both the leftover-bits metric (FR-8.1) and the $q_2$ threshold; the choice affects both paradigms equally.

---

<!-- Template for future questions:
## Q11. <title>

**Status:** Open — decision required before <phase>.

### Context
...

### Candidate resolutions
...

### Decision point
- **Where:** <phase/task>
-->