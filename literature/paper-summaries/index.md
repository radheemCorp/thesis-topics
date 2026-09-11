# xApp Conflict Mitigation — Approaches Index

## Reinforcement Learning (RL)-Based Mitigation

Learns control / arbitration policies from interaction instead of fixing priorities or thresholds offline. Best suited when conflicts are context-dependent and optimal trade-offs shift with traffic, mobility, and load. Cost: needs training data / episodes and (for cooperative variants) joint training or action sharing.

### Team Learning / Cooperative Multi-Agent Learning

Trains xApps jointly so they learn to cooperate; actions or policies are shared during training. **Distinction vs. scheduler/distillation:** conflicts are avoided inside the learned policies themselves, but this violates xApp immutability and multi-vendor independence (all xApps must be co-trained).

| Paper | File | Method / focus |
|---|---|---|
| Zhang et al., Team Learning-Based Resource Allocation for O-RAN (ICC 2022) | `../material/xapp-conflict-mitigation/2201.07385v1.pdf` | DQN team learning; xApps exchange intended actions, joint resource/power optimization. Canonical RL baseline cited by all 5 survey papers. |
| Iturria-Rivera et al., Multi-Agent Team Learning in Virtualized O-RAN (Sensors 2022) | `../material/RL-based-mitigation/sensors-22-05375.pdf` | TMADRL extension to multiple xApps controlling different RAN parameters; vs. Zhang: more agents / parameters, higher coordination overhead. |

### Distillation / Consolidation

Distills multiple teacher xApps into a single student controller. **Distinction vs. team learning:** no runtime arbitration — conflicts disappear because only one policy executes; but depends on teacher quality, needs offline data, and loses modularity (re-distill on change).

| Paper | File | Method / focus |
|---|---|---|
| Erdol et al., xApp Distillation: AI-based Conflict Mitigation in B5G O-RAN (2024) | `../material/RL-based-mitigation/2407.03068v1.pdf` | DQN student learns from multiple teacher xApps; aggregates experience instead of discarding losing actions. |

### Intent-Based MARL and DT-Enhanced RL

Uses operator intent or a digital twin to guide RL. **Distinction vs. pure team learning:** intent version degrades lower-priority objectives proportionally; DT version trains/validates against twin predictions rather than live-only feedback.

| Paper | File | Method / focus |
|---|---|---|
| Perepu et al., Intent-based MARL for Service Assurance (GLOBECOM 2022) | `../material/RL-based-mitigation/Intent-based_multi-agent_reinforcement_learning_for_service_assurance_in_cellular_networks.pdf` | Intent-defined priorities drive MARL resource allocation. |
| He et al., Digital Twin-Enhanced RL for Intelligent xApps Management (IEEE IoT Mag. 2025) | `../material/RL-based-mitigation/Digital_Twin-Enhanced_Reinforcement_Learning_for_Intelligent_xApps_Management_in_O-RAN_Systems.pdf` | DT + MARL for IoT-enabled O-RAN xApp management; twin as training/evaluation environment. |

### RL Foundations and Surveys

Background methods referenced by the scheduler and team-learning papers. **Distinction:** not O-RAN specific — provides the algorithms (REINFORCE → actor-critic → A3C/A2C, DQN overviews).

| Paper | File | Method / focus |
|---|---|---|
| Williams, REINFORCE (Machine Learning 1992) | `../material/RL-based-mitigation/BF00992696.pdf` | Policy-gradient foundation used by A2C scheduler derivation. |
| Mnih et al., Asynchronous Methods for Deep RL (2016) | `../material/RL-based-mitigation/1602.01783v2.pdf` | A3C; synchronous variant A2C trains the xApps + scheduler in `2504.06867v3`. |
| Xu et al., A Comprehensive Discussion on DRL (CISCE 2021) | `../material/RL-based-mitigation/A_Comprehensive_Discussion_on_Deep_Reinforcement_Learning.pdf` | DRL survey / background. |

## Game-Theoretic and QoS-Aware Optimization

Formulates mitigation as bargaining / constrained optimization over a shared parameter. No joint training and no data sharing — only KPI utilities per candidate value are needed. Best when per-xApp QoS thresholds (SLAs) must be satisfied rather than just maximizing total throughput.

### Nash / EG Bargaining (Baseline)

Maximizes collective welfare (NSWF product or EG weighted sum). **Distinction vs. QACM:** QoS-blind — can leave individual xApps below their thresholds while the aggregate looks good.

| Paper | File | Method / focus |
|---|---|---|
| Wadud et al., Conflict Management in the Near-RT-RIC: A Game Theoretic Approach (2023) | `../material/xapp-conflict-mitigation/2311.13389v1.pdf` | NSWF + EG solutions for shared-parameter conflicts; precursor to QACM. |

### QoS-Aware Optimization and SLA Projection

