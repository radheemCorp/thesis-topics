# O-RAN Testbed Limitations

This document catalogues every known limitation of the consolidated O-RAN
testbed (Open5GS 5GC + ORAN-SC near-RT RIC + OCUDU/srsRAN gNB). It covers
interfaces, E2 service models, metrics, 5GC functions, hardware constraints,
and missing O-RAN architectural components. Each limitation is annotated with
its impact on use-case feasibility and potential future work to close the gap.

---

## 1. E2 Interface — Supported Service Models

Source: ORAN-SC near-RT RIC documentation and `src/ocudu/configs/gnb_zmq.yml`.

### 1.1 E2SM-RC (RAN Control)

| Aspect | Status | Detail |
|---|---|---|
| Control Service Style 1 — Radio Bearer Control | **Not supported** | Cannot modify DRB configuration, bearer setup/teardown |
| Control Service Style 2 — Radio Resource Allocation | **Supported** | Slice-level and UE-level PRB quota (min/max/dedicated ratio) via action 6 |
| Control Service Style 3 — Connected Mode Mobility Control | **Not supported** | Cannot trigger handover or conditioning from the RIC |
| Control Service Style 4 — UE Context Management | **Not supported** | Cannot modify UE context at the gNB |
| Control Service Style 5 — RRC State Transition Control | **Not supported** | Cannot move UEs between RRC_IDLE / RRC_CONNECTED / RRC_INACTIVE |
| Control Service Style 6 — Reporting (E2SM-RC service) | **Not supported** | No event-triggered reporting from E2SM-RC |
| Control Service Style 7 — MIMO Beamforming Control | **Not supported** | Cannot configure beamforming weights, beam muting, or spatial multiplexing |
| Control Service Style 8 — Power Control | **Not supported** | Cannot adjust UE or cell transmit power |
| E2SM-RC subscription (RIC Subscription via Style 1) | **Not supported** | Only control (write) is available; no subscription-based reporting from E2SM-RC |

**Impact:** Only PRB allocation/reallocation is controllable. Use cases requiring
power control, beamforming, mobility, bearer configuration, or RRC state
transitions cannot be implemented.

### 1.2 E2SM-KPM (Key Performance Metrics)

| Aspect | Status | Detail |
|---|---|---|
| Report Service Style 1 — Cell-level aggregate | **Supported** | All UEs combined into a single report |
| Report Service Style 2 — Per-UE (periodic) | **Supported** | Single UE identified by `gNB-CU-UE-F1AP-ID` |
| Report Service Style 3 — Per-UE (event-triggered) | **Supported** | Matching conditions on UL RSRP (dummy condition) |
| Report Service Style 4 — Per-UE group | **Supported** | Matching conditions on UL RSRP (dummy condition) |
| Report Service Style 5 — Multiple UEs | **Supported** | Requires at least 2 UE IDs |
| Monitoring period minimum | **1 second** | Cannot request sub-second granularity |

### 1.3 E2SM-CCC (Common Control Channel)

| Aspect | Status | Detail |
|---|---|---|
| E2SM-CCC enabled in gNB config | **Disabled** (`e2sm_ccc_enabled: false`) | Enabling it causes the srsRAN DU to fail E2 setup, preventing any DU node from registering |
| E2SM-CCC module in xApp framework | **Implemented** (Style 2, O-RRM Policy Ratio) | Code exists in `lib/e2sm_ccc_module.py` but cannot be used in production due to gNB crash |

**Impact:** CCC is non-functional. The xApp library is available for
development/testing but not for live operation.

---

## 2. E2SM-KPM — Exposed Metrics

The gNB exposes only **9 metrics** via E2:

### 2.1 ORAN-Defined Metrics (6)

| Metric | Description |
|---|---|
| `DRB.UEThpDl` | DL throughput per UE (kbps) |
| `DRB.UEThpUl` | UL throughput per UE (kbps) |
| `DRB.RlcPacketDropRateDl` | DL RLC packet drop rate |
| `DRB.PacketSuccessRateUlgNBUu` | UL RLC packet success rate |
| `DRB.RlcSduTransmittedVolumeDL` | DL RLC SDU transmitted volume |
| `DRB.RlcSduTransmittedVolumeUL` | UL RLC SDU transmitted volume |

