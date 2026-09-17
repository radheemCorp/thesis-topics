### Overview of the Paper & Dataset

The paper **"Conflict Management in the Near-RT-RIC of Open RAN: A Game Theoretic Approach"** (Wadud et al.) proposes an independent **Conflict Management System (CMS)** operating inside the Near-Real-Time RAN Intelligent Controller (Near-RT-RIC). 

The system consists of three main operational modules:
1. **Performance Monitoring (PMon):** Monitors Key Performance Indicators (KPIs) against Service Level Agreement (SLA) / Quality of Service (QoS) thresholds.
2. **Conflict Detection Controller (CDC):** Identifies whether an active conflict is **Direct**, **Indirect**, or **Implicit** by querying recent database logs.
3. **Conflict Mitigation Controller (CMC):** Uses cooperative game theory—specifically **Nash’s Social Welfare Function (NSWF)** for non-priority scenarios and the **Eisenberg-Galle (EG)** convex optimization model for priority scenarios—to calculate an optimal value for conflicting parameters.

The accompanying GitHub repository (`cmsORAN`) provides the synthetic training datasets (`data1.csv` through `data4.csv`, plus primed versions) used to train polynomial regression models that simulate xApp KPI predictions based on input parameter configurations.

---

### Database Parameters (Infrastructure Prerequisites)

To detect conflicts and compute optimal parameter values without direct xApp-to-xApp communication, the CMS relies on a **Shared Data Layer (SDL)** that tracks six key database tables:

| Database Parameter / Table | Role & Purpose |
| :--- | :--- |
| **Recently Changed Parameters (RCP)** | Logs recently modified parameter values alongside their exact timestamps. Used by CDC to detect **Direct Conflicts**. |
| **Parameter Group Definition (PGD)** | Groups parameters that influence the same operational domain (e.g., Remote Electrical Tilt [RET] and Cell Individual Offset [CIO] both belong to the `Handover Boundary` group). Used by CDC to detect **Indirect Conflicts**. |
| **Recently Changed Parameter Group (RCPG)** | Tracks modifications to parameters belonging to PGD groups, noting timestamps and co-involved parameters. |
| **Parameter and KPI Ranges (PKR)** | Stores the physical min/max bounds for control parameters (\\(p_{\text{min}}, p_{\text{max}}\\)) and baseline KPI bounds (\\(o_{\text{min}}, o_{\text{max}}\\)) for each cell. |
| **Decision Correlated with KPI Degradation (DCKD)** | Stores individual KPI target thresholds corresponding to required QoS/SLA levels. |
| **KPI Degradation Occurrences (KDO)** | Records any instance where a KPI drops below its defined DCKD threshold following an xApp parameter change. |

---

### Core Parameters Used in the Paper & Mathematical Model

The paper defines several operational and mathematical parameters to model xApp behavior and resolve clashes:

#### 1. Input Control Parameters (ICPs / \\(p \in P\\))
* **Role:** These are the **controllable network settings / "knobs"** managed by xApps (e.g., Transmission Power [\\(TxP\\)], Cell Individual Offset [\\(CIO\\)], Remote Electrical Tilt [\\(RET\\)], Time-To-Trigger [\\(TTT\\)]).
* **In the Evaluation Setup:**
  * **\\(p_1\\):** The primary **conflicting ICP** shared across xApps (e.g., cell transmit power, evaluated across a range of \\([-150, 150]\\)).
  * **\\(p_2, p_3, p_4, p_5, p_6, p_7\\):** Non-conflicting local ICPs set to fixed values or specific operating bounds (e.g., \\(p_2 = 20, p_3 = 60, p_4 \in [-100, 100], p_5 = 60, p_6 \in [-50, 150], p_7 = 60\\)) to construct the multi-xApp environment.

#### 2. Output Parameters / Key Performance Indicators (KPIs / \\(o \in O\\))
* **Role:** The **measurable network performance outcomes** resulting from specific ICP settings (e.g., throughput in Mbps, call drop rate, energy efficiency, ping-pong handover frequency).
* **In the Model:** Represented as Gaussian functions (\\(o_1, o_2, o_3, o_4\\)) of the ICPs to mirror real-life cellular behavior.

