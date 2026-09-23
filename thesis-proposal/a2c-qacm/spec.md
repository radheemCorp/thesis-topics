# Specification: Comparative Evaluation of A2C Context-Aware Scheduler vs. QACM in ns-O-RAN

**Status:** Draft
**Scope:** Experiment specification for the head-to-head evaluation of two xApp conflict-mitigation frameworks inside the Near-RT RIC, on the ns-O-RAN testbed.
**Sources:**
- Approach: `thesis-proposal/a2c-qacm/approach.md`, `a2c-scheduler-flow.md`, `qacm-flow.md`, `implementation.md`
- Literature: `literature/Context-Aware Dynamic Schedulers/2504.06867v3.md` (A2C Scheduler), `literature/Rule-Based & SLA Constraint Projection/2405.07324v2.md` (QACM)
- Testbed: `literature/testbed-info/ns3/available-params.md`

---

## 1. Experiment Overview

Two active, closed-loop conflict-mitigation engines are implemented inside the Near-RT RIC and evaluated under identical ns-O-RAN network conditions:

| | **A2C Context-Aware Scheduler** | **QACM** |
| :--- | :--- | :--- |
| **Role** | Macro-level action coordinator | Micro-level parameter bargaining engine |
| **Core engine** | Advantage Actor-Critic (A2C) DRL | Constrained optimization / Heuristic Alg. 1 + ANN KPI regression |
| **Input** | Context variables $c^\dagger$ (load $d$, speed $v$) + intent $f^\dagger$ | Conflicting parameter $p_l$, QoS thresholds $q'$, weights $w_i$, ranges $[p_{min},p_{max}]$ |
| **Output** | xApp activation mask $\mu^\dagger \in \{0,1\}^n$ | Optimal compromise parameter $p_l^{opt}$ via E2SM-RC |
| **QoS guarantee** | System-wide (normalized transmission rate) | Explicit per-xApp QoS threshold satisfaction |
| **Re-training** | Lightweight scheduler only; xApps immutable | ANN regression models per xApp |

The experiment answers the repository's central question: *how can independently developed SON xApps safely share RAN control while preserving objectives, QoS/SLA requirements, and near-real-time constraints?* — by comparing the two dominant runtime-mitigation paradigms (action scheduling vs. parameter bargaining) on a common testbed.

### 1.1 Reference Scenario (from 2504.06867v3)

- 4 O-RUs ($B$), 16 users ($U$), 12 RBGs per O-RU ($R$), 20 MHz carrier.
- Two A2C-trained xApps: **Power allocation** ($X_1$) and **RBG allocation** ($X_2$); two baseline equal-allocation xApps ($X_3$, $X_4$).
- Context variables: mean data arrival rate $d_e \in \{3,5,7,9\}$ Mbps; user speed $v_u \in [1,50]$ m/s.
- Scheduling period $\dagger = 10$ time steps; slot duration $T_s = 100$ ms; episodes $T = 50$ steps; $10^5$ training episodes.
- Reward: normalized transmission rate $\tau_e = \sum_t \tau_{t,e} / (d_e \cdot R \cdot B)$.
- Conflict severity is context-dependent: ~5% degradation at low load/speed vs. ~16% at high load/speed (8 Mbps, 45 m/s).

### 1.2 Reference Scenario (from 2405.07324v2)

