# QoE Optimization (Use Case 4.4)

## Problem

Highly demanding 5G native applications — **cloud VR, industrial automation, online multiplayer gaming, connected vehicles** — are bandwidth-intensive and latency-sensitive. These applications are currently handled at a **best-effort basis** with no application-specific optimization.

The **semi-static QoS framework** fails to satisfy diversified QoE requirements that vary during an application's lifetime, especially given fluctuating radio transmission capability and dynamic application performance demands. Preloading static QoS profiles into RAN nodes is becoming unmanageable as the variety of mobile applications grows.

The O-RAN architecture enables a **user-centric, closed-loop QoE optimization** approach where:
- External systems (user applications) can request/request RAN behavior without preloaded static configuration
- Applications receive feedback on SLA compliance or RAN performance to self-optimize (e.g., TCP window adjustment, video coding rate)
- AI/ML models embedded in the RAN predict QoE, recognize traffic types, and enforce QoS in near-real-time

## Proposed Solution

O-RAN facilitates QoE optimization via a **"user RAN policy"** hosted at the Non-RT RIC (slow loop) or Near-RT RIC (fast loop). An rApp or xApp applies QoE configuration for specific users, slices, or 5QI flows in response to external requests or UE mobility, providing feedback including SLA information.

### QoE Connection Policy — Non-RT RIC (O1 + A1)

Operators configure RAN connection-level behaviors per network slice, 5QI flow per device, user type, or user ID via the Non-RT RIC. The **O1 interface** activates feature constellations across the network; the **A1 interface** maps feature sets to specific users/flows.

A feature constellation may include: carrier aggregation, traffic steering, mobility, power control, scheduling priority, and DRX. Applied as a user-centric policy via A1.

### QoE Performance Policy — Non-RT RIC (A1)

A continuous closed-loop including feedback from user applications:

1. External systems (or application-layer measurement reporting via **MeasReportAppLayer RRC containers** forwarded from RAN) provide QoE feedback to Non-RT RIC
2. Non-RT RIC translates this into a user-centric performance policy with specific latency, bitrate, and jitter targets
3. The A1 interface sends this policy to Near-RT RIC
4. Near-RT RIC enforces the policy on E2 nodes hosting the target UEs
5. Near-RT RIC reports RAN performance back to enable SLA measurement or application-level adjustment

### QoE Performance Policy — Near-RT RIC (fast loop)

Same usage patterns as Non-RT RIC, but the QoE performance policy is hosted at the **Near-RT RIC**. Only necessary for edge-hosted applications co-located with Near-RT RIC or CU-UP nodes. Input comes via vendor-specific interfaces or via forwarded MeasReportAppLayer RRC containers.

### AI/ML QoE Enhancements

Non-RT RIC constructs AI/ML models trained on SMO data, network-level measurements, and policies. Deployed in Near-RT RIC for inference to:
- Predict application/traffic types
- Predict QoE
- Estimate available bandwidth

### Radio Performance Analytics Exposure

Near-RT RIC exposes radio performance predictions to external applications via two paths:
- **Local NEF** (3GPP-defined) — for external apps
- **MEC app server** (ETSI MEC) — for co-located edge apps

External apps use this to execute logic control: TCP sending window adjustment, video coding rate selection, etc.

## State of the Art

- Research envisions QoE estimation from the application level to handle radio transmission uncertainty and improve resource efficiency
- QoE indices such as **VMOSS** (Video, Mobile, Opinion, Score) are used to map network QoS metrics to user-perceived experience levels
- O-RAN enables **proactive closed-loop optimization** — the way congested cells are detected and resources automatically allocated based on end-user experience is fundamentally improved over manual per-site parameter configuration
- Application-layer measurement reporting (RRC containers) provides a complementary path for QoE feedback with reduced latency

## Testbed Feasibility

The testbed has **no dedicated QoE E2SM**. QoE optimization relies on E2SM-KPM (measurement) and E2SM-RC (control).

### Measurements: E2SM-KPM (29/288 metrics, read-only)

**Relevant for QoE:**

| Metric | Relevance |
|--------|-----------|
| `DRB.RlcSduDelayDl/Ul`, `DRB.AirIfDelayUl` | Latency — core QoE metric |
| `DRB.UEThpDl/Ul` | Throughput/bandwidth |
| `DRB.RlcPacketDropRateDl` | Packet loss |
| `DRB.RlcSduTransmittedVolumeDL/UL` | Data volume |
| `DRB.PacketSuccessRateUlgNBUu`, `DRB.PdcpReordDelayUl` | PDCP success/reordering |
| `RRU.PrbUsedDl/Ul` | Resource contention |
| `RRC.ConnEstabSucc/Att` | Connection success rate |

**Critical gaps:**

| Priority | Missing | Impact |
|----------|---------|--------|
| **High** | CQI/RSRP/RSRQ per-UE (bug: reports UE 0 only) | Cannot assess per-UE link quality |
| **High** | DRB Setup/Release per-flow | No per-5QI flow metrics |
| **High** | MRO HO failures (69 types, 0 implemented) | No mobility QoE insight |
| **Medium** | Transport Block errors | No physical-layer success rate |

### Control: E2SM-RC (2 actions)

| Action | Scope | QoE relevance |
|--------|-------|---------------|
| Handover Control (CU-CP) | Intra-CU, target cell only | Mobility management |
| Slice PRB Quota (DU) | Per S-NSSAI min/max/dedicated ratio | Slice resource guarantees |

**Missing for QoE control:**

- Per-UE scheduling priority/weight
- 5QI QoS flow configuration (GBR, MBR, delay budget, error budget)
- DRX configuration
- Traffic steering / carrier aggregation
- Power control
- MCS adaptation

### What's Needed for a Viable QoE Testbed

1. **Fix KPM bugs** — CQI/RSRP/RSRQ per-UE, not UE 0
2. **Add DRB Setup/Release** per-5QI, per-flow
3. **Add per-UE scheduling priority** and 5QI flow configuration via E2SM-RC
4. **Build QoE xApp** — map KPM metrics to QoE indices (VMOSS-style), trigger E2SM-RC control commands, and expose analytics via simulated NEF/MEC interfaces
5. **Add MRO HO failure metrics** for mobility-aware QoE

## Future Directions

- **Explainable AI (XAI)** for auditable QoE optimization decisions
- **LLM integration** for intent-based networking — natural language QoE policies
- **Digital twins** (ns-3) for safe RL agent validation before live deployment
- **Unified conflict mitigation** between rApps and xApps optimizing QoE parameters simultaneously
- **Cross-domain QoE** — manage QoE across terrestrial, aerial (UAV), and satellite layers
- **Real-time stability analysis** of AI-in-the-loop QoE systems in high-mobility 6G
