# Data Sheet: Telemetry & State Parameters Extracted from ns-3 (`ns-O-RAN`)

In **ns-O-RAN**, the `ns-3` simulator connects to the O-RAN Near-RT RIC over the **E2 interface**, using the **E2SM-KPM** (Key Performance Measurement) and **E2SM-RC** (RAN Control) service models. The platform supports streaming up to **40 UE-level, cell-level, and node-level KPMs** at near-real-time periodicities (e.g., 100 ms).

Below is the structured data sheet of the parameters extracted from the `ns-3` simulation environment, categorized by network node layer, parameter symbol, data type, and description [37–39].

---

## 1. Telemetry Data Sheet

| Category | Parameter Symbol / Name | Originating E2 Node / Layer | Data Scope | Description |
| :--- | :--- | :--- | :--- | :--- |
| **UE Identifiers & Context** | **$u$ (UE ID)** | CU-CP | Per-UE | Unique identifier for each User Equipment (UE) active in the network. |
| | **$c \in C'_{u,t}$ (Cell IDs)** | CU-CP | Per-UE / Neighbor | Set of Cell Identifiers representing the serving primary cell and neighboring candidate cells for UE $u$ at time $t$. |
| **Radio Channel & Signal Quality** | **$\text{SINR}_{u,c,t}$** | CU-CP (L3 RRC) | Per-UE per Cell | **Signal-to-Interference-plus-Noise Ratio** of UE $u$ measured with respect to serving and neighboring cells $c \in C'_{u,t}$. |
| | **$\text{RSRP}_{u,c,t}$** | CU-CP (L3 RRC) | Per-UE per Cell | **Reference Signal Received Power** reported via L3 RRC measurement reports periodically or on mobility events. |
| **User Data & Throughput** | **$R_{u,t}$** | CU-UP (PDCP Layer) | Per-UE | **Instantaneous PDCP-layer Downlink Throughput** (combining LTE eNB and 5G NR split-bearers in EN-DC NSA mode). |
| **Cell Resource Utilization** | **$\text{PRB}_{c,t}$** | DU (MAC Layer) | Cell-Level | **Physical Resource Block (PRB) Utilization Percentage** for cell $c$ during reporting window $t$. |
| | **$Z_{c,t}$** | DU (MAC Layer) | Cell-Level | **Active User Count**, defined as the number of UEs in cell $c$ with active Transmission Time Interval (TTI) data transmissions at time $t$. |
| **Transport & Modulation Statistics** | **$P_{c,t}$** | DU (MAC Layer) | Cell-Level | **Total Transmitted Transport Blocks**, counting all MAC-layer transport blocks transmitted by cell $c$ across all served UEs at time $t$. |
| | **$p^{QPSK}_{c,t}$** | DU (MAC Layer) | Cell-Level | Ratio of successfully transmitted transport blocks using **QPSK modulation** normalized by $P_{c,t}$. |
| | **$p^{16QAM}_{c,t}$** | DU (MAC Layer) | Cell-Level | Ratio of successfully transmitted transport blocks using **16QAM modulation** normalized by $P_{c,t}$. |
| | **$p^{64QAM}_{c,t}$** | DU (MAC Layer) | Cell-Level | Ratio of successfully transmitted transport blocks using **64QAM modulation** normalized by $P_{c,t}$. |
| **Mobility & Penalty Metrics** | **$k(c_{u,t})$** | Near-RT RIC (Calculated) | Per-UE | **Handover Cost Penalty Factor**, calculated as an exponential decay function $K_0 e^{-\delta (t - t'_u)}$ based on the elapsed time since the UE's previous handover ($t - t'_u$), penalizing ping-ponging/frequent handovers [34, 38–39]. |

---

## 2. Operational Characteristics & Ingestion Details

* **Reporting Periodicity:** E2SM-KPM reports and L3 RRC measurements are streamed from `ns-3` to the RIC every **100 ms**.
* **Feature Vector Dimension:** For each UE $u$, the inputs from all serving and neighbor cells $C'_{u,t}$ are flattened into a consolidated feature matrix ($B \text{ parameters} \times C \text{ cells}$) and passed to the xApp inference model.
* **Missing Data Ingestion:** If any telemetry parameter is delayed or dropped in transit, the RIC ETL service uses a lookback window ($\epsilon = \text{tens to hundreds of ms}$) to fetch recent historical values and fill telemetry gaps.

---

**Follow-Up Suggestion:** Would you like to generate a Python data-preprocessing script that parses raw `ns-3` CSV traces and constructs these exact normalized input vectors for your ML models?