#### 3. Normalized Utility (\\(u_i\\) or \\(f_i(x)\\))
* **Role:** Raw KPIs have completely different units and scales (e.g., Mbps vs. Watts). The CMC uses min-max normalization to transform raw KPIs into a **uniform scalar utility score** between \\(\\) (or \\(\\) in simulations):
  \\[f_i(x) = u_i = \frac{1}{|J|} \sum_{j \in J} \left( \frac{o_{ij} - o_{ij}^{\text{min}}}{o_{ij}^{\text{max}} - o_{ij}^{\text{min}}} \times 10 \right)\\]
* **Function:** Provides an "apples-to-apples" metric representing xApp satisfaction so that game-theoretic equations can maximize collective system welfare.

#### 4. Priority / Bargaining Weights (\\(w_i\\))
* **Role:** Operator-assigned weights (\\(\sum w_i = 1\\), e.g., \\(w_1 = 0.4, w_2 = 0.6\\)) that represent the **relative bargaining power** of each xApp.
* **Function:** Used in the **Eisenberg-Galle (EG)** convex linear program (\\(\max \sum w_i f_i(x)\\)) to intentionally favor a critical xApp (such as prioritizing Mobility Robustness Optimization during a spike in dropped calls) while still finding a compromise value for lower-priority apps.

#### 5. Decision Variable (\\(x\\) or \\(p_1'\\))
* **Role:** The **optimal parameter value** calculated by the CMC.
* **Function:** The final compromise setting returned over messaging channel 2 to configure the RAN nodes, resolving the conflict while maximizing overall network utility.

---

### Dataset & Experimental Setup Analysis

The dataset available in the GitHub repository (`cmsORAN`) supports the paper's experimental validation:

```
      p1 ------>  |...........|
                  |  xApp_1   |-------> O_1
      p2 ------>  |...........|
```

1. **Dataset Structure (`data1.csv` through `data4.csv`):**
   * **Feature Matrix (\\(X\\)):** Contains pairs of input parameters `[[p11, p21], [p12, p22], ...]`.
   * **Target Vector (\\(y\\)):** Contains corresponding raw KPI values `[y1, y2, y3]` generated via Gaussian distribution functions.
2. **Machine Learning Model:** Each intelligent xApp is modeled using **Polynomial Regression Blocks** in Python trained on these CSV datasets. This allows each xApp to predict its output KPI (\\(y\\)) for any candidate parameter value (\\(X\\)) suggested by the CMC during the closed-loop bargaining process.
3. **Tested Conflict Scenarios:**
   * **Direct Conflict (\\(\text{xApp}_1\\) vs. \\(\text{xApp}_2\\)):** Both xApps clash directly over \\(p_1\\) (\\(\text{xApp}_1\\) demands \\(p_1 = 50\\), \\(\text{xApp}_2\\) demands \\(p_1 = -50\\)).
   * **Indirect Conflict (\\(\text{xApp}_2\\) vs. \\(\text{xApp}_4\\)):** \\(\text{xApp}_2\\) modifies \\(p_1\\) to \\(0\\) at timestamp \\(t_2\\), which indirectly collapses the utility of \\(\text{xApp}_4\\) near zero.
   * **Implicit Conflict (\\(\text{xApp}_1\\) vs. \\(\text{xApp}_3\\)):** \\(\text{xApp}_1\\) sets \\(p_1 = -85\\) at timestamp \\(t_2'\\), causing an unmapped performance drop in \\(\text{xApp}_3\\) below its \\(0.4\\) satisfaction threshold.

---

### Summary of Parameter Roles

* **\\(p_1 \dots p_7\\) (ICPs):** The control knobs being adjusted.
* **\\(o_1 \dots o_4\\) (KPIs):** The raw network measurements resulting from parameter settings.
* **\\(u_1 \dots u_4\\) / \\(f_i(x)\\) (Utilities):** The normalized 0-to-1 satisfaction scores.
* **\\(w_i\\) (Priority Weights):** Operator preferences balancing trade-offs.
* **\\(x\\) / \\(p_1'\\) (Decision Variable):** The final negotiated setting sent back to the RAN.
* **CSV Files (`data1`–`data4`):** Provide training samples for polynomial regression models that simulate live xApp response curves.
