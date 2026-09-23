# Gap Analysis: Implementation Plan Requirements vs. Available Data

This report compares the parameters required by the A2C/QACM implementation plan (`thesis-proposal/a2c-qacm/implementation.md`) against what is actually available in the ns-O-RAN telemetry exports (`data/`). It is the companion to `data/data-report.md`, which documents the raw data in detail.

## 1. Required Telemetry Input Vector ($s_{t,e}$) vs. Available

The implementation plan (Section 5, "Telemetry Input Vector") specifies six E2SM-KPM metrics as the CNN/A2C input. Status against the data:

| Required Metric | Required Source | Available in Data? | Where / Notes |
| :--- | :--- | :--- | :--- |
| SINR | E2SM-KPM | **Yes** | UE-level `SINR` (`cucp_ue_report.csv`), cell-level `Avg_Serving_SINR` / `Neighbor_Avg_SINR` (`cucp_cell_report.csv`, `cucp_neighbor_report.csv`). Only quality metric populated at all granularities. |
| Active UEs ($Z_{c,t}$) | E2SM-KPM | **Yes** | `Num_Active_UEs` (`cucp_cell_report.csv`). |
| PRB Utilization | E2SM-KPM | **No** | DU/MAC-layer metric; absent from CU-CP exports. |
| Throughput (PDCP) | E2SM-KPM | **No** | CU-UP metric; no PDCP throughput column in any export. |
| Modulation Prob. (QPSK/16QAM/64QAM) | E2SM-KPM | **No** | DU/MAC-layer metric; absent. |
| Queue Occupancy | E2SM-KPM | **No** | Absent; no latency/queue metric exported. |

**Result: 2 of 6 required telemetry metrics are available.**

## 2. Required Control Parameter Space ($a_{t,e}$) vs. Available

The plan (Section 5, "Control Parameter Space") manages three NCPs. These are *control* outputs (E2SM-RC), not telemetry, so they are not expected in the KPM exports — but the data must at least expose the state they act on:

| Required NCP | Available in Data? | Where / Notes |
| :--- | :--- | :--- |
| Transmission Power (TXP) | **Partial** | `Avg_Serving_TxPower` (`cucp_cell_report.csv`) is populated (0/30 dBm) at cell level; UE-level `TxPower` is all zero. |
| RBG Assignments | **No** | No frequency-domain allocation data; also no PRB utilization to drive it. |
| Mobility Thresholds (TTT & CIO) | **No** | No TTT/CIO parameters; `Avg_DynMobility` is the only mobility-related signal. |

## 3. CNN Input Vector Requirement vs. Available

The plan (Section 4, "CNN Hyperparameters") requires a per-cell input vector of **B = 8 parameters × C cells**, with the Conv1D kernel/stride of 8 aligned to those 8 parameters.

**Feasible input vector from current data (per cell):**

| # | Parameter | Source Column | Status |
| ---: | :--- | :--- | :--- |
| 1 | SINR (serving) | `Avg_Serving_SINR` | Available |
| 2 | SINR (neighbor avg) | `Neighbor_Avg_SINR` | Available |
| 3 | Active UEs ($Z_{c,t}$) | `Num_Active_UEs` | Available |
| 4 | RSRP (serving) | `Avg_Serving_RSRP` | Available |
| 5 | RSRQ (serving) | `Avg_Serving_RSRQ` | Available |
| 6 | TxPower (serving) | `Avg_Serving_TxPower` | Available |
| 7 | Mobility activity | `Avg_DynMobility` | Available (proxy) |
| 8 | Neighbor count | `Num_Neighbor_Cells` | Available |

The **8-parameter vector can be filled**, but only by substituting the plan's intended metrics (PRB utilization, throughput, modulation, queue occupancy) with weaker proxies (RSRP/RSRQ, mobility, neighbor count). The vector is structurally complete but semantically different from the plan.

## 4. Success Metrics vs. Available

The plan (Section 7, "Success Metrics") evaluates against three KPIs:

| Success Metric | Available in Data? | Where / Notes |
| :--- | :--- | :--- |
| Normalized Transmission Rate | **No** | Requires throughput + transport-block counts; neither is exported. |
| Throughput Percentiles (avg & 10th) | **No** | Requires PDCP throughput; absent. |
| Mobility Overhead ($H_u$) | **Partial** | `Avg_DynMobility` is a mobility-activity proxy; handover counts/penalty $k(c_{u,t})$ must be derived from it. |

## 5. Additional Requirements Not Covered by Telemetry

| Requirement | Status | Notes |
| :--- | :--- | :--- |
| A1 Interface Enrichment Information (EI) | **No** | Capacity forecasts / operator intents are external inputs; not in the exports. |
| 100 ms reporting periodicity | **Partial** | Reports are ~1 ms apart in the export; the 100 ms cadence is a pipeline configuration, not a data column. |
| 40M+ data points for offline training | **No** | Current export is ~8.3k rows; far below the plan's training-volume target. |

## 6. Summary

| Category | Required | Available | Gap |
| :--- | ---: | ---: | :--- |
| Telemetry input metrics | 6 | 2 | PRB utilization, PDCP throughput, modulation probabilities, queue occupancy |
| Control NCPs | 3 | 0 (1 partial) | RBG assignments, TTT/CIO; TXP only at cell level |
| CNN input vector (8 params/cell) | 8 | 8 (with proxies) | Semantics differ from plan |
| Success metrics | 3 | 0 (1 partial) | Normalized transmission rate, throughput percentiles |
| Training data volume | 40M+ | ~8.3k | 3 orders of magnitude short |

**Bottom line:** The current CU-CP exports cover the *channel-quality and congestion* dimension (SINR, active UEs, RSRP/RSRQ) but are missing the entire *resource-utilization and throughput* dimension (PRB, PDCP throughput, modulation, queue occupancy) that the A2C/QACM plan depends on. Closing the gap requires exporting DU/MAC-layer KPMs (PRB utilization, transport blocks, modulation ratios) and CU-UP KPMs (PDCP throughput) from ns-O-RAN, plus a longer simulation run to reach the target data volume.