# Iteration Index

Tracks iterations of the experiment specification and implementation plan. Each entry records the iteration ID, the files, if applicable, the problem that triggered the pivot, and the rationale for the new direction.

---

## Iteration 1 (iter-1)

**Archived files:**
- `iteration-1/spec-iter-1.md`
- `iteration-1/implementation-plan-iter-1.md`

**Date:** 2026-09-23

### Problem

The iter-1 spec and implementation plan left the **common evaluation scenario undecided**. The two source papers use structurally different scenarios:

- **QACM (2405.07324v2, §VIII):** ES vs. CCO **direct conflict over TXP** — a single shared scalar NCP (transmit power).
- **A2C Scheduler (2504.06867v3):** Power xApp + RBG xApp **indirect conflict** — two different NCPs (TXP and RBG allocation) affecting the same KPM.

iter-1 deferred the choice to Phase 0/1 (pending E2SM-RC control-surface verification) and treated the A2C scenario as the default reference, with QACM to be re-targeted onto it.

### Why we pivoted

Analysis (see `open-questions.md`, Q2) showed that mapping the **QACM scenario** as the common scenario is the better direction:

1. **QACM cannot express the A2C scenario.** QACM's machinery (z-score utility curves over a scalar range, single-parameter optimization) fits a scalar NCP like TXP. The A2C scenario's RBG allocation is a **combinatorial assignment** and involves **two NCPs** — QACM's scalar bargaining cannot represent it without a fundamental redesign.
2. **The A2C scheduler *can* be adapted to the QACM scenario.** The activation-mask mechanism can arbitrate a direct conflict over TXP (select ES-only / CCO-only / both / baseline), accepting the complications documented in `open-questions.md` Q2 (reward redesign, conflict-type extension, no compromise granularity, etc.).
3. **TXP is the one NCP both papers already use**, and it is the natural fit for QACM's utility curves — making the comparison apples-to-apples on the identical scenario, xApps, context, and metrics.

### New direction (iter-2)

- Common scenario: **ES vs. CCO direct conflict over TXP** (QACM scenario).
- A2C scheduler extended to arbitrate the direct TXP conflict (activation masks over {ES, CCO} + baselines, multi-objective reward).
- QACM implemented as in the paper (CDC/CMC/CS xApp, ANN KPI prediction, exact + heuristic solver).
- Both paradigms evaluated on the same metrics: throughput, power consumption, QoS satisfaction, control volatility, mitigation latency.

---

## Iteration 2 (iter-2)

**files:**
- `iteration-2/spec.md`
- `iteration-2/implementation-plan.md`

**Date:** 2026-09-23

### Summary

iter-2 implements the pivot: the **QACM scenario** (ES vs. CCO direct conflict over TXP) is the common evaluation scenario. The A2C scheduler is adapted to arbitrate the direct TXP conflict (activation masks over {ES, CCO} + baselines, multi-objective reward). Key additions over iter-1:

- **Critical gate (Phase 0.2):** verify E2SM-RC TXP (power) control in ns-O-RAN; fallback = extend the simulator or map the conflict onto a supported scalar NCP (PRB quota).
- **Power-consumption model** (Phase 1.2): $k_{ES}$ is not a native ns-O-RAN KPM; modeled from TXP + PRB utilization, calibrated to the paper's 25 Wh threshold.
- **KPI-vs-TXP sweep datasets** (Phase 2.6) for QACM ANN training.
- **QACM fallback decision** (Phase 4.9) — open question Q1.
- **A2C reward decision** (Phase 3.5) — open question Q3 (QoS satisfaction vs. weighted throughput+power).
- Scenario extended with context variables ($d \in \{5,10,15\}$ Gbps, $v \in \{1,3,5\}$ m/s) so the A2C scheduler is context-aware.

**Current files:** `iteration-2/spec.md`, `iteration-2/implementation-plan.md`

---

## Iteration 3 (iter-3)

**Archived files:**
- `iteration-3/spec.md`
- `iteration-3/implementation-plan.md`

**Date:** 2026-09-23

### Problem

iter-2 (Proposal A) adapted the A2C scheduler to the QACM scenario (ES vs. CCO direct conflict over TXP). Analysis of the proposal (see `open-questions.md`, Q2) showed this distorts the A2C side: reward redesign (Q3), conflict-type extension, destroyed Method 1/2 semantics, and an artificial discretization problem. The comparison was structurally asymmetric in the wrong direction.

### Why we pivoted

A new proposal (Proposal B, `open-questions.md` Q2) keeps the **A2C scenario** (Power xApp + RBG xApp indirect conflict) as the common scenario and extends **QACM** to bargain over the joint control vector $\mathbf{p} = [p_{power}, p_{RBG}]$:

1. **A2C runs exactly as published** — native reward (normalized rate $\tau_e$), Method 1/2 semantics, activation masks, pre-trained immutable xApps. No reward redesign → Q3 becomes moot.
2. **QACM's design intent covers the scenario** — the paper explicitly handles direct/indirect/implicit conflicts (2405.07324v2:103, 204, 242) and its §VII-C case study evaluates indirect conflicts (2405.07324v2:356). The two-NCP indirect conflict is within its framework.
3. **Context is native** — $c^\dagger = [d, v]$ is passed into QACM's ANN as features alongside candidate parameter settings, so both paradigms are context-aware.
4. **The macro-vs-micro asymmetry becomes the intended finding** — activation scheduling vs. parameter bargaining — instead of a distortion.

**Accepted QACM-side extensions (reported in the thesis):** joint-parameter bargaining (paper's solver is single-parameter), context-conditioned ANN, scalarized RBG allocation, and QoS thresholds defined for the A2C scenario ($q_1$: $\tau_e \geq 0.9$; $q_2$: leftover ratio $\leq 0.05$).

### New direction (iter-3)

- Common scenario: **Power + RBG indirect conflict** (A2C scenario), adapted to the testbed (2 gNBs / 10 UEs / 12 RBGs per gNB / 20 MHz).
- A2C scheduler implemented **as published** (native $\tau_e$ reward, Method 1/2, confidence-gated fallback).
- QACM **extended** to joint-parameter bargaining over $\mathbf{p} = [p_{power}, p_{RBG}]$ with context-conditioned ANN KPI prediction.
- Both paradigms evaluated on the same metrics: $\tau_e$, leftover bits, QoS satisfaction, control volatility, mitigation latency.

**Current files:** `iteration-3/spec.md`, `iteration-3/implementation-plan.md`