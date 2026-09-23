# Specification: Comparative Evaluation of A2C Context-Aware Scheduler vs. QACM in ns-O-RAN

**Status:** Draft (iter-2)
**Scope:** Experiment specification for the head-to-head evaluation of two xApp conflict-mitigation frameworks inside the Near-RT RIC, on the ns-O-RAN testbed.
**Iteration:** iter-2 — common scenario is the **QACM scenario** (ES vs. CCO direct conflict over TXP). See `../bak/iteration-index.md` for the pivot rationale.
**Sources:**
- Approach: `thesis-proposal/a2c-qacm/approach.md`, `a2c-scheduler-flow.md`, `qacm-flow.md`, `implementation.md`
- Literature: `literature/Context-Aware Dynamic Schedulers/2504.06867v3.md` (A2C Scheduler), `literature/Rule-Based & SLA Constraint Projection/2405.07324v2.md` (QACM)
- Testbed: `literature/testbed-info/ns3/available-params.md`
- Decisions: `thesis-proposal/a2c-qacm/open-questions.md` (Q1, Q2)

---

## 1. Experiment Overview

Two active, closed-loop conflict-mitigation engines are implemented inside the Near-RT RIC and evaluated under identical ns-O-RAN network conditions, on the **same scenario** (ES vs. CCO direct conflict over TXP):

| | **A2C Context-Aware Scheduler** | **QACM** |
| :--- | :--- | :--- |
| **Role** | Macro-level action coordinator | Micro-level parameter bargaining engine |
| **Core engine** | Advantage Actor-Critic (A2C) DRL | Constrained optimization / Heuristic Alg. 1 + ANN KPI regression |
| **Input** | Context variables $c^\dagger$ (load $d$, speed $v$) + intent $f^\dagger$ | Conflicting parameter $p_l$ (TXP), QoS thresholds $q'$, weights $w_i$, range $[p_{min},p_{max}]$ |
| **Output** | xApp activation mask $\mu^\dagger \in \{0,1\}^n$ | Optimal compromise TXP $p_l^{opt}$ via E2SM-RC |
| **QoS guarantee** | System-wide (multi-objective reward) | Explicit per-xApp QoS threshold satisfaction |
| **Re-training** | Lightweight scheduler only; xApps immutable | ANN regression models per xApp |

The experiment answers the repository's central question: *how can independently developed SON xApps safely share RAN control while preserving objectives, QoS/SLA requirements, and near-real-time constraints?* — by comparing the two dominant runtime-mitigation paradigms (action scheduling vs. parameter bargaining) on a common testbed and a common scenario.

### 1.1 Common Scenario (from 2405.07324v2 §VIII, extended with context)

- **Conflict:** ES (Energy Saving) vs. CCO (Capacity and Coverage Optimization) **direct conflict over TXP** (transmit power).
  - CCO maximizes downlink throughput ($\delta_{CCO}=0$, QoS threshold 9.5 Gbps).
  - ES minimizes power consumption ($\delta_{ES}=1$, QoS threshold 25 Wh).
  - Conflict trigger: ES sets TXP to 6 dBm from CCO's previous 40 dBm → throughput collapses below $q_{CCO}$.
- **Topology:** 2 gNBs, 10 UEs, 2.4 GHz, 20 MHz carrier, 10 min simulation at 100 ms time steps (matches E2SM-KPM periodicity).
- **Fixed ICPs:** CIO 2 dB, HYS 0.5 dB, TTT 0.1 ms, RET 1.5°, adjustment interval 1000 ms.
- **Optimal configuration range:** TXP ∈ [6, 40] dBm.
- **Reference result (paper):** QACM → 15 dBm (non-priority), QACMP → 16 dBm (priority); NSWF → 6 dBm, EG → 40 dBm.

### 1.2 Context Extension (for the A2C scheduler)

The QACM paper's scenario has no context dimension; the A2C scheduler requires context to be "context-aware". The scenario is therefore extended with the A2C paper's two context variables (2504.06867v3:315):