### 2.2 Dummy / Placeholder Metrics (3)

| Metric | Description | Note |
|---|---|---|
| `CQI` | Channel Quality Indicator | Dummy value; may be removed in future releases |
| `RSRP` | Reference Signal Received Power | Dummy value; may be removed in future releases |
| `RSRQ` | Reference Signal Received Quality | Dummy value; may be removed in future releases |

### 2.3 Metrics NOT Available

The following metrics are defined in O-RAN specifications but **not exposed**
by the srsRAN/OCUDU gNB:

| Category | Missing Metrics |
|---|---|
| **Scheduling** | `DRB.UschedulTimeDl`, `DRB.UschedulTimeUl`, `RRC.ConnEstabAtt`, `RRC.ConnEstabSucc` |
| **Mobility** | `HOAttempt`, `HOFailure`, `HOExec`, `RACHAttempt`, `RACHSuccess` |
| **Beam** | `BeamRSRP`, `BeamRSRQ`, `BeamSINR`, all massive MIMO beam metrics |
| **Slice** | `DRB.SliceThpDl`, `DRB.SliceThpUl` (slice-level aggregates) |
| **Latency** | `DRB.RTTimeDl`, `DRB.RTTimeUl` (round-trip time) |
| **Error** | `DRB.RlcRetxRateDl`, `DRB.PdcpRetxRateDl` |
| **Power** | `TxPower`, `RxPower`, all power control metrics |
| **RRC** | `RRC.ConnMean`, `RRC.ConnMax`, `RRC.ConnEstabFail` |
| **PRB** | `PRB.UsedDl`, `PRB.UsedUl`, `PRB.AvailDl`, `PRB.AvailUl` (total/available PRB usage) |
| **QoS** | `DRB.QoSDelayDl`, `DRB.QoSBERDl`, `DRB.QoSPLR` |

**Impact:** Use cases requiring beam management, mobility analytics, PRB
utilization monitoring, latency measurement, or detailed QoS monitoring
cannot be implemented with the available metrics.

---

## 3. O-RAN Interfaces — Not Deployed

### 3.1 Interfaces Present in the Testbed

| Interface | Status | Implementation |
|---|---|---|
| E2 (SCTP :36421) | **Working** | ORAN-SC e2term ↔ srsRAN gNB |
| N2 (NGAP, SCTP :38412) | **Working** | gNB ↔ Open5GS AMF |
| N3 (GTP-U, UDP :2152) | **Working** | gNB ↔ Open5GS UPF |
| N6 | **Working** | UPF → internet (NAT) |
| O1 (metrics) | **Partial** | Telegraf scrapes gNB JSON metrics WS :8001; not a full O1 NRM implementation |

### 3.2 Interfaces NOT Deployed

| Interface | Purpose | Impact |
|---|---|---|
| **A1** | Non-RT RIC → Near-RT RIC policy interface | No standardized policy delivery; must simulate via HTTP or shared DB |
| **O1** (full) | SMO ↔ managed elements (configuration, alarms, performance) | No centralized configuration management; gNB config is static YAML |
| **O2** | SMO ↔ O-Cloud (resource lifecycle) | No O-Cloud, no dynamic resource provisioning |
| **O3** | SMO ↔ SMO (federation) | No multi-operator federation |
| **Open Fronthaul (M-Plane)** | SMO ↔ O-RU management | No O-RU; ZMQ or USRP B210 only |
| **Open Fronthaul (U-Plane)** | DU ↔ O-RU user data | No O-RU; all RF is virtual (ZMQ) or SDR (UHD) |
| **Open Fronthaul (C-Plane)** | DU ↔ O-RU scheduling | No O-RU |
| **R1** | Non-RT RIC ↔ SMO | No SMO deployed |
| **Y1** | O-Cloud ↔ external orchestrator | No O-Cloud |

**Impact:** The testbed is a Near-RT RIC-only deployment. Any use case
requiring Non-RT RIC ↔ Near-RT RIC communication via A1, SMO-mediated
configuration, or O-Cloud resource management cannot use standardized
interfaces.

