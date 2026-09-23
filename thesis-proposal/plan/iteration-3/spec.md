# Specification: Comparative Evaluation of A2C Context-Aware Scheduler vs. QACM in ns-O-RAN

**Status:** Draft (iter-3)
**Scope:** Experiment specification for the head-to-head evaluation of two xApp conflict-mitigation frameworks inside the Near-RT RIC, on the ns-O-RAN testbed.
**Iteration:** iter-3 — common scenario is the **A2C scenario** (Power xApp + RBG xApp indirect conflict), with QACM extended to joint-parameter bargaining. See `../iteration-index.md` for the iteration history.
**Sources:**
- Approach: `thesis-proposal/a2c-qacm/approach.md`, `a2c-scheduler-flow.md`, `qacm-flow.md`, `implementation.md`
- Literature: `literature/Context-Aware Dynamic Schedulers/2504.06867v3.md` (A2C Scheduler), `literature/Rule-Based & SLA Constraint Projection/2405.07324v2.md` (QACM)
- Testbed: `literature/testbed-info/ns3/available-params.md`
- Decisions: `thesis-proposal/open-questions.md` (Q1, Q2 → Proposal B, Q3 → moot)

---

## 1. Experiment Overview

Two active, closed-loop conflict-mitigation engines are implemented inside the Near-RT RIC and evaluated under identical ns-O-RAN network conditions, on the **same scenario** (Power + RBG indirect conflict over TXP and RBG allocation):

| | **A2C Context-Aware Scheduler** | **QACM** |
| :--- | :--- | :--- |
| **Role** | Macro-level action coordinator | Micro-level parameter bargaining engine |
| **Core engine** | Advantage Actor-Critic (A2C) DRL | Constrained optimization / Heuristic Alg. 1 + ANN KPI regression |
| **Input** | Context variables $c^\dagger$ (load $d$, speed $v$) + intent $f^\dagger$ | Joint control vector $\mathbf{p} = [p_{power}, p_{RBG}]$ + context $(d, v)$, QoS thresholds $q'$, weights $w_i$ |
| **Output** | xApp activation mask $\mu^\dagger \in \{0,1\}^n$ | Optimal joint compromise $\mathbf{p}^{opt}$ via E2SM-RC |
| **QoS guarantee** | System-wide (native reward $\tau_e$) | Explicit per-xApp QoS threshold satisfaction |
| **Re-training** | Lightweight scheduler only; xApps immutable | ANN regression models per xApp |
| **Fidelity** | **As published** (2504.06867v3) | **Extended** beyond the paper (joint-parameter bargaining, context-conditioned ANN, scalarized RBG) |

The experiment answers the repository's central question: *how can independently developed SON xApps safely share RAN control while preserving objectives, QoS/SLA requirements, and near-real-time constraints?* — by comparing the two dominant runtime-mitigation paradigms (action scheduling vs. parameter bargaining) on a common testbed and a common scenario.

### 1.1 Common Scenario (from 2504.06867v3, adapted to the testbed)

- **Conflict:** Power xApp ($X_1$) + RBG xApp ($X_2$) **indirect conflict** over two NCPs — TXP and RBG allocation — affecting the shared throughput KPM.
  - $X_1$ (Power) maximizes the normalized transmission rate $\tau_e$ by setting per-cell TXP.
  - $X_2$ (RBG) maximizes $\tau_e$ by allocating RBGs to users.
  - Conflict trigger (paper): the Power xApp assigns power to RBGs not allocated to any user; the RBG xApp assigns RBGs to users that receive low power → throughput drops and leftover (discarded) bits accumulate.
