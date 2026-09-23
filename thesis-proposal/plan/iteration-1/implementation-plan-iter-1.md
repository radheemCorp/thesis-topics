# Implementation Plan: A2C Scheduler vs. QACM Comparative Experiment

**Status:** Draft
**Target testbed:** ns-O-RAN (ns-3 + Near-RT RIC over E2)
**Companion doc:** `spec.md` (requirements, data, infrastructure)

---

## Phase 0 — Environment Bring-Up & Control-Surface Verification

**Goal:** Working ns-O-RAN + Near-RT RIC baseline; confirm what can be measured and controlled.

| # | Task | Deliverable | Depends on |
| :--- | :--- | :--- | :--- |
| 0.1 | Deploy ns-O-RAN (ns-3) with Near-RT RIC; verify E2 setup and 100 ms E2SM-KPM streaming | Running testbed, KPM xApp receiving reports | — |
| 0.2 | Inventory E2SM-RC control actions actually supported (PRB quota vs. power vs. mobility) | Control-surface capability matrix | 0.1 |
| 0.3 | Verify all 40 KPMs from `available-params.md` are emitted; confirm SINR/RSRP/throughput/PRB/modulation/handover-penalty | Telemetry validation report | 0.1 |
| 0.4 | Confirm 4 O-RU / 16 UE / 12 RBG topology and 20 MHz carrier are configurable | Scenario config template | 0.1 |
| 0.5 | Set up containerized component skeleton (RIC xApps, scheduler, QACM, CS xApp, shared DB) | Repo scaffold + CI | 0.1 |
| 0.6 | Decide the concrete conflicting NCP for QACM (candidate: PRB allocation quota) and its range | NCP decision record | 0.2 |

**Exit criteria:** E2SM-KPM flows at 100 ms; at least one E2SM-RC control action verified end-to-end; scenario template runs.

---

## Phase 1 — Data Pipeline & Simulated A1

**Goal:** Telemetry ingestion, context/intent injection, and trace export.

| # | Task | Deliverable | Depends on |
| :--- | :--- | :--- | :--- |
| 1.1 | Implement ETL: flatten $B \times C$ feature matrix, lookback gap-filling ($\epsilon$) | ETL module | 0.3 |
| 1.2 | Implement simulated A1 EI: inject $c^\dagger=[d,v]$ and intent $f^\dagger$ per scheduling period | A1 simulator | 0.5 |
| 1.3 | Add leftover/discarded-bit trace source (queue/buffer stats or derived from $R_{u,t}$ vs. $d_e$) | Reward inputs | 0.3 |
| 1.4 | Implement CMS data store: RCP, PGD, RCPG, PKR, DCKD, KDO | Shared DB schema | 0.5 |
| 1.5 | Implement trace export (CSV/Parquet) with full state/action/reward logging | Trace exporter | 1.1 |
| 1.6 | Implement PMon: KPM vs. QoS-threshold comparison, KDO logging | PMon module | 1.4 |

**Exit criteria:** Telemetry lands in shared DB; A1 EI injectable; traces exportable; PMon flags KPI degradation.

---

## Phase 2 — xApp Implementation

**Goal:** Pre-trained A2C xApps and baseline xApps, immutable after training.

| # | Task | Deliverable | Depends on |
| :--- | :--- | :--- | :--- |
| 2.1 | Implement Power allocation xApp ($X_1$) with A2C (state, action over power levels, reward) | Power xApp | 1.1 |
| 2.2 | Implement RBG allocation xApp ($X_2$) with A2C (RBG→UE assignment) | RBG xApp | 1.1 |
| 2.3 | Implement baseline equal-allocation xApps ($X_3$ power, $X_4$ RBG) | Baseline xApps | 1.1 |
| 2.4 | Train $X_1$, $X_2$ offline ($10^5$ episodes, $T=50$, $d\in\{3,5,7,9\}$, $v\in\{10,20,30,40\}$) | Trained model artifacts | 2.1, 2.2 |
| 2.5 | Validate xApp training curves (MA reward, sliding window 500) vs. paper Fig. 4 | Training report | 2.4 |
| 2.6 | Implement xApp Inference Host (IH): activation-mask enforcement + data-repo access control | IH module | 2.4 |

**Exit criteria:** Trained xApps reproduce paper training behavior; IH enforces activation masks.

---

## Phase 3 — A2C Scheduler

**Goal:** Context-aware scheduler with confidence-gated fallback; Methods 1 and 2.

| # | Task | Deliverable | Depends on |
| :--- | :--- | :--- | :--- |
| 3.1 | Implement state construction $s^\dagger=[c_1^\dagger,c_2^\dagger,f^\dagger]$ | State builder | 1.2 |
| 3.2 | Implement Actor network (activation-mask distribution) and Critic network | A2C networks | 2.6 |
| 3.3 | Implement confidence-gated fallback (EWMA mean/dispersion, z-score threshold, $T_{back}$, $\pi_{safe}$, frozen stats) | Safety layer | 3.2 |
| 3.4 | Implement Method 1 (retain previous action) and Method 2 (baseline extension, $\mu_1+\mu_3=1$, $\mu_2+\mu_4=1$) | Scheduling methods | 3.2 |
| 3.5 | Implement reward computation ($\tau_e$ normalized transmission rate + leftover-bit penalty) | Reward module | 1.3 |
| 3.6 | Implement online training loop (policy gradient + critic MSE, $\eta=10^{-4}$, $\gamma=0.95$) | Trainer | 3.5 |
| 3.7 | Train scheduler for both methods; evaluate on 9 test scenarios ($d\in\{2,5,8\}$, $v\in\{5,25,45\}$) | Trained schedulers + eval | 3.6 |