- CMS framework: PMon, CDC, CMC, CS xApp, and database components (RCP, PGD, RCPG, PKR, DCKD, KDO).
- KPI→utility via z-score normalization $U(p) = (k(p)-\mu)/\sigma$, range $[-3,+3]$.
- ANN KPI regression: 4 hidden layers × 128 neurons, tanh, dropout 0.2, Adam, MSE, 10 epochs.
- Objective: $\min_{p_l} \sum_i w_i d_i \zeta - (\sum_i s_i)^2$; exact form $4|X'|$ vars / $4|X'|+2|N|+3$ constraints; heuristic $O(N \cdot |X'|)$.
- Example: ES vs. CCO over TXP → QACM 15 dBm (non-priority), 16 dBm (priority); NSWF 6 dBm, EG 40 dBm.

---

## 2. Data Requirements

### 2.1 Met (available in ns-O-RAN telemetry, `available-params.md`)

| Requirement | Symbol | Source / Layer | Used by |
| :--- | :--- | :--- | :--- |
| UE identifier | $u$ | CU-CP | Both (per-UE state) |
| Serving/neighbor cell IDs | $c \in C'_{u,t}$ | CU-CP | Both (feature matrix columns) |
| SINR per UE per cell | $\text{SINR}_{u,c,t}$ | CU-CP (L3 RRC) | A2C state, QACM KPI |
| RSRP per UE per cell | $\text{RSRP}_{u,c,t}$ | CU-CP (L3 RRC) | A2C state, QACM KPI |
| PDCP DL throughput | $R_{u,t}$ | CU-UP (PDCP) | A2C reward, QACM KPI |
| PRB utilization % | $\text{PRB}_{c,t}$ | DU (MAC) | A2C state, QACM KPI |
| Active user count | $Z_{c,t}$ | DU (MAC) | A2C state (congestion) |
| Transport blocks | $P_{c,t}$ | DU (MAC) | QACM KPI (throughput proxy) |
| Modulation ratios | $p^{QPSK}_{c,t}, p^{16QAM}_{c,t}, p^{64QAM}_{c,t}$ | DU (MAC) | QACM KPI (link quality) |
| Handover cost penalty | $k(c_{u,t})$ | Near-RT RIC (calc.) | A2C reward shaping |
| 100 ms reporting periodicity | — | E2SM-KPM | Both (control-loop cadence) |
| Feature matrix $B \times C$ | — | RIC ETL | Both (model input) |
| Missing-data lookback $\epsilon$ | — | RIC ETL | Both (gap filling) |

### 2.2 Missing (must be generated, configured, or derived)

| Requirement | Symbol | Why missing | How to close |
| :--- | :--- | :--- | :--- |
| Context variable: arrival rate | $c_1^\dagger = d$ | Not in telemetry sheet; is a simulation input / A1 EI | Expose as simulation config; inject via simulated A1 EI |
| Context variable: mobility speed | $c_2^\dagger = v$ | Not in telemetry sheet | Derive from ns-3 mobility model; inject via simulated A1 EI |
| Operator intent target | $f^\dagger$ | Not in telemetry sheet | Define fixed intent (maximize $\tau_e$); inject via simulated A1 |
| Leftover/discarded bits | $\tau_{t,e}$ overflow | Not in available-params (queue/buffer stats absent) | Add ns-3 trace source or compute from $R_{u,t}$ vs. offered load $d_e$ |
| QoS thresholds per xApp | $q'_i$ | Not in telemetry sheet; SLA-defined | Define per-xApp thresholds (e.g., from Table IV of QACM paper) |
| Priority weights | $w_i$ | Produced by CS xApp (not present) | Implement CS xApp logic (MNO policy + network state) |
| Conflicting parameter & ranges | $p_l, [p_{min},p_{max}]$ | Depends on E2SM-RC control surface (not specified in sheet) | Verify ns-O-RAN E2SM-RC actions; select controllable NCP (PRB quota / power) |
| KPI prediction training data | $\{(p_l, k)\}$ | Must be collected from ns-3 runs | Generate via sweep runs; train ANN per xApp |
| KPI→utility statistics | $\mu, \sigma$ | Derived | Compute from collected KPI distributions |
| Conflict ground truth / labels | — | Not in telemetry sheet | Derive from KPI degradation events + parameter-change logs (CDC logic) |
| Reward normalization constants | $d_e, R, B$ | Config | Read from scenario config |

---

## 3. Infrastructure Requirements

### 3.1 Met

| Component | Status | Notes |
| :--- | :--- | :--- |
| ns-3 simulator (ns-O-RAN) | Met | Full protocol stack, 3GPP channel models |
| E2 interface (E2SM-KPM / E2SM-RC) | Met | 100 ms KPM streaming; control service model present |
| Near-RT RIC | Met | To be included in the testbed (per experiment brief) |
| RIC ETL / data aggregation | Met | Feature matrix $B \times C$, lookback gap-filling |
| Python ML environment | Met | A2C (PyTorch/TF), ANN regression (Keras/TF) |

### 3.2 Missing

| Component | Status | Impact / Closure |
| :--- | :--- | :--- |
| A1 interface / Non-RT RIC | Missing | No standardized EI delivery; simulate via HTTP/shared DB or direct injection |
| CS xApp (QACM weight provider) | Missing | Implement as lightweight xApp reading MNO policy + network state |
| CDC (Conflict Detection Controller) | Missing | Implement direct/indirect/implicit detection from KPM + parameter-change logs |
| PMon (Performance Monitoring) | Partial | KPM xApp exists; needs QoS-threshold comparison + KDO logging |
| CMS database (RCP, PGD, RCPG, PKR, DCKD, KDO) | Missing | Implement as shared data store (Redis/InfluxDB/MongoDB) |
| xApp Inference Host (IH) | Missing | Implement activation-mask enforcement + data-repo access control |
| E2SM-RC control surface detail | Unverified | Confirm which control actions ns-O-RAN supports (PRB quota vs. power) |
| DRL training infrastructure | Missing | Compute for $10^5$ episodes; GPU optional, CPU feasible for small state |
| Experiment orchestration / scenario runner | Missing | Seed control, scenario matrix, repetition management |
| Metrics & logging backend | Missing | Structured logs, CSV/Parquet traces, reproducibility metadata |

---

## 4. Functional Requirements

### FR-1 Telemetry Ingestion
- FR-1.1 Stream E2SM-KPM reports at 100 ms periodicity for all configured metrics.
- FR-1.2 Flatten per-UE/per-cell inputs into the $B \times C$ feature matrix.
- FR-1.3 Fill missing/delayed telemetry using the lookback window $\epsilon$.

### FR-2 Context & Intent Provisioning (simulated A1)
- FR-2.1 Provide context variables $c^\dagger = [d, v]$ per scheduling period.
- FR-2.2 Provide intent target $f^\dagger$ (e.g., maximize $\tau_e$).
- FR-2.3 Allow MNO policy configuration (weights, thresholds, fallback threshold).

### FR-3 A2C Scheduler
- FR-3.1 Build state $s^\dagger = [c_1^\dagger, c_2^\dagger, f^\dagger]$.
- FR-3.2 Actor inference $\pi_\theta(a^\dagger|s^\dagger)$ → distribution over activation decisions.
- FR-3.3 Critic inference $V_\phi(s^\dagger)$ → state-value baseline.
- FR-3.4 Confidence-gated fallback: EWMA of critic mean/dispersion, z-score threshold, $T_{back}$ override with $\pi_{safe}$; freeze statistics during back-off.
- FR-3.5 Action sampling → activation mask $\mu^\dagger$.
- FR-3.6 Method 1 (retain previous action) and Method 2 (baseline extension, $\mu_1+\mu_3=1$, $\mu_2+\mu_4=1$).
- FR-3.7 Online training update: policy gradient + critic MSE loss.
- FR-3.8 Reward computation: normalized transmission rate $\tau_e$ (+ leftover-bit penalty).

### FR-4 QACM
- FR-4.1 Conflict notification from CDC (parameter $p_l$, xApp set $X'$).
- FR-4.2 Optimal-range estimation: union of per-xApp ranges.
- FR-4.3 Weight assignment from CS xApp ($\sum w_i = 1$).
- FR-4.4 KPI prediction per xApp via ANN regression (4×128, tanh, dropout 0.2, Adam, MSE).
- FR-4.5 KPI→utility conversion via z-score normalization.
- FR-4.6 Solve QACM objective (exact or Heuristic Alg. 1, $O(N\cdot|X'|)$).
- FR-4.7 Dispatch $p_l^{opt}$ via E2SM-RC control.
- FR-4.8 Loop on new KPI degradation / conflict (PMon → CDC → CMC).

### FR-5 Control Execution
- FR-5.1 Enforce activation mask via xApp IH (A2C path).
- FR-5.2 Apply compromise parameter via E2SM-RC (QACM path).
- FR-5.3 Log all control directives with timestamps for reproducibility.

### FR-6 Benchmarks & Baselines
- FR-6.1 Conflicting independent deployment (both xApps active, no mitigation).
- FR-6.2 NSWF (non-priority game-theoretic benchmark).
- FR-6.3 EG (priority game-theoretic benchmark).
- FR-6.4 Baseline equal-allocation policies ($X_3$, $X_4$).

### FR-7 Experiment Orchestration
- FR-7.1 Scenario matrix: $d \in \{2,5,8\}$ Mbps × $v \in \{5,25,45\}$ m/s (9 combos) + training set $\{3,5,7,9\}$ Mbps × $\{10,20,30,40\}$ m/s.
- FR-7.2 Fixed RNG seeds per run; N repetitions for statistical significance.
- FR-7.3 Isolated runs per method under identical conditions (per `approach.md` §3).

### FR-8 Metrics & Reporting
- FR-8.1 Normalized transmission rate $\tau_e$ and leftover/discarded bits.
- FR-8.2 Per-xApp QoS satisfaction rate $s_i$ and KPI shortfall $d_i$.
- FR-8.3 Control-policy volatility: COV, SD, RMSSD of parameter/allocation series.
- FR-8.4 Mitigation latency: QACM solver/ANN time vs. A2C forward-pass time.
- FR-8.5 Conflict rate and context-dependence (low vs. high load/speed).

---

## 5. Non-Functional Requirements

### NFR-1 Latency
- NFR-1.1 Full control loop within Near-RT RIC budget (10 ms – 1 s).
- NFR-1.2 QACM solver + ANN inference must complete within the scheduling period.
- NFR-1.3 A2C actor/critic forward pass must be a small fraction of the period.

### NFR-2 Scalability
- NFR-2.1 Support $n \geq 2$ xApps; QACM heuristic must scale to large $|X'|$ and $N$.
- NFR-2.2 Scheduler action space must extend to additional xApps without redesign.

### NFR-3 Reproducibility
- NFR-3.1 Fixed seeds, versioned scenario configs, and full parameter logging.
- NFR-3.2 Identical network conditions across compared methods (same topology, mobility, traffic).

### NFR-4 Extensibility
- NFR-4.1 Pluggable xApps, mitigation methods, and schedulers via common interfaces.
- NFR-4.2 New conflict types (direct/indirect/implicit) addable without core changes.

### NFR-5 Observability
- NFR-5.1 Structured logging of states, actions, rewards, and control directives.
- NFR-5.2 Trace export (CSV/Parquet) for post-hoc analysis and thesis figures.

### NFR-6 Performance
- NFR-6.1 Training time for A2C scheduler ($10^5$ episodes) must be tractable on available compute.
- NFR-6.2 ANN training per xApp must be fast (small datasets, 10 epochs).

### NFR-7 Reliability & Safety
- NFR-7.1 Confidence-gated fallback must bound worst-case performance out-of-distribution.
- NFR-7.2 No xApp data sharing (QACM assumption); vendor isolation preserved.
- NFR-7.3 Graceful degradation on telemetry loss (lookback fill, fallback policy).

### NFR-8 Portability
- NFR-8.1 Code runs on the ns-O-RAN testbed and, with minimal change, on the TU Ilmenau ICS testbed (E2SM-RC Style 2 PRB control).
- NFR-8.2 Containerized components (RIC xApps, scheduler, QACM, CS xApp).

---

## 6. Assumptions & Constraints

- A1 EI is simulated (no Non-RT RIC in the ns-O-RAN testbed).
- xApps are immutable after training (O-RAN WG2 requirement); only the scheduler / CMC adapt.
- The controllable NCP surface is limited by ns-O-RAN's E2SM-RC implementation; the concrete conflicting parameter must be verified during Phase 1 (candidate: PRB allocation quota; TXP/RET/CIO only if supported).
- QACM's KPI prediction assumes the ANN generalizes to live conditions; drift handling is out of scope for the core comparison but noted as a limitation.
- The A2C scheduler optimizes a single intent (maximize $\tau_e$) in the baseline experiment.

---

## 7. Acceptance Criteria

1. Both mitigation engines run end-to-end on ns-O-RAN with a Near-RT RIC and produce control directives over E2SM-RC.
2. All 9 test scenarios × all methods (conflicting, A2C M1, A2C M2, QACM, QACMP, NSWF, EG) complete with logged metrics.
3. A2C scheduler outperforms the conflicting baseline; Method 2 ≥ Method 1 (reproducing 2504.06867v3).
4. QACM satisfies more per-xApp QoS thresholds than NSWF/EG (reproducing 2405.07324v2).
5. Latency of both engines measured and reported against the 10 ms–1 s budget.
6. Results reproducible from committed configs and seeds.