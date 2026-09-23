# Gap Analysis: Implementation Plan Requirements vs. Available Data

This report compares the parameters required by the A2C/QACM experiment (`plan/iteration-3/spec.md` §2 and `plan/iteration-3/implementation-plan.md`) against what is actually available in the ns-O-RAN telemetry exports (`data/`). It is the companion to `data/data-report.md`, which documents the raw data in detail.

> **Note:** This analysis tracks the current iter-3 plan (A2C scenario: Power + RBG indirect conflict). Earlier iterations referenced the CNN-based input vector, queue occupancy, and TTT/CIO mobility thresholds from `a2c-qacm/implementation.md`; those are superseded.

## 1. Required Telemetry Input vs. Available

The iter-3 spec (§2.1) requires the following E2SM-KPM metrics. Status against the data:

| Required Metric | Required Source | Available in Data? | Where / Notes |
| :--- | :--- | :--- | :--- |
| UE identifier ($u$) | E2SM-KPM | **Yes** | `UE_ID` (`cucp_ue_report.csv`). |
| Cell IDs ($c \in C'_{u,t}$) | E2SM-KPM | **Partial** | `ServingCellID` / `NeighborCellID` / `Neighbor_PCI`. |
| SINR | E2SM-KPM | **Yes** | UE-level `SINR` (`cucp_ue_report.csv`), cell-level `Avg_Serving_SINR` / `Neighbor_Avg_SINR`. Only quality metric populated at all granularities. |
| RSRP | E2SM-KPM | **Partial** | Cell-level `Avg_Serving_RSRP` only; UE/neighbor RSRP all zero. |
| PDCP DL throughput ($R_{u,t}$) | E2SM-KPM | **No** | CU-UP metric; no throughput column in any export. |
| PRB utilization ($\text{PRB}_{c,t}$) | E2SM-KPM | **No** | DU/MAC-layer metric; absent from CU-CP exports. |
| Active user count ($Z_{c,t}$) | E2SM-KPM | **Yes** | `Num_Active_UEs` (`cucp_cell_report.csv`). |
| Transport blocks ($P_{c,t}$) | E2SM-KPM | **No** | DU/MAC-layer metric; absent. |
| Modulation ratios (QPSK/16QAM/64QAM) | E2SM-KPM | **No** | DU/MAC-layer metric; absent. |
| Handover cost penalty ($k(c_{u,t})$) | RIC (calc.) | **Partial** | `Avg_DynMobility` is a mobility-activity proxy; the penalty must be computed from it. |
| 100 ms reporting periodicity | E2SM-KPM | **Partial** | Reports are ~1 ms apart in the export; the 100 ms cadence is a pipeline configuration, not a data column. |
| Feature matrix $B \times C$ | RIC ETL | **Derived** | Built from the above in the ETL. |
| Missing-data lookback $\epsilon$ | RIC ETL | **Derived** | Gap-filling configuration. |

**Result: 3 of 10 telemetry metrics are fully available (UE id, SINR, active UEs); 4 partial; 4 missing (throughput, PRB utilization, transport blocks, modulation ratios).**

## 2. Required Control Parameter Space vs. Available

The iter-3 plan manages two NCPs. These are *control* outputs (E2SM-RC), not telemetry, so they are not expected in the KPM exports — but the data must at least expose the state they act on:

| Required NCP | Available in Data? | Where / Notes |
| :--- | :--- | :--- |
| Transmission Power ($p_{power}$) | **Partial** | `Avg_Serving_TxPower` (`cucp_cell_report.csv`) is populated (0/30 dBm) at cell level — telemetry only. E2SM-RC power control (Style 8) is unverified in ns-O-RAN (risk R1). |
| RBG Allocation ($p_{RBG}$) | **No** | No frequency-domain allocation data; also no PRB utilization to drive it. E2SM-RC PRB quota (Style 2) is expected supported but unverified (risk R2). |

> TTT/CIO mobility thresholds are **no longer in scope** — the iter-3 scenario is the Power + RBG indirect conflict.

## 3. A2C State Construction vs. Available

The iter-3 A2C scheduler state is $s^\dagger = [c_1^\dagger, c_2^\dagger, f^\dagger] = [d, v, \text{intent}]$ (context variables), with the $B \times C$ feature matrix as the ETL output feeding the models. The earlier CNN input vector (B = 8 params × C cells, Conv1D kernel 8) from `a2c-qacm/implementation.md` is **superseded**.

| State element | Source | Available in Data? | Notes |
| :--- | :--- | :--- | :--- |
| Arrival rate $c_1^\dagger = d$ | Simulation config / A1 EI | **No** | Must be exposed as simulation config and injected via simulated A1. |
| Mobility speed $c_2^\dagger = v$ | ns-3 mobility model | **No** | Must be derived from the mobility model and injected via simulated A1. |
| Intent $f^\dagger$ | A1 EI | **No** | Fixed intent (maximize total transmission rate) defined in the spec. |

The $B \times C$ feature matrix can only be partially filled from current data (SINR, cell-level RSRP/RSRQ, active UEs, cell-level TxPower, mobility, neighbor count); the resource-utilization and throughput columns are empty.

## 4. Success Metrics vs. Available

The iter-3 plan (spec §FR-8) evaluates against five metrics:

| Success Metric | Available in Data? | Where / Notes |
| :--- | :--- | :--- |
| Normalized transmission rate ($\tau_e$) | **No** | Requires throughput + transport-block counts; neither is exported. |
| Leftover (discarded) bits | **No** | Derived from offered load $d$ vs. delivered $R_{u,t}$; requires throughput. |
| QoS satisfaction ($s_i$) | **No** | Requires $\tau_e$ / leftover thresholds ($q_1$: $\tau_e \geq 0.9$; $q_2$: leftover ratio $\leq 0.05$); needs throughput. |
| Control volatility (COV, SD, RMSSD) | **Partial** | Computable from the TXP/RBG control series once control is implemented. |
| Mitigation latency | **Partial** | Measured at runtime (QACM solver/ANN vs. A2C forward pass). |

## 5. Additional Requirements Not Covered by Telemetry

| Requirement | Status | Notes |
| :--- | :--- | :--- |
| A1 Interface Enrichment Information (EI) | **No** | Context ($d$, $v$) and intent are external inputs; not in the exports. Must be simulated. |
| Leftover-bits derivation | **No** | Needs $R_{u,t}$ (missing) + offered load $d$ (sim config). |
| QoS thresholds ($q_1$, $q_2$) | **No** | Defined in the spec; cannot be evaluated without throughput. |
| KPI prediction training data (TXP × RBG sweep) | **No** | Must be generated from ns-3 sweep runs for the QACM ANN. |
| 100 ms reporting periodicity | **Partial** | Reports are ~1 ms apart in the export; the 100 ms cadence is a pipeline configuration, not a data column. |
| Training data volume | **No** | Current export is ~8.3k rows; the plan targets $10^5$ episodes × $T = 50$ time steps. |

## 6. Summary

| Category | Required | Available | Gap |
| :--- | ---: | ---: | :--- |
| Telemetry input metrics | 10 | 3 (4 partial) | PDCP throughput, PRB utilization, transport blocks, modulation ratios |
| Control NCPs | 2 | 0 (1 partial) | RBG allocation; TXP only at cell level (telemetry) |
| A2C state (context) | 3 | 0 | $d$, $v$, $f^\dagger$ must be injected via simulated A1 |
| Success metrics | 5 | 0 (2 partial) | $\tau_e$, leftover bits, QoS satisfaction all require throughput |
| Training data volume | $10^5$ episodes | ~8.3k rows | Orders of magnitude short |

**Bottom line:** The current CU-CP exports cover the *channel-quality and congestion* dimension (SINR, active UEs, RSRP/RSRQ) but are missing the entire *resource-utilization and throughput* dimension (PRB, PDCP throughput, transport blocks, modulation) that the iter-3 plan depends on. Throughput ($R_{u,t}$) is now **more critical than in earlier iterations**: it is the basis of the native A2C reward ($\tau_e$), the leftover-bits KPI, and the QACM QoS-satisfaction objective. Closing the gap requires exporting DU/MAC-layer KPMs (PRB utilization, transport blocks, modulation ratios) and CU-UP KPMs (PDCP throughput) from ns-O-RAN, plus a longer simulation run to reach the target data volume.