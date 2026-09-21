**QACM** and the **A2C Context-Aware Scheduler** are the two best-suited frameworks for a direct, head-to-head comparative evaluation.

---

### Why QACM vs. A2C Scheduler is the Best Comparison

#### 1. They Share the Same Functional Objective (Active Runtime Mitigation)
* **Active Execution Engines:** Both frameworks reside inside the Near-RT RIC and actively issue control decisions over the E2 interface to resolve runtime xApp conflicts and preserve network Quality of Service (QoS).
* **Contrast with GRAPHICA:** In contrast, **GRAPHICA** is fundamentally a **passive predictive detector and diagnostic tool** that classifies conflict states via a 2-layer Graph Convolutional Network (GCN) and pinpoints root causes without issuing control commands.

---

#### 2. They Represent the Two Primary Runtime Mitigation Paradigms
Comparing QACM against the A2C Scheduler allows you to evaluate two distinct architectural philosophies for solving runtime conflicts:

* **Micro-Level Parameter Bargaining (QACM):** Intercepts contentious numerical requests for shared control parameters (e.g., transmit power, RET, CIO) and uses z-score utility optimization to calculate an optimal compromise parameter value ($p_l^{\text{opt}}$) that explicitly satisfies individual xApp QoS thresholds ($q'$) [111, 134–135, 159–160].
* **Macro-Level Action Coordination (A2C Scheduler):** Operates as a policy orchestrator that ingests physical context variables (e.g., traffic arrival rate $d$, user speed $v$) and uses Advantage Actor-Critic DRL to dynamically select an xApp activation mask ($\mu^\dagger$) or fall back to baseline equal-allocation policies [297, 343–345, 353–354].

---

#### 3. Common Benchmarking Metrics in ns-3
Because both frameworks actively modify network operations, they can be evaluated under identical ns-3 simulation conditions across the same key performance metrics:
* **End-to-End QoS & Throughput Preservation:** Measuring normalized transmission rates ($\tau_e$), packet drop/leftover bit reductions, and individual xApp QoS satisfaction rates [111, 346–348].
* **Control Policy Volatility:** Measuring parameter/allocation stability using Coefficient of Variation (**COV**), Standard Deviation (**SD**), and Root Mean Square of Successive Differences (**RMSSD**).
* **RIC Latency Budget:** Comparing the execution time of QACM's optimization solver/ANN regression passes against the forward-pass inference latency of the A2C Actor network within the Near-RT RIC timescale (10 ms – 1 s) [1, 154–156, 162, 350].

---

### Where GRAPHICA could be fit

Rather than directly competing against QACM or the A2C Scheduler, **GRAPHICA is best paired *with* one of them in a two-stage cooperative pipeline**:
1. **Detector Stage (GRAPHICA):** Predicts an impending conflict at time $t_1$ prior to physical manifestation ($t_2$) and identifies the root-cause xApps.
2. **Actuator Stage (QACM or A2C Scheduler):** Triggered by GRAPHICA's alert to dynamically adjust parameters (via QACM) or switch active xApp policies (via A2C Scheduler) before physical KPI degradation occurs [1, 159–160, 351, 429].
