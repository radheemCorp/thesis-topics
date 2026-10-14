Technical Report: Comparative Analysis of Conflict Mitigation Frameworks in O-RAN Near-RT RIC

1. Strategic Significance of Conflict Mitigation in Open RAN Architecture

In the O-RAN Alliance framework, specifically within the scope of Work Group 3 (WG3), the Near-Real-Time RAN Intelligent Controller (Near-RT RIC) is the central point of intelligence for the Radio Access Network. As Mobile Network Operators (MNOs) move toward multi-vendor ecosystems, the Near-RT RIC must host a variety of xApps—potentially developed by different vendors—that simultaneously optimize the same underlying RAN resources. This environment creates an inherent risk of conflicting control actions, where one xApp’s optimization logic may countermand another’s, leading to network instability and the breach of Service Level Agreements (SLAs). Effective conflict mitigation is technically imperative to ensure that the coordination of these distributed intelligence layers maintains a stable, high-performance state.

According to the O-RAN architecture, the Near-RT RIC is positioned as a regional intelligence controller. It interfaces with the E2 node components, sitting above the Central Unit (CU) and the Distributed Unit (DU/RU). While the CU and DU/RU handle lower-level, high-frequency control functions, the RIC provides a centralized point for intelligence-driven policies.

The primary objective of this report is to provide a rigorous technical comparison between three distinct mitigation frameworks: QoS-Aware Conflict Mitigation (QACM) and two game-theoretic solutions, the Nash Social Welfare Function (NSWF) and the Eisenberg-Galle (EG) formulation. This analysis evaluates how these frameworks govern the complex interaction between specialized xApps described in the following ecosystem.

2. The xApp Ecosystem: Telemetry Inputs and Control Parameters

The efficacy of RAN intelligence relies on the bidirectional exchange of granular telemetry and precise control. xApps ingest E2 Key Performance Measurements (KPMs) via the E2 interface to derive a state representation and, in turn, output Inter-Component Parameters (ICPs) to drive RAN behavior. This closed-loop relationship (e.g., an RSRP degradation triggering a change in Cell Individual Offset) is the foundation of modern O-RAN automation.

xApp Taxonomy and Functional Scope

The following xApps represent the primary functional agents within the Near-RT RIC. While their specific optimization goals differ, they share a common algorithmic heritage in Asynchronous Deep Reinforcement Learning.

xApp Name	Primary Objective	Algorithmic Basis (Mnih et al.)
Energy Saving (ES)	Minimize RAN power consumption without breaching coverage floors.	Asynchronous Advantage Actor-Critic (A3C)
Coverage & Capacity (CCO)	Optimize antenna parameters for uniform signal distribution.	Asynchronous Advantage Actor-Critic (A3C)
Mobility Robustness (MRO)	Reduce Handover Failures (HOF) and Ping-Pong effects.	Asynchronous Advantage Actor-Critic (A3C)
Mobility Load Balancing (MLB)	Equalize traffic distribution across neighboring cells.	Asynchronous Advantage Actor-Critic (A3C)
Data Rate Maximization (DRM)	Maximize user-plane throughput via spectral efficiency.	Asynchronous Advantage Actor-Critic (A3C)

The integration of the A3C paradigm is a critical strategic "win" for the Near-RT RIC. As established in the foundational research by Mnih et al., asynchronous gradient descent allows these models to achieve state-of-the-art results using single multi-core CPUs rather than specialized GPUs. This enables the deployment of high-performance xApps on standard, cloud-native edge compute nodes.

Telemetry and Control Mapping

To function, these xApps require a robust set of E2 KPM/Telemetry inputs:

* Physical Layer: PRB utilization, SINR, Transmit Power metrics.
* Signal Quality: RSRP, RSRQ.
* Connection Stability: Active UE count, RLF counters, Buffer size.
* Performance: Throughput, Power consumption.

The resulting outputs target Inter-Component Parameters (ICPs) via the E2SM-RC (RAN Control) service model:

* Transmit Power (TXP) and Remote Electrical Tilt (RET) for coverage.
* Cell Individual Offset (CIO) and Time-To-Trigger (TTT) for mobility.
* PRB quotas and RBG allocations for resource management.

Under stabilized network conditions, these parameters are managed through a standard operational baseline without active controller intervention.

3. Operational Baseline: The Passive Control Loop (No-Conflict State)

To maximize computational efficiency and minimize latency, the Near-RT RIC operates in "Passive Mode" whenever the RAN is in a state of stability. This mode allows xApps to execute commands directly to the RAN, bypassing complex bargaining logic when conflicts are absent.

