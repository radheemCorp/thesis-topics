Available approaches for resolving conflicts between xApps in a multi-service RAN environment include:

* **Binary / Priority-Based Arbitration (Baseline):** Assigns static or dynamic priority scores to xApps (e.g., Emergency > Mobility > Energy Saving). The highest-priority proposal executes while lower-priority conflicting actions are completely rejected or discarded.

    * link to paper: https://ieeexplore.ieee.org/document/10121578

* **NDT-Guided Resolution Policies:** Candidate actions from conflicting xApps are run pre-execution through a Network Digital Twin (NDT) to evaluate KPI outcomes. The NDT enforces specific scoring policies, such as:
    * *MaxTS:* Maximum Throughput-based Selection
    * *MinPS:* Minimum Power-based Selection
    * *EES:* Energy Efficiency-based Selection
    * *TVS:* Throughput SLA Violation-based Selection
    * *EEVS:* Energy Efficiency SLA Violation-based Selection
    * link to paper: https://arxiv.org/abs/2501.14619


* **Continuous Action Blending:** Constructs a unified intermediate policy vector ($\mathbf{a}_{\text{blended}}$) using continuous weighting factors rather than binary winner-takes-all selection. The candidate blend vector is simulated in an NDT to find a Pareto-optimal trade-off that satisfies multiple xApp objectives simultaneously.
    * link to paper: https://arxiv.org/abs/2607.22857


* **Context-Aware Dynamic Schedulers (e.g., A2C-based):** Operates at the Near-RT RIC level to dynamically schedule, prioritize, or hold xApp execution based on real-time context variables (such as user mobility and traffic arrival rates) without requiring joint offline retraining or altering xApp immutability.
    * link to paper: https://arxiv.org/abs/2504.06867


* **Expanded Action Pool / Baseline Fallbacks:** Extends the scheduler's available actions beyond complex DRL xApps to include simpler baseline strategies (e.g., equal power allocation or equal RBG distribution) or deterministic safe fallbacks when out-of-distribution context is detected.



* **Graph Neural Network (GNN) Dependency Mapping:** Uses inductive graph models (such as GraphSAGE or GCNs) to map multi-dimensional topologies of xApp parameters, KPIs, and cell nodes to detect and mitigate indirect and implicit conflicts before execution.
    * link to paper: https://arxiv.org/abs/2503.03523


* **Rule-Based & SLA Constraint Projection:** Projects candidate policy vectors onto pre-defined polyhedral constraint spaces, clipping any parameter action that violates hard SLA boundaries to the nearest valid threshold.
    * link to paper: https://arxiv.org/abs/2405.07324