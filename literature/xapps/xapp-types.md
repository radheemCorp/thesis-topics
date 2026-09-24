In O-RAN specifications, reporting and controlling capabilities are defined using **Service Styles**:

* **Reporting Styles (E2SM-KPM / E2SM-RC):** Define the granularity and format in which the gNB sends periodic performance measurements, event-driven reports, or call process/UE information.
* **Control Styles (E2SM-RC):** Standardized command frameworks that dictate what RAN function is being modified (e.g., Radio Resource Allocation, Mobility, Cell Configuration).

---

## O-RAN App Categories, E2 Interface Parameters & Styles

| App Category | Primary Inputs (Telemetry / Metrics) | Output Control Actions | E2 Reporting Style | E2 Control Style (E2SM-RC) |
| --- | --- | --- | --- | --- |
| **QoS Optimization & Resource Management** | Per-slice/UE throughput & latency, Packet loss & buffer occupancy, Active PRB utilization | PRB quota & scheduling weights, 5QI priority overrides, Slice-level admission limits | **E2SM-KPM Style 1** *(E2 Node Measurement)* **E2SM-KPM Style 3** *(Per-UE Measurement)* | **Control Style 2** *(Radio Resource Allocation Control)* **Control Style 1** *(Radio Bearer Control)* |
| **Energy Saving (ES)** | Per-cell PRB utilization rates, Total cell power consumption, Active UE count & traffic profiles | Toggle `energySavingState` (cell/carrier off), Reduce Transmit Power / RF tilt, Deactivate spatial streams / antenna layers | **E2SM-KPM Style 1** *(E2 Node Measurement)* **E2SM-RC Style 1** *(Message-based Reporting)* | **Control Style 7** *(Cell Configuration & State Control)* **E2SM-CCC** *(Cell Config & Control)* |
| **Traffic Steering & Load Balancing** | Serving & Neighbor RSRP/RSRQ/SINR, Cell-level load metrics, UE Measurement Reports (A3/A5 events) | Override Cell Individual Offsets (CIO), Trigger direct E2-based UE handovers, Update Carrier Aggregation config | **E2SM-KPM Style 1** *(E2 Node Measurement)*, **E2SM-RC Style 3** *(UE Information Reporting)* | **Control Style 3** *(Connected Mode Mobility Control)*, **Control Style 5** *(Carrier Aggregation Control)* |
| **Mobility Management / Handover Optimization** | UE Speed estimates & Timing Advance, RLF counters & HO success/failure logs,Event A3/A5 trigger history | Tweak Time-To-Trigger (TTT), Modify Handover Hysteresis & offsets, Force direct handover execution | **E2SM-RC Style 2** *(Call Process Info Reporting)* **E2SM-KPM Style 3** *(Per-UE Measurement)* | **Control Style 3** *(Connected Mode Mobility Control)*, **Control Style 6** *(Idle Mode Mobility Control)* |
| **Massive MIMO & Beamforming Optimization** | Per-beam CSI feedback, SRS measurements, Angular UE distribution map | Adjust per-beam power allocation, Modify digital beam azimuth & tilt, Dynamic beamwidth shaping | **E2SM-RC Style 3** *(UE Information Reporting)* **E2SM-KPM Style 3** *(Per-UE Measurement)* | **Control Style 2** *(Radio Resource Allocation Control)***Control Style 7** *(Cell Configuration & State Control)* |
| **Interference Management (eICIC / CoMP)** | Uplink/Downlink SINR distributions, Inter-cell interference feedback, Sounding measurements | Modify Downlink Transmit Power limits, Set Almost Blank Subframe (ABS) patterns, Apply Coordinated Multipoint schedules | **E2SM-KPM Style 1** *(E2 Node Measurement)* **E2SM-KPM Style 4** *(UE Condition Reporting)* | **Control Style 2** *(Radio Resource Allocation Control)* **Control Style 4** *(Radio Admission Control)* |

---

### Key Takeaways on E2SM Execution

1. **E2SM-KPM Reporting Styles:**
* **Style 1:** Cell-level / Node-level aggregated metrics (used for broad network state monitoring like Energy Saving or Load Balancing).
* **Style 3:** Per-UE fine-grained metrics (used when xApps need to make targeted changes to specific users, such as steering a high-throughput UE).


2. **E2SM-RC Service Modes:**
* **Control Service:** Near-RT RIC actively pushes a **Control Request** message over E2 to force a parameter change immediately.
* **Policy Service:** Near-RT RIC installs a **Policy Directive** in the E2 Node, allowing the gNB to run its own localized RRM logic as long as it operates within the bounds defined by the RIC.