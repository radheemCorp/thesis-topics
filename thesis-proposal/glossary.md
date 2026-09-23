# Glossary: A2C Scheduler vs. QACM Experiment

Domain terms and acronyms used across the experiment material (`spec.md`, `implementation-plan.md`, `approach.md`, the two source papers, and the ns-O-RAN testbed notes).

---

## 1. O-RAN Architecture

| Term | Expansion | Definition |
| :--- | :--- | :--- |
| **O-RAN** | Open Radio Access Network | Disaggregated, virtualized, vendor-neutral RAN architecture with standardized interfaces enabling multi-vendor interoperability. |
| **RIC** | RAN Intelligent Controller | Control platform hosting intelligent applications that reconfigure the RAN. Split into Near-RT and Non-RT tiers. |
| **Near-RT RIC** | Near-Real-Time RAN Intelligent Controller | RIC tier operating control loops at 10 ms – 1 s timescales; hosts xApps. |
| **Non-RT RIC** | Non-Real-Time RAN Intelligent Controller | RIC tier operating at >1 s timescales; hosts rApps; provides guidance, enrichment information, and AI/ML model management. |
| **xApp** | Extended Application | Third-party control application hosted in the Near-RT RIC for radio resource management. |
| **rApp** | RAN Application | Third-party application hosted in the Non-RT RIC for non-real-time optimization. |
| **SMO** | Service Management and Orchestration | Management layer that orchestrates RAN components and hosts the Non-RT RIC. |
| **E2** | E2 Interface | Interface connecting the Near-RT RIC to RAN nodes (E2 nodes) for near-real-time monitoring and control. |
| **A1** | A1 Interface | Interface between Non-RT RIC and Near-RT RIC for policy-based management and enrichment information (EI) transfer. |
| **O1** | O1 Interface | Management interface between SMO and RAN components (configuration, alarms, performance). |
| **O2** | O2 Interface | Interface between SMO and O-Cloud for resource lifecycle management. |
| **E2 Node** | E2 Node | RAN node (O-CU, O-DU, O-RU) connected to the Near-RT RIC via E2. |
| **E2SM** | E2 Service Model | Defines the information elements and procedures for a specific service over E2 (e.g., KPM, RC). |
| **E2SM-KPM** | E2 Service Model — Key Performance Measurement | Service model for streaming performance measurements (telemetry) from E2 nodes to the RIC. |
| **E2SM-RC** | E2 Service Model — RAN Control | Service model for issuing control directives from the RIC to E2 nodes. |
| **E2SM-CCC** | E2 Service Model — Common Control Channel | Service model for common control channel operations (non-functional in the TU Ilmenau testbed). |
| **E2AP** | E2 Application Protocol | Application protocol carrying E2 messages (setup, subscription, control, indication). |
| **EI** | Enrichment Information | Contextual data (e.g., capacity forecasts, external analytics) relayed from Non-RT RIC to Near-RT RIC via A1. |
| **IH** | Inference Host | Component hosting xApp models for inference; receives activation masks from the scheduler. |
| **O-CU / O-DU / O-RU** | O-RAN Central Unit / Distributed Unit / Radio Unit | Disaggregated gNB functional splits: CU (higher layers), DU (lower layers), RU (RF). |
| **CU-CP / CU-UP** | CU Control Plane / User Plane | Functional split of the O-CU into control-plane (RRC/PDCP-C) and user-plane (SDAP/PDCP-U). |
| **E2SM-RC Style 2** | Control Service Style 2 — Radio Resource Allocation Control | PRB quota control (min/max/dedicated ratios per slice/UE/UE-group); the main supported control surface in open-source testbeds. |
| **E2SM-RC Style 8** | Control Service Style 8 — Power Control | Transmit-power control; generally not supported in open-source gNB stacks. |
| **O-Cloud** | O-RAN Cloud | Cloud platform hosting O-RAN functions (Near-RT RIC, O-CU, O-DU). |

---

## 2. Conflict Taxonomy

