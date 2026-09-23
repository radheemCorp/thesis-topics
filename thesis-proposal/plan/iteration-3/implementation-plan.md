# Implementation Plan: A2C Scheduler vs. QACM Comparative Experiment

**Status:** Draft (iter-3)
**Target testbed:** ns-O-RAN (ns-3 + Near-RT RIC over E2)
**Companion doc:** `spec.md` (requirements, data, infrastructure)
**Iteration:** iter-3 — common scenario is the **A2C scenario** (Power + RBG indirect conflict), with QACM extended to joint-parameter bargaining. See `../iteration-index.md` for the iteration history.

---

## Phase 0 — Environment Bring-Up & Control-Surface Verification

**Goal:** Working ns-O-RAN + Near-RT RIC baseline; **confirm TXP and RBG/PRB-quota control** (critical gates for the A2C scenario).

| # | Task | Deliverable | Depends on |
| :--- | :--- | :--- | :--- |
| 0.1 | Deploy ns-O-RAN (ns-3) with Near-RT RIC; verify E2 setup and 100 ms E2SM-KPM streaming | Running testbed, KPM xApp receiving reports | — |
| 0.2 | **Verify E2SM-RC TXP (power) control**: inspect RAN Function Definition for power-control styles/actions; empirically probe with a RIC Control message and confirm TXP changes in the simulator | TXP control capability report | 0.1 |
| 0.3 | **Verify E2SM-RC RBG / PRB quota control (Style 2)**: confirm RBG allocation can be set per gNB | RBG control capability report | 0.1 |
| 0.4 | If TXP control unsupported: assess extension effort (custom E2SM-RC action / direct simulator control) | Decision record (extend vs. adapt) | 0.2 |
| 0.5 | Verify all 40 KPMs from `available-params.md` are emitted; confirm SINR/RSRP/throughput/PRB/modulation/handover-penalty | Telemetry validation report | 0.1 |
| 0.6 | Confirm 2 gNB / 10 UE topology, 20 MHz carrier, 12 RBGs/gNB, and UE mobility (1–50 m/s) are configurable | Scenario config template | 0.1 |
| 0.7 | Set up containerized component skeleton (RIC xApps, scheduler, QACM, CS xApp, shared DB) | Repo scaffold + CI | 0.1 |

**Exit criteria:** E2SM-KPM flows at 100 ms; **TXP and RBG control verified end-to-end (or extension decision recorded)**; scenario template runs.

---

## Phase 1 — Data Pipeline, Leftover-Bits Derivation & Simulated A1

**Goal:** Telemetry ingestion, leftover-bits KPI, context/intent injection, and trace export.

| # | Task | Deliverable | Depends on |
| :--- | :--- | :--- | :--- |
| 1.1 | Implement ETL: flatten $B \times C$ feature matrix, lookback gap-filling ($\epsilon$) | ETL module | 0.5 |
| 1.2 | **Implement leftover-bits derivation** $L = \max(0, d - \sum_u R_{u,t})$ per period | Leftover-bits module | 0.5 |
| 1.3 | Implement simulated A1 EI: inject $c^\dagger=[d,v]$ and intent $f^\dagger$ per scheduling period | A1 simulator | 0.7 |
| 1.4 | Implement CMS data store: RCP, PGD, RCPG, PKR, DCKD, KDO | Shared DB schema | 0.7 |
| 1.5 | Implement trace export (CSV/Parquet) with full state/action/reward logging | Trace exporter | 1.1 |
| 1.6 | Implement PMon: KPM vs. QoS-threshold comparison ($\tau_e \geq 0.9$, leftover ratio $\leq 0.05$), KDO logging | PMon module | 1.4 |

**Exit criteria:** Telemetry lands in shared DB; leftover bits computed; A1 EI injectable; traces exportable; PMon flags KPI degradation.

---

## Phase 2 — xApp Implementation & KPI Prediction Datasets

**Goal:** Pre-trained A2C xApps (Power, RBG) and baseline xApps, immutable after training; KPI-vs-(TXP, RBG, context) datasets for QACM.

| # | Task | Deliverable | Depends on |
| :--- | :--- | :--- | :--- |
| 2.1 | Implement Power xApp ($X_1$) with A2C: state, action over TXP levels, reward = $\tau_e$ | Power xApp | 1.1 |
| 2.2 | Implement RBG xApp ($X_2$) with A2C: state, action over RBG allocation, reward = $\tau_e$ | RBG xApp | 1.1 |
| 2.3 | Implement baseline xApps ($X_3$ equal allocation, $X_4$ fixed TXP) | Baseline xApps | 1.1 |
| 2.4 | Train $X_1$, $X_2$ offline (training set $d \in \{3,5,7,9\}$ Mbps × $v \in \{10,20,30,40\}$ m/s) | Trained model artifacts | 2.1, 2.2 |
| 2.5 | Validate xApp training curves (MA reward, sliding window 500) | Training report | 2.4 |
| 2.6 | **Collect KPI-vs-(TXP, RBG, d, v) datasets** via TXP × RBG sweep runs for QACM ANN training | Training datasets | 0.4, 1.1 |
| 2.7 | Implement xApp Inference Host (IH): activation-mask enforcement + data-repo access control | IH module | 2.4 |

