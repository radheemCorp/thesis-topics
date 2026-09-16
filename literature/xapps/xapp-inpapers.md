### List of xApps Used in the Studies

Across the sources, xApps are deployed for specific network management and optimization tasks. Below is a comprehensive list of xApps evaluated in the literature, along with their respective **Inputs** (state observations/telemetry) and **Outputs** (actions/controllable parameters):

---

#### 1. Power Allocation xApp
* **Inputs:** Signal-to-Interference-plus-Noise Ratio (SINR), current transmission rate, current transmission power, Channel State Information (CSI), and buffer/queue length.
* **Outputs:** Transmission power levels for Resource Block Groups (RBGs) or base stations (\\(p_{n,m}\\)).
* **paper**: Team Learning-Based Resource Allocation for Open Radio Access Network (O-RAN) Han Zhang, Hao Zhou, and Melike Erol-Kantarci, Senior Member, IEEE
---

#### 2. Radio Resource / RBG Allocation xApp
* **Inputs:** SINR, current transmission rate, current transmission power, buffer length, and the **intended/assigned power levels** communicated from the Power Allocation xApp.
* **Outputs:** Resource Block (RB) or Resource Block Group (RBG) assignment to specific User Equipments (UEs).
* **paper**: Team Learning-Based Resource Allocation for Open Radio Access Network (O-RAN) Han Zhang, Hao Zhou, and Melike Erol-Kantarci, Senior Member, IEEE

---

#### 3. Mobility Load Balancing (MLB) xApp
* **Inputs:** Traffic load, resource utilization rate, cell load metrics, and handover statistics.
* **Outputs:** Time-To-Trigger (TTT), Cell Individual Offset (CIO), Cell Transmit Power (TXP), and Remote Electrical Tilt (RET).
* **paper**: QACM: QoS-Aware xApp Conflict Mitigation in Open RANAbdul Wadud, Graduate Student Member, IEEE, Fatemeh Golpayegani, Senior Member, IEEE, and Nima Afraz, Senior Member, IEEE
---

#### 4. Mobility Robustness Optimization (MRO) xApp
* **Inputs:** Handover Success Rate, Call Drop Rate, Call Block Rate, ping-pong handover counters, and Radio Link Failures (RLFs).
* **Outputs:** Time-To-Trigger (TTT), Handover Hysteresis (HYS), Cell Individual Offset (CIO), and Transmit Power (TXP).
* **paper**: QACM: QoS-Aware xApp Conflict Mitigation in Open RANAbdul Wadud, Graduate Student Member, IEEE, Fatemeh Golpayegani, Senior Member, IEEE, and Nima Afraz, Senior Member, IEEE

---

#### 5. Energy Saving (ES) xApp
* **Inputs:** System energy efficiency metrics (bits/Joule) and total power consumption (Watts).
* **Outputs:** Cell transmission power level (\\(P_{\text{ES}}\\) or \\(P_{\text{tx}}\\)) or deactivation of Radio Units (RUs).
* **paper**: QACM: QoS-Aware xApp Conflict Mitigation in Open RANAbdul Wadud, Graduate Student Member, IEEE, Fatemeh Golpayegani, Senior Member, IEEE, and Nima Afraz, Senior Member, IEEE

---

#### 6. Coverage & Capacity Optimization (CCO) xApp
* **Inputs:** SINR and Downlink Throughput.
* **Outputs:** Cell Transmit Power (\\(P_{\text{tx}}\\)) and Remote Electrical Tilt (RET).
* **paper**: Twin-Fidelity-Aware Resolution of Direct xApp Conflicts in Open RANAkram Almohammedi, Member, IEEE, Mohammed Balfaqih, Senior Member, IEEE, Sam Darshi, Senior Member, IEEE, Rami Langar, Member, IEEE, and Wael Jaafar, Senior Member, IEEE

---

