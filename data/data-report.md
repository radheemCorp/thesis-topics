# Data Report: ns-O-RAN CU-CP Telemetry Exports

This report documents the contents of the three CSV exports in `data/`, describes every parameter, and maps them against the reference parameter sheet in `literature/testbed-info/ns3/available-params.md`.

## 1. Dataset Overview

| File | Rows (excl. header) | Scope | Source |
| :--- | ---: | :--- | :--- |
| `cucp_cell_report.csv` | 270 | Per-cell aggregates | CU-CP (L3 RRC) |
| `cucp_neighbor_report.csv` | 2,502 | Per (cell, neighbor) pair | CU-CP (L3 RRC) |
| `cucp_ue_report.csv` | 5,496 | Per (UE, neighbor) pair | CU-CP (L3 RRC) |

All three files share the same reporting cycle keyed by `EntryIndex` and `Timestamp`:

* **Report cycles:** 225 unique `EntryIndex` values (3–272), each representing one E2SM-KPM report interval.
* **Unique timestamps:** 88. The bulk of reports are spaced ~1 ms apart (not the nominal 100 ms), with one large gap between the first sample (`80 01:33:00.850`) and the rest (`80 04:21:33.x`). The leading `80` is the ns-3 simulation time (seconds); the trailing value is the wall-clock time.
* **Topology:** 10 serving cells (`ServingCellID` ∈ {2, 5, 7, 8, 9, 11, 12, 13, 14, 15}), 14 distinct neighbor cells, 49 distinct UEs (`UE_ID` 00001–00070, sparse).
* **Cell identity:** `CellIdentity` uses the `131-<gNBID><CellID>` format (e.g. `131-13335000000`); `CellObjectID` is constant `NRCellCU`.

## 2. File-by-File Parameter Reference

### 2.1 `cucp_cell_report.csv` — Per-Cell Aggregates

| Column | Type | Range (observed) | Meaning |
| :--- | :--- | :--- | :--- |
| `Index` | int | 1 | Report index (constant in this export). |
| `EntryIndex` | int | 3–272 | Report cycle ID; joins to the other two files. |
| `Timestamp` | str | `80 01:33:00.850` … `80 04:21:33.581` | ns-3 sim time + wall-clock time of the report. |
| `ServingCellID` | int | 2–15 | Serving cell identifier (PCI). |
| `CellIdentity` | str | 10 values | Global cell identity `131-<gNBID><CellID>`. |
| `CellObjectID` | str | `NRCellCU` | O-RAN object type (CU-CP cell). |
| `Num_Active_UEs` | int | 0–4 | Number of UEs with active data transmission in the cell → maps to $Z_{c,t}$ (Active User Count). |
| `Avg_Serving_RSRP` | float | 0–97 | Cell-average Reference Signal Received Power (dBm) of the serving cell. |
| `Avg_Serving_RSRQ` | float | 0–127 | Cell-average Reference Signal Received Quality (dB). |
| `Avg_Serving_SINR` | float | 0–67 | Cell-average Signal-to-Interference-plus-Noise Ratio (dB) → maps to $\text{SINR}_{u,c,t}$ aggregated to cell level. |
| `Avg_Serving_TxPower` | float | 0, 30 | Cell-average transmission power (dBm). |
| `Num_Neighbor_Cells` | int | 0–13 | Number of neighbor cells reported for this serving cell. |
| `Neighbor_Avg_RSRP` | float | 0 (all zero) | Average RSRP across neighbor cells — **not populated in this export**. |
| `Neighbor_Avg_RSRQ` | float | 0 (all zero) | Average RSRQ across neighbor cells — **not populated in this export**. |
| `Neighbor_Avg_SINR` | float | 0–7.125 | Average SINR across neighbor cells (dB). |
| `Avg_DynLoad` | float | 0 (all zero) | Dynamic load indicator — **not populated in this export**. |
| `Avg_DynMobility` | float | 0–32 | Dynamic mobility indicator (handover/mobility activity). |

### 2.2 `cucp_neighbor_report.csv` — Per (Cell, Neighbor) Pair