- Mean data arrival rate $c_1^\dagger = d \in \{5, 10, 15\}$ Gbps (bracketing the 9.5 Gbps QoS threshold).
- Average user speed $c_2^\dagger = v \in \{1, 3, 5\}$ m/s (within the QACM paper's 0–5 m/s range).

**Test matrix:** 9 combinations ($d \times v$). **Training set:** $d \in \{3, 7, 11\}$ Gbps × $v \in \{1, 3, 5\}$ m/s.

### 1.3 A2C Scheduler Adaptation (from 2504.06867v3, adapted to a direct conflict)

- **xApps:** ES ($X_1$) and CCO ($X_2$), both A2C-trained over TXP; baseline fixed-TXP policies ($X_3$ = low TXP, $X_4$ = high TXP).
- **State:** $s^\dagger = [c_1^\dagger, c_2^\dagger, f^\dagger] = [d, v, \text{intent}]$.
- **Action:** activation mask $\mu^\dagger$.
  - Method 1: $\mu^\dagger = [\mu_{ES}, \mu_{CCO}]$; a deactivated xApp **retains its last TXP action**.
  - Method 2: select one ES policy (A2C or baseline) and one CCO policy (A2C or baseline), $\mu_{ES}+\mu_{ES}^{base}=1$, $\mu_{CCO}+\mu_{CCO}^{base}=1$.
- **Reward (multi-objective):** primary = **QoS satisfaction** (number of xApps meeting thresholds, aligning with QACM's objective); alternative = weighted throughput + power term. See open question Q3.
- **Safety:** confidence-gated fallback (EWMA critic-value z-score → deterministic $\pi_{safe}$).

### 1.4 QACM (from 2405.07324v2)

- CMS framework: PMon, CDC, CMC, CS xApp, and database components (RCP, PGD, RCPG, PKR, DCKD, KDO).
- KPI→utility via z-score normalization $U(p) = (k(p)-\mu)/\sigma$, range $[-3,+3]$.
- ANN KPI regression: 4 hidden layers × 128 neurons, tanh, dropout 0.2, Adam, MSE, 10 epochs.
- Objective: $\min_{p_l} \sum_i w_i d_i \zeta - (\sum_i s_i)^2$; exact form $4|X'|$ vars / $4|X'|+2|N|+3$ constraints; heuristic $O(N \cdot |X'|)$.

---

## 2. Data Requirements

### 2.1 Met (available in ns-O-RAN telemetry, `available-params.md`)

| Requirement | Symbol | Source / Layer | Used by |
| :--- | :--- | :--- | :--- |
| UE identifier | $u$ | CU-CP | Both (per-UE state) |
| Serving/neighbor cell IDs | $c \in C'_{u,t}$ | CU-CP | Both (feature matrix columns) |
| SINR per UE per cell | $\text{SINR}_{u,c,t}$ | CU-CP (L3 RRC) | A2C state, QACM KPI |
| RSRP per UE per cell | $\text{RSRP}_{u,c,t}$ | CU-CP (L3 RRC) | A2C state, QACM KPI (handover) |
| PDCP DL throughput | $R_{u,t}$ | CU-UP (PDCP) | CCO KPI, A2C reward |
| PRB utilization % | $\text{PRB}_{c,t}$ | DU (MAC) | A2C state, power-model input |
| Active user count | $Z_{c,t}$ | DU (MAC) | A2C state (congestion) |
| Transport blocks | $P_{c,t}$ | DU (MAC) | Throughput proxy |
| Modulation ratios | $p^{QPSK}_{c,t}, p^{16QAM}_{c,t}, p^{64QAM}_{c,t}$ | DU (MAC) | Link-quality indicator |
| Handover cost penalty | $k(c_{u,t})$ | Near-RT RIC (calc.) | A2C reward shaping |
| 100 ms reporting periodicity | — | E2SM-KPM | Both (control-loop cadence) |
| Feature matrix $B \times C$ | — | RIC ETL | Both (model input) |
| Missing-data lookback $\epsilon$ | — | RIC ETL | Both (gap filling) |

### 2.2 Missing (must be generated, configured, or derived)

| Requirement | Symbol | Why missing | How to close |
| :--- | :--- | :--- | :--- |
| **TXP control action** | $p_l$ | Not in telemetry sheet; E2SM-RC power control (Style 8) unverified in ns-O-RAN | Verify in Phase 0; if unsupported, extend ns-O-RAN with a TXP control action or fall back to PRB-quota variant (see risk R1) |
| **Power consumption KPI** | $k_{ES}$ | Not in `available-params.md` | Model from TXP + PRB utilization via a configurable power model (e.g., $P = P_{base} + \alpha \cdot P_{tx}(TXP) \cdot \text{PRB}_{c,t}$); calibrate to the paper's 25 Wh threshold |
| Context variable: arrival rate | $c_1^\dagger = d$ | Not in telemetry sheet; simulation input / A1 EI | Expose as simulation config; inject via simulated A1 EI |
| Context variable: mobility speed | $c_2^\dagger = v$ | Not in telemetry sheet | Derive from ns-3 mobility model; inject via simulated A1 EI |
| Operator intent target | $f^\dagger$ | Not in telemetry sheet | Define fixed intent (maximize QoS satisfaction); inject via simulated A1 |
| QoS thresholds per xApp | $q'_i$ | SLA-defined | Use paper values: 9.5 Gbps (CCO), 25 Wh (ES) |
| Priority weights | $w_i$ | Produced by CS xApp (not present) | Implement CS xApp logic (MNO policy + network state) |
| KPI prediction training data | $\{(p_l, k)\}$ | Must be collected from ns-3 runs | Generate via TXP sweep runs; train ANN per xApp |
| KPI→utility statistics | $\mu, \sigma$ | Derived | Compute from collected KPI distributions |
| Conflict ground truth / labels | — | Not in telemetry sheet | Derive from KPI degradation events + TXP-change logs (CDC logic) |
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
| **E2SM-RC TXP (power) control** | Unverified | **Critical gate.** If ns-O-RAN lacks power control, extend the simulator or map the conflict onto a supported scalar NCP (PRB quota) |
| A1 interface / Non-RT RIC | Missing | No standardized EI delivery; simulate via HTTP/shared DB or direct injection |
| CS xApp (QACM weight provider) | Missing | Implement as lightweight xApp reading MNO policy + network state |
| CDC (Conflict Detection Controller) | Missing | Implement direct/indirect/implicit detection from KPM + parameter-change logs |
| PMon (Performance Monitoring) | Partial | KPM xApp exists; needs QoS-threshold comparison + KDO logging |
| CMS database (RCP, PGD, RCPG, PKR, DCKD, KDO) | Missing | Implement as shared data store (Redis/InfluxDB/MongoDB) |
| xApp Inference Host (IH) | Missing | Implement activation-mask enforcement + data-repo access control |
| Power-consumption model | Missing | Derive $k_{ES}$ from TXP + PRB utilization; calibrate to paper |
| DRL training infrastructure | Missing | Compute for scheduler + xApp training; CPU feasible for small state |
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
- FR-2.2 Provide intent target $f^\dagger$ (maximize QoS satisfaction).
- FR-2.3 Allow MNO policy configuration (weights, thresholds, fallback threshold).

### FR-3 A2C Scheduler (adapted to direct TXP conflict)
- FR-3.1 Build state $s^\dagger = [c_1^\dagger, c_2^\dagger, f^\dagger]$.
- FR-3.2 Actor inference $\pi_\theta(a^\dagger|s^\dagger)$ → distribution over activation decisions.
- FR-3.3 Critic inference $V_\phi(s^\dagger)$ → state-value baseline.
- FR-3.4 Confidence-gated fallback: EWMA of critic mean/dispersion, z-score threshold, $T_{back}$ override with $\pi_{safe}$; freeze statistics during back-off.
- FR-3.5 Action sampling → activation mask $\mu^\dagger$.
- FR-3.6 Method 1 (retain previous TXP action) and Method 2 (baseline extension, $\mu_{ES}+\mu_{ES}^{base}=1$, $\mu_{CCO}+\mu_{CCO}^{base}=1$).
- FR-3.7 Online training update: policy gradient + critic MSE loss.
- FR-3.8 Reward computation: QoS satisfaction (primary) or weighted throughput+power (alternative).

### FR-4 QACM
- FR-4.1 Conflict notification from CDC (parameter TXP, xApp set $X'$).
- FR-4.2 Optimal-range estimation: union of per-xApp ranges (TXP ∈ [6, 40] dBm).
- FR-4.3 Weight assignment from CS xApp ($\sum w_i = 1$).
- FR-4.4 KPI prediction per xApp via ANN regression (4×128, tanh, dropout 0.2, Adam, MSE).
- FR-4.5 KPI→utility conversion via z-score normalization.
- FR-4.6 Solve QACM objective (exact or Heuristic Alg. 1, $O(N\cdot|X'|)$).
- FR-4.7 Dispatch $p_l^{opt}$ via E2SM-RC control.
- FR-4.8 Loop on new KPI degradation / conflict (PMon → CDC → CMC).

### FR-5 Control Execution
- FR-5.1 Enforce activation mask via xApp IH (A2C path).
- FR-5.2 Apply compromise TXP via E2SM-RC (QACM path).
- FR-5.3 Log all control directives with timestamps for reproducibility.

### FR-6 Benchmarks & Baselines
- FR-6.1 Conflicting independent deployment (both xApps active, no mitigation).
- FR-6.2 NSWF (non-priority game-theoretic benchmark).
- FR-6.3 EG (priority game-theoretic benchmark).
- FR-6.4 Baseline fixed-TXP policies (low 6 dBm, high 40 dBm, mid 23 dBm).

### FR-7 Experiment Orchestration
- FR-7.1 Scenario matrix: $d \in \{5, 10, 15\}$ Gbps × $v \in \{1, 3, 5\}$ m/s (9 combos) + training set $\{3, 7, 11\}$ Gbps × $\{1, 3, 5\}$ m/s.
- FR-7.2 Fixed RNG seeds per run; N repetitions for statistical significance.
- FR-7.3 Isolated runs per method under identical conditions (per `approach.md` §3).

### FR-8 Metrics & Reporting
- FR-8.1 Downlink throughput (CCO KPI) and power consumption (ES KPI).
- FR-8.2 Per-xApp QoS satisfaction rate $s_i$ and KPI shortfall $d_i$.
- FR-8.3 Control-policy volatility: COV, SD, RMSSD of the TXP series.
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
- NFR-6.1 Training time for A2C scheduler and xApps must be tractable on available compute.
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
- **Critical constraint (R1):** the QACM scenario requires TXP control over E2SM-RC. ns-O-RAN's power-control support is unverified. If unsupported, the experiment must either (a) extend ns-O-RAN with a TXP control action, or (b) fall back to a PRB-quota variant of the same ES/CCO conflict (QACM is parameter-agnostic; the machinery is unchanged, but the paper's 15/16 dBm reference no longer applies).
- Power consumption is not a native ns-O-RAN KPM; it must be modeled from TXP + PRB utilization and calibrated to the paper's 25 Wh threshold.
- QACM's KPI prediction assumes the ANN generalizes to live conditions; drift handling is out of scope for the core comparison but noted as a limitation.
- **Open decision (QACM fallback, Q1):** the QACM formulation always returns a compromise $p_l^{opt}$ (bounded search over $[p_{min,opt}, p_{max,opt}]$), so no infeasibility branch exists in the paper or flowchart. Neither specifies a fallback when the best compromise still leaves some/all xApps below their QoS thresholds ($s_i = 0$). The experiment must define one — candidates: (a) dispatch anyway and log the shortfall, (b) reject the action and keep the previous parameter value, (c) escalate to the CS xApp / MNO policy. This is a fair comparison point against the A2C scheduler's confidence-gated fallback.
- **Open decision (scenario mapping, Q2):** the QACM scenario is the common scenario; the A2C scheduler is extended to arbitrate a direct TXP conflict. The complications (reward redesign, conflict-type extension, no compromise granularity) are accepted and reported.
- **Open decision (A2C reward, Q3):** primary reward = QoS satisfaction (aligns with QACM's objective); alternative = weighted throughput + power. To be decided in Phase 3.

---

## 7. Acceptance Criteria

1. Both mitigation engines run end-to-end on ns-O-RAN with a Near-RT RIC and produce TXP control directives over E2SM-RC.
2. All 9 test scenarios × all methods (conflicting, A2C M1, A2C M2, QACM, QACMP, NSWF, EG) complete with logged metrics.
3. QACM reproduces the paper's qualitative result: QACM/QACMP satisfy more per-xApp QoS thresholds than NSWF/EG (2405.07324v2); on the reference case, QACM ≈ 15 dBm, QACMP ≈ 16 dBm.
4. A2C scheduler outperforms the conflicting baseline; Method 2 ≥ Method 1 on the multi-objective reward (adapted from 2504.06867v3).
5. Latency of both engines measured and reported against the 10 ms–1 s budget.
6. Results reproducible from committed configs and seeds.