**Exit criteria:** Trained xApps reproduce paper training behavior; KPI-vs-(TXP, RBG, context) datasets collected; IH enforces activation masks.

---

## Phase 3 — A2C Scheduler (as published)

**Goal:** Context-aware scheduler with confidence-gated fallback; Methods 1 and 2; native reward $\tau_e$.

| # | Task | Deliverable | Depends on |
| :--- | :--- | :--- | :--- |
| 3.1 | Implement state construction $s^\dagger=[c_1^\dagger,c_2^\dagger,f^\dagger]$ | State builder | 1.3 |
| 3.2 | Implement Actor network (activation-mask distribution) and Critic network | A2C networks | 2.7 |
| 3.3 | Implement confidence-gated fallback (EWMA mean/dispersion, z-score threshold, $T_{back}$, $\pi_{safe}$, frozen stats) | Safety layer | 3.2 |
| 3.4 | Implement Method 1 (retain previous action of deactivated xApp) and Method 2 (baseline extension over $\{X_1, X_2, X_3, X_4\}$) | Scheduling methods | 3.2 |
| 3.5 | Implement reward: **native** normalized transmission rate $\tau_e$ (no redesign; Q3 moot) | Reward module | 1.1 |
| 3.6 | Implement online training loop (policy gradient + critic MSE, $\eta=10^{-4}$, $\gamma=0.95$) | Trainer | 3.5 |
| 3.7 | Train scheduler for both methods; evaluate on 9 test scenarios ($d \in \{2,5,8\}$, $v \in \{5,25,45\}$) | Trained schedulers + eval | 3.6 |

**Exit criteria:** Scheduler outperforms the conflicting baseline; Method 2 ≥ Method 1 on $\tau_e$; conflict severity context-dependent.

---

## Phase 4 — QACM (extended to joint-parameter bargaining)

**Goal:** QoS-aware parameter bargaining engine (CMC) over the joint vector $\mathbf{p} = [p_{power}, p_{RBG}]$ with context-conditioned ANN KPI prediction.

| # | Task | Deliverable | Depends on |
| :--- | :--- | :--- | :--- |
| 4.1 | Implement CDC: indirect-conflict detection from KPM + TXP/RBG-change logs | CDC module | 1.6 |
| 4.2 | Implement CS xApp: weight assignment from MNO policy + network state ($\sum w_i=1$) | CS xApp | 1.4 |
| 4.3 | Train context-conditioned ANN regression per xApp (inputs $(\mathbf{p}, d, v)$; 4×128, tanh, dropout 0.2, Adam, MSE, 10 epochs); compare vs. polynomial regression | ANN artifacts + report | 2.6 |
| 4.4 | Implement KPI→utility z-score conversion ($U(\mathbf{p})=(k-\mu)/\sigma$) | Utility module | 4.3 |
| 4.5 | Implement QACM exact optimization over the joint range ($|P| \times (R+1)$ candidates) | Solver | 4.4 |
| 4.6 | Implement 2D-grid heuristic for dynamic/large-scale cases | Heuristic | 4.4 |
| 4.7 | Implement optimal-range estimation ($p_{power} \in [1, 38]$ dBm, $p_{RBG} \in \{0, \dots, 12\}$) and dispatch via E2SM-RC | Range + dispatch | 4.5/4.6 |
| 4.8 | Implement NSWF and EG benchmarks over the joint vector | Benchmark solvers | 4.4 |
| 4.9 | **Decide QACM fallback (Q1)**: dispatch-and-log / reject-and-keep-previous / escalate to CS xApp | Fallback decision record | 4.5 |
| 4.10 | Validate: QACM satisfies more QoS thresholds than NSWF/EG; heuristic matches exact solver on small instances | Validation report | 4.5–4.9 |

**Exit criteria:** QACM (joint-parameter) satisfies more per-xApp QoS thresholds than NSWF/EG; heuristic matches exact solver on small instances.

---

## Phase 5 — Benchmarks & Baselines

**Goal:** Complete comparison set under identical conditions.

| # | Task | Deliverable | Depends on |
| :--- | :--- | :--- | :--- |
| 5.1 | Implement conflicting independent deployment (both xApps, no mitigation) | Baseline runner | 2.4 |
| 5.2 | Wire NSWF/EG into the same E2SM-RC dispatch path as QACM | Benchmark integration | 4.8 |
| 5.3 | Implement isolated-run orchestration per `approach.md` §3 (identical topology/mobility/traffic per method) | Orchestrator | 3.7, 4.10, 5.1, 5.2 |
| 5.4 | Add seed control and N repetitions per scenario | Reproducibility harness | 5.3 |

**Exit criteria:** All methods runnable from one command per scenario with fixed seeds.

---

## Phase 6 — Experiment Execution

**Goal:** Run the full scenario matrix and collect metrics.

