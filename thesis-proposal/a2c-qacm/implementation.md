# Architectural Specification: Context-Aware Conflict Mitigation via A2C Scheduling and QACM in Near-RT RIC

## 1. Executive Context and Strategic Framework

The evolution of Radio Access Networks (RAN) from monolithic, hardware-centric "black boxes" to disaggregated, Open RAN (O-RAN) architectures marks a definitive shift toward multi-vendor interoperability and data-driven intelligence. By decoupling the RAN software from the underlying hardware through standardized interfaces, O-RAN enables the deployment of third-party control applications, or xApps, within a Near-Real-Time RAN Intelligent Controller (Near-RT RIC). However, the proliferation of independent xApps—each pursuing narrow optimization targets—presents a critical stability risk. Without a centralized reconciliation framework like the Advantage Actor-Critic (A2C) Scheduler and QoS-Aware Conflict Mitigation (QACM), the network is susceptible to uncoordinated control loops that degrade performance.

The "So What?" of this architecture lies in the mitigation of severe operational frictions. For example, a Power Allocation xApp may attempt to mitigate inter-cell interference by reducing transmission power, while a simultaneous Traffic Steering xApp attempts to increase it to eliminate a cell-edge outage. Such friction results in oscillating transmission power and incompatible Resource Block Group (RBG) assignments, directly undermining 5G/6G Key Performance Indicators (KPIs) including throughput and spectral efficiency. To avoid these "non-stationary" environment risks, where one xApp's actions shift the underlying data distribution for others, a context-aware coordination layer is required.

The objective of this specification is to deploy an A2C-based scheduler and QACM logic that reconciles xApp directives in real-time. Crucially, this framework eliminates the need for expensive re-training of vendor-specific models. By utilizing a Critic network to stabilize the learning process against varying network contexts, the system achieves a "Zero-Touch" automation framework. This document details the technical implementation from the ns-O-RAN testbed to the mathematical foundations of the A2C model.

## 2. Integrated System Architecture: Near-RT RIC and ns-O-RAN Testbed

Bridging the gap between AI/ML research and production deployment requires a high-fidelity sandbox. The ns-O-RAN framework serves as this bridge, integrating production-grade Near-RT RIC platforms with 3GPP-compliant discrete-event simulations in ns-3. This strategy is vital for avoiding "Online Exploration Risks," where poorly trained Reinforcement Learning (RL) agents might cause service outages in a live commercial network.

### Dual-Instance Deployment Strategy

The architecture utilizes a bifurcated environment to ensure both training scalability and execution reliability:

* Simulated Environment (ns-3): Models the full protocol stack (PHY to SDAP) using 3GPP stochastic channel models. It generates the high-volume datasets (exceeding 40 million data points) required for offline training of conflict-mitigation policies.
* Real-World Near-RT RIC: A cloud-native platform hosting xApps and platform services. It interacts with the simulation or physical RAN nodes via standardized E2AP messaging.

### Near-RT RIC Platform Services

The Near-RT RIC provides the foundational infrastructure to handle high-frequency telemetry and control:

* E2 Termination: Manages SCTP-based routing of messages between the RIC and disaggregated RAN nodes (E2 Nodes).
* Subscription Management: Validates and filters xApp requests for Key Performance Measurements (KPMs) to prevent duplicate data requests and unnecessary overhead.
* Data Pipeline (ETL/Data Aggregation): Extracts, transforms, and loads raw telemetry into a shared data repository, correlating UE-level metrics into time-series records for ML inference.

### The ns-O-RAN Bridge and Synchronization Requirements

The ns-O-RAN bridge is a prescriptive requirement for maintaining the validity of the 100ms control loop:

* "e2sim" Extensions: The bridge extends the e2sim library to support multiple disaggregated endpoints (CU-CP, CU-UP, DU) simultaneously, allowing a single simulation process to represent a multi-cell environment with unique IP/port identifiers for each node.
* Unix-based Time Synchronization: To reconcile the simulator's discrete-event clock with the RIC's wall-clock time, the bridge establishes a baseline Unix timestamp. This ensures a consistent "happened-before" relationship for all E2 messages, critical for real-time inference.

## 3. Taxonomy of xApp Conflicts and Mitigation Logic

Identifying the specific archetype of a conflict is the strategic prerequisite for applying mitigation logic. In dynamic 5G environments, static priority rules (e.g., "always prioritize throughput") fail because xApps may coexist in low-load states but conflict severely under high UE density.

### O-RAN Conflict Taxonomy

| Conflict Type | Description | Primary Example Scenario |
| :--- | :--- | :--- |
| Direct Conflict | Multiple xApps request incompatible adjustments to the same NCP. | One xApp increases antenna tilt for coverage while another decreases it for capacity. |
| Indirect Conflict | xApps modify different NCPs but impact the same KPM. | Power Allocation xApp vs. RBG Allocation xApp impacting the normalized transmission rate. |
| Implicit Conflict | Independent KPM optimization causing latent degradation. | An Energy Efficiency xApp deactivates RUs, causing a Throughput xApp to fail QoS targets. |
| Contextual Conflict | Conflicts triggered only by specific operational factors. | High UE mobility patterns or traffic load (e.g., C-Band congestion) triggering inter-cell interference. |

The "So What?" of context-dependency is that the A2C scheduler must go beyond simple threshold-based rules. It must learn that the optimal action is a function of current network variables like UE speed and PRB utilization.

## 4. Algorithmic Foundation: A2C Scheduler and QACM Mechanics

The A2C model provides a strategic advantage over standard REINFORCE or DQN methods. In the volatile RAN environment, A2C utilizes a Critic to establish a baseline return, reducing variance and stabilizing the learning process. This is particularly effective for multi-vendor coordination where xApp actions create a non-stationary environment.