| Term | Definition |
| :--- | :--- |
| **Conflict** | Adverse interaction between control applications operating on shared RAN resources, degrading KPIs. |
| **Direct conflict** | Multiple xApps request incompatible adjustments to the same network control parameter (NCP). |
| **Indirect conflict** | xApps modify different NCPs that affect the same KPM, unintentionally interfering with each other's objectives. |
| **Implicit conflict** | xApps optimize distinct KPMs via different NCPs but inadvertently degrade each other's performance; latent and hard to detect. |
| **Contextual conflict** | Conflict triggered only under specific operational conditions (e.g., high load or mobility); dormant otherwise. |
| **NCP** | Network Control Parameter | A RAN parameter controlled by xApps (e.g., TXP, RET, CIO, TTT, PRB quota). |
| **KPM** | Key Performance Measurement | A measured performance indicator (O-RAN terminology; ≈ KPI). |
| **KPI** | Key Performance Indicator | A performance metric associated with an xApp's objective (e.g., throughput, SINR, power consumption). |
| **ICP** | Input Control Parameter | A control parameter that an xApp directly sets. |
| **PG** | Parameter Group | Set of parameters affecting the same network zone/KPM (used for indirect-conflict detection). |
| **CDC** | Conflict Detection Controller | CMS component that detects direct, indirect, and implicit conflicts. |
| **CMC** | Conflict Mitigation Controller | CMS component that computes the optimal compromise parameter value. |
| **PMon** | Performance Monitoring | CMS component that monitors KPIs against QoS thresholds and logs degradations. |
| **CS xApp** | Conflict Supervision xApp | xApp that assigns priority weights to conflicting xApps based on MNO policy and network state. |
| **CMS** | Conflict Management System | Framework of PMon, CDC, CMC, CS xApp, and supporting database components. |
| **RCP** | Recently Changed Parameter | Database component logging recently modified parameters with timestamps. |
| **PGD** | Parameter Group Definition | Database component cataloging parameters affecting the same network zone. |
| **RCPG** | Recently Changed Parameter Group | Database component logging parameter-group changes with timestamps. |
| **PKR** | Parameter and KPI Ranges | Database component storing min/max permissible parameter and KPI values. |
| **DCKD** | Decision Correlated with KPI Degradation | Database component storing KPI thresholds derived from QoS/SLA requirements. |
| **KDO** | KPI Degradation Occurrences | Database component tracking KPI degradation events with timestamps. |

---

## 3. Mitigation Approaches