| # | Task | Deliverable | Depends on |
| :--- | :--- | :--- | :--- |
| 6.1 | Run 9 test scenarios × 7 methods (conflicting, A2C M1, A2C M2, QACM, QACMP, NSWF, EG) × N reps | Raw traces | 5.4 |
| 6.2 | Collect per-xApp QoS satisfaction $s_i$, KPI shortfall $d_i$, $\tau_e$, leftover bits | Metrics dataset | 6.1 |
| 6.3 | Measure mitigation latency: QACM solver/ANN vs. A2C forward pass | Latency dataset | 6.1 |
| 6.4 | Compute control-policy volatility (COV, SD, RMSSD of TXP and RBG series) | Volatility dataset | 6.1 |

**Exit criteria:** Complete, logged dataset for all cells of the matrix.

---

## Phase 7 — Evaluation & Analysis

**Goal:** Answer the research questions and produce thesis figures.

| # | Task | Deliverable | Depends on |
| :--- | :--- | :--- | :--- |
| 7.1 | Compare A2C vs. QACM on $\tau_e$ and leftover bits | Analysis report | 6.2 |
| 7.2 | Compare QoS satisfaction rates (QACM/QACMP vs. NSWF/EG; A2C vs. conflicting) | Analysis report | 6.2 |
| 7.3 | Analyze context-dependence of conflict severity (low vs. high load/speed) | Analysis report | 6.2 |
| 7.4 | Analyze latency vs. Near-RT RIC budget (10 ms–1 s) | Latency analysis | 6.3 |
| 7.5 | Analyze control stability (volatility metrics) | Stability analysis | 6.4 |
| 7.6 | Discuss limitations: QACM extensions (joint-vector, context ANN, RBG scalarization), ANN drift, A1 simulation, TXP control surface | Limitations section | 7.1–7.5 |
| 7.7 | Produce figures/tables for thesis | Figure set | 7.1–7.6 |

**Exit criteria:** All evaluation questions from the repository README answered with data.

---

## Phase 8 — Documentation & Write-Up

**Goal:** Reproducible, documented experiment.

| # | Task | Deliverable | Depends on |
| :--- | :--- | :--- | :--- |
| 8.1 | Document configs, seeds, and run instructions | README / runbook | 7.x |
| 8.2 | Archive datasets and model artifacts | Data archive | 7.x |
| 8.3 | Write thesis chapter / paper section on methodology and results | Write-up | 7.x |
| 8.4 | Update repository index (README.md) with experiment links | Index update | 8.1–8.3 |

**Exit criteria:** A third party can reproduce the experiment from committed material.

---

## Dependency Graph (summary)

```
Phase 0 ──► Phase 1 ──► Phase 2 ──► Phase 3 ──► Phase 5 ──► Phase 6 ──► Phase 7 ──► Phase 8
                │            │            │
                │            └──► Phase 4 ─┘
                └──────────────────────────┘
```

- Phase 3 and Phase 4 are independent after Phase 2 (xApps) and Phase 1 (data/A1).
- Phase 5 merges both engines into the comparison harness.
- Phases 6–8 are sequential.

## Risk Register

| Risk | Likelihood | Impact | Mitigation |
| :--- | :--- | :--- | :--- |
| **R1: E2SM-RC TXP (power) control unsupported in ns-O-RAN** | High | High | Verify in Phase 0.2; extend ns-O-RAN with a TXP control action (the scenario needs both TXP and RBG control, so no parameter-agnostic fallback exists) |
| R2: E2SM-RC RBG / PRB quota control (Style 2) unsupported in ns-O-RAN | Medium | High | Verify in Phase 0.3; extend ns-O-RAN or map RBG allocation to PRB-utilization control |
| R3: Leftover-bits KPI not native to ns-O-RAN | High | Medium | Derive from offered load vs. delivered throughput; report derivation assumptions |
| R4: A2C scheduler training time too long | Medium | Medium | Reduce episodes; parallelize; CPU-optimized env |
| R5: ANN KPI prediction drift under dynamic conditions | High | Medium | Report as limitation; evaluate prediction error on held-out scenarios |
| R6: QACM has no defined fallback when the best compromise satisfies zero QoS thresholds | Medium | Medium | Decide in Phase 4.9 (dispatch-and-log / reject-and-keep-previous / escalate to CS xApp); compare against A2C's confidence-gated fallback |
| R7: QACM joint-parameter extension complexity (2D search, latency) | Medium | Medium | Use 2D-grid heuristic for large ranges; measure solver latency in Phase 6.3 |
| R8: RBG scalarization loses combinatorial structure | Medium | Medium | Report as a finding (micro-level bargaining over scalarized control vs. macro-level activation scheduling) |
| R9: Reproducing paper numbers exactly | Medium | Low | Target qualitative ordering (M2 ≥ M1 > conflicting; QACM > NSWF/EG), not exact values |
| R10: Near-RT RIC integration complexity | Medium | Medium | Containerized components; incremental bring-up in Phase 0 |