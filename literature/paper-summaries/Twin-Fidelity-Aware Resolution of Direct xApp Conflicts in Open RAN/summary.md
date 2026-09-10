### **Problem**

* **Context & Issue:** In Open RAN (O-RAN), independently developed xApps running on the Near-Real-Time RAN Intelligent Controller (Near-RT RIC) can issue conflicting control actions for shared control parameters. This paper focuses on a direct conflict where an Energy Saving (ES) xApp (lowering transmit power) and a Coverage/Throughput-Oriented (CTO) xApp (increasing transmit power) simultaneously attempt to control the same cell's downlink transmit power. Applying static policies or binary arbitration sacrifices one objective for another, while using an unmonitored Network Digital Twin (NDT) to evaluate compromise actions leads to severe performance degradation when the NDT drifts from live network reality.


* **Goal:** To perform continuous action blending between conflicting xApp requests by selecting an optimal blend weight $\alpha \in [0, 1]$ online to maximize an energy-aware utility, while explicitly monitoring NDT drift to prevent live network degradation.



---

### **Related Work**

* **Conflict Detection & Profiling:** Uses sandbox profiling (PACIFISTA), policy risk analysis, and graph learning/causal inference (GraphSAGE, GRAPHICA) to reconstruct conflict graphs, identify root causes, and screen rApp policies pre-deployment.


* **Conflict Mitigation & Arbitration:** Applies rule-based prioritization (Conflict Mitigation Framework - CMF), QoS-threshold optimization (QACM), team-learning/distillation, context-aware scheduling, and NDT-based policy evaluation (COMIX).


* **Digital Twins & Runtime Assurance:** Focuses on NDT frameworks for testing/assurance, safety verification layers (Safety Copilot), traffic analytics realignment (AIDITA), and MARL-driven IoT management.


* **Key Gap Addressed:** Prior works either assume the digital twin/learned model remains accurate during runtime, focus on static QoS satisfaction, or require complex offline joint retraining. A lightweight, training-free arbiter that explicitly handles NDT drift during direct conflict resolution was lacking.



---

### **Approach**

#### 1. System Model & Action Parameterization

* **Continuous Blending:** The downlink transmit power $P(\alpha)$ (in dBm) is parameterized using a blending factor $\alpha \in [0, 1]$:



$$P(\alpha) = P_{\text{ES}} + \alpha (P_{\text{CTO}} - P_{\text{ES}})$$



where $\alpha = 0$ corresponds to the ES proposal ($P_{\text{ES}}$) and $\alpha = 1$ to the CTO proposal ($P_{\text{CTO}}$).


* **Action Discretization:** The action space is discretized into 21 candidate actions: $\mathcal{A} = \{0, 0.05, 0.10, \dots, 1.0\}$.


* **Utility Metric:** Candidate actions are evaluated using an energy-aware utility function balancing throughput $T(\alpha)$ (Mbit/s) and linear power consumption $P_W(\alpha)$ (W):



$$U(\alpha) = T(\alpha) - w_E P_W(\alpha)$$



where $w_E \ge 0$ is an operator-defined energy weight.


* **NDT Drift Modeling:** Twin prediction error is modeled by introducing a power offset $d$ (in dB) on neighbor cells in the twin environment: $P_{\text{neighbor}}^{(\text{twin})} = P_{\text{neighbor}}^{(\text{live})} + d$.



#### 2. Twin-Fidelity-Aware Hard-Switching Arbiter

* **Twin Recommendation:** At each control step $t$, the arbiter queries the NDT for predicted utilities $\hat{U}(\alpha)$ across all candidate actions $\alpha \in \mathcal{A}$ and identifies $\alpha_{\text{twin}, t} = \arg\max_{\alpha \in \mathcal{A}} \hat{U}(\alpha)$.


* **On-Policy EWMA Fidelity Monitoring:** The arbiter tracks the absolute prediction mismatch $e_t = \vert{}\hat{U}(\alpha_t) - U_{\text{live}}(\alpha_t)\vert{}$ on applied actions and maintains an Exponentially Weighted Moving Average (EWMA) fidelity signal $\epsilon_t$:



$$\epsilon_t = \beta \epsilon_{t-1} + (1 - \beta) e_t \quad (\text{with } \beta = 0.70)$$


* **Last-Known-Good (LKG) Online Learning:** The arbiter records the highest realized utility observed on the live network up to step $t$ ($U_{\text{best}}$) and retains the corresponding action as the fallback anchor $\alpha_{\text{LKG}}$.