**Exit criteria:** Scheduler reproduces paper results (Method 2 ≥ Method 1 > conflicting baseline; ~5% low vs. ~16% high degradation).

---

## Phase 4 — QACM

**Goal:** QoS-aware parameter bargaining engine (CMC) with ANN KPI prediction.

| # | Task | Deliverable | Depends on |
| :--- | :--- | :--- | :--- |
| 4.1 | Implement CDC: direct/indirect/implicit conflict detection from KPM + parameter-change logs | CDC module | 1.6 |
| 4.2 | Implement CS xApp: weight assignment from MNO policy + network state ($\sum w_i=1$) | CS xApp | 1.4 |
| 4.3 | Collect KPI-vs-parameter datasets via ns-3 sweep runs (per xApp) | Training datasets | 0.6, 1.1 |
| 4.4 | Train ANN regression per xApp (4×128, tanh, dropout 0.2, Adam, MSE, 10 epochs); compare vs. polynomial regression | ANN artifacts + report | 4.3 |
| 4.5 | Implement KPI→utility z-score conversion ($U(p)=(k-\mu)/\sigma$) | Utility module | 4.4 |
| 4.6 | Implement QACM exact optimization (4$\|X'\|$ vars, 4$\|X'\|$+2$\|N\|$+3 constraints) | Solver | 4.5 |
| 4.7 | Implement Heuristic Alg. 1 ($O(N\cdot\|X'\|)$) for dynamic/large-scale cases | Heuristic | 4.5 |
| 4.8 | Implement optimal-range estimation (union of per-xApp ranges) and dispatch via E2SM-RC | Range + dispatch | 4.6/4.7 |
| 4.9 | Implement NSWF and EG benchmarks | Benchmark solvers | 4.5 |
| 4.10 | Validate on paper case studies (2-xApp direct conflict; ES vs. CCO TXP → 15/16 dBm) | Validation report | 4.6–4.9 |

**Exit criteria:** QACM satisfies more xApp QoS thresholds than NSWF/EG; heuristic matches exact solver on small instances.

---

## Phase 5 — Benchmarks & Baselines

**Goal:** Complete comparison set under identical conditions.

| # | Task | Deliverable | Depends on |
| :--- | :--- | :--- | :--- |
| 5.1 | Implement conflicting independent deployment (both xApps, no mitigation) | Baseline runner | 2.4 |
| 5.2 | Wire NSWF/EG into the same E2SM-RC dispatch path as QACM | Benchmark integration | 4.9 |
| 5.3 | Implement isolated-run orchestration per `approach.md` §3 (identical topology/mobility/traffic per method) | Orchestrator | 3.7, 4.10, 5.1, 5.2 |
| 5.4 | Add seed control and N repetitions per scenario | Reproducibility harness | 5.3 |

**Exit criteria:** All methods runnable from one command per scenario with fixed seeds.

---

## Phase 6 — Experiment Execution

**Goal:** Run the full scenario matrix and collect metrics.

| # | Task | Deliverable | Depends on |
| :--- | :--- | :--- | :--- |
| 6.1 | Run 9 test scenarios × 7 methods (conflicting, A2C M1, A2C M2, QACM, QACMP, NSWF, EG) × N reps | Raw traces | 5.4 |
| 6.2 | Collect per-xApp QoS satisfaction $s_i$, KPI shortfall $d_i$, normalized rate $\tau_e$, leftover bits | Metrics dataset | 6.1 |
| 6.3 | Measure mitigation latency: QACM solver/ANN vs. A2C forward pass | Latency dataset | 6.1 |
| 6.4 | Compute control-policy volatility (COV, SD, RMSSD) | Volatility dataset | 6.1 |

**Exit criteria:** Complete, logged dataset for all cells of the matrix.

---

## Phase 7 — Evaluation & Analysis

**Goal:** Answer the research questions and produce thesis figures.

| # | Task | Deliverable | Depends on |
| :--- | :--- | :--- | :--- |
| 7.1 | Compare A2C vs. QACM on system-wide throughput and leftover bits | Analysis report | 6.2 |
| 7.2 | Compare QoS satisfaction rates (QACM/QACMP vs. NSWF/EG; A2C vs. conflicting) | Analysis report | 6.2 |
| 7.3 | Analyze context-dependence of conflict severity (low vs. high load/speed) | Analysis report | 6.2 |
| 7.4 | Analyze latency vs. Near-RT RIC budget (10 ms–1 s) | Latency analysis | 6.3 |
| 7.5 | Analyze control stability (volatility metrics) | Stability analysis | 6.4 |
| 7.6 | Discuss limitations: ANN drift, A1 simulation, single-intent scheduler, NCP surface | Limitations section | 7.1–7.5 |
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
| E2SM-RC control surface too limited (no power control) | Medium | High | Verify in Phase 0.6; fall back to PRB-quota conflict (still valid for both methods) |
| A2C training time ($10^5$ episodes) too long | Medium | Medium | Reduce episodes for scheduler (paper uses same order); parallelize; CPU-optimized env |
| Leftover-bit metric unavailable | Medium | Medium | Derive from $R_{u,t}$ vs. offered load; or add ns-3 trace source |
| ANN KPI prediction drift under dynamic conditions | High | Medium | Report as limitation; evaluate prediction error on held-out scenarios |
| QACM has no defined fallback when the best compromise satisfies zero QoS thresholds | Medium | Medium | Decide in Phase 4 (dispatch-and-log / reject-and-keep-previous / escalate to CS xApp); compare against A2C's confidence-gated fallback |
| Reproducing paper numbers exactly | Medium | Low | Target qualitative ordering (M2 ≥ M1 > conflicting; QACM > NSWF/EG), not exact values |
| Near-RT RIC integration complexity | Medium | Medium | Containerized components; incremental bring-up in Phase 0 |