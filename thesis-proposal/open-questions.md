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

### Proposal: map the QACM scenario as the common scenario

Mapping the **QACM scenario** (ES vs. CCO over TXP) as the shared scenario is the better direction, because the reverse (mapping the A2C scenario onto QACM) is worse:

- QACM's machinery (z-score utility curves over a scalar range, single-parameter optimization) fits **TXP** perfectly — TXP is a scalar NCP.
- The A2C scenario's RBG allocation is a **combinatorial assignment**, not a scalar parameter; QACM's scalar bargaining cannot express it naturally.
- The A2C scenario has **two NCPs** (TXP + RBG allocation); QACM optimizes a single $p_l$ per conflict.
- The A2C scheduler *can* be adapted to the direct TXP conflict (with the complications above), whereas QACM cannot be adapted to the RBG-allocation conflict without a fundamental redesign.

**Consequence:** the A2C scheduler must be extended to arbitrate a direct conflict over TXP (activation mask over {ES, CCO} + baselines, multi-objective reward). The complications in the previous section are accepted as the cost of a fair comparison and should be reported as such in the thesis.

### Decision point

- **Where:** Phase 2 (xApp training) / Phase 3 (A2C scheduler) — `implementation-plan.md` tasks 3.x.
- **Risk register entry:** "Scenario mapping between the two papers" (add if not present).
- **Comparison note:** the A2C scheduler's inability to express a continuous compromise (problem 4) is itself a finding — macro-level activation scheduling vs. micro-level parameter bargaining — and should be discussed in the thesis.

---

## Q3. What reward should the A2C scheduler use in the QACM scenario?

**Status:** Open — decision required before Phase 3 (A2C scheduler).

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

<!-- Template for future questions:
## Q4. <title>

**Status:** Open — decision required before <phase>.

### Context
...

### Candidate resolutions
...

### Decision point
- **Where:** <phase/task>
-->