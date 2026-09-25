To test conflict mitigation mechanisms in the Near-RT RIC, it is essential to map out the participating xApps, their **E2 inputs** (telemetry/KPMs gathered via **E2SM-KPM**), their **RAN control parameters** (actions enforced via **E2SM-RC / E2SM-CCC**), and how they interact to produce conflicts.

---

### Key E2 Parameters & Control Capabilities by xApp Category

| xApp Category | Primary Telemetry Inputs (E2SM-KPM) | Output Control Parameters (E2SM-RC) |
| :--- | :--- | :--- |
| **Power & Energy Management** *(Energy Saving - ES, CCO)* | PRB utilization, total cell power consumption, active UE count | Transmit Power (TXP), cell/carrier deactivation state, antenna layer configuration |
| **Mobility & Traffic Steering** *(MLB, MRO, Handover Control)* | Serving/neighbor RSRP, RSRQ, SINR, RLF counters, HO success/failure logs | Cell Individual Offset (CIO), Time-To-Trigger (TTT), Handover Hysteresis, explicit UE Handover execution |
| **Coverage & Antenna Tuning** *(CCO, Beamforming)* | Per-beam CSI feedback, SRS measurements, cell-edge SINR distributions | Remote Electrical Tilt (RET) / Antenna Tilt, per-beam power allocation |
| **Resource Allocation & Slicing** *(QoS Optimization, DRM, Slicing)* | Per-slice/UE throughput, latency, buffer occupancy, active PRB utilization | PRB quota/slice weights, Resource Block Group (RBG) allocations, scheduling profiles |

---

### Categorization of xApp Conflicts

O-RAN specifications categorize Near-RT RIC intra-component conflicts into **Direct**, **Indirect**, and **Implicit** conflicts.

---

#### 1. Direct Conflict xApps (Direct Control Parameter Conflicts)
**Definition:** Occurs when two or more xApps simultaneously or sequentially attempt to set incompatible values for the **exact same control parameter** (e.g., Transmit Power, PRB quota, or Handover target) for the same control target (cell or UE).

* **Energy Saving (ES) xApp vs. Coverage & Capacity Optimization (CCO / CTO) xApp**
  * **Conflicting Parameter:** Downlink Transmit Power (\\(\text{TXP}\\)).
  * **Mechanism:** The ES xApp decreases \\(\text{TXP}\\) to minimize energy consumption, whereas the CCO/CTO xApp increases \\(\text{TXP}\\) to improve cell-edge coverage, SINR, and throughput.
* **Energy Saving (ES) xApp vs. Mobility Robustness Optimization (MRO) xApp**
  * **Conflicting Parameter:** Transmit Power (\\(\text{TXP}\\)) / Cell Activation State.
  * **Mechanism:** ES attempts to lower power or deactivate cell layers to save energy, while MRO requires sufficient coverage/power to prevent Radio Link Failures (RLFs) and ping-pong handovers.
* **Data Rate Maximization (DRM) xApp vs. Energy Efficiency (EE) xApp**
  * **Conflicting Parameter:** Multi-channel Radio Unit (RU) Power Levels per channel/RB.
  * **Mechanism:** DRM increases RU power levels across channels to maximize total throughput, while the EE xApp reduces RU power levels to maximize energy efficiency.
* **Physical Resource Block (PRB) Allocation xApp vs. Slicing Management xApp**
  * **Conflicting Parameter:** PRB Allocation / Slice PRB Quota.
  * **Mechanism:** Multiple xApps issue competing commands adjusting the number of PRBs assigned to specific network slices (e.g., eMBB vs. URLLC).
* **Handover Control xApp #1 vs. Handover Control xApp #2**
  * **Conflicting Parameter:** UE Cell Assignment / Target Cell ID.
  * **Mechanism:** xApp #1 assigns a specific user to Cell A, and xApp #2 immediately reassigns the same user to Cell B, leading to conflicting handover commands.

---

#### 2. Indirect Conflict xApps (Parameter Group / Operational Area Conflicts)
**Definition:** Occurs when xApps adjust **different configuration parameters**, but those parameters influence the **same operational area, boundary, or key performance indicator** in the RAN.