- **Topology (testbed adaptation):** 2 gNBs, 10 UEs, 20 MHz carrier, 10 min simulation at 100 ms time steps (matches E2SM-KPM periodicity). The paper uses 4 O-RUs / 16 UEs; the testbed constraint is 2 gNBs / 10 UEs.
- **RBGs:** 12 RBGs per gNB (paper's granularity; 100 PRBs at 20 MHz).
- **Power:** TXP ∈ [1, 38] dBm, $K$ quantization levels (paper's discrete power set).
- **Scheduling period:** 10 time steps × 100 ms = 1 s (paper: † = 10, $T_s$ = 100 ms).
- **Episode:** $T$ = 50 time steps = 5 s.
- **Reference result (paper):** Method 2 > Method 1 > conflicting on $\tau_e$; conflict severity is context-dependent (16% degradation at high load/speed vs. 5% at low).

### 1.2 Context Variables (native to the A2C scenario)

- Mean data arrival rate $c_1^\dagger = d$: training $\{3, 5, 7, 9\}$ Mbps; test $\{2, 5, 8\}$ Mbps.
- Average user speed $c_2^\dagger = v$: training $\{10, 20, 30, 40\}$ m/s; test $\{5, 25, 45\}$ m/s.
- **Test matrix:** 9 combinations ($d \times v$).

### 1.3 A2C Scheduler (as published, 2504.06867v3)

- **xApps:** Power ($X_1$), RBG ($X_2$), both A2C-trained; baseline policies ($X_3$, $X_4$) for Method 2.
- **State:** $s^\dagger = [c_1^\dagger, c_2^\dagger, f^\dagger] = [d, v, \text{intent}]$.
- **Action:** activation mask $\mu^\dagger$.
  - Method 1: $\mu^\dagger = [\mu_1, \mu_2]$; a deactivated xApp **retains its last action**.
  - Method 2: select from $\{X_1, X_2, X_3, X_4\}$.
- **Reward:** **native** normalized transmission rate $\tau_e$ (no redesign; Q3 moot).
- **Safety:** confidence-gated fallback (EWMA critic-value z-score → deterministic $\pi_{safe}$).
- **Training:** $10^5$ episodes, $T$ = 50, scheduling period 10 steps, $\eta = 10^{-4}$, $\gamma = 0.95$.

### 1.4 QACM (extended to joint-parameter bargaining, 2405.07324v2)

- CMS framework: PMon, CDC, CMC, CS xApp, and database components (RCP, PGD, RCPG, PKR, DCKD, KDO).
- Bargains over the **joint control vector** $\mathbf{p} = [p_{power}, p_{RBG}]$:
  - $p_{power} \in [1, 38]$ dBm ($K$ levels)
  - $p_{RBG} \in \{0, \dots, 12\}$ RBGs per gNB (scalarized allocation)
- **Context-conditioned ANN:** predicts KPIs ($\tau_e$, leftover bits) from $(\mathbf{p}, d, v)$.
- KPI→utility via z-score normalization $U(\mathbf{p}) = (k(\mathbf{p})-\mu)/\sigma$, range $[-3,+3]$.
- Objective: $\min_{\mathbf{p}} \sum_i w_i d_i \zeta - (\sum_i s_i)^2$ over the joint range; exact = 2D search ($|P| \times (R+1)$ candidates); heuristic = 2D grid search.
- **QoS thresholds (defined for the A2C scenario):** $q_1$: $\tau_e \geq 0.9$ (Power xApp KPI); $q_2$: leftover-bits ratio $\leq 0.05$ (RBG xApp KPI).
- Dispatch: TXP + RBG quota via E2SM-RC.

---

## 2. Data Requirements

### 2.1 Met (available in ns-O-RAN telemetry, `available-params.md`)

| Requirement | Symbol | Source / Layer | Used by |
| :--- | :--- | :--- | :--- |
| UE identifier | $u$ | CU-CP | Both (per-UE state) |
| Serving/neighbor cell IDs | $c \in C'_{u,t}$ | CU-CP | Both (feature matrix columns) |
| SINR per UE per cell | $\text{SINR}_{u,c,t}$ | CU-CP (L3 RRC) | A2C state, QACM KPI |
| RSRP per UE per cell | $\text{RSRP}_{u,c,t}$ | CU-CP (L3 RRC) | A2C state, QACM KPI |
| PDCP DL throughput | $R_{u,t}$ | CU-UP (PDCP) | $\tau_e$ computation, QACM KPI |
| PRB utilization % | $\text{PRB}_{c,t}$ | DU (MAC) | RBG allocation proxy, A2C state |
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
| **TXP control action** | $p_{power}$ | Not in telemetry sheet; E2SM-RC power control (Style 8) unverified in ns-O-RAN | Verify in Phase 0; if unsupported, extend ns-O-RAN with a TXP control action (see risk R1) |
| **RBG allocation control** | $p_{RBG}$ | Not in telemetry sheet; E2SM-RC PRB quota (Style 2) expected supported | Verify in Phase 0; map RBG quota to PRB utilization control |
| **Leftover/discarded bits KPI** | $L$ | Not in `available-params.md` | Derive from offered load $d$ vs. delivered $R_{u,t}$: $L = \max(0, d - \sum_u R_{u,t})$ per period |
| Context variable: arrival rate | $c_1^\dagger = d$ | Not in telemetry sheet; simulation input / A1 EI | Expose as simulation config; inject via simulated A1 EI |
| Context variable: mobility speed | $c_2^\dagger = v$ | Not in telemetry sheet | Derive from ns-3 mobility model; inject via simulated A1 EI |
| Operator intent target | $f^\dagger$ | Not in telemetry sheet | Define fixed intent (maximize total transmission rate); inject via simulated A1 |
| QoS thresholds per xApp | $q'_i$ | SLA-defined; A2C scenario has none | Define: $q_1$: $\tau_e \geq 0.9$; $q_2$: leftover ratio $\leq 0.05$ |
| Priority weights | $w_i$ | Produced by CS xApp (not present) | Implement CS xApp logic (MNO policy + network state) |
| KPI prediction training data | $\{(\mathbf{p}, d, v) \to k\}$ | Must be collected from ns-3 runs | Generate via TXP × RBG sweep runs; train context-conditioned ANN per xApp |
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
| **E2SM-RC TXP (power) control** | Unverified | **Critical gate.** If ns-O-RAN lacks power control, extend the simulator with a TXP control action |
| **E2SM-RC RBG / PRB quota control (Style 2)** | Expected supported | Verify in Phase 0; used for the RBG xApp and QACM's $p_{RBG}$ dispatch |
| A1 interface / Non-RT RIC | Missing | No standardized EI delivery; simulate via HTTP/shared DB or direct injection |
| CS xApp (QACM weight provider) | Missing | Implement as lightweight xApp reading MNO policy + network state |
| CDC (Conflict Detection Controller) | Missing | Implement indirect-conflict detection from KPM + parameter-change logs |
| PMon (Performance Monitoring) | Partial | KPM xApp exists; needs QoS-threshold comparison + KDO logging |
| CMS database (RCP, PGD, RCPG, PKR, DCKD, KDO) | Missing | Implement as shared data store (Redis/InfluxDB/MongoDB) |
| xApp Inference Host (IH) | Missing | Implement activation-mask enforcement + data-repo access control |
| Leftover-bits derivation | Missing | Derive $L$ from offered load vs. delivered throughput |
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
- FR-2.2 Provide intent target $f^\dagger$ (maximize total transmission rate).
- FR-2.3 Allow MNO policy configuration (weights, thresholds, fallback threshold).

### FR-3 A2C Scheduler (as published, 2504.06867v3)
- FR-3.1 Build state $s^\dagger = [c_1^\dagger, c_2^\dagger, f^\dagger]$.
- FR-3.2 Actor inference $\pi_\theta(a^\dagger|s^\dagger)$ → distribution over activation decisions.
- FR-3.3 Critic inference $V_\phi(s^\dagger)$ → state-value baseline.
- FR-3.4 Confidence-gated fallback: EWMA of critic mean/dispersion, z-score threshold, $T_{back}$ override with $\pi_{safe}$; freeze statistics during back-off.
- FR-3.5 Action sampling → activation mask $\mu^\dagger$.
- FR-3.6 Method 1 (retain previous action of deactivated xApp) and Method 2 (baseline extension over $\{X_1, X_2, X_3, X_4\}$).
- FR-3.7 Online training update: policy gradient + critic MSE loss.
- FR-3.8 Reward computation: **native** normalized transmission rate $\tau_e$.

### FR-4 QACM (extended to joint-parameter bargaining)
- FR-4.1 Conflict notification from CDC (parameters TXP + RBG, xApp set $X'$).
- FR-4.2 Optimal-range estimation: union of per-xApp ranges ($p_{power} \in [1, 38]$ dBm, $p_{RBG} \in \{0, \dots, 12\}$).
- FR-4.3 Weight assignment from CS xApp ($\sum w_i = 1$).
- FR-4.4 Context-conditioned KPI prediction per xApp via ANN regression (inputs $(\mathbf{p}, d, v)$; 4×128, tanh, dropout 0.2, Adam, MSE).
- FR-4.5 KPI→utility conversion via z-score normalization.
- FR-4.6 Solve QACM objective over the joint range (exact 2D search or 2D-grid heuristic).
- FR-4.7 Dispatch $\mathbf{p}^{opt} = [p_{power}^{opt}, p_{RBG}^{opt}]$ via E2SM-RC control.
- FR-4.8 Loop on new KPI degradation / conflict (PMon → CDC → CMC).

### FR-5 Control Execution
- FR-5.1 Enforce activation mask via xApp IH (A2C path).
- FR-5.2 Apply joint compromise (TXP + RBG quota) via E2SM-RC (QACM path).
- FR-5.3 Log all control directives with timestamps for reproducibility.

### FR-6 Benchmarks & Baselines
- FR-6.1 Conflicting independent deployment (both xApps active, no mitigation).
- FR-6.2 NSWF (non-priority game-theoretic benchmark over the joint vector).
- FR-6.3 EG (priority game-theoretic benchmark over the joint vector).
- FR-6.4 Baseline policies $X_3$, $X_4$ (equal allocation / fixed TXP) for Method 2.

### FR-7 Experiment Orchestration
- FR-7.1 Scenario matrix: test $d \in \{2, 5, 8\}$ Mbps × $v \in \{5, 25, 45\}$ m/s (9 combos); training $d \in \{3, 5, 7, 9\}$ Mbps × $v \in \{10, 20, 30, 40\}$ m/s.
- FR-7.2 Fixed RNG seeds per run; N repetitions for statistical significance.
- FR-7.3 Isolated runs per method under identical conditions (per `approach.md` §3).

### FR-8 Metrics & Reporting
- FR-8.1 Normalized transmission rate $\tau_e$ and leftover (discarded) bits.
- FR-8.2 Per-xApp QoS satisfaction rate $s_i$ and KPI shortfall $d_i$ (thresholds $q_1$, $q_2$).
- FR-8.3 Control-policy volatility: COV, SD, RMSSD of the TXP and RBG series.
- FR-8.4 Mitigation latency: QACM solver/ANN time vs. A2C forward-pass time.
- FR-8.5 Conflict rate and context-dependence (low vs. high load/speed).

---

## 5. Non-Functional Requirements

### NFR-1 Latency
- NFR-1.1 Full control loop within Near-RT RIC budget (10 ms – 1 s).
- NFR-1.2 QACM solver + ANN inference must complete within the scheduling period (1 s).
- NFR-1.3 A2C actor/critic forward pass must be a small fraction of the period.

### NFR-2 Scalability
- NFR-2.1 Support $n \geq 2$ xApps; QACM heuristic must scale to large $|X'|$ and joint ranges.
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
- **Critical constraint (R1):** the scenario requires TXP control over E2SM-RC (Style 8), which is unverified in ns-O-RAN. RBG/PRB quota control (Style 2) is expected supported. If TXP control is unsupported, the experiment must extend ns-O-RAN with a TXP control action.
- Leftover bits are not a native ns-O-RAN KPM; they are derived from offered load vs. delivered throughput.
- **QoS thresholds are defined for the A2C scenario** (design decision): $q_1$: $\tau_e \geq 0.9$; $q_2$: leftover ratio $\leq 0.05$. The A2C paper has no QoS thresholds (it optimizes $\tau_e$); these make QACM's objective and the comparison meaningful.
- **QACM is extended beyond the paper** (joint-parameter bargaining, context-conditioned ANN, scalarized RBG allocation). These extensions are accepted and reported as such in the thesis.
- **Open decision (QACM fallback, Q1):** the QACM formulation always returns a compromise $\mathbf{p}^{opt}$ (bounded search), so no infeasibility branch exists in the paper or flowchart. Neither specifies a fallback when the best compromise still leaves some/all xApps below their QoS thresholds ($s_i = 0$). The experiment must define one — candidates: (a) dispatch anyway and log the shortfall, (b) reject the action and keep the previous parameter values, (c) escalate to the CS xApp / MNO policy. This is a fair comparison point against the A2C scheduler's confidence-gated fallback.
- **Scenario mapping (Q2):** Proposal B — the A2C scenario is the common scenario; QACM is extended to joint-parameter bargaining. The QACM-side extensions are accepted and reported.
- **A2C reward (Q3):** moot under Proposal B — the native reward $\tau_e$ is used.
- **Additional open decisions (Q4–Q11, see `open-questions.md`):** QoS thresholds for the A2C scenario (Q4); RBG scalarization and enforcement (Q5); QACM joint-parameter optimization formulation (Q6); Power xApp control granularity (Q7); context-conditioned ANN training data and leakage (Q8); testbed scenario parameter selection (Q9); leftover-bits derivation (Q10); A2C training location (Q11).

---

## 7. Acceptance Criteria

1. Both mitigation engines run end-to-end on ns-O-RAN with a Near-RT RIC and produce TXP + RBG control directives over E2SM-RC.
2. All 9 test scenarios × all methods (conflicting, A2C M1, A2C M2, QACM, QACMP, NSWF, EG) complete with logged metrics.
3. A2C scheduler reproduces the paper's qualitative result: Method 2 ≥ Method 1 > conflicting on $\tau_e$; conflict severity is context-dependent (16% degradation at high load/speed vs. 5% at low, 2504.06867v3).
4. QACM (joint-parameter) satisfies more per-xApp QoS thresholds than NSWF/EG (adapted from 2405.07324v2).
5. Latency of both engines measured and reported against the 10 ms–1 s budget.
6. Results reproducible from committed configs and seeds.