---

## 4. 5G Core (Open5GS) Limitations

### 4.1 Deployed NFs

| NF | Status | Notes |
|---|---|---|
| AMF | **Working** | NGAP, SBI |
| SMF | **Working** | PFCP, GTP-C |
| UPF | **Working** | GTP-U, N6 egress |
| UDM / UDR | **Working** | Subscriber data in MongoDB |
| AUSF | **Working** | Authentication |
| NRF | **Working** | Service discovery |
| SCP | **Working** | Service communication proxy |
| PCF | **Working** | Policy control (basic) |
| NSSF | **Working** | Network slice selection (basic) |
| BSF | **Working** | Binding support function |

### 4.2 NFs NOT Deployed or Disabled

| NF | Status | Impact |
|---|---|---|
| **NWDAF** | **Not present** | No network data analytics function; cannot export RAN analytics to 5GC |
| **SEPP** | **Disabled** (`no_sepp: true`) | No inter-PLMN signaling proxy |
| **SMSF** | **Not present** | No SMS over NAS |
| **LMF** | **Not present** | No location management; cannot support positioning use cases |
| **EASF** | **Not present** | No edge application support |
| **CHF** | **Not present** | No charging function |
| **UDSF** | **Not present** | No unstructured data storage |

### 4.3 Network Slicing Limitations

| Aspect | Status | Detail |
|---|---|---|
| Single slice configured | SST=1 only | No multi-slice isolation demonstrated |
| NSSF basic slice selection | **Working** | Selects slice based on subscriber data |
| Slice-level QoS enforcement | **Not working** | No slice-specific PRB isolation at gNB (single slice) |
| Slice-level monitoring | **Not available** | No slice-specific KPM metrics exposed |
| Multiple SSTs/SDs | **Not configured** | `update_slice.sh` can change SST/SD but only one slice active at a time |

**Impact:** Use cases requiring multi-slice isolation, slice-level SLA
assurance, or inter-slice resource optimization cannot be fully implemented.

### 4.4 Subscriber Management

| Aspect | Status |
|---|---|
| Subscriber provisioning | `open5gs-dbctl` (CSV → MongoDB) |
| Authentication | SIM-based (USIM in srsUE or soft-SIM in ZMQ) |
| QoS profiles | Basic 5QI mapping (not dynamically adjustable via O-RAN interfaces) |
| Policy control | PCF present but not integrated with RIC |

---

## 5. gNB (OCUDU / srsRAN) Limitations

### 5.1 Deployment Model

| Aspect | Status | Detail |
|---|---|---|
| Single cell | PCI 1, Band 3, 20 MHz | No multi-cell, no inter-cell interference |
| Single gNB | One DU + CU-CP + CU-UP | No multi-gNB coordination |
| Fronthaul split | 7.2x (Open Fronthaul) | Not a real split; all processing in one container |
| O-RU | **Not present** | ZMQ (virtual RF) or USRP B210 (SDR) |

### 5.2 Radio Configuration

| Aspect | Status | Detail |
|---|---|---|
| Bandwidth | 20 MHz fixed | Cannot dynamically adjust |
| SCS | 15 kHz fixed | Cannot switch to 30/60/120 kHz |
| MIMO layers | **1 (SISO)** | No 2x2, 4x4, or massive MIMO |
| Beamforming | **None** | No GoB, no codebook, no beam management |
| Carrier Aggregation | **Not supported** | Single carrier only |
| Duplex mode | TDD | FDD not configured |

### 5.3 Scheduler

| Aspect | Status | Detail |
|---|---|---|
| DL scheduler | srsRAN built-in | Not externally configurable via E2 |
| UL scheduler | srsRAN built-in | Not externally configurable via E2 |
| PRB granularity | **Cell-level only** | No per-slice or per-UE PRB accounting exposed |
| Scheduling algorithm | Round-robin / proportional fair | Not adjustable |
| DRX | **Not configured** | No discontinuous reception for UEs |
| SPS | **Not configured** | No semi-persistent scheduling |

### 5.4 Mobility