In the passive state, the Performance Monitoring (PMon) function utilizes the E2 REPORT service to track KPMs. The Conflict Detection Controller (CDC) remains in a low-power, dormant state, monitoring proposed ICP changes but not intervening as long as xApp decisions are orthogonal (e.g., ES decreasing power on Cell A while DRM increases PRBs on Cell B).

In this state, xApp decisions are executed either sequentially or through the E2SM-RC service model. This ensures that the system maintains a high-speed control loop without unnecessary computational overhead. However, once the CDC detects a parameter collision—where two xApps attempt to manipulate the same ICP in opposing directions—the system transitions to an active mitigation state.

4. Comparative Analysis of Mitigation Workflows and Mathematical Formulations

The shift from passive monitoring to active mitigation is triggered by two events: a KPI degradation detected by PMon or a parameter collision detected by the CDC. At this point, the Conflict Mitigation Controller (CMC) engages the E2 INSERT/CONTROL services to pause direct execution and initiate a bargaining process via "Messaging Channel 2."

This bargaining is governed by three primary mathematical frameworks:

Nash Social Welfare Function (NSWF)

NSWF is a cooperative game theory approach that seeks a balanced resolution without enforcing explicit operator priorities. It aims to find a parameter set x that maximizes the geometric product of individual xApp utilities: \text{Maximize } \Phi(x) = \prod_{i=1}^{n} f_i(x) By maximizing the product, NSWF inherently prevents any single xApp from receiving zero utility, promoting a "fair" distribution of gains. However, its lack of weighting makes it difficult for operators to enforce specific SLA priorities.

Eisenberg-Galle (EG)

The EG framework introduces MNO policy into the mitigation logic through a convex linear programming formulation. It maximizes the weighted sum of utilities based on operator-defined weights (w_i): \text{Maximize } \Psi(x) = \sum_{i=1}^{n} w_i f_i(x) Subject to: x \in \mathcal{C} (Parameter bounds) This framework is highly sensitive to the w_i values, allowing an operator to prioritize, for instance, DRM over ES during peak hours.

QoS-Aware Conflict Mitigation (QACM)

QACM is a heuristic, threshold-driven framework that prioritizes SLA fulfillment. It converts raw KPIs into normalized z-score utilities U(p). The optimization objective is dual-pronged: minimize the weighted shortfall from KPI thresholds (q_i) while maximizing the square of the number of satisfied xApps (s_i): \text{Minimize } \sum_{i=1}^{n} w_i q_i \quad \text{and Maximize } \left(\sum_{i=1}^{n} s_i\right)^2 Where s_i = 1 if U_i(p) \geq \text{threshold}, else 0. This ensures the system prioritizes "saving" as many services as possible from SLA breaches.

5. Framework Limitations and Comparative Risk Assessment

Choosing a mitigation framework requires a trade-off between mathematical optimality and the practical constraints of a live RAN.

Critical Limitations Matrix

Feature	NSWF	EG	QACM
Hard QoS Enforcement	Low (Utility focused)	Moderate (Weight dependent)	High (Threshold focused)
Priority Sensitivity	None (Equitable)	High (Static weights)	Moderate (Heuristic)
Complexity	O(n^2)	O(n \log n)	High (Prediction dependent)
Stability	High	Low (Risk of oscillation)	Moderate

Detailed Evaluation of Failure Modes

* NSWF: The primary failing is its inability to prioritize critical SLAs. In scenarios where a minor xApp (e.g., ES) conflicts with a critical one (e.g., MRO), NSWF may degrade MRO performance to achieve a "fair" geometric balance.
* EG: EG suffers from high parameter volatility. Research has shown EG can cause extreme ICP swings—such as 256% increases in transmit power—if weights are not perfectly tuned. This can lead to severe non-prioritized KPI shortfalls and hardware strain.
* QACM: While strong on QoS, QACM relies on offline KPI prediction models. If these models are erroneous, the heuristic will fail. Furthermore, the manual tuning of z-score weights adds operational complexity.

Near-RT vs. Non-RT Considerations

These Near-RT solutions are essential because Non-RT solutions (like DECOR) operate on a centralized architecture that represents a single point of failure. Furthermore, Non-RT search spaces scale at O(|A|^k), where |A| represents the number of possible actions and k represents the number of agents (xApps). As k increases in a multi-vendor environment, the search space expands exponentially, making the asynchronous, thread-based optimization of the Near-RT RIC (leveraging the CPU speedups noted by Mnih et al.) the only viable path for real-time control.

Strategic Recommendation

For modern O-RAN deployments, QACM provides the most robust path for SLA protection, despite its complexity. However, as asynchronous RL matures, a hybrid approach—using NSWF for non-critical xApps and transitioning to EG-weighted logic during peak congestion—offers the best balance of mathematical elegance and practical network stability.
