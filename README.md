### **1. Testbed Review & Feasibility Analysis**
The current setup (Open5GS + Near-RT RIC + srsRAN gNB) provides a functional O-RAN environment, but the sources highlight several "blocking limitations" for many standard use cases:
*   **Infrastructure Constraints:** The testbed is restricted to a **single cell (SISO)**, a **single host compute** (no distributed O-Cloud), and relies on **ZMQ (virtual RF)** or a **single SDR**. 
*   **Metric Gaps:** Critical metrics for massive MIMO (Beam SINR), mobility (Handover failures/attempts), and slice-level aggregates (Slice throughput) are **not exposed** by the current gNB implementation.
*   **Control Limitations:** The testbed is a **Near-RT RIC only** deployment, meaning use cases requiring the A1 interface or SMO-mediated configuration are not natively supported and must be simulated.

**Feasible Use Cases for The Thesis:**
*   **QoS/QoE Resource Optimization (UC 4.8 / 4.4):** Feasible because KPM data and PRB control are available.
*   **Congestion Prediction (UC 4.16):** Highly feasible as it relies on the KPM data pipeline and E2SM-RC control loops already present.
*   **Signalling Storm Protection (UC 4.15):** Partially feasible; you can generate load using the phones, though E2 throttling control may require custom development.

---

### **2. Identified Research Gaps (The Contribution Surface)**
The literature identifies three "major learning" areas where academic research is currently deficient:
*   **The "Sim-to-Reality" Gap:** 82% of studies rely solely on simulations, while only 5% validate results on real-world testbeds or hardware-in-the-loop (HIL) systems.
*   **Multi-Vendor Conflict Surface:** The interaction between different applications (xApps/rApps) from different vendors is cited as the "single biggest unsolved problem" in RIC deployments.
*   **Quantifying AI "Cost":** Most papers report performance gains but fail to detail the computational complexity, runtime cost, or hardware impact of the AI models on the RIC host.

---

### **3. Master's Thesis Directions**


#### **A. Sim-to-Reality Benchmark of O-RAN Control Loops**
*   **Problem:** Simulators (like ns-3) often fail to capture hardware impairments, real RF fading, and compute latency.
*   **Contribution:** Use the **2 SDRs and 4 phones** to implement a QoS optimization xApp. Run the exact same scenario in the hardware setup and in a ZMQ-based virtual environment.
*   **Outcome:** Quantify the "performance gap" in SINR and throughput. This provides the "reality check" that is currently missing from 90% of O-RAN literature.

#### **B. Near-RT Conflict Mitigation (Horizontal Conflicts)**
*   **Problem:** Simultaneous xApps (e.g., one for throughput, one for energy efficiency) often issue contradictory commands, leading to "ping-ponging" or instability.
*   **Contribution:** Develop a **Conflict-Aware Coordinator (CAC)** for the Near-RT RIC. Since you lack a Non-RT RIC, focus on **Horizontal Conflicts**.
*   **Task:** Implement two competing xApps and use the **E2 Guidance procedures** (introduced in 2023) to provide preemptive advice before actions are committed to the gNB.

#### **C. Data-Driven Congestion Prediction with Real Datasets**
*   **Problem:** There is a persistent lack of reliable, standardized, real-world O-RAN datasets for training models.
*   **Contribution:** Use the 4 phones to generate diverse traffic patterns (bursty gaming, 4K streaming, etc.). Collect and clean the KPM data landing in the **InfluxDB**.
*   **Outcome:** Train a **Congestion Prediction model** (UC 4.16) and release the "Real-World O-RAN KPM Dataset" to the research community. This addresses the reproducibility gap mentioned in nearly every survey.

