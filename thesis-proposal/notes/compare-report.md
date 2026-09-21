Architectural Design Specification: Context-Aware Conflict Mitigation for Near-RT RIC

1. Project Overview and Strategic Rationale

The strategic migration toward O-RAN disaggregation facilitates a multi-vendor ecosystem but introduces a critical risk: network instability arising from uncoordinated, autonomous control loops. In a disaggregated environment, independent xApps often issue conflicting directives as they optimize local objectives (e.g., maximizing throughput vs. minimizing power consumption). Such uncoordinated execution leads to performance oscillations and breach of Service Level Agreements (SLAs). To protect the Operator’s Return on Investment (ROI), a centralized scheduler is a non-negotiable architectural requirement to ensure Key Performance Metric (KPM) stability and provide a robust mediation layer between third-party applications.

This specification defines the "Context-Aware" paradigm for conflict mitigation. This architecture transitions the Near-RT RIC from passive monitoring to active, intent-driven control by mitigating Direct, Indirect, and Implicit conflicts in real time. The core objective is to reconcile xApp outputs based on fluctuating network conditions—such as user mobility and traffic load—without the prohibitive computational and commercial overhead of re-training third-party xApp models. By treating xApps as immutable, pluggable microservices, the system maintains vendor neutrality while ensuring operational reliability.

2. O-RAN Near-RT RIC Integration Framework

Standardized interface compliance (A1, E2, and O1) is the fundamental prerequisite for the mediator logic of the Near-RT RIC. These interfaces provide the telemetry and control conduits required for the Scheduler to synchronize disparate xApp outputs.

Structural Integration and Component Workflow

The Scheduler shall be integrated as a core mediation service within the Near-RT RIC, interacting with the following ecosystem components:

* xApp Inference Host (IH): Hosts third-party modules (e.g., Power and RBG allocation xApps). The Scheduler manages these as immutable black boxes, issuing activation masks (\mu) to enable or disable their control logic.
* Data Access Platform & Common Data Repository: Serves as the middleware for real-time telemetry access. The Scheduler pulls current RAN states from this shared repository to ensure a "single version of truth" for all coordination logic.
* The E2 Interface: Facilitates the primary control loop. The system shall ingest E2SM-KPM Reports as the primary input trigger and issue E2SM Control directives as the final reconciled output to the RAN.
* The A1 Interface: Ingests Enrichment Information (EI) and high-level Intent-based configurations from the Non-RT RIC. This allows the Scheduler to align near-real-time actions with long-term operator goals.

Visual Data Flow Representation

The following logic flow describes the Scheduler’s role as the mediator between intent and execution:

Stage	Input/Trigger	Component	Action/Output
Ingestion	A1-EI & MNO Intent	Scheduler	Target Objective (f^\dagger) Defined
Monitoring	E2SM-KPM Reports	Scheduler	Context State (s_t) Identified
Mediation	xApp Inference Vectors	A2C / QACM Engine	Activation Mask (\mu) Generated
Execution	Reconciled Logic	E2 Interface	E2SM Control Command

This structural design ensures that the Advantage Actor-Critic (A2C) scheduler possesses a comprehensive view of both the physical network context and the administrative intent.

3. Technical Specification: A2C Scheduler Design

The system shall utilize the Advantage Actor-Critic (A2C) method as the primary Deep Reinforcement Learning (DRL) engine. A2C is selected for its superior balance of variance reduction and learning stability, utilizing a Critic to estimate a state-value baseline that prevents the Actor from making erratic updates in response to transient network noise.

Internal Logic and State Space

The A2C Scheduler shall process a comprehensive context vector to determine optimal xApp activation. Per the system model, the State Space (s_{t,e}) is defined as: s_{t,e} = [\zeta_{b,r,u}, \Psi_{b,r,u}, p_{b,r,u}, \varrho_{b,r,u}] Where:

* \zeta: Logarithmic normalized channel state information.
* \Psi: Current transmission rate (last state).
* p: Prevailing transmission power levels.
* \varrho: Mean data arrival rate (load).

The Action Space (a_t) shall consist of activation masks (\mu), which are binary vectors determining which xApp is permitted to influence specific Network Control Parameters (NCPs). The Advantage Function (A_t) reduces variance by calculating the delta between the one-step return and the Critic’s baseline, ensuring stable convergence.

Implementation Methodologies

The architecture supports two distinct operational modes for xApp coordination:

