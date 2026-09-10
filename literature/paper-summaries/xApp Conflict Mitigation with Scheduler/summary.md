### **1. Problem and Other Similar Work Mentioned**

#### Problem

Open RAN (O-RAN) architectures allow multi-vendor, data-driven control loops via third-party microservice applications called **xApps** running on the Near-Real-Time RAN Intelligent Controller (Near-RT RIC). Although the O-RAN specifications require xApps to undergo offline training and validation prior to deployment, uncoordinated xApps operating concurrently can issue conflicting actions. These operational conflicts heavily depend on dynamic, real-time network contexts (e.g., user density, traffic load, user mobility). Because deployed xApps are immutable (they cannot be modified post-deployment) and typically originate from different vendors, joint retraining or co-training of xApps is infeasible.



#### Similar Work Mentioned in the Paper

* **Self-Organizing Networks (SON) & Intent-Driven Networking (IDN):** Historical paradigms that encountered direct, indirect, logical dependency, measurement, contextual, and latent conflicts among distinct control functions. Resolution involved static policy rules, joint co-design, objective-driven optimization, or game-theoretic bargaining.


* **Prioritization & Static Rule Schemes in O-RAN:** Frameworks like those proposed by Adamczyk & Kliks use parameter groups and flag conflicts to prioritize one xApp while rejecting others. These rely on simplistic resolution mechanisms and cumbersome parameter group configurations.


* Digital Twin / Scoring Approaches (e.g., COMIX): Evaluate proposed xApp actions via a Network Digital Twin (NDT) using scoring functions (e.g., maximum throughput). However, evaluating every parameter combination in real-time introduces severe latency challenges and relies heavily on digital twin prediction accuracy.


* Statistical Profiling (e.g., PACIFISTA): Monitors parameter and Key Performance Indicator (KPI) distributions in the SMO environment to block or remove conflicting xApps. The main limitation is the complexity of building statistical profiles across all possible operational scenarios.


* Game-Theoretic / Utility Optimization (e.g., QACM): Resolves conflicts by optimizing distance metrics from Quality of Service (QoS) thresholds. However, it requires highly reliable Key Performance Metric (KPM) estimations, which are difficult to maintain in dynamic RAN environments.


* Team Learning & Distillation (e.g., TMADRL, xApp Distillation): Train multiple xApps jointly using Multi-Agent Reinforcement Learning (MARL) or distill multiple teacher xApps into a single student DQN controller. These approaches assume xApps can be co-trained or retrained, violating O-RAN immutability constraints and limiting operational flexibility.





---

### **2. Gap Addressed**

Existing literature relies heavily on:

1. Accurate, real-time **KPM estimation** (which requires complex Digital Twins).


2. Assumptions of **joint offline training or online retraining/modification** of deployed xApps (violating O-RAN specifications on xApp immutability).


3. Ignoring the **context-dependent nature of conflicts**, treating conflicts with static or over-generalized priority rules.



**The Gap Addressed:** This paper proposes a context-aware conflict mitigation framework that dynamically orchestrates pre-trained xApps via a lightweight Near-RT RIC scheduler based on real-time network context variables and operator intent—**without requiring xApp retraining, joint co-training, or modification of deployed xApps**.

---

### **3. Approach**

The proposed framework introduces an **A2C-based Context-Aware Scheduler** inside the Near-RT RIC that operates on top of pre-trained, immutable xApps.

* **System & Conflict Setup:**
* Evaluates downlink multi-cell O-RAN environments featuring multiple O-RUs serving mobile users.


* Focuses on an **indirect conflict** scenario between two independently pre-trained Advantage Actor-Critic (A2C) xApps:
1. **Power Allocation xApp ($\mathcal{X}_1$):** Dynamically allocates discrete transmission power levels per Resource Block Group (RBG).


2. **RBG Allocation xApp ($\mathcal{X}_2$):** Assigns available RBGs across O-RUs to connected users.




* Both xApps are pre-trained independently using A2C to maximize normalized data transmission rate.




* **Scheduler Architecture & Workflow:**
* **Inputs:** Receives high-level operator intents from the Non-RT RIC (e.g., "maximize total transmission rate"), along with contextual variables $c_t$ (e.g., mean user speed $c_t^1$ and mean data arrival rate $c_t^2$) passed as Enrichment Information (EI) over the A1 interface.


* **Decision Mechanism:** The scheduler's A2C actor network takes the network state $s_\dagger = [c_\dagger^1, c_\dagger^2, f_\dagger]$ and outputs dynamic activation decisions $\mu_\dagger$ to orchestrate which xApps run during each scheduling period.


* **Two Scheduling Methods Evaluated:**
* **Method 1 (Retain Previous Action):** The scheduler chooses between activating $\mathcal{X}_1$, $\mathcal{X}_2$, or both. If one xApp is deactivated for a period, the network holds/retains its last valid configuration, serving as an A2C-enhanced prioritization scheme.


* **Method 2 (Extended Action Space with Baselines):** The scheduler is provided an expanded action pool containing the A2C xApps plus simple baseline xApps ($\mathcal{X}_3$ for equal power allocation, $\mathcal{X}_4$ for equal RBG distribution). It dynamically selects one power strategy ($\mathcal{X}_1$ vs. $\mathcal{X}_3$) and one resource allocation strategy ($\mathcal{X}_2$ vs. $\mathcal{X}_4$) based on prevailing network context.




* **Confidence-Gated Safety Fallback:** Incorporates a z-score monitoring mechanism on the critic's value function $V_\phi(s_\dagger)$. If an out-of-distribution network context is encountered, the scheduler suppresses RL actions and temporarily defaults to a deterministic safe fallback policy.





---

### **4. Results**

Simulations were performed on a 4 O-RU network with 16 mobile users across 9 context scenarios combining different user speeds (5, 25, 45 m/s) and traffic arrival rates (2, 5, 8 Mbps):

* **Context-Dependence of Conflicts:** Uncoordinated simultaneous deployment of both A2C xApps resulted in severe conflict-driven performance degradation. Under high traffic/high mobility (8 Mbps, 45 m/s), uncoordinated operation degraded performance by **16%**, whereas under low conditions (2 Mbps, 5 m/s), degradation was only **5%**.


* **Method 1 Performance:** Utilizing the A2C scheduler to dynamically retain and prioritize xApp actions consistently outperformed the uncoordinated conflicting baseline.


* **Method 2 (Best Overall Performance):** Expanding the scheduler's action space to include baseline xApps yielded the highest overall normalized reward (transmission rate) and the lowest amount of discarded/leftover bits across all context regimes.


* **Impact of Traffic vs. Mobility:** The analysis revealed that variations in data arrival rate exerted a significantly stronger impact on xApp conflicts and overall network performance than changes in user mobility speed.



---

### **5. Conclusion**

* Conflicts among independently developed O-RAN xApps are inherently context-dependent; two xApps may severely interfere under high traffic/speed conditions yet peacefully coexist under lighter workloads.


* Dynamic, context-aware scheduling at the Near-RT RIC effectively mitigates multi-xApp conflicts and enhances total network transmission without violating O-RAN specifications regarding xApp immutability or requiring expensive joint retraining.


* Granting schedulers access to an expanded action pool (combining ML-based policies with simple baseline strategies) maximizes network performance and operational flexibility, underscoring the vital role of adaptive scheduling in future 6G automated network management.