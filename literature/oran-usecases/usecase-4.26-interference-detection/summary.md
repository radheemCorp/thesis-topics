# Interference Detection, Prediction and Optimization (Use Case 4.26)

## Problem

LTE and 5G networks use co-frequency networking due to limited radio resources, making **co-channel interference (CCI)** and adjacent channel interference the performance bottleneck. This is compounded by heterogeneous and ultra-dense networks. Traditional **Inter-Cell Interference Coordination (ICIC)** approaches exhibit several limitations:

- Resources allocated statically or in non-real time — no dynamic support, causing low utilization
- Dependent on ideal cell networking structures; performance degrades with complex topologies
- Allocation is cell-level, not UE-level or UE-group level
- Measurement data used only for post-interference analysis (non-real-time)

The RF environment is inherently **stochastic** — fading, noise, and mobility patterns are difficult to predict with traditional mathematical models. Model-driven approaches are often **NP-hard**, preventing real-time execution within sub-10ms 5G/6G requirements. Additional challenges:

- DL models lack **interpretability** (black box nature)
- AI models demand substantial compute power for resource-constrained edge devices
- Models are vulnerable to **inference attacks** (extracting signal data from outputs)
- **82% of research** relies on simulations that ignore hardware impairments and real-world signal distortions

## Proposed Solution

O-RAN architecture enables **multi-cell collaborative, real-time interference detection, prediction, and optimization** via open A1/E2/O1 interfaces, shifting from static rule-based avoidance to dynamic, data-driven suppression.

### Fast Loop — Near-RT RIC (A1/E2 interfaces)

Non-RT RIC sends interference policies (reference signal type, measurement thresholds, detection periods) via A1. Near-RT RIC obtains measurements via E2, constructs **interference graphs**, and generates real-time optimization policies:

- **Detection** — Reference signal configuration, PRB interference levels/patterns, and mMIMO beam analysis at UE and RAN level
- **Interference relationships** — Graphs between UEs, UE groups, RAN slices, PRBs based on scheduled resources
- **Optimization** — Radio resource coordination or active interference avoidance (Tx power, PRB blanking, carrier aggregation, beam forming/muting, per-slice resource separation)

### Slow Loop — Non-RT RIC (O1 interface)

Non-RT RIC generates policies for long-term traffic optimization via O1, handling slower trends.

### Interference Prediction for MCS Optimization

AI/ML models trained on historical interference data (prediction granularities: wideband/RB/TTI/frame) are deployed in Near-RT RIC for inference. Predictions replace outdated channel measurements to **optimize MCS** — adjusting SINR estimation or target BLER — maximizing efficiency while ensuring reliability.

## State of the Art

Research has transitioned traditional techniques into O-RAN as **xApps and rApps**:

- **DL architectures** (CNNs, RNNs, Autoencoders) outperform traditional filters (Zero-forcing, MMSE) by **>40% in SINR gains**
- **Multi-cell collaborative detection** constructs interference graphs for cross-cell resource coordination
- **Integrated SON functions** (MLB, MRO) operate as intelligent applications in live network trials (autonomous actions every 15 min)
- **Lightweight AI** (pruning, quantization, Knowledge Distillation) achieves inference within the 10ms–1s window
- **Federated Learning** enables decentralized, privacy-preserving collaboration — training interference models without sharing raw signal data

## Future Directions

- **Explainable AI (XAI)** for auditable, compliant models
- **LLM integration** for intent-based networking (natural language policies)
- **Digital twins** (ns-3) for safe RL agent validation before live deployment
- **Unified conflict mitigation** between rApps and xApps optimizing the same parameters
- **Cross-domain management** across terrestrial, aerial (UAV), and satellite layers
- **Real-time stability analysis** of AI-in-the-loop systems to prevent ping-ponging in 6G

## Testbed Feasibility Analysis

The testbed implements **E2SM-KPM**, a read-only monitoring service on the E2 interface between Near-RT RIC (consumer) and DU/CU-UP/CU-CP (providers). Near-RT RIC subscribes to periodic reports via 5 report styles:

| Style | Scope | What it delivers |
|-------|-------|-----------------|
| 1 | E2-node | All 3 providers — DU, CU-UP, CU-CP at node level |
| 2 | Per UE | DU-level only |
| 3 | Per UE (conditional) | Triggers only when conditions are met |
| 4 | UE group | Common conditions for multiple UEs |
| 5 | UE group | Multi-UE at group level |

**29 of ~288 spec metrics implemented** (~10%):

- **DU (18):** PRB utilization (6), DRB throughput/delay/volume/drops (7), RACH (1), CQI/RSRP/RSRQ (3 — all report UE 0 only, known bug)
- **CU-CP (9):** RRC connection setup/success/fail/re-establishment counts + mean/max active connections
- **CU-UP (2):** PDCP reordering delay, UL success rate

KPM is **read-only** — no control-service implementation exists for interference command/optimization.

### Gaps for interference detection

The current catalog has gaps that matter for interference-specific work:

**Must have (already implemented):** PRB usage/availability (`RRU.PrbUsedDl/Ul`, `RRU.PrbAvailDl/Ul`), per-UE throughput (`DRB.UEThpDl/Ul`), packet drops (`DRB.RlcPacketDropRateDl`), delay (`DRB.RlcSduDelayDl`).

**Should add — missing but defined in spec:**

| Priority | Metric | Spec count | Implemented |
|----------|--------|-----------|-------------|
| High | Mobility/HO failures (MRO) | 69 | 0 |
| High | CQI per-UE (currently UE 0 only) | 20 | 3 (bug) |
| High | RSRP/RSRQ per-UE (mis-reported as PUSCH SNR) | in CQI group | 2 (bug) |
| High | Transport Block errors | 10 | 0 |
| Medium | Beam/MIMO metrics | 20 | 0 |
| Medium | DRB Setup/Release | 13 | 0 |
| Medium | 5QI call duration | 4 | 0 |
| Low | SM (PDU Session) | 5 | 0 |
| Low | GTP/N3 network delay | 4 | 0 |

Handover failures, per-UE CQI/RSRP, and transport block errors are the highest-impact additions needed to make the testbed viable for interference detection, as they directly measure interference symptoms on the air interface.

