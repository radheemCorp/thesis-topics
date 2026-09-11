# Relevant Papers: Common Citations & RL for Conflict Mitigation

Analysis of the 5 papers in this collection:
- COMIX (2501.14619v1)
- GRAPHICA (2503.03523v3)
- QACM (2405.07324v2)
- Scheduler (2504.06867v3)
- Twin-Fidelity-Aware (2607.22857v1)

---

## Papers Cited by Multiple Papers (Common Citations)

### Cited by ALL 5 papers

| Paper | Cited In |
|---|---|
| **Polese et al., "Understanding O-RAN: Architecture, interfaces, algorithms, security, and research challenges"** (IEEE COMST, 2023) | COMIX[1], GRAPHICA[1], QACM[2], Scheduler[61], Twin-Fidelity[1] |
| **Adamczyk & Kliks, "Conflict mitigation framework and conflict detection in O-RAN Near-RT RIC"** (IEEE Commun. Mag., 2023) | COMIX[7], GRAPHICA[25], QACM[6], Scheduler[86], Twin-Fidelity[2] |
| **Zhang, Zhou & Erol-Kantarci, "Team learning-based resource allocation for O-RAN"** (ICC 2022) | COMIX[12], GRAPHICA[12], QACM[7], Scheduler[92], Twin-Fidelity[11] |

### Cited by 4 papers

| Paper | Cited In |
|---|---|
| **Wadud, Golpayegani & Afraz, "Conflict management in the Near-RT-RIC of Open RAN: A game theoretic approach"** (2023) | COMIX[11], GRAPHICA[13], QACM[1], Scheduler[91] |
| **del Prever et al., "PACIFISTA: Conflict evaluation and management in Open RAN"** (2024/25) | GRAPHICA[26], QACM[8], Scheduler[89], Twin-Fidelity[8] |

### Cited by 3 papers

| Paper | Cited In |
|---|---|
| **Wadud et al., "QACM: QoS-aware xApp conflict mitigation in Open RAN"** (2024) | GRAPHICA[14], Scheduler[90], Twin-Fidelity[10] |
| **Giannopoulos et al., "COMIX: Generalized conflict management in O-RAN xApps"** (2025) | GRAPHICA[33], Scheduler[88/120], Twin-Fidelity[5] |
| **Zolghadr et al., "Learning and reconstructing conflicts in O-RAN: A graph neural network approach"** (2024/25) | COMIX[19], GRAPHICA[15], Twin-Fidelity[17] |
| **Armstrong et al., "Pre-emptive conflict detection architecture for O-RAN SMO"** (2024) | COMIX[9], GRAPHICA[34], Twin-Fidelity[19] |
| **Yungaicela-Naula et al., "Misconfiguration in O-RAN: Analysis of the impact of AI/ML"** (2024) | COMIX[6], Scheduler[1], Twin-Fidelity[16] |
| **Erdol et al., "xApp distillation: AI-based conflict mitigation in B5G O-RAN"** (2024) | GRAPHICA[27], Scheduler[94], Twin-Fidelity[12] |
| **Wadud et al., "xApp-level conflict mitigation in O-RAN, a mobility driven energy saving case"** (2024/25) | COMIX[10], GRAPHICA[23], Twin-Fidelity[4] |
| **O-RAN WG3, "Near-RT RIC architecture"** (spec) | COMIX[8], QACM[5], Scheduler[84] |

---

## Papers Most Relevant to RL for Conflict Mitigation & Optimization

### Tier 1 — RL directly applied to xApp conflict mitigation

| Paper | Method | Relevance |
|---|---|---|
| **Zhang, Zhou & Erol-Kantarci, "Team learning-based resource allocation for O-RAN"** (ICC 2022) | DQN team learning | **Cited by all 5 papers** — the canonical RL conflict-mitigation baseline; xApps exchange actions and jointly optimize |
| **Erdol et al., "xApp distillation: AI-based conflict mitigation in B5G O-RAN"** (2024) | DQN distillation | Cited by 3 papers — consolidates multiple xApps into one DQN controller, eliminating inter-xApp conflicts |
| **Cinemre, Mahmoodi & Farzaneh, "xApp conflict mitigation with scheduler"** (2025) | A2C scheduler | The scheduler paper itself — context-aware A2C scheduler activates xApps without retraining |
| **Iturria-Rivera et al., "Multi-agent team learning in virtualized O-RAN"** (2022) | TMADRL | Extends team learning to multiple xApps controlling different RAN parameters |
| **He et al., "Digital twin-enhanced reinforcement learning for intelligent xApps management in O-RAN"** (2025) | DT + MARL | Combines digital twin with MARL for xApp management |
| **Perepu et al., "Intent-based multi-agent reinforcement learning for service assurance in cellular networks"** (GLOBECOM 2022) | Intent-based MARL | RL resource allocation driven by intent-defined priorities |