| Aspect | Status | Detail |
|---|---|---|
| Handover | **Single cell only** | No neighbor cells, no handover possible |
| RRC state transitions | Basic | Idle ↔ Connected only |
| Measurement reports | **Not exposed via E2** | No A1/A2/B1 event reporting |
| Measurement gaps | **Not configured** | No inter-frequency measurement |

### 5.5 Features NOT Supported

| Feature | Status | Impact |
|---|---|---|
| PDCP duplication | Not available | No ultra-reliability enhancement |
| Ethernet Header Compression (EHC) | Not available | No industrial IoT optimization |
| SDAP | Not available | No QoS flow to DRB mapping |
| DSS (Dynamic Spectrum Sharing) | Not available | 5G SA only; no 4G coexistence |
| DTX (Discontinuous Transmission) | Not available | No power saving via DTX |
| Advanced Sleep Modes | Not available | No energy saving via ASM |

---

## 6. Hardware Limitations

| Aspect | Status | Detail |
|---|---|---|
| Compute | Single host machine | No distributed O-Cloud |
| RF (ZMQ) | Virtual, no real RF | No over-the-air propagation, fading, or interference |
| RF (UHD/USRP B210) | Single SDR | One antenna, 2x2 MIMO max (but not configured for MIMO) |
| Real UEs | **Not available** | Only srsUE (ZMQ) or single COTS phone (UHD) |
| O-RU | **Not available** | No remote radio head |
| BBU pooling | **Not available** | No centralized BBU pool |
| Multi-vendor | **Not available** | Single vendor (srsRAN/OCUDU) throughout |

---

## 7. AI/ML Framework Limitations

| Aspect | Status | Detail |
|---|---|---|
| InfluxDB 2 datastore | **Ready** | AIMLFW-compatible; KPM data lands continuously |
| Feature group | **Deployed** | No AIMLFW instance running |
| Data extraction | **Deployed** | No Cassandra feature store |
| Model training (Kubeflow) | **Deployed** | No ML training pipeline |
| Model serving (KServe) | **Deployed** | No inference endpoint |
| Model artifact | **Not available** | No pre-trained models |

**Impact:** The data pipeline to feed an ML framework exists, but the framework
itself must be deployed externally or simulated with a standalone Python
process.

---

## 8. Non-RT RIC Limitations

| Aspect | Status | Detail |
|---|---|---|
| Non-RT RIC platform | **Not deployed** | No rApp platform, no A1 interface |
| rApp hosting | **Not available** | Must run as standalone Python process |
| A1 interface | **Not available** | No standardized policy delivery to Near-RT RIC |
| rApp → Near-RT RIC communication | **Must simulate** | HTTP REST, shared MongoDB, or Kafka |
| Non-RT RIC data analytics | **Not available** | No rApp framework for long-term analytics |
| Policy management | **Not available** | No A1 policy types, no policy lifecycle |

---

## 9. Telemetry Pipeline Limitations

| Aspect | Status | Detail |
|---|---|---|
| KPM xApp → Kafka | **Working** | Single producer, JSON on `xapp-metrics` topic |
| Kafka → InfluxDB 3 | **Working** | Grafana feed |
| Kafka → InfluxDB 2 | **Working** | AIMLFW-compatible feed |
| Kafka → MongoDB | **Working** | Non-RT RIC rApp feed |
| gNB JSON metrics → Telegraf → InfluxDB 3 | **Working** | Operational monitoring |
| Additional xApps publishing | **Not wired** | Only KPM xApp publishes; new xApps need manual Kafka integration |
| Metric deduplication | **None** | If multiple xApps publish, duplicates may occur |
| Backpressure handling | **Basic** | No Kafka consumer lag monitoring |

---

## 10. Summary — Use Case Feasibility Matrix