#### 7. Coverage/Throughput-Oriented (CTO) xApp
* **Inputs:** Reference Signal Received Power (RSRP), SINR, and aggregate UE throughput.
* **Outputs:** Downlink transmit power (\\(P_{\text{CTO}}\\)).
* **paper**: Twin-Fidelity-Aware Resolution of Direct xApp Conflicts in Open RANAkram Almohammedi, Member, IEEE, Mohammed Balfaqih, Senior Member, IEEE, Sam Darshi, Senior Member, IEEE, Rami Langar, Member, IEEE, and Wael Jaafar, Senior Member, IEEE

---

#### 8. Data Rate Maximization (DRM) xApp
* **Inputs:** O-RAN state vector \\(s(t)\\) containing associated RU IDs, RB IDs, Channel Quality Indicators (CQI), UE spatial locations, and buffer states.
* **Outputs:** Multi-channel transmit power vector (\\(a_1 = p_{n,m}\\)) for all RUs and Resource Blocks.
* **paper**: COMIX: Generalized Conflict Management in O-RAN xApps - Architecture, Workflow, and a Power Control caseAnastasios E. Giannopoulos, Sotirios T. Spantideas, Levis George, Kalafatelis Alexandros, and Panagiotis Trakadas

---

#### 9. Energy Efficiency Maximization (EE) xApp
* **Inputs:** O-RAN state vector \\(s(t)\\) containing CQI, serving RU/RB IDs, and throughput metrics.
* **Outputs:** Multi-channel transmit power vector (\\(a_2 = p_{n,m}\\)) optimizing the ratio of data rate to power consumption.
* **paper**: COMIX: Generalized Conflict Management in O-RAN xApps - Architecture, Workflow, and a Power Control caseAnastasios E. Giannopoulos, Sotirios T. Spantideas, Levis George, Kalafatelis Alexandros, and Panagiotis Trakadas

---

#### 10. Stochastic & DRL-Based Slicing xApps (\\(a_1\\)–\\(a_5\\), \\(a_7\\))
* **Inputs:** Historical and live Key Performance Measurements (KPMs) per network slice (eMBB throughput, URLLC buffer occupancy/latency, mMTC transmitted packets).
* **Outputs:** Physical Resource Block (PRB) allocation across network slices.
* **paper**: PACIFISTA: Conflict Evaluation and Management in Open RAN Pietro Brach del Prever, Student Member, IEEE , Salvatore D’Oro, Member, IEEE , Leonardo Bonati, Member, IEEE , Michele Polese, Member, IEEE , Maria Tsampazi, Student Member, IEEE , Heiko Lehmann, Tommaso Melodia, Fellow, IEEE

---

#### 11. Downlink Scheduling xApps (\\(a_6\\), \\(a_8\\))
* **Inputs:** Real-time KPMs including buffer size, downlink throughput, and transmitted packet counts.
* **Outputs:** Internal downlink scheduling policy selection (e.g., Round Robin, Proportional Fair, Waterfilling).
* **paper**: PACIFISTA: Conflict Evaluation and Management in Open RAN Pietro Brach del Prever, Student Member, IEEE , Salvatore D’Oro, Member, IEEE , Leonardo Bonati, Member, IEEE , Michele Polese, Member, IEEE , Maria Tsampazi, Student Member, IEEE , Heiko Lehmann, Tommaso Melodia, Fellow, IEEE
---

#### 12. Connection Management / Handover Control xApp
* **Inputs:** Received signal metrics (RSRP, SINR), user mobility trajectories, and user utility scores.
* **Outputs:** Handover decisions, target cell selection, or disconnect (DC) commands.
* **paper**: xApp Distillation: AI-based Conflict Mitigation in B5G O-RAN Hakan Erdol ∗ , Xiaoyang Wang † , Robert Piechocki ∗ , George Oikonomou ∗ , Arjun Parekh

---

#### 13. Beamforming / Beam Selection xApp
* **Inputs:** 3D spatial coordinates \\((x, y, z)\\), RSRP, RSRQ, and channel state indicators.
* **Outputs:** Antenna radiation patterns, beam ID selection, and beam-level transmit power.
* **paper**: Digital Twin-Enhanced Reinforcement Learning for Intelligent xApps Management in O-RAN Systems Zhizhou He , Member, IEEE, Ahmed Al-Tahmeesschi , Member, IEEE, Chuan Heng Foh , Senior Member, IEEE, Hamed Ahmadi , Senior Member, IEEE, and Mohammad Shojafar , Senior Member, IEEE
---

