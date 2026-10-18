# Product Definition

## Initial Concept
Build a modular O-RAN Near-RT-RIC research testbed that reproduces the **QACM (QoS-Aware Conflict Mitigation)** scenario: independently developed xApps (CCO, ES, and future xApps) that produce conflicting control decisions over shared Input Control Parameters (ICPs), plus a Conflict Mitigation Controller (CMC) that finds a QoS-aware compromise.

## Vision
An extensible Python framework where: (1) surrogate xApps predict KPIs from ICPs via regression models (poly/ANN), (2) each xApp emits a structured control request, and (3) a CMC resolves direct conflicts using the QACM heuristic (minimize weighted QoS deviation, maximize # of satisfied xApps) — with no data sharing between xApps.

## Target Users
- Thesis/research engineer reproducing and extending the QACM paper (2405.07324v2)
- Future contributors adding new xApps (MRO, MLB, etc.) to the conflict-mitigation testbed

## Goals
1. Reproduce the QACM pre-mitigation state: CCO (throughput-max) and ES (power-min) produce conflicting requests over shared ICPs.
2. Implement the CMC MVP: given conflicting xApps, compute a compromise p* that improves QoS satisfaction vs. uncoordinated operation.
3. Keep every component modular (SurrogateModel, BaseXApp, CMC) so new xApps plug in without touching CMC logic.
4. Provide reproducible, testable, documented code (uv + pytest).

## Non-Goals (for now)
- Real Near-RT-RIC / E2 integration (MATLAB/simulation-only in paper)
- Indirect/implicit conflict types (MVP targets direct conflicts over a shared ICP)
- Continuous optimizers/solvers (MVP uses the discrete heuristic, Algorithm 1)