| Column | Type | Range (observed) | Meaning |
| :--- | :--- | :--- | :--- |
| `Index` | int | 1–13 | Per-cycle row index (neighbor rank). |
| `EntryIndex` | int | 3–272 | Report cycle ID; joins to the other files. |
| `Timestamp` | str | — | Report time (same format as above). |
| `ServingCellID` | int | 2–15 | Serving cell (PCI). |
| `NeighborCellID` | int | 2–15 | Neighbor cell (PCI) → maps to $c \in C'_{u,t}$ (candidate neighbor cells). |
| `Neighbor_Avg_RSRP` | float | 0 (all zero) | Neighbor-cell average RSRP — **not populated**. |
| `Neighbor_Avg_RSRQ` | float | 0 (all zero) | Neighbor-cell average RSRQ — **not populated**. |
| `Neighbor_Avg_SINR` | float | 0–36 | Neighbor-cell average SINR (dB). |

### 2.3 `cucp_ue_report.csv` — Per (UE, Neighbor) Pair

| Column | Type | Range (observed) | Meaning |
| :--- | :--- | :--- | :--- |
| `Index` | int | 1–32 | Per-cycle row index (UE/neighbor rank). |
| `EntryIndex` | int | 3–272 | Report cycle ID; joins to the other files. |
| `Timestamp` | str | — | Report time. |
| `ServingCellID` | int | 2–15 | Serving cell (PCI) of the UE. |
| `CellIdentity` | str | 10 values | Global cell identity of the serving cell. |
| `CellObjectID` | str | `NRCellCU` | O-RAN object type. |
| `UE_ID` | str | 00001–00070 (49 unique) | UE identifier → maps to $u$ (UE ID). |
| `Serving_PCI` | int | 2–15 | Physical Cell ID of the serving cell. |
| `Neighbor_PCI` | int | 2–15 | Physical Cell ID of the neighbor cell being measured. |
| `RSRP` | float | 0 (all zero) | UE-level RSRP toward the neighbor — **not populated**. |
| `RSRQ` | float | 0 (all zero) | UE-level RSRQ toward the neighbor — **not populated**. |
| `SINR` | float | 0–59 | UE-level SINR toward the neighbor (dB) → maps to $\text{SINR}_{u,c,t}$. |
| `TxPower` | float | 0 (all zero) | UE transmit power — **not populated**. |

## 3. Mapping to the Reference Parameter Sheet

| Reference param (available-params.md) | Present in data? | Where |
| :--- | :--- | :--- |
| $u$ (UE ID) | Yes | `cucp_ue_report.csv` → `UE_ID` |
| $c \in C'_{u,t}$ (Cell IDs) | Partial | `ServingCellID` / `NeighborCellID` / `Neighbor_PCI` |
| $\text{SINR}_{u,c,t}$ | Yes | `cucp_ue_report.csv` → `SINR`; cell-level in `Avg_Serving_SINR` / `Neighbor_Avg_SINR` |
| $\text{RSRP}_{u,c,t}$ | Partial | Cell-level only (`Avg_Serving_RSRP`); UE/neighbor RSRP all zero |
| $R_{u,t}$ (PDCP throughput) | **No** | Not exported (CU-UP data absent) |
| $\text{PRB}_{c,t}$ (PRB utilization) | **No** | Not exported (DU/MAC data absent) |
| $Z_{c,t}$ (Active UEs) | Yes | `cucp_cell_report.csv` → `Num_Active_UEs` |
| $P_{c,t}$ (Transport blocks) | **No** | Not exported (DU/MAC data absent) |
| $p^{QPSK/16QAM/64QAM}_{c,t}$ | **No** | Not exported (DU/MAC data absent) |
| $k(c_{u,t})$ (Handover penalty) | Indirect | `Avg_DynMobility` (mobility activity) is the closest proxy; penalty must be computed |

## 4. Data Quality Observations

1. **Missing DU/MAC-layer metrics:** PRB utilization, transport-block counts, and modulation ratios are absent — these come from the DU (MAC layer) and are not in these CU-CP exports.
2. **Missing CU-UP throughput:** No PDCP-layer throughput column; the reference sheet's $R_{u,t}$ must come from a separate CU-UP report.
3. **Unpopulated columns:** `Neighbor_Avg_RSRP`, `Neighbor_Avg_RSRQ`, `Avg_DynLoad`, UE-level `RSRP`, `RSRQ`, and `TxPower` are all zero in this export.
4. **Reporting cadence:** Reports are ~1 ms apart rather than the nominal 100 ms; only 88 unique timestamps across 225 cycles, with a large wall-clock gap after the first sample.
5. **Sparse UE set:** 49 UEs across 10 cells; `UE_ID` values are non-contiguous (00001–00070).
6. **SINR is the richest signal:** It is the only quality metric populated at all three granularities (UE, cell, neighbor) and is the primary usable feature for the A2C/CNN input vector.