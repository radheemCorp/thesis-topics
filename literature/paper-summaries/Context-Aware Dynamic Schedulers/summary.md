Here is a detailed summary of the paper following your requested template, incorporating full details on the approach and results based on the provided source materials.

---

### **1. Problem**

* **xApp Policy Conflicts:** Open RAN (O-RAN) architectures introduce dynamic, programmable control through Near-Real-Time RAN Intelligent Controllers (Near-RT RICs) running third-party microservices (xApps). However, when independently developed xApps operate concurrently over shared Radio Units (RUs), they issue competing control parameters.


* **Operational Risks & Instability:** Uncoordinated execution leads to network instability, severe performance degradation, high power consumption, and Service-Level Agreement (SLA) breaches.


* **Context Sensitivity:** Conflict severity is context-dependent—for instance, uncoordinated xApp actions degrade performance by up to 16% under high traffic and high user mobility, whereas under lighter workloads, degradation is only 5%.


* **O-RAN Constraints:** Deployed xApps are immutable and often come from different third-party vendors, making joint co-training or post-deployment retraining infeasible.



---

### **2. Similar Work Mentioned in the Paper**

* **Self-Organizing Networks (SON) & Intent-Driven Networking (IDN):** Addressed direct, indirect, logical dependency, measurement, contextual, and latent conflicts using static policy rules, joint co-design, objective-driven optimization, or game-theoretic bargaining.


* **Prioritization & Static Rule Schemes in O-RAN:** Frameworks (e.g., Adamczyk & Kliks) use parameter groups and flags to prioritize one xApp while rejecting others, relying on simplistic binary decisions and complex static group setups.


* **Digital Twin / Scoring Approaches (e.g., COMIX):** Evaluate proposed xApp actions in a Network Digital Twin (NDT) using scoring functions (e.g., maximum throughput). However, testing every parameter combination in real time creates high decision latency and relies heavily on simulator accuracy.


* **Statistical Profiling (e.g., PACIFISTA):** Tracks parameter and Key Performance Indicator (KPI) distributions within the Service Management and Orchestration (SMO) layer to block conflicting xApps. A key limitation is the complexity of building statistical profiles across all potential operational states.


* **Game-Theoretic / Utility Optimization (e.g., QACM):** Resolves conflicts by optimizing distance metrics relative to QoS thresholds. However, it relies on accurate Key Performance Metric (KPM) estimations, which fluctuate significantly in dynamic RAN environments.


* **Team Learning & Distillation (e.g., TMADRL, xApp Distillation):** Trains multiple xApps jointly via Multi-Agent Reinforcement Learning (MARL) or distills teacher xApps into a single Deep Q-Network (DQN) controller. These approaches violate O-RAN xApp immutability rules and restrict operational deployment.



---

### **3. Gap Addressed**

Existing solutions depend on accurate real-time KPM estimations (which require heavy Digital Twins), assume joint co-training or retraining of xApps (violating O-RAN immutability), or ignore the context-dependent nature of conflicts by applying static priority rules.

**The Gap Addressed:** The paper proposes a context-aware conflict mitigation framework that dynamically orchestrates pre-trained, immutable xApps via a lightweight Near-RT RIC scheduler based on real-time network context variables and operator intent—**without requiring xApp retraining, co-training, or modification of deployed xApps**.

---

### **4. Approach**

The framework places an **Advantage Actor-Critic (A2C)-based Context-Aware Scheduler** inside the Near-RT RIC on top of existing, immutable xApps.

#### **A. System Setup & Indirect Conflict Scenario**

* Evaluates a multi-cell O-RAN downlink environment with multiple O-RUs serving mobile users.


* Focuses on an **indirect conflict** scenario between two independently pre-trained A2C xApps:


1. **Power Allocation xApp ($\mathcal{X}_1$):** Allocates discrete transmission power levels per Resource Block Group (RBG).


2. **RBG Allocation xApp ($\mathcal{X}_2$):** Distributes available RBGs across O-RUs to connected users.




* Both xApps are pre-trained independently using A2C to maximize the normalized data transmission rate.



#### **B. Context-Aware Scheduler Architecture & Workflow**

* **Inputs:** Receives high-level operator intents (e.g., "maximize total transmission rate") from the Non-RT RIC, alongside contextual variables $c_t$ (mean user speed $c_t^1$ and mean data arrival rate $c_t^2$) provided as Enrichment Information (EI) over the A1 interface.


* **Decision Loop:** The scheduler's A2C actor network evaluates the network state $s_t = [c_t^1, c_t^2, f_t]$ and produces dynamic activation decisions $\mu_t$ to determine which xApps execute in a given scheduling period.


* **Evaluated Scheduling Schemes:**
* **Method 1 (Retain Previous Action):** The scheduler selects between activating $\mathcal{X}_1$, $\mathcal{X}_2$, or both. If an xApp is deactivated, the system holds its last valid configuration, serving as an A2C-guided prioritization scheme.


* **Method 2 (Extended Action Space with Baselines):** The scheduler is provided an expanded action pool combining the A2C xApps with simple baseline xApps ($\mathcal{X}_3$ for equal power allocation, $\mathcal{X}_4$ for equal RBG distribution). It dynamically picks one power strategy ($\mathcal{X}_1$ vs. $\mathcal{X}_3$) and one resource allocation strategy ($\mathcal{X}_2$ vs. $\mathcal{X}_4$) based on prevailing network context.





#### **C. Safety Mechanism**

* Implements a confidence-gated fallback mechanism using a z-score monitor on the critic's value function $V_\phi(s_t)$.


* If an out-of-distribution or unusual network context is detected, the scheduler suppresses RL actions and falls back to a deterministic safe policy.



---

### **5. Results**

Simulations were conducted on a 4 O-RU network with 16 mobile users across 9 context scenarios combining user mobility speeds (5, 25, 45 m/s) and traffic arrival rates (2, 5, 8 Mbps):

* **Context-Dependence Validation:** Simultaneous deployment of both pre-trained A2C xApps without coordination resulted in severe performance loss. The degradation reached **16%** under high traffic/speed conditions (8 Mbps, 45 m/s) compared to only **5%** under low traffic/speed conditions (2 Mbps, 5 m/s).


* **Method 1 Performance:** Using the A2C scheduler to dynamically prioritize and hold xApp actions consistently outperformed the uncoordinated baseline across all contexts.


* **Method 2 (Best Overall Performance):** Granting the scheduler access to the expanded action space (combining RL xApps and simple baseline xApps) achieved the highest overall normalized reward (transmission rate) and left the lowest amount of unserved/leftover bits across all context regimes.


* **Impact of Traffic vs. Mobility:** Variations in traffic data arrival rates exerted a noticeably stronger influence on xApp conflict severity and network performance than variations in user speed.



---

### **6. Conclusion**

* **Context Sensitivity:** Conflicts among independently developed xApps are context-dependent; xApps that interfere under high traffic or fast user mobility can operate smoothly during lighter workloads.


* **Immutability Compliance:** Dynamic, context-aware scheduling at the Near-RT RIC successfully mitigates multi-xApp conflicts while adhering to O-RAN immutability standards without requiring expensive co-training or retraining.


* **Expanded Action Pool Benefit:** Equipping the scheduler with an expanded action space containing both ML-based policies and simple baseline strategies optimizes network throughput and operational flexibility, serving as a key model for automated 6G management.