| Use Case | Feasible? | Blocking Limitation |
|---|---|---|
| UC 4.1 — Dynamic HO Management | **No** | Single cell, no handover, no mobility control |
| UC 4.2 — UAV Resource Allocation | **No** | No UAV infrastructure, no beam control |
| UC 4.3 — UAV Application Scenarios | **No** | No UAV, no edge compute platform |
| UC 4.4 — QoS Optimization | **Partial** | KPM + PRB control available; no app feedback loop |
| UC 4.5 — Traffic Steering | **No** | Single RAT, single cell, no multi-access |
| UC 4.6 — Massive MIMO Optimization | **No** | No massive MIMO hardware, no beamforming |
| UC 4.7 — RAN Sharing | **No** | Single operator, no O-Cloud, no remote E2 |
| UC 4.8 — QoS Resource Optimization | **Yes** | KPM + E2SM-RC Style 2 + rApp simulation |
| UC 4.9 — RAN Slice SLA Assurance | **Partial** | Single slice, no slice-level KPM; PRB control possible |
| UC 4.10 — Multi-vendor Slices | **No** | Single vendor |
| UC 4.11 — Dynamic Spectrum Sharing | **No** | 5G SA only, no 4G, no MAC scheduler control |
| UC 4.12 — NSSI Resource Allocation | **Partial** | Single slice; PRB control possible but no slice isolation |
| UC 4.13 — Indoor Positioning | **No** | No LMF, no SRS positioning data via E2 |
| UC 4.14 — MU-MIMO Grouping | **No** | No massive MIMO |
| UC 4.15 — Signalling Storm Protection | **Partial** | Can generate load; no E2 control for throttling |
| UC 4.16 — Congestion Prediction | **Yes** | KPM + ML pipeline + E2SM-RC Style 2 |
| UC 4.17 — Industrial IoT | **No** | No PDCP duplication, no EHC |
| UC 4.18 — BBU Pooling | **No** | No O-Cloud, no BBU pool |
| UC 4.19 — Integrated SON | **No** | Single vendor, limited E2SM-RC |
| UC 4.20 — Shared O-RU | **No** | No O-RU, no multi-O-DU |
| UC 4.21 — Network Energy Saving | **No** | No sleep modes, no PA power control |
| UC 4.22 — MU-MIMO Optimization | **No** | No MU-MIMO |
| UC 4.23 — Sharing RIC Data with Core | **No** | No NWDAF, no R1 interface |
| UC 4.24 — Industrial Vision SLA | **No** | No industrial cameras, no MES |
| UC 4.26 — Interference Optimization | **No** | Single cell, no beamforming, no power control |
| UC 4.27 — CCIN | **No** | No O-Cloud, no Y1 interface |

---

## 11. Future Work — Closing the Gaps

### High Priority (enables more use cases)

| Gap | What to Add | Enables |
|---|---|---|
| A1 interface | Deploy A1 policy agent or simulate via HTTP | All Non-RT RIC → Near-RT RIC use cases |
| Multiple slices | Configure SST=1 + SST=2 in Open5GS and gNB | UC 4.8, 4.9, 4.12 |
| PRB utilization metrics | Add `PRB.UsedDl/AvailDl` to gNB E2 exposure | Congestion detection, resource optimization |
| NWDAF | Deploy Open5GS NWDAF or custom analytics NF | UC 4.23, core-RAN analytics sharing |

### Medium Priority (improves fidelity)

| Gap | What to Add | Enables |
|---|---|---|
| E2SM-RC Style 1 or 3 | Extend srsRAN E2 agent | Bearer control, mobility control |
| Multiple cells | Deploy second gNB container | Handover, inter-cell interference |
| AIMLFW or standalone ML | Deploy Kubeflow/KServe or use scikit-learn | UC 4.16, AI-driven optimization |
| Real UEs | Use COTS phones with USRP B210 | Realistic traffic patterns, mobility |
| Full O1 NRM | Deploy O1 managed function | Centralized configuration, alarms |

### Low Priority (nice-to-have)

| Gap | What to Add | Enables |
|---|---|---|
| Massive MIMO | srsRAN with MU-MIMO or commercial gNB | UC 4.6, 4.14, 4.22 |
| O-Cloud | Kubernetes-based O-Cloud deployment | UC 4.7, 4.18, 4.20, 4.27 |
| Multi-vendor | Add second gNB vendor (e.g., OpenAirInterface) | UC 4.10, 4.19 |
| 4G LTE | Deploy EPC + eNB alongside 5GC + gNB | UC 4.11 (DSS) |
| E2SM-CCC | Fix srsRAN CCC crash, enable in gNB config | CCC-based control use cases |