* **Mobility Load Balancing (MLB) xApp vs. Coverage & Capacity Optimization (CCO) / MRO xApp**
  * **Parameters Involved:** Cell Individual Offset (\\(\text{CIO}\\)) controlled by MLB vs. Remote Electrical Tilt (\\(\text{RET}\\)) / Antenna Tilt controlled by CCO/MRO.
  * **Shared Impact Area:** Effective Cell Handover Boundary.
  * **Mechanism:** MLB adjusts \\(\text{CIO}\\) to balance traffic load between cells, while CCO/MRO adjusts \\(\text{RET}\\) or Time-To-Trigger (\\(\text{TTT}\\)). Changing \\(\text{RET}\\) alters the physical cell footprint, inadvertently disrupting the handover boundary and invalidating the load balancing achieved via \\(\text{CIO}\\).
* **Power Allocation xApp vs. Resource Block (RBG) Allocation xApp**
  * **Parameters Involved:** Per-RBG Transmit Power controlled by Power xApp vs. Time-frequency RBG Assignment controlled by RBG Allocation xApp.
  * **Shared Impact Area:** Achievable User SINR and Throughput.
  * **Mechanism:** The RBG Allocation xApp assigns resource blocks to UEs, while the Power Allocation xApp regulates power per block. Conflict arises when the Power xApp assigns high power to unallocated RBGs or low power to heavily allocated RBGs, degrading throughput unpredictably.

---

#### 3. Implicit Conflict xApps (Competing Objective / Cross-KPI Conflicts)
**Definition:** Occurs when xApps tune **separate parameters to optimize distinct, independent objectives**, but their decisions interfere in a subtle, non-obvious manner, causing unintended system-wide KPI degradation (detectable reactively via performance monitoring).

* **QoS Optimization / Data Rate Maximization xApp vs. Handover Minimization xApp**
  * **Parameters Involved:** Dynamic UE Resource/Cell Steering parameters vs. Handover Hysteresis / Trigger thresholds.
  * **Competing Objectives:** Maximize User Throughput/QoS vs. Minimize Handover Frequency.
  * **Mechanism:** The QoS xApp aggressively re-allocates resources or triggers steering to maintain user throughput, while the Handover Minimization xApp attempts to stabilize cell connections. The throughput optimization triggers frequent handovers, degrading the mobility stability target.
* **Latency / Service Assurance xApp vs. Mobility Load Balancing (MLB) xApp**
  * **Parameters Involved:** 5QI Scheduling Priority / Dedicated PRB Reservations vs. Cell Traffic Offloading thresholds.
  * **Competing Objectives:** Minimize Latency (URLLC SLAs) vs. Uniform Cell Load Distribution.
  * **Mechanism:** The Latency xApp reserves low-latency radio resources across cells, while the Load Balancing xApp shifts traffic onto those same cells to relieve network congestion, inadvertently violating latency guarantees.
* **Energy Efficiency (EE) xApp vs. Slice Management / High-Throughput xApp**
  * **Parameters Involved:** Cell Carrier / Spatial Stream Deactivation vs. Slice PRB Allocation / Bandwidth Expansion.
  * **Competing Objectives:** Reduce Power Consumption vs. Satisfy High Slice Bandwidth Demands.
  * **Mechanism:** The EE xApp powers down antenna streams or carriers during lower traffic periods, while the Slice Management xApp simultaneously requests expanded bandwidth for bandwidth-intensive video streaming applications, resulting in degraded service quality.

---

### Summary Checklist for Testing Conflict Mitigation

1. **Direct Conflict Test Suite:** Deploy **ES + CCO** (competing on `TXP`) or **MLB + MRO** (competing on `TTT`/`CIO`) to verify pre-action filtering or parameter arbitration.
2. **Indirect Conflict Test Suite:** Deploy **MLB + Antenna Tilt (RET) xApp** or **Power Allocation + RB Allocation xApp** to verify parameter-group monitoring and post-action/graph-based correlation.
3. **Implicit Conflict Test Suite:** Deploy **QoS Throughput xApp + Handover Minimization xApp** or **EE xApp + Slice Assurance xApp** to test reactive performance monitoring (PM) anomaly detection and cross-objective trade-off balancing.