| Term | Expansion | Definition |
| :--- | :--- | :--- |
| **A2C Scheduler** | Advantage Actor-Critic Context-Aware Scheduler | DRL-based macro-level coordinator that selects which pre-trained xApps are active based on context and intent. |
| **QACM** | QoS-Aware xApp Conflict Mitigation | Micro-level parameter bargaining method that finds the compromise parameter value maximizing the number of xApps meeting QoS thresholds. |
| **QACMP** | QACM Priority | QACM variant with priority weights for conflicting xApps. |
| **NSWF** | Nash's Social Welfare Function | Game-theoretic benchmark maximizing the product of xApp utilities (non-priority case). |
| **EG** | Eisenberg-Gale | Game-theoretic benchmark maximizing weighted utility (priority case). |
| **Activation mask** | — | Binary vector $\mu^\dagger \in \{0,1\}^n$ indicating which xApps are active in a scheduling period. |
| **Method 1** | Retain previous action | Scheduler activates chosen A2C xApps; a deactivated xApp keeps its last action. |
| **Method 2** | Extend with baselines | Scheduler selects one power xApp (A2C or baseline) and one RBG xApp (A2C or baseline), subject to $\mu_1+\mu_3=1$, $\mu_2+\mu_4=1$. |
| **Confidence-gated fallback** | — | Safety layer that overrides the learned action with a deterministic fallback policy when the critic's value z-score falls below a threshold. |
| **$\pi_{safe}$** | Safe fallback policy | Deterministic fallback: equal resource allocation or the single xApp with highest offline reward. |
| **Utility** | — | Scalar representation of an xApp's KPI, obtained via z-score normalization $U(p)=(k(p)-\mu)/\sigma$. |
| **QoS threshold** | Quality of Service threshold | Per-xApp KPI target $q'$ derived from SLA requirements; used to compute satisfaction $s_i$ and shortfall $d_i$. |
| **Satisfaction indicator** | — | Binary $s_i$ indicating whether xApp $i$ meets its QoS threshold for a candidate parameter value. |
| **Shortfall** | — | Distance $d_i$ between an xApp's utility and its QoS threshold (direction-dependent via $\delta_i$). |
| **$\delta_i$** | KPI direction | Binary: 0 = KPI to maximize, 1 = KPI to minimize. |
| **$\zeta$** | Tuning constant | Constant balancing weighted distance vs. satisfaction in the QACM objective (used value $10^3$). |
| **Optimal configuration range** | — | Union of per-xApp ranges $[p_{min,opt}, p_{max,opt}]$ for the conflicting parameter. |
| **Heuristic Alg. 1** | — | $O(N \cdot \|X'\|)$ discrete search over candidate parameter values for large/dynamic instances. |

---

## 4. Reinforcement Learning

| Term | Expansion | Definition |
| :--- | :--- | :--- |
| **RL** | Reinforcement Learning | Learning paradigm where an agent maximizes cumulative reward through interaction with an environment. |
| **DRL** | Deep Reinforcement Learning | RL with deep neural networks as function approximators. |
| **A2C** | Advantage Actor-Critic | Synchronous actor-critic algorithm using the advantage function to reduce policy-gradient variance. |
| **A3C** | Asynchronous Advantage Actor-Critic | Asynchronous variant of A2C. |
| **REINFORCE** | — | Basic Monte-Carlo policy-gradient algorithm (high variance). |
| **DQN** | Deep Q-Network | Value-based DRL using a deep network to approximate Q-values. |
| **Actor** | — | Policy network $\pi_\theta(a\|s)$ outputting a probability distribution over actions. |
| **Critic** | — | Value network $V_\phi(s)$ estimating expected return from a state (baseline). |
| **Advantage** | — | $A(s,a) = G_{t:t+1} - V_\phi(s)$; how much better/worse an action is than the baseline. |
| **Policy gradient** | — | Gradient of expected return w.r.t. policy parameters; drives the actor update. |
| **State** | — | $s^\dagger = [c_1^\dagger, c_2^\dagger, f^\dagger]$ for the scheduler; per-UE/per-cell feature matrix for xApps. |
| **Action** | — | Scheduler: activation mask; Power xApp: power level per RBG; RBG xApp: RBG-to-UE assignment. |
| **Reward** | — | Scheduler: normalized transmission rate $\tau_e$; xApps: per-episode normalized data transmission. |
| **Return** | — | Discounted sum of future rewards $G_t = \sum_j \gamma^j \tau_{t+j}$. |
| **Discount factor** | — | $\gamma$ weighting future rewards (paper uses 0.95). |
| **Episode** | — | One training run of $T$ time steps (paper: $T=50$). |
| **Scheduling period** | — | $\dagger$; interval between scheduler decisions (paper: 10 time steps). |
| **EWMA** | Exponentially Weighted Moving Average | Recursive mean estimate with forgetting factor $\beta$; used for critic-value statistics in the confidence gate. |
| **z-score** | — | Standardized score $(x-\mu)/\sigma$; used for KPI→utility conversion and out-of-distribution detection. |
| **Out-of-distribution** | — | State whose critic value z-score falls below the MNO-defined threshold; triggers fallback. |

---

## 5. Network & Telemetry

| Term | Expansion | Definition |
| :--- | :--- | :--- |
| **ns-3** | Network Simulator 3 | Discrete-event network simulator. |
| **ns-O-RAN** | ns-3 O-RAN | ns-3 framework connecting the simulator to a Near-RT RIC over E2 (E2SM-KPM/E2SM-RC). |
| **UE** | User Equipment | Mobile device served by the RAN. |
| **gNB** | Next-Generation NodeB | 5G base station (disaggregated into O-CU/O-DU/O-RU in O-RAN). |
| **O-RU** | O-RAN Radio Unit | RF unit; in ns-O-RAN, virtual (ZMQ) or SDR. |
| **RB** | Resource Block | Smallest frequency-domain scheduling unit (12 subcarriers). |
| **RBG** | Resource Block Group | Bundle of consecutive resource blocks; smallest allocable time-frequency unit for user assignment. |
| **PRB** | Physical Resource Block | Physical resource block; PRB utilization = fraction of PRBs used. |
| **PRB quota** | — | Min/max/dedicated PRB allocation ratio per slice/UE/UE-group (E2SM-RC Style 2 control). |
| **TXP** | Transmit Power | Cell/UE transmit power; a common conflicting NCP (requires E2SM-RC Style 8). |
| **RET** | Remote Electrical Tilt | Antenna tilt control parameter. |
| **CIO** | Cell Individual Offset | Handover boundary offset parameter. |
| **TTT** | Time-to-Trigger | Handover trigger timing parameter. |
| **HYS** | Handover Hysteresis | Hysteresis margin for handover decisions. |
| **SINR** | Signal-to-Interference-plus-Noise Ratio | Channel quality metric. |
| **RSRP** | Reference Signal Received Power | Measured reference-signal power. |
| **RSRQ** | Reference Signal Received Quality | Reference-signal quality metric. |
| **CQI** | Channel Quality Indicator | Reported channel quality (dummy/placeholder in some testbeds). |
| **PDCP** | Packet Data Convergence Protocol | Layer carrying user data; PDCP throughput $R_{u,t}$ is the primary rate metric. |
| **RLC** | Radio Link Control | Layer providing ARQ/segmentation; RLC drop rate and SDU delay are KPMs. |
| **MAC** | Medium Access Control | Layer performing scheduling; source of PRB and transport-block metrics. |
| **TTI** | Transmission Time Interval | Scheduling time unit (1 ms in LTE/NR). |
| **Transport block** | — | MAC-layer data unit transmitted per TTI. |
| **Modulation** | — | QPSK/16QAM/64QAM; modulation ratios indicate link quality. |
| **Leftover bits** | — | Discarded bits from buffer overflow when offered load exceeds transmission capacity. |
| **Normalized transmission rate** | — | $\tau_e = \sum_t \tau_{t,e} / (d_e \cdot R \cdot B)$; scheduler reward. |
| **Handover cost penalty** | — | $k(c_{u,t}) = K_0 e^{-\delta(t-t'_u)}$; penalizes frequent/ping-pong handovers. |
| **COV / SD / RMSSD** | Coefficient of Variation / Standard Deviation / Root Mean Square of Successive Differences | Control-policy volatility metrics. |
| **ETL** | Extract, Transform, Load | Data pipeline converting raw telemetry into model-ready feature matrices. |
| **Lookback window** | — | $\epsilon$; recent-history window used to fill missing/delayed telemetry. |

---

## 6. Testbed & Infrastructure

| Term | Expansion | Definition |
| :--- | :--- | :--- |
| **Open5GS** | — | Open-source 5G core (AMF, SMF, UPF, etc.). |
| **srsRAN / OCUDU** | — | Open-source gNB stack used in the TU Ilmenau testbed. |
| **ZMQ** | ZeroMQ | Virtual RF transport (no real over-the-air propagation). |
| **USRP B210** | Universal Software Radio Peripheral | SDR used for real RF in the TU Ilmenau testbed. |
| **SCTP** | Stream Control Transmission Protocol | Transport for E2 (port 36421) and N2 (port 38412). |
| **GTP-U** | GPRS Tunnelling Protocol — User Plane | User-plane tunnel on N3 (UDP 2152). |
| **Kafka** | — | Message bus for telemetry distribution (xapp-metrics topic). |
| **InfluxDB** | — | Time-series database for KPM storage (Grafana/AIMLFW feeds). |
| **MongoDB** | — | Document store used for subscriber data and rApp feeds. |
| **Telegraf** | — | Metrics collector scraping gNB JSON metrics. |
| **Grafana** | — | Visualization front-end for time-series data. |
| **AIMLFW** | AI/ML Framework | O-RAN ML workflow framework (not deployed in the TU Ilmenau testbed). |
| **Kubeflow / KServe** | — | ML training/serving platforms (not deployed). |
| **Colosseum** | — | Hardware-in-the-loop wireless emulator (OpenRAN Gym). |
| **mobile-env** | — | Minimalist Python environment for RL coordination in wireless networks. |
| **Digital Twin** | — | High-fidelity virtual replica of the network for offline training/validation. |

---

## 7. xApps & Use Cases

| Term | Expansion | Definition |
| :--- | :--- | :--- |
| **Power xApp ($X_1$)** | — | A2C-trained xApp allocating transmit power per RBG. |
| **RBG xApp ($X_2$)** | — | A2C-trained xApp assigning RBGs to users. |
| **Baseline power xApp ($X_3$)** | — | Equal-allocation power policy. |
| **Baseline RBG xApp ($X_4$)** | — | Equal-allocation RBG policy. |
| **ES** | Energy Saving | xApp minimizing power consumption / maximizing energy efficiency. |
| **CCO** | Capacity and Coverage Optimization | xApp maximizing throughput / minimizing SINR. |
| **MRO** | Mobility Robustness Optimization | xApp maximizing handover success / minimizing call drops. |
| **MLB** | Mobility Load Balancing | xApp balancing cell load / maximizing resource use. |
| **SON** | Self-Organizing Network | Legacy automation framework (self-configuration/optimization/healing); precursor to xApps. |
| **SONF** | SON Function | Individual SON automation function (≈ xApp in O-RAN). |
| **IBNM** | Intent-Based Network Management | Non-RT RIC service converting high-level operator intents into low-level directives. |
| **IO** | Intelligent Orchestration | Non-RT RIC service ensuring xApps/rApps fulfil intents and avoid conflicts. |
| **MARL** | Multi-Agent Reinforcement Learning | RL with multiple learning agents (e.g., team learning). |
| **TMADRL** | Team Multi-Agent Deep RL | Team-learning DRL framework for multiple xApps. |
| **NDT** | Network Digital Twin | Digital replica used to evaluate candidate actions (e.g., COMIX). |
| **PACIFISTA** | — | SMO-level conflict evaluation/management framework using statistical severity profiling. |
| **GRAPHICA** | — | Near-RT RIC conflict-prediction classifier using a Graph Convolutional Network. |
| **COMIX** | — | Conflict-management framework using a digital twin to score candidate actions. |

---

## 8. Metrics & Evaluation

| Term | Definition |
| :--- | :--- |
| **QoS satisfaction rate** | Fraction of conflicting xApps meeting their QoS thresholds ($\sum s_i / \|X'\|$). |
| **KPI shortfall** | Distance of an xApp's utility from its QoS threshold ($d_i$). |
| **Conflict rate** | Frequency of conflicting control actions over the experiment. |
| **Mitigation latency** | Time from conflict detection to control dispatch (QACM solver/ANN vs. A2C forward pass). |
| **Control-policy volatility** | Stability of parameter/allocation series (COV, SD, RMSSD). |
| **ISD** | Inter-Site Distance | Distance between base-station sites (scenario parameter). |
| **GBR** | Guaranteed Bit Rate | Traffic class with reserved resources (e.g., URLLC, IM). |
| **URLLC / eMBB / mMTC** | Ultra-Reliable Low-Latency Communications / enhanced Mobile Broadband / massive Machine-Type Communications | 5G service classes with distinct QoS thresholds. |
| **V2X** | Vehicle-to-Everything | Vehicular communication scenario used for QoS threshold examples. |
| **5QI** | 5G QoS Identifier | QoS profile identifier for 5G bearers. |
| **DRB** | Data Radio Bearer | Bearer carrying user data between UE and core. |
| **SDU** | Service Data Unit | Payload unit at a protocol layer (e.g., RLC SDU). |
| **RACH** | Random Access Channel | Uplink channel for initial access. |
| **NGAP** | NG Application Protocol | Control-plane protocol between gNB and AMF. |
| **PFCP** | Packet Forwarding Control Protocol | Control protocol between SMF and UPF. |
| **NRF / NSSF / PCF / AMF / SMF / UPF** | Network Repository Function / Network Slice Selection Function / Policy Control Function / Access and Mobility Management Function / Session Management Function / User Plane Function | 5G core network functions. |
| **NWDAF** | Network Data Analytics Function | 5GC analytics function (not deployed in the TU Ilmenau testbed). |
| **SST / SD** | Slice/Service Type / Slice Differentiator | Network-slice identifiers. |
| **MCS** | Modulation and Coding Scheme | Link-adaptation indicator. |
| **EVS** | Explained Variance Score | Regression quality metric (used to compare ANN vs. polynomial). |
| **MSE** | Mean Squared Error | Regression loss/quality metric. |
| **R²** | Coefficient of Determination | Regression quality metric. |
| **MA reward** | Moving Average reward | Smoothed training reward (sliding window 500 in the A2C paper). |