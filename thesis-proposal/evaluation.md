### Evaluation Methodology

GRAPHICA and the A2C Context-Aware Scheduler fulfill different functional roles
- GRAPHICA is a predictive anomaly detector and diagnostic tool 
- A2C Scheduler is an active policy coordinator and mitigation engine 
- they can only be compared directly when evaluated on their end-to-end impact on the Near-RT RIC control loop 

To structure an effective comparison in ns-3 or on the testbed, evaluate them across the following five technical dimensions:
1. End-to-End Network KPI Preservation
    - When coupled with a basic reaction policy (e.g., pausing the root-cause xApp flagged by GRAPHICA), both systems ultimately aim to protect network Quality of Service (QoS).
    - What to measure in ns-3:
        - Normalized Transmission Rate & Throughput: Evaluate how effectively each framework prevents throughput degradation under uncoordinated xApp execution.
        - Leftover / Discarded Bits: Quantify the reduction in dropped bits caused by buffer overflows during conflict events.
        - Control Policy Stability: Measure allocation volatility using Coefficient of Variation (COV), Standard Deviation (SD), and Root Mean Square of Successive Differences (RMSSD).
2. Near-RT RIC Real-Time Latency & Computational Overhead
    - Both frameworks operate within the Near-RT RIC control loop (10 ms – 1 s) 13, 14.
    - What to measure in ns-3:
        - Inference Latency (ms): Measure the time required for GRAPHICA's 2-layer GCN graph convolution and mean pooling versus the forward-pass execution time of the A2C Actor network.
        - Data Pipeline Overhead: Compare the processing cost of constructing binary-state subgraphs ($G^{PA}, G^{KP}, G^{P'P}$) against formatting physical context vectors ($c^\dagger$).
3. Adaptability Across Dynamic Network Contexts
    - A major bottleneck in conflict management is that conflicts are context-dependent—two xApps may coexist peacefully under low load or speed, but heavily conflict under high mobility or load 10, 26.
    - What to measure in ns-3:
        - Context Sensitivity: Test both models across diverse operational scenarios combining varying traffic arrival rates ($d \in \{2, 5, 8\}\text{ Mbps}$) and user mobility speeds ($v \in \{5, 25, 45\}\text{ m/s}$).
        - Out-of-Distribution Handling: Evaluate GRAPHICA's classification accuracy using Focal Loss under class imbalance versus the A2C Scheduler's behavior (and its confidence-gated fallback mechanism) when encountering unseen context states.
4. Diagnostic Capability & Explainability (RCA vs. Black-Box Control)
    - GRAPHICA: Provides explicit Root Cause Analysis (RCA) by inspecting graph nodes with multiple incoming edges, allowing operators to see exactly which xApps and parameters caused the clash 2, 33, 34.
    - A2C Scheduler: Functions as an active decision engine that selects or overrides xApp actions, but operates as a black-box policy without providing explicit structural causal graphs 4, 35, 36.
5. Training & Maintenance Requirements
    - GRAPHICA: Is distribution-independent and trained on structural binary state transitions ($S_t \in \{0, 1\}$) 19-21, 37, 38. It does not require re-training when traffic distributions shift.
    - A2C Scheduler: Requires lightweight online re-training whenever a new set of xApps or new operator intent target ($f^\dagger$) is onboarded.
6. Cooperative Pipeline
    - The two approaches can be combined into a unified two-stage framework: GRAPHICA acts as the Detector ($t_1$) to raise an early warning and identify root causes, which then triggers the A2C Scheduler as the Actuator ($t_2$) to dynamically alter active xApp policies before physical KPI degradation occurs.

### Comparison Summary Matrix

| Metric | Dimension,GRAPHICA Module | A2C Context-Aware Scheduler |
| -------- | ------------------------- | ------------------------- |
| Primary Role | "Predictive Anomaly Detection & RCA" | "Active Action Coordination & Mitigation"
| Input Signals | "Binary-state vectors ($S_t = \{s_A, s_P, s_K\}$)" | "Context variables ($c^\dagger$: load, speed) + Intent ($f^\dagger$) " |
| Core AI Engine | "2-layer GCN with Focal Loss" | "Advantage Actor-Critic (A2C) DRL" |
| Primary Output | "Conflict label (0–3) + Root-cause xApp list" | "Action selection / xApp activation mask ($\mu^\dagger$)" |
| Explainability | High (Subgraph inspection of incoming edges)  | Low (Black-box RL policy decisions) |
| Re-training Need | Trained once on multi-entity graph structures | Re-trained when xApp sets or intents change |

