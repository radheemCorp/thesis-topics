# Product Definition

## Initial Concept
Build a modular O-RAN Near-RT-RIC research testbed that reproduces the **QACM (QoS-Aware Conflict Mitigation)** scenario: independently developed xApps (CCO, ES, and future xApps) that produce conflicting control decisions over shared Input Control Parameters (ICPs), plus a Conflict Mitigation Controller (CMC) that finds a QoS-aware compromise.

## Vision
An extensible Python framework where: (1) surrogate xApps predict KPIs from ICPs via regression models (poly/ANN), (2) each xApp emits a structured control request, and (3) a CMC resolves **direct and indirect** conflicts over one or more shared ICPs using the QACM heuristic (minimize weighted QoS deviation, maximize # of satisfied xApps), including joint 2-D `(p1, p2)` bargaining — with no data sharing between xApps.

## Target Users
- Thesis/research engineer reproducing and extending the QACM paper (2405.07324v2)
- Future contributors adding new xApps (MRO, MLB, etc.) to the conflict-mitigation testbed

## Goals
1. Reproduce the QACM pre-mitigation state: CCO (throughput-max) and ES (power-min) produce conflicting requests over shared ICPs.
2. Implement the CMC: given conflicting xApps, compute a compromise `p*` that improves QoS satisfaction vs. uncoordinated operation — first as the scalar QACM heuristic, then extended to joint 2-D `(p1, p2)` bargaining.
3. Cover both **direct** conflicts (different requested values for the same ICP) and **indirect** conflicts (one xApp's ICP choice shifts another xApp's KPI surface), using reproducible synthetic datasets.
4. Keep every component modular (SurrogateModel, BaseXApp, CMC) so new xApps plug in without touching CMC logic.
5. Provide reproducible, testable, documented code (uv + pytest).

## Non-Goals (for now)
- Real Near-RT-RIC / E2 integration (MATLAB/simulation-only in paper)
- Implicit conflict types (hidden parameter–KPI relationships not visible from the requested points)
- Continuous/MILP optimizers in the production path (the production CMC uses the discrete grid heuristic; an exact brute-force solver exists only as a test oracle)