1. Method 1 (Previous Action Retention): If an xApp is deactivated, the system retains its last valid action. This ensures KPM continuity and prevents configuration "snapping" during xApp handovers.
2. Method 2 (Baseline Extension): The system shall possess the capability for hybrid selection. The Scheduler may independently select one module for power (e.g., A2C xApp) and another for RBG allocation (e.g., Baseline equal-allocation) to maximize performance in high-mobility scenarios where xApp models may struggle.

A2C Action Space Configuration

Feature	Method 1: Previous Action Retention	Method 2: Baseline Extension
Flexibility	Moderate (xApp-bound)	High (Hybrid Module Selection)
Fallback Capability	Implicit (Holds last valid state)	Explicit (Switches to deterministic baseline)
Strategic Advantage	Consistency in stable loads	Highest performance in high-load/high-mobility

4. Technical Specification: QoS-Aware Conflict Mitigation (QACM)

To address performance floors, the architecture shall support QoS-Aware Conflict Mitigation (QACM), functioning as a Conflict Mitigation Controller (CMC). Unlike the A2C engine, QACM is distribution-agnostic, making it a superior choice for dynamic RAN conditions where KPM behavior deviates from Gaussian assumptions.

QACM utilizes Nash Social Welfare and Eisenberg-Gale solutions to reconcile xApp utilities based on their distance from operator-defined QoS thresholds. This engine provides a deterministic "So What?" factor: during resource scarcity, QACM prioritizes xApp outputs that are closest to breaching their performance floors. This ensures that critical service intents (e.g., URLLC) are maintained even when the global throughput-optimizing RL policy would otherwise de-prioritize them.

5. Deployment Workflow & Interface Operations

The system shall follow a "Zero-Touch" operational workflow to bypass the "Immutability of Deployed xApps" bottleneck. Coordination is achieved by managing the activation of the apps rather than attempting to modify their internal, vendor-proprietary weights.

Execution Sequence

1. Intent Ingestion: MNO provides high-level goals (e.g., "Maximize Throughput") via the SMO Intent Interface.
2. EI Dispatch: Non-RT RIC translates intent into Enrichment Information (EI) delivered via A1.
3. Context Monitoring: Scheduler monitors E2SM-KPM reports for load (\varrho) and speed (v) triggers.
4. Inference & Activation: Scheduler executes A2C or QACM logic to issue activation masks (\mu).
5. Control Execution: Reconciled xApp actions are issued as E2SM Control commands.

Safety Layer: Confidence-Gated Fallback

The system shall implement a safety layer to manage Out-of-Distribution (OOD) scenarios. Using a forgetting factor (\beta) for exponentially weighted moving models, the system shall calculate a z-score based on the Critic's value estimate. If the z-score falls below a predefined threshold, the RL action is suppressed, and a deterministic fallback (e.g., equal-resource allocation) is invoked until the network state stabilizes.

6. Comparative Performance & Evaluation Metrics

Benchmarking separate A2C and QACM instances is required to identify the optimal engine for specific network "Contexts."

Primary KPMs for Evaluation

* Normalized Transmission Rate (\tau_e): Preservation of end-to-end throughput.
* Leftover / Discarded Bits: Reduction in buffer overflows/packet drops.
* Control Policy Stability: Statistical measures including COV, SD, and RMSSD to identify and eliminate allocation oscillations.
* Inference Latency: Ensuring processing remains within the 10ms–1s Near-RT RIC window.

Comparative Framework: GRAPHICA

Prior to active mitigation, the system may utilize GRAPHICA, a GCN-based passive diagnostic tool. GRAPHICA identifies root causes by processing binary-state transitions (S_t)—which track changes in xApps, parameters, and KPIs relative to the previous timestamp—to identify which specific apps are triggering direct, indirect, or implicit conflicts.

Comparison Summary Matrix

Metric	GRAPHICA (Diagnostic)	A2C Scheduler (Active)	QACM (Active)
Primary Role	Anomaly Detection & RCA	Active Action Coordination	QoS Resource Fairness
Input Signals	Binary transitions (S_t)	Context (\varrho, v) + Intent	Utility & QoS Thresholds
Explainability	High (Subgraph inspection)	Low (Black-box RL policy)	Moderate (Math Utility)
Re-training Need	None (Structural/Static)	Lightweight (On intent change)	None (Threshold-based)

By integrating context-sensitive A2C scheduling with distribution-agnostic QACM controls, this architecture ensures a robust, vendor-neutral O-RAN deployment capable of maintaining stability in the most demanding 6G environments.