Adds explicit QoS thresholds to the game-theoretic objective; clips/projects actions to the feasible SLA region. **Distinction vs. pure bargaining:** minimizes weighted QoS deviation and maximizes the count of satisfied xApps.

| Paper | Summary | Method / focus |
|---|---|---|
| Wadud et al., QACM (2024) | `Rule-Based & SLA Constraint Projection/QACM-summary.md` | Weighted QoS-deviation objective + binary satisfaction indicators; handles direct/indirect/implicit conflicts; `https://arxiv.org/abs/2405.07324` |
| Rule-Based & SLA Constraint Projection template | `Rule-Based & SLA Constraint Projection/2405.07324v2.md` | Source paper for above. |

## Framework, Priority, and NDT-Guided Arbitration

Architecture-level arbitration: who decides, in what order, and with what pre-execution check. Lightweight and deployable without retraining xApps.

### Priority / Rule-Based Framework (CMF Baseline)

Static or dynamic priority scores; highest-priority proposal wins, others rejected. **Distinction vs. NDT/blending:** O(1) decision, no twin queries, but binary winner-takes-all — sacrifices the losing objective entirely.

| Paper | File | Method / focus |
|---|---|---|
| Adamczyk & Kliks, Conflict Mitigation Framework and Conflict Detection (2023) | `../material/xapp-conflict-mitigation/2305.07117v1.pdf` | CMF in Near-RT RIC: CD + CR modules, parameter groups, per-type detection flows; prioritization-based resolution. Also: `https://ieeexplore.ieee.org/document/10121578` |

### NDT-Guided Resolution Policies (COMIX)

Runs each candidate action through an NDT pre-execution and applies a scoring policy (MaxTS, MinPS, EES, TVS, EEVS). **Distinction vs. priority:** KPI-aware selection instead of fixed ranks; **vs. blending:** still picks one xApp's action rather than an intermediate compromise; assumes twin stays accurate.

| Paper | Summary | Method / focus |
|---|---|---|
| Giannopoulos et al., COMIX (2025) | `COMIX/summary.md` | NDT evaluates conflicting power-control actions; policy-specific winner selection; `https://arxiv.org/abs/2501.14619` |

### Twin-Fidelity-Aware Continuous Blending

Interpolates a continuous blend weight between proposals and gates twin usage on a live fidelity signal (EWMA prediction error) with fallback to a live-validated action. **Distinction vs. COMIX:** compromise action + explicit drift robustness instead of blind twin trust.

| Paper | Summary | Method / focus |
|---|---|---|
| Twin-Fidelity-Aware Resolution (2025) | `Continuous Action Blending/Twin-Fidelity-Aware-summary.md` | Blend α ∈ [0,1] over ES/CTO power; hard-switch on fidelity threshold τ; source: `Continuous Action Blending/2607.22857v1.md`, `https://arxiv.org/abs/2607.22857` |

## Detection, Prediction, and Context-Aware Scheduling

Avoids or predicts conflicts before / without resolving parameter values directly.

### GNN Dependency Mapping

Maps xApp–parameter–KPI–cell topology with inductive graph models to predict direct/indirect/implicit conflicts and root causes. **Distinction:** detection/prediction layer — tells *what will conflict*, not *which value to apply*; pairs with a downstream mitigator (e.g., QACM, scheduler).

| Paper | Summary | Method / focus |
|---|---|---|
| GRAPHICA (2025) | `Graph Neural Network (GNN) Dependency Mapping/GRAPHICA-summary.md` | GCN conflict prediction under class imbalance; source: `Graph Neural Network (GNN) Dependency Mapping/2503.03523v3.md`, `https://arxiv.org/abs/2503.03523` |

### Context-Aware Dynamic Scheduler (A2C)

Scheduler activates/deactivates xApps per scheduling period from context variables (speed, arrival rate) and operator intent — xApps stay immutable, no joint retraining. **Distinction vs. team learning:** coordination happens via *activation selection*, not shared policies; Method 2 adds baseline fallbacks for out-of-distribution contexts.

| Paper | Summary | Method / focus |
|---|---|---|
| Cinemre et al., xApp Conflict Mitigation with Scheduler (2025) | `Context-Aware Dynamic Schedulers/Scheduler-Conflict-Mitigation-summary.md` | A2C power + RBG xApps; scheduler Methods 1 (retain-last-action) / 2 (baseline pool) + confidence-gated fallback; source: `Context-Aware Dynamic Schedulers/2504.06867v3.md`, `https://arxiv.org/abs/2504.06867` |

## Cross-Cutting Reference

| Paper | File | Use |
|---|---|---|
| relevant-papers.md — common citations + RL-for-mitigation tiers | `relevant-papers.md` | 3 papers cited by all 5 (Polese survey, Adamczyk & Kliks CMF, Zhang team learning); Tier 1/2/3 RL reading list. |
