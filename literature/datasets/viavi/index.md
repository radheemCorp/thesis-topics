The **VIAVI Network Digital Twin White Paper** outlines the actual parameters, modeling inputs, ingested telemetry, and calculated output metrics offered across its digital twin architecture. 

---

### 1. Radio & Channel Parameters (Radio Model)
* **3D Environmental Geometry & Ray Tracing:** Models 3D maps, buildings, walls, corners, obstacles, and indoor/outdoor terrain using AI-powered ray tracing.
* **Material Properties:** Captures physical material characteristics—such as **permittivity, conductivity, reflectivity, and scattering**—to calculate signal reflections and attenuation from moving targets like pedestrians, vehicles, drones, and walls.
* **Channel & Propagation Metrics:** Emulates high-fidelity radio propagation channels, multipath delay profiles, 3D channel models, and dynamic fading across sub-6 GHz (FR1) and mmWave/6G (FR3) frequency bands.
* **Beamforming & Antenna Setup:** Configures 3D beamforming codebooks, beam steering angles, beam width, power allocations, antenna tilts, and sectorized or isotropic cell configurations for MIMO and MU-MIMO setups.
* **Beam Path Loss Predictions:** Predicts beam-level path loss directly at gNBs using ray tracing without requiring UE Reference Signal Received Power (RSRP) reports.

---

### 2. Traffic & User Parameters (Traffic Model)
* **UE Scale & Emulation:** Emulates thousands of active mobile devices using the **TM500 Network Tester**.
* **Subscriber Profiles & Mobility:** Captures 3D spatial positioning, trajectories, speeds, and mobility patterns for static, vehicular, and indoor devices.
* **Application & QoS Profiles:** Models real-data traffic profiles, application utilization, QoS requirements, dynamic resource allocation, URLLC, voice, and video traffic.
* **Geolocation & Interaction Trace Data:** Ingests subscriber interaction analytics, geolocated call trace data, and device location context via **NITRO Location Intelligence**.
* **Surge & Security Attack Parameters:** Simulates **signalling storms** (millions of simultaneous connection attempts), cyber-attack scenarios, spoofing, and fuzzing injections.

---

### 3. Network & Component Parameters (Network Model)
* **Emulated Network Nodes:** Replicates full stack components, including Radio Units (**RU**), Distributed Units (**DU**), Centralised Units (**CU**), **Core Network** nodes, and cloud-native **RICs** (Near-RT and Non-RT).
* **Standardised Interfaces:** Operates over open O-RAN interfaces such as **E2, O1, and U1**.
* **Control Actions:** Executes sector power reductions, cell deactivations, Physical Resource Block (PRB) allocations, handover threshold adjustments, and rate limiting.

---

### 4. Live Telemetry & Ingestion Parameters
* **AIOps Performance Feeds:** Aggregates real-time performance measurements from physical networks via the **Cloud-Native NITRO AIOps** platform.
* **Field Instrument Measurements:** Captures live field data using wireless field instruments such as **xEDGE** and **OneAdvisor 800** to maintain synchronization with physical network states.

---

### 5. Output Metrics & Evaluated KPIs
* **QoS & Capacity:** Measures user throughput, Transport Block Error Rate (**BLER**), latency, and the number of active supported UEs.
* **Coverage & Mobility Performance:** Tracks signal quality, call success rates, and handover efficiency.
* **Energy & Sustainability:** Evaluates sector power consumption, percentage of energy saved (e.g. 5% reduction), and operational expenditure (**OPEX**) savings (e.g. 2.5% reduction).
* **Infrastructure & Security KPIs:** Tracks CPU processing load, rate limits, latency impact, and security breach vulnerability under traffic surges.

---

### 6. Core Modules in the VIAVI Suite
The white paper maps these parameters to specific platform modules:
* **TM500 Network Tester:** Multi-UE subscriber emulation.
* **TeraVM AI RAN Scenario Generator (AI RSG):** Topology, fading, and traffic scenario generation.
* **TeraVM CU/DU & Core Emulator:** Virtualised protocol stack and core network emulation.
* **TeraVM App Validation & Security Engine:** xApp/rApp testing and security vulnerability testing.
* **VAMOS Automation:** Campaign testing orchestration.
