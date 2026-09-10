### **1. The Two Conflicting Policies**

Suppose two independently developed xApps attempt to set the downlink transmit power ($P$) for the same cell of interest:

* **Policy 1: Energy Saving (ES) xApp**
* **Goal:** Minimize radiated transmit power to reduce operational cost and inter-cell interference.


* **Proposed Action ($P_{\text{ES}}$):** $10\text{ dBm}$ ($0.01\text{ W}$).




* **Policy 2: Coverage/Throughput-Oriented (CTO) xApp**
* **Goal:** Maximize user received signal quality and aggregate system throughput.


* **Proposed Action ($P_{\text{CTO}}$):** $46\text{ dBm}$ ($39.81\text{ W}$).





A traditional **binary policy** forces a choice between $10\text{ dBm}$ or $46\text{ dBm}$. Continuous action blending parameterizes the decision using a blend weight $\alpha \in [0, 1]$ across a candidate grid $\mathcal{A} = \{0, 0.05, 0.10, \dots, 1.0\}$:

$$P(\alpha) = P_{\text{ES}} + \alpha (P_{\text{CTO}} - P_{\text{ES}})$$

---

### **2. System Utility Function & Operator Objective**

The conflict resolution module evaluates each candidate action $\alpha$ using an energy-aware system utility function $U(\alpha)$:

$$U(\alpha) = T(\alpha) - w_E \cdot P_W(\alpha)$$

* $T(\alpha)$ is the aggregate network throughput in Mbit/s.


* $P_W(\alpha) = 10^{\frac{P(\alpha) - 30}{10}}$ is the applied transmit power in Watts.


* $w_E$ is the operator-defined energy weight.



Assume the operator sets **$w_E = 0.1$** (a throughput-oriented preference that penalizes power moderately).

---

### **3. Continuous Action Evaluation & Step-by-Step Calculation**

The Network Digital Twin (NDT) or real-time context model evaluates candidate blend weights $\alpha \in \mathcal{A}$. Consider three candidate actions:

#### **Option A: Full ES Policy ($\alpha = 0$)**

* **Power:** $P(0) = 10\text{ dBm} \implies P_W(0) = 0.01\text{ W}$.


* **Throughput ($T$):** Low transmit power yields an aggregate throughput $T(0) = 62.0\text{ Mbit/s}$ due to limited cell-edge coverage.


* **Utility Calculation:**

$$U(0) = 62.0 - (0.1 \times 0.01) = 62.0 - 0.001 = \mathbf{61.999}$$



#### **Option B: Full CTO Policy ($\alpha = 1.0$)**

* **Power:** $P(1.0) = 46\text{ dBm} \implies P_W(1.0) = 39.81\text{ W}$.


* **Throughput ($T$):** High power improves signal strength but creates heavy inter-cell interference, resulting in an aggregate throughput $T(1.0) = 62.8\text{ Mbit/s}$.


* **Utility Calculation:**

$$U(1.0) = 62.8 - (0.1 \times 39.81) = 62.8 - 3.981 = \mathbf{58.819}$$



#### **Option C: Blended Policy ($\alpha = 0.50$)**

* **Power:** $P(0.50) = 10 + 0.50(46 - 10) = 28\text{ dBm} \implies P_W(0.50) = 0.631\text{ W}$.


* **Throughput ($T$):** Intermediate power satisfies coverage demands without triggering excessive inter-cell interference, maintaining $T(0.50) = 62.0\text{ Mbit/s}$.


* **Utility Calculation:**

$$U(0.50) = 62.0 - (0.1 \times 0.631) = 62.0 - 0.0631 = \mathbf{61.937}$$



---

### **4. Resolution Outcome Comparison**

| Candidate Policy | Blend Factor ($\alpha$) | Applied Transmit Power | Linear Power ($P_W$) | Network Throughput ($T$) | System Utility ($U$) | Resolution Result |
| --- | --- | --- | --- | --- | --- | --- |
| **Pure ES Request** | $0.00$ | $10.0\text{ dBm}$ | $0.01\text{ W}$ | $62.0\text{ Mbit/s}$ | **$61.999$** | Sub-optimal if throughput is prioritized |
| **Pure CTO Request** | $1.00$ | $46.0\text{ dBm}$ | $39.81\text{ W}$ | $62.8\text{ Mbit/s}$ | **$58.819$** | Penalty high due to high power cost |
| **Optimal Blend ($\alpha^*$)** | **$0.53$** | **$29.08\text{ dBm}$** | **$0.809\text{ W}$** | **$63.2\text{ Mbit/s}$** | **$63.119$** | **SELECTED / EXECUTED** |

---

### **5. Summary of Resolution**

1. **Binary Selection Failure:** Choosing Policy 2 (CTO) yields the lowest utility ($58.819$) because radiating $39.81\text{ W}$ causes heavy energy costs and inter-cell interference for marginal throughput gains. Choosing Policy 1 (ES) ignores the CTO xApp's request entirely.


2. **Continuous Blending Outcome:** The conflict resolution module selects **$\alpha^* \approx 0.53$** ($29.08\text{ dBm}$). This blended action achieves the highest net utility ($63.119$), delivering optimal throughput while consuming only $0.809\text{ W}$ instead of $39.81\text{ W}$.