#### 14. Context-Aware Scheduler xApp / Orchestrator
* **Inputs:** Operator intent targets (\\(f^\dagger\\)), Enrichment Information (EI) received via the A1 interface (mean user mobility speed, mean data arrival rate), and critic value function estimates (\\(V_\phi(s_\dagger)\\)).
* **Outputs:** Binary activation messages (\\(\mu^\dagger\\)) that select, hold, or suppress active xApps or toggle baseline fallbacks.
* **paper**: xApp Conflict Mitigation with Scheduler IDRIS CINEMRE, (Member, IEEE) , TOKTAM MAHMOODI, (Senior Member, IEEE) , AMIRMOHAMMAD FARZANEH, (Member, IEEE)

---

#### 15. Distilled / Multi-Task Student xApp
* **Inputs:** Replay buffer state vector aggregating multi-vendor observations.
* **Outputs:** Multi-headed action vector executing Handover, RB Allocation, and Cell Power Control simultaneously.
* **paper**: xApp Distillation: AI-based Conflict Mitigation in B5G O-RAN Hakan Erdol ∗ , Xiaoyang Wang † , Robert Piechocki ∗ , George Oikonomou ∗ , Arjun Parekh
---

### Available Datasets in the Literature

The sources highlight several datasets and repository benchmarks used for training, evaluating, and simulating multi-xApp conflict mitigation:

1. **QACM & CMS Repository Datasets (`GitHub`)**:
   * **Location / Reference:** `dewanwadud1/QACM` and `dewanwadud1/cmsORAN`.
   * **Description:** Contains synthetic conflict tables generated for stochastic xApps. Includes Gaussian-distributed KPI values, normalized utility metrics (min-max and z-score), and input control parameter ranges for direct, indirect, and implicit conflict scenarios.

2. **GRAPHICA Binary-State & Synthetic Graph Datasets**:
   * **Description:** Event-driven binary-state datasets capturing state transitions (\\(1\\) for change, \\(0\\) for no change) across 10 xApps, 15 controllable parameters, and 20 KPIs. It includes skewed conflict datasets at varying imbalance ratios (40%, 30%, 20%, and 10% conflict prevalence) as well as Gaussian-distributed KPI benchmark datasets.

3. **Colosseum Rome Scenario / OpenRAN Gym Dataset**:
   * **Description:** Extracted from the Colosseum wireless network emulator reproducing a real-world cellular deployment in Rome, Italy, using OpenCelliD GPS base station coordinates. It includes MGEN traffic generator logs serving eMBB (4 Mbps CBR), URLLC (89.29 kbps Poisson), and mMTC (44.64 kbps Poisson) slices across 50 PRBs, capturing over 30 KPMs per UE.

4. **Viavi RIC Testbed Synthetic UE-Level Dataset**:
   * **Description:** Synthesized from a Viavi RIC testbed containing 30,000 records with 25 to 41 features per record. It includes radio indicators (RSRP, RSRQ, SINR), QoS scores, 5QI indices, PRB consumption, scheduled transport blocks, and 3D spatial coordinates across 3 base stations, 6 cells, and 20 IoT UEs.

5. **`mobile-env` Gymnasium Environment Dataset**:
   * **Reference:** Schneider et al. open platform for reinforcement learning in wireless networks.
   * **Description:** Used in xApp distillation research to generate trajectory and state-action-reward transition replay memory buffers for Handover, RB Allocation, and Power Control.

6. **OpenCelliD Dataset**:
   * **Location / Reference:** OpenCelliD open-source database.
   * **Description:** Contains real-world GPS coordinates and structural topology of cell towers, used to construct realistic physical base station layouts in digital twin emulators.

7. **Raca et al. 5G Context Dataset**:
   * **Reference:** Raca et al. (2020).
   * **Description:** A 5G dataset containing channel metrics, throughput metrics, and context variables used for KPI normalizations and network state modeling.