### Tier 2 — RL for RAN optimization (power/resource allocation, directly reusable)

| Paper | Method | Focus |
|---|---|---|
| **Nasir & Guo, "Multi-agent deep RL for dynamic power allocation in wireless networks"** (JSAC 2019) | MADRL | Power allocation |
| **Ahmed & Hossain, "A deep Q-learning method for downlink power allocation in multi-cell networks"** (2019) | DQN | Downlink power |
| **Yang et al., "Dynamic power allocation based on multi-agent double deep RL"** (2022) | DDQN | Power allocation |
| **Zhang et al., "Dynamic power allocation in power-domain NOMA using actor-critic RL"** (2018) | A2C | NOMA power |
| **Rahmani et al., "DRL-based power allocation in uplink cell-free massive MIMO"** (2022) | DRL | Cell-free MIMO |
| **Luo et al., "Downlink power control for cell-free massive MIMO with DRL"** (2022) | DRL | Cell-free MIMO |
| **Mollahasani et al., "Dynamic CU-DU selection for resource allocation in O-RAN using actor-critic learning"** (GLOBECOM 2021) | A2C | O-RAN resource allocation |
| **Meng et al., "Power allocation in multi-user cellular networks with deep Q learning"** (ICC 2019) | DQN | Power allocation |
| **Oh et al., "Multi-objective RL for power allocation in massive MIMO"** (2024) | MORL | Spectral/energy trade-off |
| **Giannopoulos et al., "Learning to fulfill user demands in 5G through power allocation: An RL approach"** (DRCN 2023) | RL | Power allocation |
| **Spantideas et al., "Joint energy-efficient and throughput-sufficient transmissions in 5G cells with deep Q-learning"** (2021) | DQN | Energy/throughput |
| **Giannopoulos et al., "DRL for energy-efficient multichannel transmissions in 5G cognitive HetNets"** (2021) | DRL | Energy efficiency |
| **Ahmadian et al., "Long-term throughput maximization in wireless powered networks: multi-task DRL"** (2024) | Multi-task DRL | Throughput |
| **Ullah et al., "Sum rate maximization in IoT networks with DRL-guided approach"** (2024) | DRL | Sum rate |
| **Bhattacharya et al., "A deep-Q learning scheme for secure spectrum allocation and resource management in 6G"** (2022) | DQN | Spectrum allocation |
| **Sun et al., "Combining DRL with GNNs for optimal VNF placement"** (2021) | DRL+GNN | VNF placement |

### Tier 3 — RL foundations (cited by the scheduler paper)

| Paper | Contribution |
|---|---|
| **Mnih, "Asynchronous methods for deep reinforcement learning"** (2016) | A3C — origin of A2C |
| **Konda & Tsitsiklis, "Actor-critic algorithms"** (1999) | Actor-critic foundations |
| **Williams, "Simple statistical gradient-following algorithms for connectionist RL"** (1992) | REINFORCE |
| **Sutton & Barto, "Reinforcement learning: An introduction"** (2018) | RL textbook |
| **Xu et al., "A comprehensive discussion on deep reinforcement learning"** (2021) | DRL survey |

---

## Summary

The three papers cited by all 5 papers (Polese O-RAN survey, Adamczyk & Kliks CMF, Zhang team learning) form the core canon. For RL-based conflict mitigation specifically, the key chain is **Zhang (team learning, 2022) → Erdol (distillation, 2024) → Cinemre (A2C scheduler, 2025)**, with **Iturria-Rivera (TMADRL)** and **He (DT+MARL)** as the strongest supporting works.