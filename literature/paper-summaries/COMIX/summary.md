# Summary of COMIX: Generalized Conflict Management in O-RAN xApps

## 1. Problem

* **xApp Objective Conflicts:** Concurrent operation of multiple independent xApps targeting the same underlying RAN nodes (RUs) with conflicting goals (e.g., maximizing data rate vs. minimizing energy consumption) leads to network instability, suboptimal performance, and increased interference.


* **Uncertainty & Safety Risks:** Direct execution of competing actions on live networks can degrade service quality or cause Service-Level Agreement (SLA) breaches.



---

## 2. What Already Existed and the Gap Addressed

### What Existed:
* Standard O-RAN Alliance Conflict Mitigation Framework (CMF) architectural guidelines.


* Prior methods focused on game theory, preemptive SMO architectures, or cooperative team-learning frameworks.




### Gap Addressed:
* Existing literature lacked concrete use-case validations and quantitative performance comparisons under realistic network conditions.


* Absence of a proactively guided decision pipeline leveraging Network Digital Twins (NDT) to evaluate conflicting Deep Reinforcement Learning (DRL) actions before execution on live infrastructure.





---

## 3. Approach

* **COMIX Framework Integration:** Integrates a CMF component into the Near-RT RIC along with a Network Digital Twin (NDT).


* **Conflict Classification Pipeline:**
* **Direct Conflict (DC) Checker:** Proactively checks for overlapping Control Parameters (CPs) across xApps.


* **Indirect Conflict (IC) Checker:** Groups CPs into clusters based on the Key Performance Indicators (KPIs) they affect.


* **Implicit Conflict Support:** Uses a KPI Notifier to monitor unexpected performance degradation and dynamically update CP/KPI association matrices over long-term operation.




* **NDT-Guided Resolution Policies:** Conflicting actions from two DRL-based xApps—a Data Rate Maximization (DRM) xApp and an Energy Efficiency (EE) xApp—are applied to an NDT instance. The NDT evaluates KPI outcomes pre-execution according to five enforced resolution policies:


1. *MaxTS:* Maximum Throughput-based Selection.


2. *MinPS:* Minimum Power-based Selection.


3. *EES:* Energy Efficiency-based Selection.


4. *TVS:* Throughput SLA Violation-based Selection.


5. *EEVS:* Energy Efficiency SLA Violation-based Selection.





---

## 4. Results

* **Energy Savings:** CMF-backed resolution policies (MinPS, EES, TVS, EEVS) achieved substantial power consumption reductions compared to baseline, CMF-free setups (which overwrite parameters based on arrival time).


* **Throughput Retention:** Energy-oriented resolution policies achieved energy savings with minimal to no degradation of overall system data rates.


* **Selection Frequency:** The EE xApp's actions were selected by the CMF in the majority of time slots across balanced policies because it naturally optimizes the data rate-to-power consumption ratio.



---

## 5. Conclusion

* COMIX demonstrates that combining proactive conflict classification with NDT pre-execution scoring successfully resolves direct xApp conflicts in multi-channel power control scenarios.


* The framework enables mobile network operators to balance antagonistic operational objectives—such as user QoS and system energy efficiency—without risking live network disruption.