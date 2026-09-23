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