### A2C Scheduler Architecture

The scheduler utilizes a dual-network Actor-Critic structure:

* The Actor: Outputs a probability distribution $\pi_\theta$ over potential activation decisions $\mu_n \in \{0, 1\}$. This determines the optimal combination of xApp directives to execute.
* The Critic: Estimates the state-value function $V_\phi(s)$ to establish the baseline. It calculates the Advantage Function: $A_t = G_{t:t+1} - V_\phi(s_t)$ where $G_{t:t+1}$ is the one-step discounted return. This advantage quantifies whether the Actor's chosen action outperformed the expected average return.

### QoS-Aware Conflict Mitigation (QACM)

QACM acts as the final safety layer, leveraging Enrichment Information (EI) from the A1 interface to define "QoS satisfaction indicators." It reconciles conflicting xApp utilities by solving an optimization problem grounded in Nash's Social Welfare Function and Eisenberg-Gale solutions. By minimizing the weighted distance of xApp outputs from pre-defined QoS thresholds, QACM ensures that no critical service—such as URLLC or GBR traffic—is sacrificed for secondary optimizations.

### CNN Hyperparameters and Processing

To process the high-dimensional telemetry from per-UE and per-cell vectors, the following 1D Convolutional Neural Network (CNN) architecture is specified (Ref: Source 1, Table 1):

* Input Layer: Per-UE/per-cell parameters (B params x C cells).
* Conv1D Layer: 32 filters, Kernel Size = 8, Strides = 8. The kernel/stride alignment to 8 is critical to match the 8 input parameters per cell, ensuring spatial feature extraction from cell-specific metrics.
* Flatten & Dense Layers: Transitions features into a 128-neuron dense layer, followed by a 32-neuron layer, finally outputting the probability distribution over the action space.

## 5. Interface Specifications and Telemetry Data Model

The Near-RT RIC maintains closed-loop control at 10ms–1s granularities using E2SM-KPM (telemetry) and E2SM-RC (control).

### Telemetry Input Vector ($s_{t,e}$)

The A2C model and CNN require the following E2 metrics to characterize cell congestion and channel quality:

| Metric | Source | Impact on A2C/CNN Model |
| :--- | :--- | :--- |
| SINR | E2SM-KPM | Indicates channel quality and feasible modulation. |
| PRB Utilization | E2SM-KPM | Identifies cell-level resource occupancy/congestion. |
| Throughput (PDCP) | E2SM-KPM | Primary utility measure for per-UE and cell-level rate. |
| Active UEs ($Z_{c,t}$) | E2SM-KPM | Informs the CNN of current cell-level congestion. |
| Modulation Prob. | E2SM-KPM | Normalizes success rates of QPSK, 16QAM, 64QAM. |
| Queue Occupancy | E2SM-KPM | Signals latency risks for GBR and URLLC traffic. |

### Control Parameter Space ($a_{t,e}$)

The scheduler manages the activation and reconciliation of the following NCPs:

* Transmission Power (TXP): Discrete power levels to balance inter-cell interference and coverage.
* RBG Assignments: Frequency-domain allocation to optimize spectral efficiency.
* Mobility Thresholds (TTT & CIO): Time-to-Trigger and Cell Individual Offset to prevent "ping-pong" handovers.

The A1 Interface provides Enrichment Information (EI), such as capacity forecasts or high-level operator intents, which guide the QACM logic in setting dynamic QoS weights.

## 6. Operational Workflow and Execution Logic

A structured workflow is critical for maintaining "Zero-Touch" network automation. The 100ms reporting periodicity is a hard requirement to prevent "measurement conflicts" where decisions are based on stale RAN states.

1. Observation: The Near-RT RIC fetches KPMs (SINR, $Z_{c,t}$, PRB load) via E2SM-KPM reports from E2 Nodes.
2. Enrichment: The A1 interface provides contextual enrichment variables, such as external traffic load patterns or operator-defined intent shifts.
3. Inference: The A2C Actor processes the state and EI to generate a probability distribution $\pi_\theta$ over potential xApp actions. The optimal action is sampled from this distribution to maximize the expected Advantage.
4. Conflict Check: The QACM module validates the sampled actions against Nash Social Welfare criteria and QoS thresholds derived from A1 intents.
5. Execution: The RIC issues E2SM-RC Control Service messages to E2 Nodes to implement reconciled NCP adjustments.

## 7. Comparative Test Scenarios and Performance Evaluation

To validate the A2C architecture, it is evaluated against baseline heuristics (SON1, SON2, and RAN RRM) to prove strategic value-add in multi-vendor environments.

### Validation Environments

* Scenario A (Low-Band 850 MHz): Focuses on macro-cell coverage and handover performance with a 1700m Inter-Site Distance (ISD).
* Scenario B (C-Band 3.5 GHz): Focuses on capacity and spectral efficiency in a dense urban environment with a 1000m ISD.

### Traffic Model Mixture

The evaluation utilizes a 25% split across four traffic types: Full-buffer MBR, Video Streaming, Web Browsing, and Instant Messaging (GBR).

### Success Metrics

The A2C Scheduler is expected to outperform independent xApp deployments significantly:

* Normalized Transmission Rate: Primary target for Power/RBG reconciliation, aiming for 30–50% gains.
* Throughput Percentiles: Improving both average and 10th percentile (cell-edge) performance.
* Mobility Overhead ($H_u$): Specifically for Traffic Steering xApps, reducing unnecessary handovers while maintaining spectral efficiency.

By integrating the A2C Advantage function with QACM's QoS-aware validation, this architecture provides a scalable, non-intrusive path to intelligent conflict resolution, ensuring that disaggregated O-RAN ecosystems remain stable under the most dynamic 5G/6G network conditions.