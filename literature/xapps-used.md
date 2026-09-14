
### 1. Mobility & Traffic Management xApps
* **Mobility Load Balancing (MLB) xApp:** Balances traffic load across base stations by adjusting Cell Individual Offset (CIO) and handover thresholds.
* **Mobility Robustness Optimization (MRO) xApp:** Tunes Time-To-Trigger (TTT) and handover hysteresis to minimize radio link failures (RLFs) and ping-pong handovers.
* **Connection Management / Handover Control xApp:** Manages user handovers between cells based on signal strength, trajectories, or dual connectivity requirements.
* **Traffic Steering xApp:** Directs user traffic across different cells, frequency bands, or access technologies.

---

### 2. Power & Resource Management xApps
* **Power Allocation xApp:** Regulates discrete or continuous transmission power levels assigned to Resource Blocks (RBs) or Resource Block Groups (RBGs).
* **Radio Resource / RBG Allocation xApp:** Manages time-frequency resource allocation by distributing available RBs/RBGs among attached users.
* **Energy Saving (ES) xApp:** Lowers cell transmit power or deactivates Radio Units (RUs) to minimize energy consumption.
* **Coverage and Capacity Optimization (CCO) xApp:** Adjusts Transmit Power (TXP) and Remote Electrical Tilt (RET) to optimize cell coverage and signal quality (SINR).
* **Throughput / Data Rate Maximization (TM / DRM) xApp:** Allocates maximum available resources or power levels to optimize aggregate system throughput.
* **Coverage/Throughput-Oriented (CTO) xApp:** Raises transmit power to enhance received signal quality, cell-edge coverage, and aggregate throughput.

---

### 3. Slicing & Scheduling xApps
* **Network Slicing xApp:** Dynamically adjusts Physical Resource Block (PRB) allocations across network slices (e.g., eMBB, URLLC, and mMTC) to meet slice-specific requirements.
* **Downlink Scheduling xApp:** Controls internal scheduling algorithms (such as Round Robin, Proportional Fair, or Waterfilling) within network slices.

---

### 4. Specialized & Combined xApps
* **Beamforming / Beam Selection xApp:** Optimizes antenna radiation patterns and beam selection to maximize user throughput.
* **Interference Management xApp:** Controls transmit power or dynamic spectrum allocation to mitigate inter-cell and intra-cell interference.
* **V2X Management xApp:** Optimizes radio resource allocation and handover policies specifically for Vehicle-to-Everything (V2X) communication scenarios.
* **Distilled / Student xApps:** Multi-headed controllers trained by distilling knowledge from multiple pre-trained "teacher" xApps (e.g., combining Handover + RB Allocation and Handover + Power Control into a single xApp).
* **Deterministic Baseline xApps:** Reference xApps (such as Equal Power Allocation and Equal RBG Distribution) integrated alongside machine learning xApps in context-aware scheduling frameworks.

---

💡 Would you like to analyze a specific conflict pair from these sources (e.g., **MRO vs. MLB** or **ES vs. CCO**) and compare how different mitigation frameworks resolve their parameter clashes?
