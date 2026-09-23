### GRAPHICA vs. QACM Evaluation Methodology

While **GRAPHICA** and **QACM (QoS-Aware xApp Conflict Mitigation)** operate within the O-RAN Near-RT RIC on near-real-time timescales (10 ms – 1 s), they fulfill fundamentally different functional roles:

* **GRAPHICA** is a **predictive anomaly detector and diagnostic tool** that uses a 2-layer Graph Convolutional Network (GCN) on binary-state subgraphs to forecast conflicts before they physically manifest and pinpoint root-cause xApps.
* **QACM** is an **active, game-theoretic optimization engine** that calculates an optimal compromise parameter value ($p_l^{\text{opt}}$) to maximize the number of coexisting xApps meeting their Quality of Service (QoS) benchmarks.

To construct an effective comparative evaluation in **ns-3** or on a physical testbed, the two frameworks can be benchmarked across the following five technical dimensions, followed by a unified cooperative pipeline.

---

### Technical Evaluation Dimensions

#### 1. End-to-End Network KPI & QoS Preservation
Although GRAPHICA acts as an observer and QACM acts as a parameter optimizer, both ultimately aim to protect network Quality of Service. When GRAPHICA is paired with a simple reaction policy (e.g., pausing the root-cause xApp flagged by its RCA module), its network impact can be directly compared to QACM's continuous parameter adjustments.
* **What to measure in ns-3:**
  * **QoS Satisfaction Rate:** The percentage of active xApps that maintain their required QoS thresholds ($q_i$) under conflicting conditions.
  * **KPI Shortfall & Degradation:** The relative drop in downlink throughput (Mbps), buffer size overflow, and power consumption relative to single-app baselines.
  * **Allocation Volatility:** PRB and power allocation stability measured via the **Coefficient of Variation (COV)**, **Standard Deviation (SD)**, and **Root Mean Square of Successive Differences (RMSSD)**.

#### 2. Near-RT RIC Latency & Computational Overhead
Both frameworks must complete processing within the Near-RT RIC latency budget (10 ms – 1 s).
* **What to measure in ns-3:**
  * **Inference vs. Optimization Time (ms):** Measure GRAPHICA's GCN forward-pass time and global mean pooling against QACM's optimization solver / heuristic loop (Algorithm 1) execution time.
  * **Data Pipeline Processing Cost:** Compare the overhead of constructing binary-state subgraphs ($G^{PA}, G^{KP}, G^{P'P}$) against QACM's z-score normalization and ANN regression forward passes for KPI prediction.

#### 3. Scalability & Handling Imbalanced Datasets
* **Scalability under Increasing xApp Counts ($|X'|$):** GRAPHICA handles multi-entity interactions via graph message passing. In contrast, QACM's optimization problem complexity grows with the number of constraints ($4|X'| + 2|N| + 3$), which can make iterative bargaining less tractable for large xApp sets without heuristic approximations.
* **Class Imbalance & Rare Event Handling:** Test how GRAPHICA's **Focal Loss** ($\alpha_c, \gamma$) performs when conflicts represent only 10%–40% of operational data, compared to QACM's mathematical optimization over bounded parameter ranges ($p_{\text{min,opt}}, p_{\text{max,opt}}$).

#### 4. Diagnostic Capability & Explainability (RCA vs. Mathematical Optimization)
* **GRAPHICA:** Provides high structural explainability. Its **Root Cause Analysis (RCA)** module isolates graph nodes with more than one incoming edge to reveal the exact xApps and parameters causing the clash.
* **QACM:** Functions as a quantitative optimization engine. It computes specific utility deviation distances ($d_i$) and satisfaction scores ($s_i$), but does not generate structural causality graphs explaining *why* the parameter clash occurred.

#### 5. Data & Training Dependencies
* **GRAPHICA:** Is **distribution-independent**. It relies on binary state transitions ($S_t \in \{0, 1\}$) relative to timestamp $t-1$, making it robust against shifting traffic distributions without requiring re-training.
* **QACM:** Is dependent on **accurate KPI prediction models** (e.g., pre-trained ANN regression models) to evaluate parameter settings. If network dynamics alter the underlying KPI distribution, QACM's prediction accuracy may degrade.

---

### Comparison Summary Matrix

| Metric / Dimension | GRAPHICA Module | QACM Framework |
| :--- | :--- | :--- |
| **Primary Role** | Predictive Anomaly Detection & RCA | Post-Action QoS-Aware Parameter Optimization |
| **Input Signals** | Binary-state vectors ($S_t = \{s_A, s_P, s_K\}$) | Controllable parameters ($P$), z-score utilities ($U(p)$), QoS thresholds ($q'$) |
| **Core AI / Math Engine** | 2-layer GCN with Focal Loss | Cooperative Game Theory / Optimization Problem (or Heuristic Alg 1) + ANN Regression |
| **Primary Output** | Conflict label (0–3) + Root-cause xApp list | Optimal compromise parameter value ($p_l^{\text{opt}}$) sent over E2SM Control |
| **Explainability** | **High** (Subgraph inspection of nodes with $>1$ incoming edge) | **Medium/Low** (Quantitative utility distances $d_i$, no causal graphs) |
| **Distribution Independence** | **High** (Binary state transitions relative to $t-1$) | **Low** (Requires pre-trained ANN models for KPI prediction) |
| **Scalability ($|X'|$)** | **High** (Graph convolutional aggregation) | **Medium** (Constraint set grows as $4|X'|+2|N|+3$; relies on heuristic for large $|X'|$) |

---

### Unified Cooperative Pipeline (GRAPHICA + QACM)

In an integrated O-RAN Near-RT RIC architecture, GRAPHICA and QACM can be combined into a **two-stage predictive and resolution pipeline**:

1. **Detection Phase ($t_1$):** **GRAPHICA** continuously monitors binary state transitions over E2SM-KPM. At timestamp $t_1$, it predicts an impending conflict (prior to physical conflict onset at $t_2$ and KPI drop at $t_3$) and runs its RCA module to isolate the root-cause xApps.
2. **Mitigation Phase ($t_2$):** Instead of simply deactivating or pausing the root-cause xApp, GRAPHICA's alert triggers **QACM**. QACM ingests the QoS thresholds of the identified xApps, runs its optimization algorithm over the parameter configuration bounds, and outputs the optimal compromise parameter setting ($p_l^{\text{opt}}$) over E2SM Control to resolve the conflict before network performance degrades.

---

🎯 **Suggested Next Steps:**
* Would you like assistance drafting an **ns-3 C++ / Python logging script** to collect both binary state vectors for GRAPHICA and z-score normalized KPI utilities for QACM?
* Should we update your presentation slides in the Studio panel to include this comparison matrix?