* **Hard-Switching Logic:** If the error estimate $\epsilon_{t-1} < \tau$ (where threshold $\tau = 1$), the arbiter applies the twin recommendation $\alpha_{\text{twin}, t}$. If $\epsilon_{t-1} \ge \tau$, it immediately switches to $\alpha_{\text{LKG}}$:



$$\alpha_t = \begin{cases} \alpha_{\text{twin}, t}, & \text{if } \epsilon_{t-1} < \tau \text{ or } \alpha_{\text{LKG}} = \emptyset \\ \alpha_{\text{LKG}, t-1}, & \text{if } \epsilon_{t-1} \ge \tau \end{cases}$$


* **Algorithmic Properties:** The hard-switch design avoids traversing poor intermediate operating points in non-monotonic utility landscapes. It features an $\mathcal{O}(\vert{}\mathcal{A}\vert{})$ per-step time complexity, an $\mathcal{O}(1)$ memory overhead, requires no offline training or oracle knowledge, and naturally reverses back to twin selection if twin predictions realign with the live network.



---

### **Results**

#### 1. Operator Priority & Utility Landscape

* The optimal blend weight $\alpha^*$ varies significantly with operator energy priority $w_E$. For low energy penalties ($w_E = 0.05, 0.1$), the optimum is interior ($\alpha^* \approx 0.53 - 0.61$); as $w_E$ increases, $\alpha^*$ shifts toward lower transmit power and reaches the boundary $\alpha^* = 0$ (ES-only) at $w_E = 5$.


* Across all operator priorities, the proposed hard-switching arbiter achieves the lowest normalized utility regret ($0.017 \pm 0.006$). In comparison:


* Soft-ES: $0.036 \pm 0.013$

* ES-only & QACM-style: $0.046 \pm 0.015$

* Naive Blend ($\alpha=0.5$): $0.053 \pm 0.018$

* COMIX-style twin selector (no fidelity check): $0.159 \pm 0.052$

* CTO-only: $0.665 \pm 0.037$




#### 2. Robustness Under NDT Drift

* **Interior Optimum ($w_E = 0.1$):**
* At zero drift ($d=0$), COMIX-style selection achieves $0$ regret. However, under a severe 10 dB twin drift, COMIX regret degrades sharply to $11.19 \pm 3.58$.


* The proposed hard-switching arbiter maintains utility regret below $0.65$ across all drift levels, achieving $0.55 \pm 0.25$ regret at 10 dB drift (a $>20\times$ regret reduction over COMIX).


* The paired regret reduction relative to COMIX grows from $+1.32 \pm 0.90$ at 2 dB drift to $+10.64 \pm 3.47$ at 10 dB drift.


* Operationally at 10 dB drift, the proposed approach preserves aggregate throughput near 64 Mbit/s and stable transmit power around 28–29 dBm, whereas COMIX drops throughput to ~53 Mbit/s.




* **Boundary Optimum ($w_E = 1$):** When the true live optimum is near the boundary ($\alpha^* \approx 0.37$), twin drift naturally pushes COMIX recommendations toward low power. The proposed method matches COMIX and ES-only performance without incurring any false-intervention penalty.



#### 3. QoS Satisfaction & Parameter Sensitivity

* **QoS Satisfaction Ratio:** ES-only and QACM-style achieve a $1.000$ QoS-satisfaction ratio because the evaluated QoS target (throughput floor + low power ceiling) favors low power. The proposed utility-maximizing arbiter achieves $0.740 \pm 0.061$, outperforming COMIX ($0.724 \pm 0.066$).


* **EWMA Factor ($\beta$) Sensitivity:** Regret remains stable across tested values ($\beta \in \{0.5, 0.7, 0.9\}$), confirming low parameter sensitivity. $\beta = 0.70$ yields the best balance between fast drift detection and noise smoothing.



---

### **Conclusion**

* The paper demonstrates that relying blindly on NDT recommendations for multi-xApp conflict resolution is risky under network drift.


* Explicit runtime monitoring of digital twin fidelity provides a training-free, lightweight safety layer. By switching to an online-learned, live-validated fallback action ($\alpha_{\text{LKG}}$) upon detecting prediction errors, the Near-RT RIC maintains near-optimal throughput-power trade-offs across varying operator priorities and prevents severe performance degradation under model drift.