# PRODUCT

**What**: modular O-RAN Near-RT-RIC research testbed reproducing the QACM (QoS-Aware Conflict Mitigation) scenario. Independent surrogate xApps (CCO throughput-max, ES power-min, future MRO/MLB) issue conflicting control requests over shared ICPs `(p1, p2)`; the CMC returns a QoS-aware compromise.

**Why**: answer how independently developed SON xApps can share RAN control while preserving objectives, QoS/SLA, and near-RT constraints — without data sharing between xApps.

**Users**: thesis/research engineers reproducing QACM (2405.07324v2); contributors adding xApps.

**Success**: scalar QACM heuristic + joint 2-D `(p1, p2)` bargaining, reproducible synthetic datasets, modular components, >80% test coverage.

**Non-goals**: real E2/RIC integration, implicit conflict types, continuous/MILP production optimizers (brute force only as test oracle).
